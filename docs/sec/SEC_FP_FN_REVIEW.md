# SEC | Rủi ro False Positive / False Negative (cập nhật sau đồng bộ)

Ngày rà soát: 2026-10-29
Nguồn kiểm tra: `bot/actions.py`, `tests/test_inference.py`, `tests/test_sec_moderation_safety.py` trên nhánh `sec` mới.

## 1. Phân biệt FP và FN

- **FP (False Positive):** tin nhắn bình thường được đánh giá độc hại, có nguy cơ bị xóa nhầm.
- **FN (False Negative):** tin nhắn độc hại bị đánh giá bình thường, có nguy cơ bị bỏ sót.

## 2. Quy tắc chọn hành động trong code

| Điều kiện trên score | Hành động | Rủi ro |
|---|---|---|
| `score < threshold_low` | `ignore` | FN nếu nội dung thật sự độc hại |
| `threshold_low <= score < threshold_high` | `flag` | Cần quy trình người kiểm duyệt xem xét |
| `score >= threshold_high` | `delete` | FP nếu nội dung thật sự bình thường |

Giá trị mặc định là `threshold_low=0.30`, `threshold_high=0.90`. Tuy nhiên `classify_and_moderate()` sử dụng ngưỡng trong `server_config`, nên **có thể khác mặc định theo từng server**.

## 3. Kiểm thử SEC

File `tests/test_sec_moderation_safety.py` đã cập nhật sử dụng tham số `session` giả lập tương thích `aiohttp`, **không phát sinh HTTP/Discord/DB thật**.

- Tám trường hợp điểm giả lập: `0.00`, `0.29`, `0.299999`, `0.30`, `0.89`, `0.899999`, `0.90`, `1.00`.
- Kiểm tra trả đúng `ignore`/`flag`/`delete` và không gọi nhầm handler.
- Kiểm tra payload phân loại chỉ chứa trường `text` và timeout theo cấu hình hiện hành.
- Một tình huống timeout giả lập phải trả `bypass`, không gọi hành động xóa/đánh dấu.

**Trạng thái:** Cần chạy pytest lại trên nhánh mới để chốt kết quả. Kết quả 9 passed trước khi nhóm cập nhật code không còn là bằng chứng kiểm thử cho phiên bản mới.

## 4. Giới hạn kiểm thử

Bộ test chỉ kiểm tra lựa chọn hành động khi score là số hợp lệ và đường xử lý timeout. Không đo Precision/Recall/F1, không xác minh kết quả thực tế của mô hình AI, không kiểm tra hiệu quả gửi DM hoặc xóa tin thật, không đo tỉ lệ FP/FN trên tập dữ liệu có nhãn.

`bot/actions.py` hiện đã có handler xử lý Discord và ghi CSDL; việc hoạt động đúng trong mọi hoàn cảnh phải được kiểm thử tích hợp riêng. Không còn mô tả các handler này là TODO/NotImplementedError.

## 5. Đề xuất giảm thiểu

- Với FP: theo dõi khiếu nại, kết quả khôi phục và nguyên nhân xóa nhầm.
- Với FN: đánh giá trên tập dữ liệu song ngữ và văn bản né bộ lọc có nhãn chuẩn; đo Recall độc hại.
- Điều chỉnh ngưỡng bằng kết quả đánh giá khách quan; SEC không tự đổi ngưỡng mô hình.
- Xác minh quy trình fallback khi inference lỗi và khi Discord không thể xóa tin; tránh kết luận hành động đã thành công khi chỉ mới lưu bản ghi.

**Kết luận:** SEC cung cấp kiểm thử an toàn nhánh ra quyết định và phân tích tác động FP/FN, không thay thế kiểm thử mô hình hoặc kiểm thử tích hợp của DEV/OPS/TEST.
