# LOG_SEC.md — Nhật ký quyết định riêng của vai trò SEC

Áp dụng quy tắc log.md: entry mới nhất trên cùng, tối đa 20 entry hoạt động,
xoay vòng khi vượt giới hạn. Quyết định ảnh hưởng chung ghi thêm vào log.md.

## Active Log

| Ngày | Quyết định | Lý do | Ảnh hưởng |
|---|---|---|---|
| 2026-10-02 | Bổ sung fail-closed RBAC Discord + DB, phân quyền labeler và helper kiểm tra ownership, guild scope; giữ nguyên nghiệp vụ DEV chưa triển khai | Ngăn cấp quyền bằng role giả, truy cập ID xuyên server và khiếu nại hộ; không sửa ERD | Thêm bot/rbac.py, test DB, tài liệu tích hợp; DEV phải gọi helper tại mọi điểm đọc/ghi và triển khai audit trước khi công bố RBAC toàn hệ thống hoàn chỉnh |
| 2026-10-02 | Hoàn thiện guard /queue và /resolve cho Mod/Admin, /config cho Admin; từ chối DM/bot, nhận diện tên lệnh chính xác và bổ sung test handler | Helper có sẵn nhưng chưa được gọi ở handler; test cũ chỉ kiểm tra role | Giữ cơ chế tên role Discord và nghiệp vụ DEV; /appeal vẫn không bị giới hạn Mod/Admin; chỉnh log trùng lặp, kiểm thử chi tiết tại docs/sec/RBAC_HANDOFF.md |
| 2026-09-30 | Bổ sung kiểm tra RBAC cho lệnh /queue, chỉ Mod/Admin được phép tiếp tục xử lý lệnh | UC04 xác định /queue chỉ dành cho Mod/Admin; đã triển khai hàm kiểm tra role và kiểm thử 4 trường hợp RBAC | Chỉ bổ sung kiểm tra quyền, không thay đổi luồng xử lý queue của DEV |
| 2026-09-27 | Thêm 1 mối đe doạ vào bảng Threat Model Chương IV: máy chủ chạy Bot/Inference Service bị chiếm rồi bị cấy kênh điều khiển từ xa (C2), xảy ra sau khi một mối đe doạ khác (đặc biệt rò rỉ thông tin đăng nhập) đã thành công; biện pháp giảm thiểu là quét lỗ hổng dependency (pip-audit/Snyk), chỉ build image từ Dockerfile trong repo, chạy tiến trình bằng user không phải root, giới hạn kết nối ra ngoài của container | Người dùng yêu cầu thêm khả năng kết nối C2 vào threat model theo hướng phòng thủ (liệt kê rủi ro), đã xác nhận không phải yêu cầu xây tính năng điều khiển từ xa thật cho bot | Thêm 1 dòng bảng + cập nhật câu tóm tắt sau bảng ở Chương IV mục V; thêm bước quét dependency (pip-audit) vào pipeline CI/CD Chương V mục III để khớp đúng biện pháp giảm thiểu đã nêu; không đổi luồng Activity/Use case đã chốt ở Chương III, đúng giới hạn rule_sec.md |
| 2026-09-26 | Thêm mục "Mô hình mối đe doạ" (Threat Model) vào Chương IV: 6 nhóm đe doạ (raid/giả mạo tài khoản, spam/DoS lên Inference Service, né bộ lọc bằng ký tự lạ, rò rỉ bot token, injection khi truy vấn DB, lạm quyền nội bộ của Mod/Admin), mỗi mục nêu biện pháp giảm thiểu dựa trên cơ chế thật đã có (Discord AutoMod/verification level, giới hạn rate limit 429 của Discord API, ORM/parameterized query, biến môi trường .env, audit log decided_by đã có trong ERD) | rule_sec.md yêu cầu threat model nhưng bản cũ chưa có mục riêng, mới dừng ở RBAC + audit log; người dùng yêu cầu không bịa kỹ thuật, phải dựa trên bot Discord thật | Không đổi luồng Activity/Use case đã chốt ở Chương III (đúng giới hạn rule_sec.md); chỉ thêm 1 mục mới ở Chương IV và bảng tài liệu tham khảo tương ứng |

## Archive

*(chưa có)*
