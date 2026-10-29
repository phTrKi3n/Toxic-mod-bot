# SEC | Rà soát an toàn dữ liệu người dùng (cập nhật sau đồng bộ)

Ngày rà soát: 2026-10-29
Phạm vi: mã nguồn nhánh `sec` sau khi đồng bộ các thay đổi của nhóm.
Trạng thái: đánh giá mã nguồn, **chưa phải xác nhận bảo mật trên môi trường triển khai thật**.

## 1. Dữ liệu được xử lý

| Dữ liệu | Vị trí trong code/schema | Nguy cơ cần kiểm soát |
|---|---|---|
| ID, tên và vai trò Discord | `db/models.py` (`User`), `bot/actions.py` | Lộ thông tin định danh và quyền truy cập |
| Nội dung bình luận | `Message.content`, `classify_and_moderate()` | Có thể chứa dữ liệu cá nhân/nhạy cảm |
| Điểm phân loại | `Classification.score`, `HardCase.original_score` | Lộ thông tin kiểm duyệt hoặc gắn nhãn sai |
| Lý do kháng nghị | `Appeal.reason`, `bot/commands.py` | Có thể chứa thông tin riêng tư |
| Lịch sử xử lý | `ModerationAction`, `Appeal.resolved_by` | Cần đảm bảo quyền truy cập và khả năng truy vết |

## 2. Điều đã xác minh trong phiên bản mới

- `bot/main.py` bật `intents.message_content=True` để đọc nội dung tin nhắn.
- `bot/actions.py` giới hạn nội dung gửi inference bằng `MAX_MESSAGE_CHARS`, có hàm giới hạn tần suất theo người dùng `check_user_rate_limit()`.
- Gọi inference hiện sử dụng `aiohttp`, gửi payload `{"text": ...}` tới `INFERENCE_URL`, **không phải `httpx` hoặc URL localhost cố định**.
- `bot/actions.py` hiện có code thực hiện xóa, gửi DM, ghi `Classification`, `HardCase` và `ModerationAction` vào DB khi có session; không còn đúng khi mô tả toàn bộ hành động là `NotImplementedError`.
- `bot/commands.py` đã có code xử lý `/appeal`, `/queue`, `/resolve`, `/label`, `/config`. Chưa thể khẳng định toàn bộ đường chạy đã kiểm thử hoặc triển khai thành công trong thực tế.
- `.gitignore` có quy tắc loại trừ `.env` trong bản đã rà soát trước; vẫn cần kiểm tra lịch sử Git và môi trường chạy nếu đánh giá rò rỉ secret.

## 3. Rủi ro đáng chú ý, có bằng chứng từ code

| Rủi ro | Bằng chứng/điều kiện | Đề xuất của SEC | Đơn vị tích hợp |
|---|---|---|---|
| Lộ chi tiết lỗi nội bộ | Một số nhánh `except` ở `bot/commands.py` gửi `{e}` trực tiếp vào Discord | Chỉ gửi thông báo lỗi chung cho người dùng; lưu chi tiết nội bộ an toàn | DEV |
| Lộ thông tin hàng đợi | `_send_private_or_channel()` gửi vào kênh hiện tại nếu DM thất bại | Chỉ gửi vào DM/kênh kiểm duyệt riêng đã xác minh quyền; tránh fallback vào kênh công khai | DEV/SEC phối hợp |
| Nội dung nhạy cảm trong CSDL | `Message.content` và `Appeal.reason` được lưu theo nghiệp vụ | Áp dụng phân quyền DB, nguyên tắc tối thiểu dữ liệu; kiểm tra thời gian lưu | DEV/OPS |
| Thông tin sai về hành động thành công | Trong `bot/commands.py`, một số lỗi xóa tin có thể bị bỏ qua nhưng thông báo đã ghi nhận action | Phân biệt 'đã ghi bản ghi' và 'đã xóa tin trên Discord' | DEV |
| Thời gian lưu dữ liệu | Chưa xác nhận chính sách giữ/xóa dữ liệu | Thống nhất thời hạn lưu, xóa/anonymize và quyền truy cập | Nhóm phụ trách nghiệp vụ |
| Log lỗi và token | Có đường ghi lỗi, chưa xác minh cấu hình production | Không ghi token/nội dung nhạy cảm; kiểm tra mức log và vòng đời secret | OPS/SEC phối hợp |

## 4. Giới hạn công việc SEC

SEC chỉ **ghi nhận rủi ro, kiểm tra các điều kiện bảo mật và bàn giao**. Không tự sửa code nghiệp vụ DEV/OPS, ERD, ngưỡng phân loại hoặc luồng hoạt động đã chốt mà chưa thống nhất theo `rule_sec.md`.

## 5. Tiêu chí bàn giao

1. DEV xác nhận cách gửi thông tin hàng đợi khi DM thất bại, tránh lộ nội dung vào kênh không được phép.
2. DEV thống nhất mẫu lỗi chung thay cho việc gửi nguyên văn exception vào Discord.
3. Nhóm thống nhất chính sách lưu và xóa dữ liệu bình luận/kháng nghị.
4. SEC/TEST xác minh lại các kiểm soát này trên môi trường tích hợp khi có dữ liệu giả lập phù hợp.

**Kết luận:** Có cơ chế xử lý và lưu dữ liệu thực tế trong code mới, nhưng các nguy cơ riêng tư và hành vi trong môi trường chạy vẫn cần xác nhận; không kết luận đã xảy ra rò rỉ dữ liệu.
