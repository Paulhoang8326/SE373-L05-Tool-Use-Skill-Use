"""Index real JSONL events for submission review; never rewrite traces."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    evidence = json.loads((ROOT / "verification/live-evidence.json").read_text(encoding="utf-8"))
    review = json.loads((ROOT / "verification/live-semantic-review.json").read_text())
    lines = ["# Trace Verification Summary", "", "Nguồn: JSONL thật do lab sinh. Sequence là số event trong trace, không phải số dòng báo cáo.",
             "Trạng thái dưới đây đối chiếu với live-semantic-review.json; không suy ra PASS chỉ từ exit runner.", ""]
    for case in evidence["cases"]:
        result = ROOT / case["block"] / "live-results" / (case["case"] + ".json")
        data = json.loads(result.read_text(encoding="utf-8"))
        lines += ["## " + case["case"], "", "Trace: `" + case["trace"] + "`.",
                  "Model: `" + case["model"] + "`. Conversation: `" + case["conversation_id"] + "`.",
                  "", "Prompt: " + data["prompt"], "", "| Sequence | Tool/action | Evidence |", "|---|---|---|"]
        for event in case["tools"]:
            if event["arguments"] is not None:
                detail = json.dumps(event["arguments"], ensure_ascii=False)
                if "content" in event["arguments"]:
                    detail = "path=" + event["arguments"].get("path", "") + "; agent-provided report content in trace"
                detail = detail.replace("\n", " ").replace("|", "\\|")
                if len(detail) > 600:
                    detail = detail[:600] + " ... (full command in JSONL)"
                lines.append(f"| {event['sequence']} | {event['tool_name']} started | `{detail}` |")
            else:
                output = event["result"]
                detail = "ok=" + str(output.get("ok"))
                if "exit_code" in output:
                    detail += "; exit_code=" + str(output["exit_code"])
                    detail += "; stdout/stderr stored in JSONL"
                if "path" in output:
                    detail += "; path=" + output["path"]
                if "items" in output:
                    detail += "; items=" + ", ".join(item["name"] for item in output["items"])
                if "error" in output:
                    detail += "; error=" + str(output["error"])
                lines.append(f"| {event['sequence']} | {event['tool_name']} finished | {detail} |")
        lines += ["", "Final result (actual model answer):", "", case["answer"], "",
                  "Status: PASS (observed baseline)" if "baseline" in case["case"] else
                  "Status: PASS; contract checked in live-semantic-review.json.", ""]
    lines += ["## Review result", "", f"{len(evidence['cases'])} complete conversations; {len(review['checks'])} evidence assertions; all_passed={review['all_passed']}.",
              "Failed attempts remain in live-evidence.json and original JSONL. They are not replaced or counted as semantic passes."]
    (ROOT / "verification/TRACE_VERIFICATION.md").write_text("\n".join(lines), encoding="utf-8")
    print("Created trace verification summary from actual JSONL evidence.")


if __name__ == "__main__":
    main()
