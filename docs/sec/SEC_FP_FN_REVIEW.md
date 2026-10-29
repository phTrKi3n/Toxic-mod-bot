# SEC | Rủi ro False Positive / False Negative và kiểm thử ngưỡng

Ngày: 2026-10-29  
Nguồn kiểm tra: `bot/actions.py`, `tests/test_sec_moderation_safety.py` trong bản SEC đã giao.

## 1. Vì sao đây là việc của SEC?

Bot có thể tự xử lý tin nhắn theo điểm độc hại. Quyết định sai có thể xóa oan bình luận (false positive, FP) hoặc bỏ sót bình luận độc hại (false negative, FN). Đây là rủi ro tác động đến người dùng và độ tin cậy của hệ thống, kể cả khi cơ chế phân quyền đúng.

## 2. Quy tắc trong code hiện tại

`bot/actions.py` đặt mặc định `threshold_low = 0.30`, `threshold_high = 0.90`:

| Điểm đầu vào | Nhánh được chọn | Ý nghĩa |
|---|---|---|
| `score < 0.30` | Không hành động | Có nguy cơ FN nếu tin nhắn thực sự độc hại |
| `0.30 <= score < 0.90` | `_flag_for_review` | Đưa vào quy trình kiểm duyệt; hiện handler còn TODO |
| `score >= 0.90` | `_delete_and_warn` | Có nguy cơ FP nếu tin nhắn thực tế bình thường; hiện handler còn TODO |

Lưu ý: đây là **ngưỡng mặc định trong code**, không phải kết quả đo chất lượng model hoặc giá trị đã lấy từ bảng `server`. Hiện vẫn có TODO đọc ngưỡng theo từng server.

## 3. Unit test được bổ sung trong SEC

File: `tests/test_sec_moderation_safety.py`.

- Kiểm thử 8 mức điểm giả lập: `0.00`, `0.29`, `0.299999`, `0.30`, `0.89`, `0.899999`, `0.90`, `1.00`.
- Mock kết quả HTTP và hai handler để tránh gọi backend Discord, DB hoặc API thật.
- Xác nhận đường dẫn API, payload chỉ có `text` và thời gian timeout cấu hình 2 giây.
- Kiểm tra một `httpx.ReadTimeout` không kích hoạt xóa hoặc gắn cờ.

**Kết quả chạy trong môi trường kiểm thử độc lập:** `9 passed` (Python/pytest có sẵn trong môi trường tạo tài liệu). Cần chạy lại trong `.venv` của nhóm sau khi chép file vào repository.

**Giới hạn bằng chứng:** 9 bài này chứng minh nhánh **chọn hành động** theo score mock. Không chứng minh xóa tin nhắn thật, tạo HardCase, ghi ModerationAction, xử lý khiếu nại hay Accuracy/Precision/Recall/F1 của model. Các handler tương ứng vẫn là placeholder.

## 4. Biện pháp giảm thiểu đề xuất

- **FP:** giữ hàng đợi kiểm duyệt khi độ tin cậy chưa đủ cao; cung cấp quy trình khiếu nại và khôi phục có log; sau tích hợp, theo dõi tỉ lệ khiếu nại được chấp thuận.
- **FN:** đưa các câu né bộ lọc (teencode, chèn ký tự, nói bóng gió) vào tập đánh giá có nhãn; theo dõi Recall cho lớp độc hại ở tiếng Việt và tiếng Anh.
- **Điều chỉnh ngưỡng:** dựa trên validation độc lập và đánh đổi Precision/Recall, không đổi `threshold_low/high` tùy ý trong SEC.
- **Trường hợp bất thường:** sau khi DEV có handler thật, kiểm tra score thiếu, không hợp lệ hoặc backend lỗi có được xử lý an toàn và ghi log phù hợp hay không. Chưa khẳng định hệ thống hiện có cơ chế này.

## 5. Phân công sau bàn giao

- SEC: kiểm thử an toàn nhánh quyết định, ghi nhận rủi ro FP/FN, xác minh audit/kháng nghị sau tích hợp.
- DEV: hiện thực xóa/flag/appeal, đánh giá mô hình thật và xử lý giá trị score bất thường.
- OPS/TEST: kiểm thử hệ thống, ghi log timeout, giám sát và chạy kiểm thử tích hợp.

**Kết luận:** phần đánh giá FP/FN và unit test điều kiện ngưỡng đã có. Chưa đủ dữ liệu để kết luận hệ thống có ít FP/FN hoặc đã kiểm duyệt an toàn ở môi trường thật.
