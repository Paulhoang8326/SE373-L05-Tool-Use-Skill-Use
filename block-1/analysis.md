# Block 1 - Tra cứu chính sách đúng phiên bản

## 1. Stage 00

Source Stage 00 có TOOLS=[] và prompt nêu rõ không đọc/ghi/chạy lệnh.
Agent thiếu khả năng truy cập tài liệu chính sách. Câu trả lời suy đoán không
chứng minh đã tra tài liệu. Baseline live bằng gemini-2.5-flash đã chạy:
agent nói không có quyền truy cập policy nên không xác định eligibility.
Trace: 20261007-210823_f93a0a9b_turn01_f8e676f0.jsonl; không có tool call.

## 2. Cài đặt list_files

Ở bản sao Stage 01 và 02, tools/files.py có _list và tool list_files(path).
Tool dùng _resolve và _error hiện có. Chặn absolute POSIX/Windows, drive-relative
Windows, ~, mọi thành phần .. và symlink dẫn ra ngoài workspace.
Quy tắc tương đối được kiểm tra trên cả dấu / và backslash.
Nếu thư mục chứa symlink ra ngoài, tool trả lỗi và không trả partial listing.

Kết quả thành công có ok, path và items. Mỗi item có name, path tương đối,
type=file/directory. Chỉ đọc direct children, sort theo name. Không đọc content.
Thư mục trống hợp lệ trả items=[]; path là file hoặc không tồn tại trả error.
Tool được export trong tools/__init__.py và thêm vào TOOLS ở agent.py.
Không sửa system prompt để đưa filename hoặc business rules vào model.

## 3. refund-policy skill

Metadata YAML giúp catalog phát hiện refund-policy cùng weekly-report.
Initial system prompt chỉ chứa metadata, không chứa body/reference.
Agent phải tự đọc SKILL.md và reference bằng read_file. Automated tests xác nhận
tool content chỉ xuất hiện ở model request sau thao tác read thực tế.
Đây là mock plumbing test, không kiểm chứng model tự chọn skill.

Skill kiểm tra ba trường: ngày mua, ngày yêu cầu và activation.
Nếu thiếu, hỏi lại trước khi kết luận. Khi đủ, list data/policies, đọc các
candidate, chọn theo effective range trong nội dung và NGÀY MUA.
Tính chênh lệch ngày lịch theo ngày yêu cầu user, đối chiếu điều kiện đọc được,
rồi dùng answer-template. Không Bash, script hoặc filename hard-coded.
Policy và skill được đồng bộ vào fixtures để reset không mất bài làm.

## 4. Direct tool tests

Kết quả chi tiết: verification/stage-01-files-direct-tools.json và
verification/stage-02-skills-direct-tools.json, đường dẫn tính từ submission-d05.

| Test | Input | Expected | Actual | Pass |
|---|---|---|---|---|
| Thư mục hợp lệ | data/policies | Hai file, sorted, relative paths | refund-alpha.md, refund-beta.md; type=file; path=data/policies/... | PASS |
| Path là file | data/weekly_notes.md | NOT_A_DIRECTORY | NOT_A_DIRECTORY | PASS |
| Không tồn tại | data/missing | DIRECTORY_NOT_FOUND | DIRECTORY_NOT_FOUND | PASS |
| Traversal | ../outside | PATH_OUTSIDE_WORKSPACE | PATH_OUTSIDE_WORKSPACE | PASS |
| Absolute | /tmp/dummy | PATH_OUTSIDE_WORKSPACE | PATH_OUTSIDE_WORKSPACE | PASS |
| Home prefix | ~/dummy | PATH_OUTSIDE_WORKSPACE | PATH_OUTSIDE_WORKSPACE | PASS |

Pytest còn kiểm tra direct-only, types, schema và symlink escape bằng dummy data.
Không thử đọc secret hay file cá nhân.

## 5. Agent test cases

| Case | Kỳ vọng | Thực tế live | Trace | Trạng thái |
|---|---|---|---|---|
| A sau rename | Policy trước tháng 10; 8 ngày; không đủ | refund-alpha.md; 8 ngày; không đủ | 20261007-212439_ef587fcc_turn01_789e42d7.jsonl | PASS |
| B sau rename | Policy từ tháng 10; 10 ngày; đủ; không phí | refund-beta.md; 10 ngày; đủ; không thu phí | 20261007-212604_df36474c_turn01_379cee7a.jsonl | PASS |
| Missing activation | Hỏi đã/chưa kích hoạt; chưa kết luận | Hỏi trạng thái kích hoạt, chưa kết luận | 20261007-210927_e9c6f44e_turn01_85f0232d.jsonl | PASS |

