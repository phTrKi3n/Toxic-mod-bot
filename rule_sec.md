# RULE_SEC.md — Quy tắc riêng cho vai trò SEC

Tham chiếu gốc: xem `rule.md` mục 1, 2, 3, 6, 7 — áp dụng chung, không lặp
lại ở đây.

## Phạm vi phụ trách

- Threat model cho bot kiểm duyệt (Discord/Telegram): giả mạo, spam tấn
  công mô hình, injection vào input.
- RBAC/phân quyền giữa người dùng, kiểm duyệt viên, admin.
- An toàn dữ liệu người dùng khi thu thập/lưu bình luận; rủi ro khi bot tự
  động xoá/cảnh báo tin nhắn (false positive/negative).
- Nội dung bảo mật ở Chương III-IV của báo cáo.

## Việc SEC không được tự quyết (phải qua log.md chung)

- Thêm cơ chế bảo mật làm đổi luồng Activity/Use case đã chốt ở Chương III.

## Log riêng

Mọi quyết định trong phạm vi trên ghi **ngay** vào `log_sec.md`, cùng khuôn
5 trường như `log.md`. Quyết định ảnh hưởng phạm vi chung thì đồng thời ghi
tóm tắt sang `log.md` (theo `rule.md` mục 7).
