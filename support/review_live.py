"""Check required evidence against fixed test expectations, not agent claims."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    evidence = json.loads((ROOT / "verification/live-evidence.json").read_text(encoding="utf-8"))
    cases = {case["case"]: case for case in evidence["cases"]}
    checks = {"fresh_conversations": evidence["fresh_conversations"],
              "all_runs_completed": evidence["all_runs_completed"]}

    def finished(case, name):
        return [e for e in case["tools"] if e["tool_name"] == name and e["result"] is not None]

    for name in ("case-a-before-rename", "case-b-before-rename", "case-a-renamed", "case-b-renamed"):
        case = cases[name]
        is_a = name.startswith("case-a")
        neutral = name.endswith("renamed")
        policy = ("refund-alpha.md" if is_a else "refund-beta.md") if neutral else (
            "policy-before-oct.md" if is_a else "policy-from-oct.md")
        read_events = {e["result"].get("path"): e for e in finished(case, "read_file") if e["result"].get("ok")}
        listings = [e for e in finished(case, "list_files") if e["result"].get("ok") and e["result"].get("path") == "data/policies"]
        paths = ("skills/refund-policy/SKILL.md", "data/policies/" + policy,
                 "skills/refund-policy/references/answer-template.md")
        checks[name + "_discovery_and_reads"] = bool(listings) and all(p in read_events for p in paths)
        if checks[name + "_discovery_and_reads"]:
            checks[name + "_discovery_before_policy_read"] = listings[0]["sequence"] < read_events[paths[1]]["sequence"]
        answer = case["answer"].lower()
        checks[name + "_answer"] = (policy in answer and
            ("8 ngày" in answer and "không đủ điều kiện" in answer if is_a else
             "10 ngày" in answer and "đủ điều kiện" in answer and "không đủ điều kiện" not in answer
             and ("không thu phí" in answer or "không phí" in answer)))

    activation = cases["missing-activation"]
    checks["missing_activation_asks_without_conclusion"] = ("kích hoạt" in activation["answer"].lower()
        and "?" in activation["answer"] and "đủ điều kiện" not in activation["answer"].lower()
        and not finished(activation, "write_file"))
    expected_totals = {"Lan": 9, "Minh": 3}
    expected_excluded = [{"line": 5, "task_id": "T04", "reasons": ["invalid_hours"]},
                         {"line": 6, "task_id": "T02", "reasons": ["duplicate_id"]},
                         {"line": 7, "task_id": "T05", "reasons": ["missing_owner"]}]
    for limit in (8, 9):
        case = cases[f"threshold-{limit}"]
        results = [e["result"] for e in finished(case, "bash") if e["result"].get("exit_code") == 0]
        data = next((json.loads(result["stdout"]) for result in results if result["stdout"].lstrip().startswith("{")), {})
        checks[f"threshold_{limit}_script_json"] = (data.get("max_hours") == limit and data.get("hours_by_owner") == expected_totals
            and data.get("excluded_rows") == expected_excluded and data.get("overloaded_owners") ==
            ([{"owner": "Lan", "total_hours": 9}] if limit == 8 else []))
        reports = [e for e in finished(case, "write_file") if e["result"].get("ok") and e["result"].get("path") == "output/workload.md"]
        report = ROOT / "block-2/live-results" / f"threshold-{limit}-workload.md"
        checks[f"threshold_{limit}_report_written"] = bool(reports) and report.exists()
        if report.exists():
            text = report.read_text(encoding="utf-8")
            checks[f"threshold_{limit}_report_fields"] = all(word in text for word in
                ("Lan", "Minh", "9.0", "3.0", "invalid_hours", "duplicate_id", "missing_owner"))
    missing = cases["missing-threshold"]
    checks["missing_threshold_asks_without_execution"] = ("ngưỡng" in missing["answer"].lower()
        and not finished(missing, "bash") and not finished(missing, "write_file"))
    missing = cases["missing-file"]
    checks["missing_file_preflight_error_no_report"] = (any(not e["result"].get("ok") for e in finished(missing, "read_file"))
        and "FILE_NOT_FOUND" in missing["answer"] and not finished(missing, "write_file"))
    missing = cases.get("missing-file-script", {"tools": []})
    checks["missing_file_script_exit_error_no_report"] = (any(e["result"].get("exit_code", 0) != 0
        and e["result"].get("stderr") and not e["result"].get("stdout") for e in finished(missing, "bash"))
        and not finished(missing, "write_file"))
    output = {"checks": checks, "all_passed": all(checks.values()),
              "scope": "Single observed run per case; fixed evidence assertions, not a reliability benchmark.",
              "baseline_observations": "Stage 00 cannot access policy; Stage 03 needed 3 SyntaxError retries then returned correct totals."}
    (ROOT / "verification/live-semantic-review.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 0 if output["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
