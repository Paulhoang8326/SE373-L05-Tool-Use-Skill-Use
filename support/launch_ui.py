"""Launch unchanged Streamlit lab with task-local provider compatibility."""

import argparse
import os
from pathlib import Path
import sys

from dotenv import load_dotenv

sys.dont_write_bytecode = True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--port", required=True)
    parser.add_argument("--trace-dir", type=Path, required=True)
    args = parser.parse_args()
    load_dotenv(args.env_file)
    os.environ["MODEL_NAME"] = "gemini-3.5-flash-lite"
    os.environ["LIVE_REQUEST_INTERVAL"] = "15"
    stage = args.stage.resolve()
    trace_dir = args.trace_dir.resolve()
    os.chdir(stage)
    sys.path.insert(0, str(stage))
    import agent
    import paths
    import httpx
    from gemini_transport import GeminiMetadataTransport
    from live_case import pace_request
    from streamlit.web import cli

    original_build_model = agent.build_model

    def compatible_model(settings):
        model = original_build_model(settings)
        if settings.model_name.startswith("gemini-3"):
            client = httpx.Client(transport=GeminiMetadataTransport(),
                                  event_hooks={"request": [pace_request]})
            model.root_client = model.root_client.with_options(http_client=client, timeout=60.0, max_retries=1)
            model.client = model.root_client.chat.completions
            model.reasoning_effort = "minimal"
        return model

    agent.build_model = compatible_model
    paths.TRACES_DIR = trace_dir
    sys.argv = ["streamlit", "run", str(stage / "app.py"), "--server.port", args.port,
                "--server.address", "127.0.0.1", "--server.headless", "true",
                "--browser.gatherUsageStats", "false"]
    cli.main()


if __name__ == "__main__":
    main()
