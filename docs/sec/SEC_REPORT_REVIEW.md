# SEC | Rà soát bảo mật Chương III–IV sau đồng bộ mã nguồn

Ngày rà soát: 2026-10-29
Nguồn: báo cáo Word đã gửi trước đó và mã nguồn nhánh `sec` mới.
**Không chỉnh sửa trực tiếp báo cáo Word chung**, chờ nhóm thống nhất người phụ trách.

## 1. Nội dung đã có

- Threat Model ở Chương IV đã mô tả 7 nhóm mối đe dọa.
- Báo cáo có các mô hình dữ liệu liên quan tới người dùng, bình luận, kháng nghị và nhật ký kiểm duyệt.
- Các ngưỡng ra quyết định được mô tả ở mức thiết kế.

## 2. Các điểm cần đối chiếu/chốt với nhóm

| Vị trí/nội dung | Kiểm tra từ mã nguồn | Việc cần làm |
|---|---|---|
| Truy vấn hàng đợi dùng `BETWEEN 0.30 AND 0.90` | `BETWEEN` gồm 0.90; code dùng nhánh xóa khi `score >= threshold_high` | DEV kiểm tra logic/chỉnh mô tả hoặc SQL theo thiết kế cuối |
| Mô tả handler là chưa triển khai | `bot/actions.py` đã có xóa/gửi DM/ghi DB, `bot/commands.py` có các lệnh kiểm duyệt và kháng nghị | Bỏ nhận định cũ “tất cả còn NotImplementedError”; phân biệt có code và đã kiểm thử tích hợp |
| Chống spam/DoS | `check_user_rate_limit`, `MAX_MESSAGE_CHARS` có trong code mới | Ghi đúng tình trạng đã có code, chưa mặc định đồng nghĩa phòng thủ đủ trên môi trường production |
| Bảo mật khi hiển thị lỗi | Một số `except` trong `bot/commands.py` gửi nguyên `Exception` cho người dùng | SEC ghi rủi ro lộ chi tiết lỗi, DEV xử lý theo quy trình |
| Nội dung hàng đợi kiểm duyệt | Khi gửi DM thất bại, `_send_private_or_channel()` có thể gửi vào kênh đang gọi lệnh | DEV/SEC xác minh quyền riêng tư của kênh và bổ sung kiểm soát nếu cần |
| Audit kiểm duyệt | Code có các nhánh ghi `ModerationAction` và cập nhật kháng nghị | Chỉ khẳng định có code ghi bản ghi; tính chính xác cần test tích hợp |

## 3. Đoạn SEC đề xuất cho báo cáo (khi được nhóm đồng ý)

**An toàn dữ liệu:** Bot xử lý nội dung bình luận, điểm phân loại, dữ liệu kháng nghị và lịch sử kiểm duyệt. Mã nguồn hiện đã có các nhánh ghi dữ liệu và giới hạn tần suất/độ dài đầu vào. SEC xác định các nguy cơ cần lưu ý như thông báo lỗi lộ chi tiết nội bộ, thông tin hàng đợi bị hiển thị ở kênh không phù hợp khi DM thất bại, và chính sách lưu giữ dữ liệu chưa được xác minh. Các biện pháp giảm thiểu cần được đánh giá lại trong kiểm thử tích hợp và vận hành thực tế.

**FP/FN:** Hành động được chọn dựa trên ngưỡng thấp/cao cấu hình cho server. SEC sử dụng điểm giả lập để kiểm tra ranh giới nhánh xử lý và trường hợp inference timeout. Kết quả chỉ xác nhận logic chọn hành động trên phiên bản code kiểm thử, không thay thế đánh giá chất lượng phân loại hoặc kiểm thử xóa tin thực tế.

## 4. Trạng thái bàn giao

- [x] Đã rà soát mã nguồn mới và cập nhật tài liệu SEC cho phù hợp.
- [ ] Chạy lại bộ unit test SEC và ghi nhận kết quả sau đồng bộ.
- [ ] DEV xác nhận quy tắc truy vấn hàng đợi tại ngưỡng cao và vấn đề lộ lỗi/DM fallback.
- [ ] Người phụ trách báo cáo chung duyệt và áp dụng thay đổi vào Word (nếu cần).
- [ ] TEST/OPS xác minh hành vi trên môi trường tích hợp.

**Kết luận:** Tài liệu này phản ánh mã nguồn mới ở mức phân tích tĩnh. Không khẳng định toàn hệ thống đã kiểm thử hoàn chỉnh.
