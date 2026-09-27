# LOG_SEC.md — Nhật ký quyết định riêng của vai trò SEC

Áp dụng chung quy tắc ghi log ở `log.md` (tối đa 5 dòng/entry, entry mới
nhất trên cùng, xoay vòng khi vượt 20 entry). File này chỉ chứa quyết định
thuộc phạm vi SEC (xem `rule_sec.md`); quyết định ảnh hưởng phạm vi chung
được đồng thời ghi sang `log.md`.

## Active Log

| Ngày | Quyết định | Lý do | Ảnh hưởng |
|---|---|---|---|
| 2026-09-27 | Thêm 1 mối đe doạ vào bảng Threat Model Chương IV: máy chủ chạy Bot/Inference Service bị chiếm rồi bị cấy kênh điều khiển từ xa (C2), xảy ra sau khi một mối đe doạ khác (đặc biệt rò rỉ thông tin đăng nhập) đã thành công; biện pháp giảm thiểu là quét lỗ hổng dependency (pip-audit/Snyk), chỉ build image từ Dockerfile trong repo, chạy tiến trình bằng user không phải root, giới hạn kết nối ra ngoài của container | Người dùng yêu cầu thêm khả năng kết nối C2 vào threat model theo hướng phòng thủ (liệt kê rủi ro), đã xác nhận không phải yêu cầu xây tính năng điều khiển từ xa thật cho bot | Thêm 1 dòng bảng + cập nhật câu tóm tắt sau bảng ở Chương IV mục V; thêm bước quét dependency (pip-audit) vào pipeline CI/CD Chương V mục III để khớp đúng biện pháp giảm thiểu đã nêu; không đổi luồng Activity/Use case đã chốt ở Chương III, đúng giới hạn rule_sec.md |
| 2026-09-26 | Thêm mục "Mô hình mối đe doạ" (Threat Model) vào Chương IV: 6 nhóm đe doạ (raid/giả mạo tài khoản, spam/DoS lên Inference Service, né bộ lọc bằng ký tự lạ, rò rỉ bot token, injection khi truy vấn DB, lạm quyền nội bộ của Mod/Admin), mỗi mục nêu biện pháp giảm thiểu dựa trên cơ chế thật đã có (Discord AutoMod/verification level, giới hạn rate limit 429 của Discord API, ORM/parameterized query, biến môi trường .env, audit log decided_by đã có trong ERD) | rule_sec.md yêu cầu threat model nhưng bản cũ chưa có mục riêng, mới dừng ở RBAC + audit log; người dùng yêu cầu không bịa kỹ thuật, phải dựa trên bot Discord thật | Không đổi luồng Activity/Use case đã chốt ở Chương III (đúng giới hạn rule_sec.md); chỉ thêm 1 mục mới ở Chương IV và bảng tài liệu tham khảo tương ứng |

## Archive

*(chưa có)*
