import json

import pytest
from langchain_core.utils.function_calling import convert_to_openai_tool

from agent import TOOLS
from tools import list_files
from tools.files import _list


def test_direct_sorted_children_and_types(tmp_path):
    root = tmp_path / "workspace"
    (root / "data" / "z-folder").mkdir(parents=True)
    (root / "data" / "z-folder" / "nested.txt").write_text("nested")
    (root / "data" / "a.txt").write_text("a")
    assert _list(root, "data/") == {
        "ok": True, "path": "data", "items": [
            {"name": "a.txt", "path": "data/a.txt", "type": "file"},
            {"name": "z-folder", "path": "data/z-folder", "type": "directory"},
        ],
    }
    assert _list(root, ".")["items"][0]["path"] == "data"


@pytest.mark.parametrize("path", [
    "../outside", "data/../data", "data/../../outside", "/tmp/example",
    "~/example", r"C:\example", r"C:example", r"\\server\share", r"data\..\outside",
])
def test_unsafe_paths_rejected(tmp_path, path):
    assert _list(tmp_path, path)["error"]["code"] == "PATH_OUTSIDE_WORKSPACE"


def test_missing_file_and_empty_paths(lab_dirs):
    assert json.loads(list_files.invoke({"path": "missing"}))["error"]["code"] == "DIRECTORY_NOT_FOUND"
    assert json.loads(list_files.invoke({"path": "data/weekly_notes.md"}))["error"]["code"] == "NOT_A_DIRECTORY"
    assert json.loads(list_files.invoke({"path": ""}))["error"]["code"] == "INVALID_PATH"
    assert json.loads(list_files.invoke({"path": "output"}))["items"] == []


def test_absolute_and_symlink_escape(tmp_path):
    root = tmp_path / "workspace"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "dummy.txt").write_text("lab dummy")
    (root / "link").symlink_to(outside, target_is_directory=True)
    assert _list(root, str(outside))["error"]["code"] == "PATH_OUTSIDE_WORKSPACE"
    assert _list(root, "link")["error"]["code"] == "PATH_OUTSIDE_WORKSPACE"
    assert _list(root, ".")["error"]["code"] == "PATH_OUTSIDE_WORKSPACE"


def test_tool_schema_and_real_result(lab_dirs):
    schema = convert_to_openai_tool(next(t for t in TOOLS if t.name == "list_files"))["function"]
    assert schema["parameters"]["required"] == ["path"]
    assert schema["parameters"]["properties"]["path"]["type"] == "string"
    assert json.loads(list_files.invoke({"path": "data"}))["ok"]
