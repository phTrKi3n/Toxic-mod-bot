# SEC | Rà soát nội dung bảo mật Chương III và IV

Ngày: 2026-10-29  
Tài liệu được đối chiếu: `docs/BaoCao_DoAn_6Chuong_DevSecOps.docx` trong bản ZIP đã nhận.  
**Không sửa `.docx` chung**: theo quy định Git, phải thông báo DEV/OPS và chỉ một người sửa file Word tại một thời điểm.

## 1. Các phần đã có, không cần viết lại

- **Chương III, phần phân quyền/an toàn schema:** nêu `app_user.role`, `appeal.message_id` là UNIQUE, `moderation_action.decided_by` và các ràng buộc. Mã nguồn `db/models.py` có các trường/ràng buộc phù hợp ở mức thiết kế.
- **Chương IV, mục V Threat Model:** bảng đã có **7 nhóm mối đe dọa**: raid, spam/DoS, evasion, rò rỉ token, SQL injection, lạm quyền, máy chủ bị chiếm/C2. Không thêm nhóm trùng lặp và không đổi sơ đồ.
- **Chương III, activity theo ngưỡng:** văn bản nêu thấp hơn ngưỡng thấp là bỏ qua; ở giữa là đánh dấu; đạt ngưỡng cao là xóa. Phần này phù hợp `bot/actions.py` ở mức chọn nhánh.

## 2. Các điểm cần trao đổi, chưa tự ý sửa

| Vị trí báo cáo | Đối chiếu thực tế | Đề xuất xử lý | Người phối hợp |
|---|---|---|---|
| Chương III, IV, mục “Một số truy vấn tiêu biểu”: `WHERE c.score BETWEEN 0.30 AND 0.90` | `BETWEEN` bao gồm điểm `0.90`, trong khi `bot/actions.py` chuyển `score >= 0.90` sang nhánh xóa | DEV xác nhận và nếu thống nhất sửa điều kiện hàng đợi thành `c.score >= 0.30 AND c.score < 0.90` | DEV |
| Chương II mục IV.4, câu “Quyết định xoá, giữ, khôi phục đều ghi log” và Chương III mô tả UC04-UC06 | Đây là thiết kế/kỳ vọng; `bot/actions.py` và `bot/commands.py` còn `NotImplementedError` | Giữ nội dung nếu nói về **thiết kế dự kiến**; không trình bày như kết quả triển khai và kiểm thử đã hoàn thành | DEV, người chỉnh Word |
| Chương III, mục “Ràng buộc an toàn dữ liệu ở mức schema” | Có cấu trúc audit ở ERD, nhưng chưa xác minh log/audit được ghi thật | Chỉ khẳng định **schema hỗ trợ truy vết**, không khẳng định mọi quyết định đã được lưu | SEC/DEV |
| Chương IV, mục V, Threat Model và Chương V phần kiểm thử | Các biện pháp chủ yếu ở dạng đề xuất hoặc kế hoạch, không phải kết quả pentest; Chương VI đã nêu đồ án còn ở mức phân tích/thiết kế | Tiếp tục phân biệt “đã thiết kế”, “đã unit test” và “đã tích hợp thực tế” | SEC/OPS |

## 3. Đoạn bổ sung ngắn có thể đưa vào báo cáo nếu nhóm đồng ý

> **An toàn dữ liệu người dùng (SEC).** Hệ thống được thiết kế để lưu nội dung bình luận, điểm phân loại và lý do khiếu nại. Dữ liệu này có thể chứa thông tin riêng tư nên cần giới hạn quyền đọc, tránh ghi nội dung không cần thiết vào log và xác định thời gian lưu phù hợp. Các trường lịch sử kiểm duyệt trong mô hình dữ liệu hỗ trợ truy vết quyết định, nhưng hiệu quả kiểm soát phải được xác minh lại khi các chức năng ghi dữ liệu và xử lý khiếu nại được tích hợp hoàn chỉnh.
>
> **Rủi ro sai lệch kiểm duyệt (SEC).** Sai dương tính có thể dẫn đến xóa nhầm bình luận hợp lệ; sai âm tính khiến bình luận độc hại không được xử lý. Ở mức logic hiện có, điểm thấp hơn 0.30 không kích hoạt xử lý, điểm từ 0.30 đến dưới 0.90 được chuyển vào nhánh đánh dấu, còn điểm từ 0.90 trở lên kích hoạt nhánh xóa. Nhóm SEC đã bổ sung kiểm thử mô phỏng cho các ranh giới quyết định này. Kết quả không thay thế việc đánh giá Precision, Recall và F1-score bằng tập dữ liệu có nhãn hoặc thử nghiệm kiểm duyệt thực tế.

## 4. Trạng thái bàn giao

- [x] Đã đối chiếu nội dung SEC trên Word với code ở mức mã nguồn.
- [x] Đã ghi các nội dung có thể bổ sung mà không đổi sơ đồ/luồng.
- [ ] DEV xác nhận điều kiện truy vấn hàng đợi tại điểm 0.90.
- [ ] Nhóm thống nhất thời điểm sửa `.docx` chung và áp dụng đoạn bổ sung (nếu cần).
- [ ] Kiểm thử tích hợp sau khi DEV/OPS hiện thực các handler.

**Kết luận:** SEC đã hoàn thành rà soát và chuẩn bị nội dung. Chưa sửa báo cáo Word hay tuyên bố các chức năng đang TODO là đã hoạt động.
