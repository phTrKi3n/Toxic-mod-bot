# LOG_DEV.md — Nhật ký quyết định riêng của vai trò DEV

Áp dụng chung quy tắc ghi log ở `log.md` (tối đa 5 dòng/entry, entry mới
nhất trên cùng, xoay vòng khi vượt 20 entry). File này chỉ chứa quyết định
thuộc phạm vi DEV (xem `rule_dev.md`); quyết định ảnh hưởng phạm vi chung
được đồng thời ghi sang `log.md`.

## Active Log

| Ngày | Quyết định | Lý do | Ảnh hưởng |
|---|---|---|---|
| 2026-09-28 | Hoàn thiện ModelLoader (__init__, reload, predict) load model từ models/xlmr-finetuned và truy vấn model_version_id có is_current=True | Cung cấp inference logic cho API phân loại độc hại và hỗ trợ cơ chế reload model theo UC11/UC14 | Phục vụ trực tiếp endpoint /classify và /health trong inference_service |
| 2026-09-28 | Hoàn thiện hàm finetune() với HuggingFace Trainer, đo F1 binary trên eval split (10%), ghi model_version mới vào DB với is_current=True | Huấn luyện mô hình XLM-R và tự động cập nhật phiên bản mô hình hiện hành vào CSDL | Đảm bảo inference service luôn truy xuất được model_version mới nhất từ DB |
| 2026-09-28 | load_jigsaw dùng luật OR trên 6 cột toxic-type để gộp nhãn nhị phân; load_vihsd map label_id != 0 về 1, chuẩn hóa tên cột text/label | Chuẩn hóa dữ liệu 2 nguồn Jigsaw và ViHSD về cùng khuôn (text, label) nhị phân | Đảm bảo pipeline merge_and_export hoạt động thông suốt, data/merged_train.csv đồng nhất |
| 2026-09-26 | Trong file docx mới, gắn nhãn rõ Chương II (Xác định yêu cầu) và phần use case/ERD/SQL đầu Chương III là nội dung do DEV chủ trì, đúng phạm vi rule_dev.md; giữ nguyên actor/use case/entity, không đổi | Đồng bộ báo cáo với việc chia role đã quyết ở `log.md` 2026-09-25, không tạo nội dung kỹ thuật mới | Chỉ đổi cách trình bày/gắn nhãn, không đổi nội dung pipeline NLP hay schema DB đã chốt |

## Archive

*(chưa có)*
