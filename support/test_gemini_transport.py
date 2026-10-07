import json
import unittest
import httpx
from gemini_transport import GeminiMetadataTransport


class TransportTests(unittest.TestCase):
    def test_exact_metadata_roundtrip(self):
        requests = []
        extra = {"google": {"thought_signature": "test-provider-metadata"}}

        def respond(request):
            requests.append(json.loads(request.read()))
            return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [
                {"id": "call-1", "extra_content": extra}]}}]})

        transport = GeminiMetadataTransport()
        transport.inner.close()
        transport.inner = httpx.MockTransport(respond)
        with httpx.Client(transport=transport) as client:
            client.post("https://example.invalid/chat/completions", json={"messages": []})
            client.post("https://example.invalid/chat/completions", json={"messages": [{
                "role": "assistant", "tool_calls": [{"id": "call-1", "function": {"name": "read_file"}}]}]})
        self.assertEqual(requests[1]["messages"][0]["tool_calls"][0]["extra_content"], extra)
        self.assertEqual(transport.restored_calls, 1)

    def test_unknown_id_does_not_invent_metadata(self):
        requests = []

        def respond(request):
            requests.append(json.loads(request.read()))
            return httpx.Response(200, json={"choices": []})

        transport = GeminiMetadataTransport()
        transport.inner.close()
        transport.inner = httpx.MockTransport(respond)
        with httpx.Client(transport=transport) as client:
            client.post("https://example.invalid/chat/completions", json={"messages": [{
                "tool_calls": [{"id": "unknown"}]}]})
        self.assertNotIn("extra_content", requests[0]["messages"][0]["tool_calls"][0])
        self.assertEqual(transport.restored_calls, 0)


if __name__ == "__main__":
    unittest.main()
