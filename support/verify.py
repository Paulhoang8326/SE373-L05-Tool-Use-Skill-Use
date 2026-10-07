"""Run full suites and direct probes; no model calls or fabricated traces."""

import hashlib
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STAGES = [
    ROOT / "block-1/stage-01-files", ROOT / "block-1/stage-02-skills",
    ROOT / "block-2/stage-03-bash", ROOT / "block-2/stage-04-script-skill",
]


def child(stage, code):
    env = dict(os.environ, PYTHONPATH=str(stage), PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-c", code], cwd=stage, env=env,
                          capture_output=True, text=True, timeout=180)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--direct-only", action="store_true")
    args = parser.parse_args()
    evidence = ROOT / "verification"
    evidence.mkdir(exist_ok=True)
    runs = []
    for stage in ([] if args.direct_only else STAGES):
        cmd = [sys.executable, "-m", "pytest", "-q", "-ra"]
        result = subprocess.run(cmd, cwd=stage, capture_output=True, text=True, timeout=240)
        log = evidence / f"{stage.name}-pytest.txt"
        log.write_text(result.stdout + result.stderr, encoding="utf-8")
        runs.append({"stage": stage.name, "command": cmd, "cwd": str(stage),
                     "exit_code": result.returncode, "log": str(log.relative_to(ROOT))})
        print(stage.name, result.returncode, result.stdout[-1500:], result.stderr[-500:], flush=True)
    if runs:
        (evidence / "pytest-runs.json").write_text(json.dumps(runs, indent=2), encoding="utf-8")

    for stage in STAGES[:2]:
        probe = child(stage, """
import json
from tools import list_files
from observer import tool_schema
from agent import TOOLS
inputs = ["data/policies", "data/weekly_notes.md", "data/missing", "../outside", "/tmp/dummy", "~/dummy"]
print(json.dumps({"tools": [tool_schema(t) for t in TOOLS], "cases": [
    {"input": p, "result": json.loads(list_files.invoke({"path": p}))} for p in inputs
]}, ensure_ascii=False, indent=2))
""")
        if probe.returncode:
            raise RuntimeError(probe.stderr)
        (evidence / f"{stage.name}-direct-tools.json").write_text(probe.stdout, encoding="utf-8")

    stage = STAGES[-1]
    script = stage / "workspace/skills/csv-quality/scripts/check_csv.py"
    outdir = ROOT / "block-2/results"
    outdir.mkdir(exist_ok=True)
    for filename, threshold, output in [
        ("workload.csv", "8", "max-hours-8"), ("workload.csv", "9", "max-hours-9"),
        ("workload-edge.csv", "0", "edge-max-hours-0"), ("missing.csv", "8", "missing-file"),
    ]:
        source = stage / "workspace/data" / filename
        before = hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None
        command = [sys.executable, str(script), "--input", str(source), "--max-hours", threshold]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.stdout:
            (outdir / f"{output}.json").write_text(result.stdout, encoding="utf-8")
        (outdir / f"{output}-execution.json").write_text(json.dumps({
            "command": command, "exit_code": result.returncode, "stderr": result.stderr,
            "input_sha256_before": before,
            "input_sha256_after": hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(output, result.returncode, result.stdout[-1200:], flush=True)

    config = child(STAGES[1], """
import json
from config import load_settings
settings, missing = load_settings()
print(json.dumps({"configured": settings is not None, "missing_variables": missing}))
""")
    (evidence / "model-config-status.json").write_text(config.stdout, encoding="utf-8")
    print("MODEL CONFIG", config.stdout, flush=True)
    return 1 if any(r["exit_code"] for r in runs) else 0


if __name__ == "__main__":
    sys.exit(main())
