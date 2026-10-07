"""Run official cases with real credentials only. No mock responses."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
A = "Tôi mua ngày 28/09/2026, yêu cầu hoàn ngày 06/10/2026, chưa kích hoạt. Tôi có được hoàn không?"
B = "Tôi mua ngày 02/10/2026, yêu cầu hoàn ngày 12/10/2026, chưa kích hoạt. Tôi có được hoàn không?"


def case(stage, block, name, prompt):
    results = ROOT / block / "live-results"
    target = results / f"{name}.json"
    cmd = [sys.executable, str(ROOT / "support/live_case.py"), "--stage", str(stage),
           "--trace-dir", str(ROOT / block / "traces"), "--prompt", prompt, "--result", str(target)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    print(name, result.returncode, result.stdout.strip(), flush=True)
    if result.stderr:
        print(result.stderr[-1000:], file=sys.stderr)
    return result.returncode == 0


def rename(stage, to_neutral):
    for directory in ("workspace", "fixtures"):
        policies = stage / directory / "data/policies"
        for old, new in (("policy-before-oct.md", "refund-alpha.md"), ("policy-from-oct.md", "refund-beta.md")):
            source, dest = policies / (old if to_neutral else new), policies / (new if to_neutral else old)
            if source.exists() and dest.exists():
                raise RuntimeError("Both policy names exist; resolve before continuing.")
            if source.exists():
                before = hashlib.sha256(source.read_bytes()).hexdigest()
                source.rename(dest)
                assert hashlib.sha256(dest.read_bytes()).hexdigest() == before


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, help="Read credentials in place; never copy into submission.")
    args = parser.parse_args()
    if args.env_file:
        load_dotenv(args.env_file, override=False)
    for path in ("block-1/stage-02-skills/.env", "block-2/stage-04-script-skill/.env"):
        load_dotenv(ROOT / path, override=False)
    missing = [name for name in ("OPENAI_API_KEY", "MODEL_NAME") if not os.getenv(name, "").strip()]
    if missing:
        print("LIVE NOT RUN: missing " + ", ".join(missing), file=sys.stderr)
        return 2
    s2 = ROOT / "block-1/stage-02-skills"
    s3 = ROOT / "block-2/stage-03-bash"
    s4 = ROOT / "block-2/stage-04-script-skill"
    original = ROOT / "block-1/stage-00-chat"
    ok = case(original, "block-1", "stage-00-baseline", A)
    rename(s2, False)
    try:
        before = [case(s2, "block-1", "case-a-before-rename", A), case(s2, "block-1", "case-b-before-rename", B)]
    finally:
        rename(s2, True)
    ok = all(before) and ok
    for name, prompt in (
        ("case-a-renamed", A), ("case-b-renamed", B),
        ("missing-activation", "Tôi mua ngày 02/10/2026, muốn hoàn ngày 12/10/2026."),
    ):
        ok = case(s2, "block-1", name, prompt) and ok
    ok = case(s3, "block-2", "stage-03-baseline",
              "Dùng Python qua Bash để tính tổng hours theo owner trong data/workload.csv. Không chỉnh sửa file đầu vào. Cho biết cách xử lý dòng lỗi và task_id trùng.") and ok
    for name, prompt in (
        ("threshold-8", "Kiểm tra data/workload.csv, người nào vượt 8 giờ? Ghi báo cáo vào output/workload.md."),
        ("threshold-9", "Kiểm tra data/workload.csv, người nào vượt 9 giờ? Ghi báo cáo vào output/workload.md."),
        ("missing-threshold", "Tính tổng giờ theo người trong data/workload.csv và xác định người quá tải."),
        ("missing-file", "Kiểm tra data/khong-ton-tai.csv, người nào vượt 8 giờ? Ghi báo cáo vào output/missing.md."),
    ):
        completed = case(s4, "block-2", name, prompt)
        ok = completed and ok
        if name.startswith("threshold"):
            output = s4 / "workspace/output/workload.md"
            result_path = ROOT / "block-2/live-results" / f"{name}.json"
            result_data = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else {}
            trace_path = Path(result_data["trace"]) if result_data.get("trace") else None
            events = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()] if trace_path and trace_path.exists() else []
            wrote_report = any(
                e.get("type") == "tool_finished" and e.get("tool_name") == "write_file"
                and isinstance(e.get("result"), dict) and e["result"].get("ok")
                and e["result"].get("path") == "output/workload.md" for e in events
            )
            if completed and wrote_report and output.exists():
                saved = ROOT / "block-2/live-results" / f"{name}-workload.md"
                saved.write_bytes(output.read_bytes())
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
