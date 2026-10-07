"""Reuse imports within one stage; each case creates a new graph and history."""

import argparse
import json
from pathlib import Path
import sys

import live_case
from run_live import rename


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--block", required=True)
    parser.add_argument("--cases", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    ok = True
    try:
        for item in cases:
            if "rename" in item:
                rename(args.stage, item["rename"])
                continue
            sys.argv = [
                "live_case.py", "--stage", str(args.stage),
                "--trace-dir", str(root / args.block / "traces"),
                "--prompt", item["prompt"], "--result",
                str(root / args.block / "live-results" / (item["name"] + ".json")),
            ]
            print("RUNNING", item["name"], flush=True)
            completed = live_case.main() == 0
            ok = completed and ok
            if item["name"].startswith("threshold-"):
                result_path = root / args.block / "live-results" / (item["name"] + ".json")
                result = json.loads(result_path.read_text(encoding="utf-8"))
                events = [json.loads(line) for line in Path(result["trace"]).read_text(encoding="utf-8").splitlines()]
                wrote = any(
                    e.get("type") == "tool_finished" and e.get("tool_name") == "write_file"
                    and isinstance(e.get("result"), dict) and e["result"].get("ok")
                    and e["result"].get("path") == "output/workload.md" for e in events
                )
                output = args.stage / "workspace/output/workload.md"
                if completed and wrote and output.exists():
                    (root / args.block / "live-results" / (item["name"] + "-workload.md")).write_bytes(output.read_bytes())
    finally:
        if any("rename" in item for item in cases):
            rename(args.stage, True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
