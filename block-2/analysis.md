# Block 2 - Kiểm tra quá tải theo người

## 1. Stage 03 baseline

Bản sao Stage 03 chỉ bổ sung workload.csv vào workspace và fixtures.
Agent và tools giữ nguyên. Baseline gemini-2.5-flash đã tự viết Python qua
Bash và trả Lan=9, Minh=3; bỏ line 5 invalid hours, line 6 duplicate và line 7
missing owner. Trace: 20261007-211001_1b9a7ace_turn01_8db1e5a5.jsonl.
Agent mất ba lệnh Bash exit=1 do lỗi quote/SyntaxError trước khi lệnh thứ tư
exit=0. Stage 04 gọi script có sẵn, tránh việc viết lại logic và shell quoting.
Lan=14 là tình huống giả định trong đề nếu cộng cả dòng trùng, không phải
kết quả quan sát ở lần chạy này. Baseline đúng trên CSV này không chứng minh
code model tự viết có đủ contract/edge-case tests như script Stage 04.
Duplicate guard ở tool_started sequence 20 là
`if task_id and task_id in processed_task_ids:`, sau đó in thông báo và
`continue`; tool_finished sequence 21 trả exit=0. Toàn bộ lệnh có trong JSONL
và verification/TRACE_VERIFICATION.md. Lệnh chỉ thêm ID vào set sau khi hours
đã parse hợp lệ, nên không đáp ứng first-invalid reservation của edge case;
`int(hours_str)` cũng chưa phải finite nonnegative parser đầy đủ như Stage 04.

## 2. Thay đổi check_csv.py

Tái sử dụng csv.reader(strict=True), parse_hours, first_seen, issues và
InputError. Giữ các trường quality cũ. Bổ sung reasons theo canonical order,
excluded_rows một mục cho mỗi dòng bị loại, totals theo owner và quá tải.
Không sửa agent.py hoặc tools, không thêm capability.
Script chỉ đọc CSV, không ghi đè input.

## 3. CLI --max-hours

Parameter bắt buộc, parse bằng rule số hữu hạn không âm.
Thiếu, invalid string, NaN/Infinity hoặc âm trả stderr và exit khác 0.
Zero hợp lệ. Ngưỡng không có mặc định. Không hard-code ngưỡng đề.

## 4. Duplicate và excluded rows

Trim task_id, owner, hours; giữ nguyên hoa/thường tên owner.
Mỗi ID không rỗng reserve từ lần xuất hiện đầu, kể cả dòng đó invalid hoặc
sai số trường. Lần sau duplicate, không dùng “first valid occurrence”.
Chỉ cộng khi đủ trường, ID/owner không rỗng, hours hữu hạn không âm và ID chưa gặp.
Dòng blank bị bỏ qua như source gốc. Mọi lý do của một dòng được giữ, theo:
wrong_field_count, missing_task_id, duplicate_id, missing_owner, invalid_hours.
Quality counters vẫn xét toàn bộ data rows.

## 5. JSON output

Giữ input, row_count, missing_owner_count, invalid_hours_count,
duplicate_id_count, duplicate_ids, issues. Thêm max_hours, hours_by_owner,
overloaded_owners và excluded_rows.
Owner object và overload list sorted theo owner; excluded sorted theo line.
ID rỗng là null. Overload dùng total_hours > max_hours.
Phân tích thành công exit=0 dù có excluded rows hoặc người quá tải.
Totals vượt miền biểu diễn float hữu hạn báo InputError, không xuất JSON Infinity.

## 6. Threshold 8

Direct result: results/max-hours-8.json.
Expected theo đề: Lan=9, Minh=3, chỉ Lan vượt ngưỡng.
Dòng 5 invalid_hours, dòng 6 duplicate_id, dòng 7 missing_owner.
Execution metadata lưu command, exit và hash input trước/sau.
Thực tế direct JSON: Lan=9.0, Minh=3.0, chỉ Lan overloaded; excluded đúng ba
dòng và reasons trên. Exit=0, hash input trước/sau bằng nhau. PASS direct test.
Live gemini-2.5-flash cũng đã chạy script và ghi báo cáo thật:
live-results/threshold-8-workload.md, đủ totals/overload/excluded/quality fields.
Trace: 20261007-211112_4d28eff9_turn01_2caaa77c.jsonl. PASS live threshold 8.

## 7. Threshold 9

Direct result: results/max-hours-9.json.
Expected: totals/excluded giữ nguyên, overloaded_owners=[] vì bằng ngưỡng
không phải quá tải. Thực tế direct JSON giữ totals/excluded giống ngưỡng 8,
overloaded_owners=[], exit=0, hash input không đổi. PASS direct test.
Live gemini-3.5-flash-lite đã chạy `--max-hours 9`, nhận JSON đúng và ghi
live-results/threshold-9-workload.md. Trace:
20261007-211906_07fd1689_turn01_681de72f.jsonl. PASS live threshold 9.

## 8. Missing threshold

Skill hiện hướng dẫn hỏi lại và không lấy threshold từ yêu cầu cũ.
Live agent đọc SKILL.md rồi hỏi ngưỡng; không gọi Bash, không tự chọn 8 và
không kết luận overload. Trace:
20261007-212008_dc2a0836_turn01_4a72b37b.jsonl. PASS live.
CLI missing parameter được kiểm tra riêng bằng automated tests.

## 9. File not found

