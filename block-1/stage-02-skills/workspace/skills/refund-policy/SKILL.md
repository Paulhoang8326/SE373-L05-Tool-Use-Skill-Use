---
name: refund-policy
description: Tra cứu chính sách hoàn tiền (refund), điều kiện hoàn, phí hoàn và phiên bản chính sách áp dụng theo ngày mua của khách hàng.
---

# Quy trình tra cứu hoàn tiền

1. Kiểm tra đủ ngày mua, ngày yêu cầu hoàn và trạng thái đã/chưa kích hoạt.
   Nếu thiếu bất kỳ trường nào, hỏi lại thông tin còn thiếu và dừng trước khi kết luận
   đủ hoặc không đủ điều kiện. Không mặc định chưa kích hoạt.
2. Khi đủ dữ liệu, gọi `list_files("data/policies")` để tìm tài liệu hiện có.
   Không đoán tên file, không chọn theo filename, không dùng tài liệu từ lịch sử cũ
   thay cho discovery của yêu cầu hiện tại.
3. Dùng `read_file` đọc các policy candidate từ đường dẫn vừa liệt kê.
   Đọc nội dung để xác định phạm vi hiệu lực bao phủ NGÀY MUA, thời hạn,
   điều kiện kích hoạt và phí. Không chọn theo ngày yêu cầu hoặc ngày hiện tại.
   Nếu không có policy phù hợp hoặc phạm vi mâu thuẫn, báo chưa đủ căn cứ.
4. Phân tích ngày theo ngày/tháng/năm hoặc ISO. Nếu ngày mơ hồ, không hợp lệ
   hoặc ngày yêu cầu trước ngày mua, hỏi lại. Tính chênh lệch ngày lịch
   từ ngày mua đến ngày yêu cầu trong câu hỏi. Bằng giới hạn vẫn hợp lệ về thời gian.
5. Áp dụng giới hạn, điều kiện kích hoạt và phí đọc TỪ TÀI LIỆU.
   Không tự dựng quy tắc, không lấy kiến thức sẵn có làm căn cứ.
6. Đọc `references/answer-template.md`, tức
   `skills/refund-policy/references/answer-template.md`, rồi trả lời theo template.
   Dẫn đường dẫn policy thật đã đọc. Chỉ nêu phí áp dụng khi đủ điều kiện.
7. Chỉ dùng file tools; không yêu cầu Bash hoặc script.
