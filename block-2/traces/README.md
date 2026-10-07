# Live traces

Có trace live thật do Observer/TraceWriter của lab tạo bằng Google Gemini.
Không dùng direct-script JSON hoặc mock tests thay cho trace agent.

JSONL gồm Stage 03 baseline, threshold 8/9, missing threshold, missing file,
và case bổ sung missing-file-script kiểm tra exit/stderr qua Bash.
block-2/live-results/*.json map từng case với trace filename.
Agent-generated reports threshold 8/9 được giữ riêng trong live-results.
Các lượt quota error được giữ; verification/live-evidence.json tách riêng
failed_attempts, không dùng các lượt lỗi làm kết quả đã đạt.