Direct execution metadata: results/missing-file-execution.json.
Thực tế script exit=1, stdout rỗng, stderr "Không đọc được file ...:
No such file or directory". PASS direct test.
Agent phải báo không phân tích được, không bịa totals hoặc successful report;
Live prompt thông thường trả FILE_NOT_FOUND qua read_file và hỏi kiểm tra path,
không bịa totals, không ghi report. Trace:
20261007-212036_ca972e98_turn01_98129277.jsonl. Đây là preflight file-tool error,
không phải bằng chứng Bash exit!=0. Case bổ sung chỉ định skill/script đã đọc
SKILL.md và chạy Bash với --max-hours 8: exit=1, stdout rỗng, stderr file không
tồn tại; agent báo không thể tạo report thành công. Không có write_file.
Trace: 20261007-212858_c1f1ffb2_turn01_a6ba278d.jsonl. PASS script-error branch.

## 10. Edge case first-invalid duplicate

Input workload-edge.csv có E01 lần đầu abc, lần hai 5, E02 Minh 0.
Expected và automated assertion: hours_by_owner={Minh:0}, overload=[].
Excluded line 2 invalid_hours, line 3 duplicate_id. Không cộng 5 cho Lan.
Direct JSON: results/edge-max-hours-0.json. Thực tế đúng kỳ vọng trên, exit=0,
hash input không đổi. Automated test pass trong full suite.

## 11. Automated tests

tests/test_workload.py bao phủ threshold required/invalid/non-finite/negative,
zero, totals, > và equality, missing owner, duplicate, nhiều reasons,
ordering, whitespace, owner case, first-invalid và first-wrong-count ID,
file-not-found, input immutability và reset.
Giữ tests cũ, chỉ thêm --max-hours vào lời gọi CLI trong tests phù hợp contract mới.
Skill/script/reference được sync byte-identical vào fixtures.

## 12. Trace evidence

Vị trí event/sequence, prompt, action, result và final answer cho mỗi trace:
verification/TRACE_VERIFICATION.md (tính từ submission-d05). Summary được tạo
từ JSONL hiện có, không viết lại trace và không dùng screenshot thay evidence.

Trace thật (đường dẫn trong block-2/traces). Kết quả đã đối chiếu:

| Case | Kỳ vọng | Live thực tế | Trace |
|---|---|---|---|
| Threshold 8 | Lan 9, Minh 3, chỉ Lan quá tải; write workload.md | PASS; script JSON và báo cáo đúng | 20261007-211112_4d28eff9_turn01_2caaa77c.jsonl |
| Threshold 9 | Không ai quá tải | PASS; totals/excluded không đổi | 20261007-211906_07fd1689_turn01_681de72f.jsonl |
| Missing threshold | Hỏi ngưỡng trước khi kết luận | PASS; không Bash/write | 20261007-212008_dc2a0836_turn01_4a72b37b.jsonl |
| Missing file | Tool error; không bịa totals | PASS preflight FILE_NOT_FOUND; không Bash/write | 20261007-212036_ca972e98_turn01_98129277.jsonl |
| Missing file script | Bash exit!=0/stderr; không report | PASS exit=1, stderr, không write | 20261007-212858_c1f1ffb2_turn01_a6ba278d.jsonl |

support/live_batch.py dùng agents/Observer/TraceWriter thật, reuse imports trong
một stage nhưng mỗi case có graph/history/conversation_id mới.
live-results/*.json map case với trace.
Report do agent ghi được giữ riêng theo threshold để không bị overwrite.
Runner exit=0 chưa xác nhận semantic correctness; phải đọc trace và report.
Các lượt trước bị Gemini 2.5 quota (5 request/phút, 20/ngày) được giữ trong
verification/live-evidence.json. Gemini 3.5 Flash Lite dùng transport chỉ giữ
metadata provider-returned, không sửa agent/tool/prompt. Trace là ở lớp LangChain,
không phải HTTP wire log. Đây là single-case observation, không phải benchmark.

## 13. Pytest results

Full suites Stage 03 và 04 chạy bằng Python POSIX. Logs ở verification/.
Command từ cwd stage: ../../../.runtime/venv/bin/python -m pytest -q -ra.
Stage 03: 48 passed, 0 failed, 0 skipped (109.76s).
Stage 04: 74 passed, 0 failed, 0 skipped (135.86s).
Không có warning summary trong output pytest. WSL có cảnh báo khởi tạo
systemd user session lúc setup runtime, nhưng không ngăn tests/Python/Bash chạy.
Toàn bộ test suite Stage 01–04 đã được chạy và đạt 225 passed, 0 failed,
0 skipped. Sau phase live validation chỉ bổ sung harness/tài liệu, không
thay đổi implementation; 2 transport tests bổ sung cũng đạt.

## 14. Câu hỏi cuối bài

Script chịu trách nhiệm deterministic computation: parse, validation,
tracking ID, totals, overload, exclusion reasons và JSON.
Model hiểu yêu cầu, hỏi ngưỡng khi thiếu, truyền arguments, đọc JSON và
diễn giải thành báo cáo cho người dùng. Skill/reference nối quy trình với
output contract.

Nếu chỉ sửa script mà giữ skill/reference cũ, model có thể không truyền
--max-hours, tự đoán ngưỡng, bỏ fields mới, không liệt kê excluded rows,
hoặc giữ kết luận cũ rằng không được tính totals khi còn quality issues.
Cần cập nhật cả ba phần và kiểm tra báo cáo dựa trên JSON thực tế.
