# Báo cáo chất lượng và workload: `{input}`

Công cụ: `skills/csv-quality/scripts/check_csv.py` | exit code: {exit_code}

## Ngưỡng và tổng giờ

Ngưỡng người dùng cung cấp: {max_hours} giờ. Quá tải khi tổng > ngưỡng.

| Owner | Tổng hours từ các dòng được cộng |
|---|---|
| {owner từ hours_by_owner} | {total} |

## Người quá tải

{Owner và total_hours từ overloaded_owners; nếu rỗng: không ai vượt ngưỡng.}

## Các dòng bị loại

| Line | task_id | Reasons |
|---|---|---|
| {line} | {task_id hoặc null} | {tất cả reasons theo thứ tự JSON} |

Mã lý do: wrong_field_count (sai số trường), missing_task_id (thiếu ID),
duplicate_id (ID đã xuất hiện), missing_owner (thiếu người),
invalid_hours (giờ không phải số hữu hạn không âm).

## Tổng quan chất lượng

| Chỉ số | Giá trị |
|---|---|
| Số dòng dữ liệu không trống | {row_count} |
| Dòng thiếu owner | {missing_owner_count} |
| Dòng hours không hợp lệ | {invalid_hours_count} |
| Số ID trùng distinct | {duplicate_id_count}: {duplicate_ids} |

## Chi tiết lỗi

| Line | Cột | Loại | task_id | Mô tả |
|---|---|---|---|---|
| {line} | {column} | {type} | {task_id} | {message} |

## Đánh giá và khuyến nghị

Totals phản ánh các dòng hợp lệ được cộng, không gồm excluded_rows.
Mỗi ID chỉ xét lần đầu, kể cả lần đầu lỗi. Giữ nguyên hoa/thường của owner.
{Khuyến nghị dựa trên issues; không tự sửa input.}