Kết quả thực tế được đọc từ answer và đối chiếu tool events, không chỉ runner exit.

## 6. Rename test

Đã đổi policy-before-oct.md thành refund-alpha.md và policy-from-oct.md thành
refund-beta.md trong workspace và fixtures của cả hai bản sao.
verification/policy-rename-proof.json lưu hash trước/sau để kiểm tra nội dung.
Code, skill và prompt không đổi theo filename. Live trước rename:
A trace 20261007-212211_ac4d014a_turn01_10fc636e.jsonl chọn policy-before-oct.md,
8 ngày, không đủ; B trace 20261007-212326_b0be76f7_turn01_761e74d1.jsonl chọn
policy-from-oct.md, 10 ngày, đủ, không phí. Sau rename vẫn cùng kết luận,
nhưng dẫn tên trung tính đúng từ discovery. PASS trên các lượt quan sát này.
live_batch reuse imports nhưng tạo graph/Observer/history/conversation mới
mỗi case; initial history chỉ có HumanMessage. Không tái sử dụng policy cũ.

## 7. Missing-information test

Gemini hỏi: "Bạn có thể cho biết sản phẩm đã được kích hoạt chưa?"
Không kết luận eligibility. Trace thật:
20261007-210927_e9c6f44e_turn01_85f0232d.jsonl. PASS live.
Không dùng scripted response trong tests làm bằng chứng cho case này.

## 8. Trace evidence

Vị trí event/sequence, prompt, action, result và final answer cho mỗi trace:
verification/TRACE_VERIFICATION.md (tính từ submission-d05). Summary được tạo
từ JSONL hiện có, không viết lại trace và không dùng screenshot thay evidence.

Các required JSONL thật có trong traces/. live-results/*.json map case với trace.
verification/live-evidence.json tóm tắt model/tool/answer và các lượt lỗi trước.
Gemini 2.5 Flash gặp quota 5 request/phút và 20/ngày. Retry bằng Gemini 3.5
Flash Lite ban đầu lỗi thought_signature; harness giữ nguyên extra_content từ
provider cho đúng tool-call ID, rồi cả A/B trước/sau rename chạy hoàn chỉnh.
Không dùng chữ ký giả, không thay agent/tool/system prompt hoặc business logic.
Trace là snapshot ở lớp LangChain; provider metadata được transport chuyển tiếp
sau lớp này. Gemini 3 retry dùng minimal reasoning và request pacing 15 giây.

Đã đối chiếu:
- Initial model_request có refund-policy metadata và list_files schema.
- tool_started/tool_finished đọc skills/refund-policy/SKILL.md.
- list_files data/policies trả filename trung tính.
- read_file đọc policy chứa đúng effective range theo ngày mua.
- read_file đọc answer-template.md, nội dung xuất hiện ở model request tiếp.
- Final answer A=8 ngày, không đủ; B=10 ngày, đủ, no fee.
- Missing activation hỏi lại và chưa kết luận eligibility.

## 9. Pytest results

Trong cwd từng stage, command: ../../../.runtime/venv/bin/python -m pytest -q -ra
(POSIX/WSL). Log và command tuyệt đối được lưu ở verification/.

| Stage | Kết quả |
|---|---|
| Stage 01 | 47 passed, 0 failed, 0 skipped |
| Stage 02 | 56 passed, 0 failed, 0 skipped |

Tests dùng ScriptedChatModel hoặc tools thật trong temporary workspace.
Không phải live provider evaluation.
Toàn bộ test suite Stage 01–04 đã được chạy và đạt 225 passed, 0 failed,
0 skipped. Sau phase live validation chỉ bổ sung harness/tài liệu, không
thay đổi implementation; 2 transport tests bổ sung cũng đạt.

## 10. Câu hỏi cuối bài

Tool cung cấp capability truy cập filesystem thật: list_files biết các file
đang tồn tại sau rename; read_file lấy nội dung hiện tại.
Skill cung cấp procedure: cần thông tin nào, khi nào tìm/đọc, cách chọn policy
theo effective range và cách trình bày căn cứ.

Sửa prompt không tự tạo khả năng enumerate directory. Nếu model chỉ đọc file
với path biết trước, nhắc “hãy tìm policy” không giúp nó biết filename mới.
Tool và skill cần phối hợp; metadata/body không thay thế kết quả tool thật.
