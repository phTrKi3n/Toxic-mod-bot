# SEC | Rà soát an toàn dữ liệu người dùng

Ngày rà soát: 2026-10-29  
Phạm vi: mã nguồn trong bản `SEC-Git.zip`, nhánh `sec`, commit `4a6bcb1`.  
Trạng thái: **đánh giá thiết kế/mã nguồn**, không phải kết luận pentest hay kiểm thử bảo mật môi trường thật.

## 1. Phạm vi dữ liệu

Đề tài tập trung vào bốn chức năng đã chốt: thu thập bình luận, gắn nhãn, kiểm duyệt và khiếu nại. SEC không thay đổi luồng nghiệp vụ, cơ sở dữ liệu hoặc hành vi bot.

| Dữ liệu | Bằng chứng trong mã nguồn | Mục đích trong thiết kế | Lưu ý bảo mật |
|---|---|---|---|
| `app_user.discord_id`, `app_user.username`, `app_user.role` | `db/models.py`, lớp `User` | Nhận diện người dùng và phân quyền | Dữ liệu định danh, tránh ghi công khai |
| `message.content`, `message.user_id`, `message.server_id`, `message.created_at` | `db/models.py`, lớp `Message` | Lưu bình luận cần phân loại/kiểm duyệt | Nội dung có thể chứa thông tin nhạy cảm |
| `appeal.reason`, `appeal.user_id`, `appeal.message_id` | `db/models.py`, lớp `Appeal` | Lưu lý do khiếu nại | Nội dung khiếu nại có thể chứa thông tin riêng tư |
| `classification.score` | `db/models.py`, lớp `Classification` | Điểm dự đoán phục vụ quyết định | Cần hạn chế hiển thị ngoài phạm vi kiểm duyệt |
| `moderation_action.decided_by`, `decided_at` | `db/models.py`, lớp `ModerationAction` | Thiết kế lưu lịch sử quyết định | Cột dữ liệu có sẵn, chưa chứng minh handler đã ghi log thật |

## 2. Điều đã kiểm chứng từ code

- `bot/main.py` đặt `intents.message_content = True`, nên bot **được cấu hình để đọc nội dung** tin nhắn mà Discord cung cấp cho bot.
- `bot/actions.py` gửi `{"text": message.content}` đến `http://localhost:8000/classify`. Không thấy user ID/token trong payload của lời gọi này. Đây vẫn là nội dung bình luận gốc được gửi sang service.
- `db/models.py` có cấu trúc lưu bình luận, lý do khiếu nại và dấu vết hành động, nhưng **chỉ có mô hình dữ liệu không đủ khẳng định dữ liệu đã được ghi/lưu thực tế**.
- `.gitignore` đã loại trừ `.env`. Điều đó không chứng minh lịch sử Git hoặc máy triển khai chưa từng lộ token.
- `bot/actions.py` chưa hiện thực `_delete_and_warn`, `_flag_for_review`; `bot/commands.py` còn handler `NotImplementedError`. Chưa thể xác nhận kiểm soát truy cập dữ liệu cuối luồng, lưu/ẩn thông tin trong khiếu nại hay ghi audit thực tế.
- Chưa thấy triển khai thời hạn lưu, cơ chế xóa dữ liệu định kỳ hay quy trình xử lý yêu cầu xóa dữ liệu trong các file đã rà soát.

## 3. Bảng rủi ro và biện pháp đề xuất

| Rủi ro | Bằng chứng / điều kiện | Tác động có thể xảy ra | Khuyến nghị | Trạng thái |
|---|---|---|---|---|
| Lộ nội dung bình luận | Có `message.content` và luồng gửi nội dung gốc đến Inference Service | Tiết lộ nội dung nhạy cảm nếu quyền truy cập DB/service bị cấu hình sai | Chỉ cho dịch vụ/nhân sự cần thiết truy cập; tránh in nguyên văn nội dung vào log | Đề xuất, chưa triển khai xác minh |
| Lộ lý do khiếu nại | Có trường `appeal.reason`; handler khiếu nại còn TODO | Người khác nhìn thấy thông tin riêng tư do người dùng tự cung cấp | Giới hạn người xem theo quyền và sở hữu; không đưa lý do vào kênh công khai | Đề xuất, chờ tích hợp DEV |
| Lưu dữ liệu không giới hạn | Chưa tìm thấy chính sách giữ/xóa dữ liệu trong mã nguồn được rà soát | Dữ liệu tồn đọng làm tăng hậu quả nếu bị truy cập trái phép | Thống nhất thời gian giữ và nhu cầu xóa/anonymize với nhóm và chủ server | Chưa chốt chính sách |
| Lộ token cấu hình | Bot đọc token từ biến môi trường; `.env` nằm trong `.gitignore` | Nếu token lộ, người khác có thể điều khiển bot | Không đẩy `.env`; rà soát secret trong commit; reset token nếu nghi lộ | Có quy tắc Git; chưa đánh giá máy chủ thật |
| Audit không đầy đủ | Schema có `decided_by`, nhưng handlers chưa có thao tác ghi đầy đủ | Khó truy lại ai quyết định xóa/khôi phục | DEV triển khai ghi audit; SEC kiểm tra kết quả bằng test sau khi tích hợp | Chờ DEV/OPS |

## 4. Ranh giới trách nhiệm

**SEC tự làm:** rà soát dữ liệu/luồng, viết tiêu chí và tài liệu; kiểm tra khi có chức năng thật; báo rủi ro và theo dõi.

**Cần DEV/OPS:** thay đổi DB, triển khai xóa dữ liệu, thêm kênh kiểm duyệt riêng, log vận hành, hardening service, thay đổi cách gửi/giữ dữ liệu. Các việc này có thể ảnh hưởng luồng Activity/Use case nên phải thông qua quy trình chung.

## 5. Tiêu chí xác nhận hoàn thành sau tích hợp

1. Kiểm tra quyền đọc bình luận và khiếu nại bằng tài khoản không được phép.
2. Kiểm tra không có token/chuỗi kết nối/nội dung nhạy cảm không cần thiết trong log thực tế.
3. Xác nhận dữ liệu bình luận được lưu ở đâu, trong bao lâu, ai được đọc và ai có thể yêu cầu xóa.
4. Kiểm tra thao tác kiểm duyệt ghi được `action_type`, `decided_by`, `decided_at` theo thiết kế.

**Kết luận SEC hiện tại:** đã lập hồ sơ rủi ro riêng tư dựa trên code, chưa thể xác nhận các biện pháp tích hợp đã chạy vì phần handler/backend còn chưa hoàn thiện. Không thay đổi ERD, RBAC hay logic nghiệp vụ.
