import json
import subprocess
import sys

import pytest

import paths
from reset_workspace import reset_workspace

SCRIPT = paths.FIXTURES_DIR / "skills/csv-quality/scripts/check_csv.py"


def run(path, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(path), *args],
        capture_output=True, text=True, encoding="utf-8", timeout=10,
    )


def csv_file(tmp_path, content):
    path = tmp_path / "input.csv"
    path.write_text(content, encoding="utf-8")
    return path


@pytest.mark.parametrize("args", [(), ("--max-hours", "abc"), ("--max-hours", "-1"),
    ("--max-hours", "NaN"), ("--max-hours", "Infinity"), ("--max-hours", "-inf")])
def test_invalid_or_missing_threshold(tmp_path, args):
    result = run(csv_file(tmp_path, "task_id,owner,hours\nA,X,1\n"), *args)
    assert result.returncode != 0 and result.stderr and not result.stdout


@pytest.mark.parametrize("threshold,overloaded", [
    ("8", [{"owner": "Lan", "total_hours": 9.0}]), ("9", []),
])
def test_workload_totals_exclusions_and_quality(threshold, overloaded):
    path = paths.FIXTURES_DIR / "data/workload.csv"
    before = path.read_bytes()
    result = run(path, "--max-hours", threshold)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["hours_by_owner"] == {"Lan": 9, "Minh": 3}
    assert data["max_hours"] == float(threshold)
    assert data["overloaded_owners"] == overloaded
    assert data["excluded_rows"] == [
        {"line": 5, "task_id": "T04", "reasons": ["invalid_hours"]},
        {"line": 6, "task_id": "T02", "reasons": ["duplicate_id"]},
        {"line": 7, "task_id": "T05", "reasons": ["missing_owner"]},
    ]
    assert (data["row_count"], data["missing_owner_count"], data["invalid_hours_count"]) == (6, 1, 1)
    assert data["duplicate_ids"] == ["T02"] and data["duplicate_id_count"] == 1
    assert len(data["issues"]) == 3
    assert path.read_bytes() == before


def test_first_invalid_occurrence_reserves_id_and_zero_is_valid():
    result = run(paths.FIXTURES_DIR / "data/workload-edge.csv", "--max-hours", "0")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["hours_by_owner"] == {"Minh": 0}
    assert data["overloaded_owners"] == []
    assert data["excluded_rows"] == [
        {"line": 2, "task_id": "E01", "reasons": ["invalid_hours"]},
        {"line": 3, "task_id": "E01", "reasons": ["duplicate_id"]},
    ]


def test_trim_case_sensitivity_multiple_reasons_and_first_wrong_count(tmp_path):
    path = csv_file(tmp_path, "task_id,owner,hours\n A , Lan , 2 \nB,lan,3\nC,Zed,0\nA,,NaN,extra\n,,bad,extra\nD,Zed,1,extra\nD,Zed,4\n\n")
    data = json.loads(run(path, "--max-hours", "0").stdout)
    assert list(data["hours_by_owner"]) == ["Lan", "Zed", "lan"]
    assert data["hours_by_owner"] == {"Lan": 2, "Zed": 0, "lan": 3}
    assert [r["owner"] for r in data["overloaded_owners"]] == ["Lan", "lan"]
    assert data["excluded_rows"] == [
        {"line": 5, "task_id": "A", "reasons": ["wrong_field_count", "duplicate_id", "missing_owner", "invalid_hours"]},
        {"line": 6, "task_id": None, "reasons": ["wrong_field_count", "missing_task_id", "missing_owner", "invalid_hours"]},
        {"line": 7, "task_id": "D", "reasons": ["wrong_field_count"]},
        {"line": 8, "task_id": "D", "reasons": ["duplicate_id"]},
    ]
    assert data["row_count"] == 7 and data["duplicate_id_count"] == 2


def test_missing_file_error(tmp_path):
    result = run(tmp_path / "missing.csv", "--max-hours", "0")
    assert result.returncode == 1 and result.stderr and not result.stdout


def test_empty_owner_set_and_blank_lines(tmp_path):
    data = json.loads(run(csv_file(tmp_path, "task_id,owner,hours\n\nA,,1\nB,X,-1\n"), "--max-hours", "0").stdout)
    assert data["hours_by_owner"] == {} and data["overloaded_owners"] == []
    assert data["row_count"] == 2


def test_reset_preserves_updated_skill_script_reference_and_data(lab_dirs):
    files = ["skills/csv-quality/SKILL.md", "skills/csv-quality/scripts/check_csv.py",
             "skills/csv-quality/references/report-template.md", "data/workload.csv", "data/workload-edge.csv"]
    before = {p: (paths.WORKSPACE_DIR / p).read_bytes() for p in files}
    reset_workspace()
    assert before == {p: (paths.WORKSPACE_DIR / p).read_bytes() for p in files}
