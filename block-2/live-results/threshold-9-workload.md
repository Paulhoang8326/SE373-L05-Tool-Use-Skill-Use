# Báo cáo chất lượng và workload: `data/workload.csv`

Công cụ: `skills/csv-quality/scripts/check_csv.py` | exit code: 0

## Ngưỡng và tổng giờ

Ngưỡng người dùng cung cấp: 9.0 giờ. Quá tải khi tổng > ngưỡng.

| Owner | Tổng hours từ các dòng được cộng |
|---|---|
| Lan | 9.0 |
| Minh | 3.0 |

## Người quá tải

Không ai vượt ngưỡng.

## Các dòng bị loại

| Line | task_id | Reasons |
|---|---|---|
| 5 | T04 | invalid_hours |
| 6 | T02 | duplicate_id |
| 7 | T05 | missing_owner |

Mã lý do: wrong_field_count (sai số trường), missing_task_id (thiếu ID),
duplicate_id (ID đã xuất hiện), missing_owner (thiếu người),
invalid_hours (giờ không phải số hữu hạn không âm).

## Tổng quan chất lượng

| Chỉ số | Giá trị |
|---|---|
| Số dòng dữ liệu không trống | 6 |
| Dòng thiếu owner | 1 |
| Dòng hours không hợp lệ | 1 |
| Số ID trùng distinct | 1: T02 |

## Chi tiết lỗi

| Line | Cột | Loại | task_id | Mô tả |
|---|---|---|---|---|
| 5 | hours | invalid_hours | T04 | hours 'abc' không phải số hữu hạn không âm. |
| 6 | task_id | duplicate_id | T02 | task_id T02 đã xuất hiện ở line 3. |
| 7 | owner | missing_owner | T05 | owner trống. |

## Đánh giá và khuyến nghị

Totals phản ánh các dòng hợp lệ được cộng, không gồm excluded_rows.
Mỗi ID chỉ xét lần đầu, kể cả lần đầu lỗi. Giữ nguyên hoa/thường của owner.
Dữ liệu có lỗi về hours không hợp lệ, task_id trùng lặp và thiếu owner; cần kiểm tra lại file gốc `data/workload.csv` để chuẩn hóa các dòng bị loại.
