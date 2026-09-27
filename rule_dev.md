# RULE_DEV.md — Quy tắc riêng cho vai trò DEV

Tham chiếu gốc: xem `rule.md` mục 1 (phạm vi đề tài), mục 2 (không tự sáng
chế), mục 3 (công cụ), mục 6 (văn phong), mục 7 (đồng bộ log 2 tầng) — các
mục này áp dụng chung, không lặp lại ở đây.

## Phạm vi phụ trách

- Pipeline NLP song ngữ VI/EN: detect ngôn ngữ → tiền xử lý → embedding →
  mô hình (XLM-R fine-tune) → ngưỡng phân loại.
- Use case, ERD, entity liên quan trực tiếp tới 4 chức năng chính (Thu thập,
  Gắn nhãn, Kiểm duyệt, Khiếu nại).
- Nội dung kỹ thuật ở Chương I-III của báo cáo.

## Việc DEV không được tự quyết (phải qua log.md chung)

- Đổi mô hình nền, đổi phạm vi ngôn ngữ, đổi 4 chức năng chính, đổi actor
  hoặc entity cốt lõi đã chốt trong Chương III.

## Log riêng

Mọi quyết định trong phạm vi trên ghi **ngay** vào `log_dev.md`, cùng khuôn
5 trường như `log.md`. Quyết định ảnh hưởng phạm vi chung thì đồng thời ghi
tóm tắt sang `log.md` (theo `rule.md` mục 7).
