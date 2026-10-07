"""Summarize actual lab traces without synthesizing events or answers."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding="utf-8")


def main():
    cases = []
    failed_attempts = []
    for block in ("block-1", "block-2"):
        for trace in sorted((ROOT / block / "traces").glob("*.jsonl")):
            events = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]
            for event in events:
                if event["type"] == "run_failed":
                    failed_attempts.append({"trace": trace.relative_to(ROOT).as_posix(), "error": event["error"]})
        for path in sorted((ROOT / block / "live-results").glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            trace = ROOT / block / "traces" / Path(data["trace"]).name
            events = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]
            tools = [{key: event.get(key) for key in
                      ("sequence", "tool_name", "arguments", "result", "status")}
                     for event in events if event["type"] in ("tool_started", "tool_finished")]
            cases.append({
                "case": path.stem, "block": block, "trace": trace.relative_to(ROOT).as_posix(),
                "conversation_id": data["conversation_id"], "error": data["error"],
                "answer": data["answer"], "tools": tools,
                "model_requests": sum(e["type"] == "model_request" for e in events),
                "model": next((e["snapshot"]["model_name"] for e in events if e["type"] == "model_request"), None),
                "completed": any(e["type"] == "run_completed" for e in events),
            })
    output = {"provider": "Google Gemini", "models": sorted({c["model"] for c in cases}), "cases": cases,
              "failed_attempts": failed_attempts,
              "fresh_conversations": len({c["conversation_id"] for c in cases}) == len(cases),
              "all_runs_completed": bool(cases) and all(c["completed"] and not c["error"] for c in cases),
              "note": "Execution summary only; semantic checks require reading answers/tool results."}
    (ROOT / "verification/live-evidence.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    for case in cases:
        print(json.dumps({key: case[key] for key in ("case", "trace", "model_requests", "completed", "error", "answer")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
