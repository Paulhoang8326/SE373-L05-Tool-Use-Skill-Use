# Live traces

Có trace live thật do Observer/TraceWriter của lab tạo bằng Google Gemini.
Không dùng mock tests làm trace nộp bài.

JSONL gồm baseline, A/B trước và sau rename, missing activation.
block-1/live-results/*.json map case với trace filename và câu trả lời thật.
Các lượt lỗi quota/metadata vẫn được giữ; verification/live-evidence.json
liệt kê failed_attempts riêng. Analysis chỉ rõ trace hoàn chỉnh dùng kết luận.
