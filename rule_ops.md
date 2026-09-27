# RULE_OPS.md — Quy tắc riêng cho vai trò OPS

Tham chiếu gốc: xem `rule.md` mục 1, 2, 3, 6, 7 — áp dụng chung, không lặp
lại ở đây.

## Phạm vi phụ trách

- Triển khai, giám sát, CI/CD cho bot.
- Kiểm thử (Chương V): test case, tiêu chí đánh giá (F1-score trên tập
  validation trộn Anh-Việt).
- Xử lý sự cố vận hành, khả năng mở rộng (scaling) khi lượng tin nhắn tăng.
- Nội dung vận hành/kiểm thử ở Chương IV-V của báo cáo.

## Việc OPS không được tự quyết (phải qua log.md chung)

- Đổi kiến trúc triển khai tổng (ví dụ đổi nền tảng bot từ Discord/Telegram
  sang thứ khác).

## Log riêng

Mọi quyết định trong phạm vi trên ghi **ngay** vào `log_ops.md`, cùng khuôn
5 trường như `log.md`. Quyết định ảnh hưởng phạm vi chung thì đồng thời ghi
tóm tắt sang `log.md` (theo `rule.md` mục 7).
