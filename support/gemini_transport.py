"""Preserve provider-returned tool metadata stripped by ChatOpenAI conversion.

Only restores exact extra_content received for the same tool-call ID. Does not
invent signatures, tool calls, responses, or business rules.
"""

import json
import httpx


class GeminiMetadataTransport(httpx.BaseTransport):
    def __init__(self):
        self.inner = httpx.HTTPTransport()
        self.metadata = {}
        self.restored_calls = 0

    def handle_request(self, request):
        payload = json.loads(request.read())
        changed = False
        for message in payload.get("messages", []):
            for call in message.get("tool_calls", []):
                extra = self.metadata.get(call.get("id"))
                if extra is not None and "extra_content" not in call:
                    call["extra_content"] = extra
                    self.restored_calls += 1
                    changed = True
        if changed:
            headers = [(k, v) for k, v in request.headers.multi_items() if k.lower() != "content-length"]
            request = httpx.Request(request.method, request.url, headers=headers,
                                    content=json.dumps(payload).encode(), extensions=request.extensions)
        response = self.inner.handle_request(request)
        response.read()
        if response.status_code == 200:
            data = response.json()
            for choice in data.get("choices", []):
                for call in choice.get("message", {}).get("tool_calls", []):
                    if "extra_content" in call:
                        self.metadata[call["id"]] = call["extra_content"]
        return response

    def close(self):
        self.inner.close()
