# SE373 L05 Tool Use and Skill Use

Bài thực hành môn Kỹ thuật xây dựng hệ thống Agentic AI, gồm hai block:

- Block 1: bổ sung `list_files` và skill `refund-policy` để phát hiện tài liệu chính sách, lựa chọn theo ngày mua và hỏi lại khi thiếu thông tin.
- Block 2: mở rộng skill `csv-quality` để tính tổng giờ hợp lệ theo người, xác định quá tải theo `--max-hours` và loại dòng theo quy tắc xác định.

Repository giữ mã nguồn, kiểm thử và bằng chứng kỹ thuật. Không chứa báo cáo
tổng hợp PDF/DOCX, ảnh báo cáo, ZIP nộp bài hoặc API key. Các file
`analysis.md` là phân tích kỹ thuật; `workload.md` là kết quả thực tế do agent tạo.

## Cấu trúc

```text
block-1/
  stage-00-chat/             # Baseline nguyên bản
  stage-01-files/            # File tools và list_files
  stage-02-skills/           # Refund skill, policies, references
  traces/                   # JSONL gốc, gồm lượt lỗi được lưu riêng
  live-results/             # Ánh xạ case, câu trả lời và trace
  analysis.md
block-2/
  stage-03-bash/             # Baseline Bash
  stage-04-script-skill/     # CSV script, skill, fixtures và tests
  results/                  # JSON trực tiếp và metadata thực thi
  live-results/             # Kết quả trực tiếp, báo cáo do agent tạo
  traces/
  analysis.md
support/                    # Helper kiểm thử và tương thích provider
verification/               # Logs và đối chiếu bằng chứng đã chạy
REQUIREMENT_MATRIX.md
original-hashes.json
```

## Cài đặt và kiểm thử

Sử dụng Python >=3.11 trên Linux hoặc WSL. Bash tool của lab yêu cầu POSIX;
không chạy các Stage có Bash bằng Windows Python.

Mỗi Stage có `pyproject.toml` riêng. Từ repository root trong WSL:

```bash
cd block-1/stage-02-skills
uv sync --group dev
uv run pytest -q -ra
```

Thực hiện tương tự trong Stage 01, Stage 03 và Stage 04. Bằng chứng kiểm thử
được sao chép từ bài đã kiểm chứng: Stage 01/02/03/04 lần lượt có
47/56/48/74 passed, tổng 225 passed, 0 failed, 0 skipped. Đây là kết quả
đã ghi nhận tại workspace gốc, không phải một lần chạy mới trên checkout này.
Lệnh và đường dẫn trong các log/JSON metadata lịch sử được giữ nguyên.

## Cấu hình model

Các Stage có `.env.example` chỉ chứa tên biến và giá trị trống. Cấu hình
`OPENAI_API_KEY`, `MODEL_NAME` và tùy chọn `OPENAI_BASE_URL` trong môi trường
hoặc `.env` cục bộ của Stage. Không commit credential. Các kiểm thử giả lập
không yêu cầu gọi API; sử dụng UI hoặc chạy live sẽ gửi nội dung bài tới provider.

## Mở UI

Sau khi cài dependencies và cấu hình model, từ thư mục Stage 02:

```bash
uv run streamlit run app.py --server.port 8511
```

Stage 04 dùng port 8512. Mở `http://localhost:8511` hoặc
`http://localhost:8512`. Nếu thiếu cấu hình, app khóa ô chat.

Với Gemini 3, helper `support/launch_ui.py` giữ nguyên metadata tool-call do
provider trả về; không tạo chữ ký giả hoặc sửa source agent/tool của Stage.
Helper hiện chọn `gemini-3.5-flash-lite`. Từ repository root:

```bash
uv run --project block-1/stage-02-skills python support/launch_ui.py --stage block-1/stage-02-skills --env-file /path/to/private.env --port 8511 --trace-dir block-1/traces/local-ui
```

Không dùng tên model này cho provider khác. Chi tiết adapter nằm trong
`support/gemini_transport.py`, có kiểm thử tại `support/test_gemini_transport.py`.

## Tái chạy bằng chứng

Từ repository root, dùng môi trường Stage 04 đã cài dependencies và pytest:

```bash
uv run --project block-2/stage-04-script-skill python support/verify.py
uv run --project block-2/stage-04-script-skill python support/run_live.py --env-file /path/to/private.env
```

`verify.py` chạy đầy đủ bốn suite và tạo kết quả tool/script trực tiếp.
`run_live.py` gọi provider thật, chạy các case trong hội thoại mới và kiểm tra
đổi tên policy. Stage 00 được đặt trong repository để helper không phụ thuộc
thư mục lab gốc bên ngoài. Chỉ đường dẫn baseline trong helper được điều chỉnh;
source agent/tool/skill/script/tests giữ nguyên.

Các helper này ghi lại logs/results ở các đường dẫn hiện có, nên tạo branch
riêng trước khi tái chạy nếu cần giữ nguyên snapshot bằng chứng.

## Kết quả đã xác nhận

- Case A: 8 ngày, không đủ điều kiện; Case B: 10 ngày, đủ điều kiện, không phí.
- Đổi tên policy không làm thay đổi kết quả; thiếu kích hoạt thì hỏi lại.
- Ngưỡng 8: Lan=9, Minh=3, chỉ Lan quá tải; ngưỡng 9: không ai quá tải.
- Trường hợp đặc biệt: Minh=0; ID được ghi nhận từ lần đầu kể cả khi dòng lỗi.
- Thiếu ngưỡng: hỏi lại; file không tồn tại: báo lỗi, không bịa số liệu/báo cáo.

Xem `block-1/analysis.md`, `block-2/analysis.md` và
`verification/TRACE_VERIFICATION.md` để đối chiếu từng case với JSONL thực tế.
`verification/final-checks.json` và `original-hashes.json` ghi nhận audit của
bài nộp gốc; không phải audit filesystem của checkout mới. Requirement matrix
nhóm các yêu cầu thành Block 1 24/24 và Block 2 25/25.

Nguồn yêu cầu: [Block 1](https://pub.nndkhoa9.win/agentic-ai-engineering/d05-tool-use-skill-use/exercise-block-1.html)
và [Block 2](https://pub.nndkhoa9.win/agentic-ai-engineering/d05-tool-use-skill-use/exercise-block-2.html).
