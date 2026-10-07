"""Run one fresh conversation using the lab agent, Observer and TraceWriter."""

import argparse
import json
import os
from pathlib import Path
import sys
import time
import uuid

sys.dont_write_bytecode = True
_last_request = 0.0


def pace_request(request):
    global _last_request
    interval = float(os.environ.get("LIVE_REQUEST_INTERVAL", "0"))
    delay = interval - (time.monotonic() - _last_request)
    if delay > 0:
        time.sleep(delay)
    _last_request = time.monotonic()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--trace-dir", type=Path, required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.stage.resolve()))
    import paths
    from agent import build_agent, build_model, capabilities
    from config import load_settings, PROJECT_NAME, RECURSION_LIMIT
    from langchain_core.messages import AIMessage, HumanMessage
    from observer import Observer
    from trace import TraceWriter

    settings, missing = load_settings()
    if missing:
        print("Missing configuration: " + ", ".join(missing), file=sys.stderr)
        return 2
    paths.TRACES_DIR = args.trace_dir.resolve()
    observer = Observer(conversation_id=uuid.uuid4().hex)
    observer.start_turn(uuid.uuid4().hex)
    writer = TraceWriter(paths.TRACES_DIR, PROJECT_NAME, observer.conversation_id, observer.run_id, observer.chat_turn)
    messages = [HumanMessage(content=args.prompt)]

    def emit(kind, data):
        writer.write(observer.record(kind, data))

    caps = capabilities()
    emit("user_submitted", {"text": args.prompt, "tools": caps["tools"], "skills": caps["skills"]})
    observer.sync_messages(messages)
    error = None
    try:
        model = build_model(settings)
        transport = None
        if settings.model_name.startswith("gemini-3"):
            model.reasoning_effort = os.environ.get("LIVE_REASONING_EFFORT", "minimal")
            import httpx
            from gemini_transport import GeminiMetadataTransport
            transport = GeminiMetadataTransport()
            client = httpx.Client(transport=transport)
            model.root_client = model.root_client.with_options(http_client=client)
            model.client = model.root_client.chat.completions
        if float(os.environ.get("LIVE_REQUEST_INTERVAL", "0")) > 0:
            model.root_client._client.event_hooks["request"].append(pace_request)
        graph = build_agent(model)
        for mode, chunk in graph.stream(
            {"messages": messages}, config={"recursion_limit": RECURSION_LIMIT},
            stream_mode=["updates", "custom"],
        ):
            if mode == "custom" and isinstance(chunk, dict) and chunk.get("observer"):
                emit(chunk["event"], chunk["data"])
            elif mode == "updates" and isinstance(chunk, dict):
                for update in chunk.values():
                    if isinstance(update, dict) and update.get("messages"):
                        messages.extend(update["messages"])
                        observer.sync_messages(messages)
        answer = next((m.content for m in reversed(messages) if isinstance(m, AIMessage) and not m.tool_calls), "")
        emit("run_completed", {"answer_chars": len(str(answer)),
                               "provider_metadata_restored_calls": transport.restored_calls if transport else 0})
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        for secret in (settings.api_key,):
            if secret:
                error = error.replace(secret, "[REDACTED]")
        emit("run_failed", {"error": error})
        answer = ""
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_text(json.dumps({
        "prompt": args.prompt, "trace": str(writer.path), "answer": answer,
        "error": error, "conversation_id": observer.conversation_id,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"trace": str(writer.path), "error": error}, ensure_ascii=False))
    return 1 if error else 0


if __name__ == "__main__":
    sys.exit(main())
