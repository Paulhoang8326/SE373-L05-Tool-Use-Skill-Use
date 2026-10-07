---
name: csv-quality
description: Kiểm tra chất lượng CSV công việc (task_id, owner, hours), tính tổng giờ theo người và xác định quá tải (workload/overload) theo ngưỡng người dùng cung cấp, rồi ghi báo cáo Markdown dưới output/.
---

# CSV quality và workload

## Xác định dữ liệu và ngưỡng

1. Xác định đường dẫn CSV và ngưỡng từ YÊU CẦU HIỆN TẠI.
2. Nếu thiếu ngưỡng, hỏi lại trước khi chạy script hoặc kết luận quá tải.
   Không tự chọn mặc định và không lấy ngưỡng từ lượt/conversation cũ.
3. Ngưỡng phải là số hữu hạn không âm; nếu không hợp lệ, hỏi lại.

## Chạy script

Dùng tool `bash`, cwd là workspace:

```text
python skills/csv-quality/scripts/check_csv.py --input <CSV path> --max-hours <user_value>
```

Truyền chính xác ngưỡng user. Quote đường dẫn có khoảng trắng.
Không cần đọc source script để chạy. Không sửa CSV đầu vào.

## Kiểm tra kết quả

- `exit_code=0`: phân tích thành công dù có lỗi dữ liệu hoặc người quá tải.
  `stdout` là JSON gồm thống kê chất lượng cũ và `max_hours`,
  `hours_by_owner`, `overloaded_owners`, `excluded_rows`.
- Exit khác 0: đọc stderr, báo không phân tích được. Không bịa totals,
  không ghi successful report. `ok=false` hoặc timed_out cũng là lỗi thực thi.
- ID không rỗng giữ chỗ từ lần đầu, kể cả dòng đầu lỗi.
  Chỉ cộng dòng đủ trường, ID và owner, hours hữu hạn không âm, không trùng ID.
  Tổng bằng ngưỡng không phải quá tải.
- Thống kê chất lượng xét toàn bộ dòng dữ liệu; totals chỉ xét dòng được cộng.
  Mỗi dòng bị loại có tất cả reason codes trong `excluded_rows`.

## Viết báo cáo

1. Đọc `references/report-template.md`, tức
   `skills/csv-quality/references/report-template.md`.
2. Dùng mọi số liệu từ JSON. Không tự tính lại bằng logic khác.
3. Nêu ngưỡng, tổng theo owner, người quá tải, dòng bị loại kèm lý do,
   thống kê chất lượng và issues. Totals chưa phản ánh dòng bị loại.
4. Ghi bằng `write_file` vào path user yêu cầu (mặc định
   `output/csv-quality.md`), rồi trả đường dẫn và tóm tắt.
