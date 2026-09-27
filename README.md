# README (nhánh `dev`) — Vai trò DEV, đồ án "Hệ thống phát hiện bình luận độc hại"

## ĐỌC TRƯỚC KHI LÀM BẤT KỲ VIỆC GÌ, KHÔNG NGOẠI LỆ

> Đây là yêu cầu bắt buộc cho mọi AI agent nhận việc trên nhánh `dev`, kể cả khi nhiệm vụ được giao nghe rất nhỏ (ví dụ "sửa 1 dòng", "thêm 1 test"). Agent phải đọc đủ 5 file theo đúng thứ tự sau, trước khi tạo, sửa, hoặc xoá bất kỳ file nào:
>
> 1. `README.md` (ở nhánh `main`) — quy trình Git chung, cách tránh conflict.
> 2. `rule.md` — phạm vi chung của đồ án, KHÔNG được tự ý mở rộng.
> 3. `rule_dev.md` — phạm vi riêng của vai trò DEV.
> 4. `log.md` — lịch sử quyết định chung, đọc ít nhất các entry từ lần gần nhất có nhãn `[DEV]` hoặc `[CHUNG]`.
> 5. `log_dev.md` — toàn bộ lịch sử quyết định riêng của DEV.
>
> Nếu thiếu bất kỳ file nào trong 5 file trên, agent phải **dừng lại và báo cho người dùng biết ngay**, không tự đoán nội dung, không tự tạo file thay thế, không tự suy diễn phạm vi. Sau khi đọc xong, agent tự tóm tắt lại trong đầu (không cần viết ra) 3 điều: đề tài đang giới hạn ở 4 chức năng nào, DEV đang phụ trách đúng phần gì, quyết định gần nhất liên quan tới phần mình sắp sửa là gì.

## 1. DEV phụ trách gì

- Pipeline NLP song ngữ Việt-Anh: detect ngôn ngữ, tiền xử lý, embedding, model (XLM-R fine-tune), ngưỡng phân loại.
- Use case, ERD, entity liên quan trực tiếp tới 4 chức năng chính (Thu thập, Gắn nhãn, Kiểm duyệt, Khiếu nại).
- Nội dung kỹ thuật ở Chương I-III của báo cáo.

Chi tiết đầy đủ nằm ở `rule_dev.md`, không lặp lại ở đây; file này chỉ tóm tắt để agent định hướng nhanh.

## 2. Việc DEV không được tự quyết

Đổi mô hình nền, đổi phạm vi ngôn ngữ, đổi 4 chức năng chính, đổi actor hoặc entity cốt lõi đã chốt ở Chương III. Gặp trường hợp này, agent dừng lại, báo người dùng, không tự quyết rồi merge.

## 3. Ghi log ngay khi có quyết định

Mọi quyết định trong phạm vi DEV ghi ngay vào `log_dev.md`, đúng khuôn 5 trường (Ngày, Quyết định, Lý do, Ảnh hưởng) như `log.md`, entry mới nhất nằm trên cùng. Quyết định nào đụng phạm vi chung thì đồng thời thêm 1 dòng tóm tắt vào `log.md`, nhãn `[DEV] ...` ở đầu cột Quyết định. Không giữ quyết định trong đầu chờ gộp lại cuối phiên, ghi ngay để không mất nếu phiên làm việc kết thúc giữa chừng.

## 4. Quy tắc Git riêng cho nhánh này

- `dev` được tạo từ `main` (tạo 1 lần lúc đầu dự án, dùng lại lâu dài, không tạo lại mỗi đợt việc).
- Trước khi bắt đầu: `git checkout dev` rồi `git pull --rebase origin main`.
- Mọi thay đổi, dù nhỏ, commit ngay, không gộp nhiều việc rồi mới commit 1 lần (áp dụng cho toàn repo, xem `README.md` mục 4).
- Việc nhỏ: commit thẳng lên `dev`. Việc lớn hoặc còn thử nghiệm: tách `dev/ten-viec-ngan` từ `dev`, xong thì merge lại vào `dev` trước.
- Commit message bắt đầu bằng `[DEV] `.
- Đưa việc đã xong vào **`test`** (KHÔNG merge thẳng vào `main`): mở PR hoặc merge từ `dev` vào `test`. Nếu đụng phạm vi chung (actor, use case, entity, model, kiến trúc tổng, hoặc sửa `rule.md`), báo cho SEC/OPS biết trước khi merge. Nếu chỉ sửa trong phạm vi riêng DEV, tự merge vào `test` được.
- `test` -> `main` do 1 người đại diện nhóm phụ trách, DEV không tự ý merge `test` vào `main`.
- File `.docx` báo cáo là nhị phân, không merge được: trước khi mở sửa, báo cho SEC/OPS biết, sửa xong merge vào `test` trong ngày, không giữ nhánh mở nhiều ngày. Chi tiết đầy đủ ở `README.md` (`main`) mục 7.
- Không paste lại nguyên văn `rule.md`/`log.md` khi chỉ sửa 1 đoạn nhỏ, giữ diff gọn để dễ review.
- Sau khi `main` được cập nhật (do merge `test` vào `main`), chạy lại `git pull --rebase origin main` trên `dev` để đồng bộ.

## 5. Checklist trước khi commit hoặc mở PR

1. Đã đọc đủ 5 file ở mục "ĐỌC TRƯỚC KHI LÀM" chưa.
2. Đã `git pull --rebase origin main` gần nhất chưa.
3. Đã ghi log vào `log_dev.md` (và `log.md` nếu đụng phạm vi chung) chưa.
4. Có đổi actor/use case/entity cốt lõi không, nếu có đã hỏi người dùng/tag role khác chưa.
5. Có đang sửa file `.docx` không, nếu có đã báo trước cho SEC/OPS chưa.

## 6. Khi không chắc

Dừng lại và hỏi người dùng thay vì tự suy đoán rồi làm, đúng nguyên tắc "làm nhanh nhưng đúng phạm vi" của `rule.md` mục 4-5.
