# README (nhánh `ops`) — Vai trò OPS, đồ án "Hệ thống phát hiện bình luận độc hại"

## ĐỌC TRƯỚC KHI LÀM BẤT KỲ VIỆC GÌ, KHÔNG NGOẠI LỆ

> Đây là yêu cầu bắt buộc cho mọi AI agent nhận việc trên nhánh `ops`, kể cả khi nhiệm vụ được giao nghe rất nhỏ (ví dụ "thêm 1 bước CI", "sửa 1 dòng deploy"). Agent phải đọc đủ 5 file theo đúng thứ tự sau, trước khi tạo, sửa, hoặc xoá bất kỳ file nào:
>
> 1. `README.md` (ở nhánh `main`) — quy trình Git chung, cách tránh conflict.
> 2. `rule.md` — phạm vi chung của đồ án, KHÔNG được tự ý mở rộng.
> 3. `rule_ops.md` — phạm vi riêng của vai trò OPS.
> 4. `log.md` — lịch sử quyết định chung, đọc ít nhất các entry từ lần gần nhất có nhãn `[OPS]` hoặc `[CHUNG]`.
> 5. `log_ops.md` — toàn bộ lịch sử quyết định riêng của OPS.
>
> Nếu thiếu bất kỳ file nào trong 5 file trên, agent phải **dừng lại và báo cho người dùng biết ngay**, không tự đoán nội dung, không tự tạo file thay thế, không tự suy diễn phạm vi. Sau khi đọc xong, agent tự tóm tắt lại trong đầu (không cần viết ra) 3 điều: đề tài đang giới hạn ở 4 chức năng nào, OPS đang phụ trách đúng phần gì, quyết định gần nhất liên quan tới phần mình sắp sửa là gì (ví dụ pipeline CI/CD hiện đã có những bước nào rồi, tránh thêm trùng hoặc đổi ngược lại).

## 1. OPS phụ trách gì

- Triển khai, giám sát, CI/CD cho bot.
- Kiểm thử (Chương V): test case, tiêu chí đánh giá (F1-score trên tập validation trộn Anh-Việt).
- Xử lý sự cố vận hành, khả năng mở rộng (scaling) khi lượng tin nhắn tăng.
- Nội dung vận hành/kiểm thử ở Chương IV-V của báo cáo.

Chi tiết đầy đủ nằm ở `rule_ops.md`, không lặp lại ở đây; file này chỉ tóm tắt để agent định hướng nhanh.

## 2. Việc OPS không được tự quyết

Đổi kiến trúc triển khai tổng (ví dụ đổi nền tảng bot từ Discord/Telegram sang thứ khác). Gặp trường hợp này, agent dừng lại, báo người dùng, không tự quyết rồi merge.

## 3. Ghi log ngay khi có quyết định

Mọi quyết định trong phạm vi OPS ghi ngay vào `log_ops.md`, đúng khuôn 5 trường (Ngày, Quyết định, Lý do, Ảnh hưởng) như `log.md`, entry mới nhất nằm trên cùng. Quyết định nào đụng phạm vi chung thì đồng thời thêm 1 dòng tóm tắt vào `log.md`, nhãn `[OPS] ...` ở đầu cột Quyết định. Không giữ quyết định trong đầu chờ gộp lại cuối phiên, ghi ngay để không mất nếu phiên làm việc kết thúc giữa chừng.

Lưu ý riêng cho OPS: mọi bước CI/CD hoặc giám sát thêm vào phải dựa trên công cụ/dịch vụ có thật và phổ biến (GitHub Actions, Docker, health-check, webhook cảnh báo...), không bịa quy trình hay dịch vụ không tồn tại, đúng nguyên tắc `rule.md` mục 2.

## 4. Quy tắc Git riêng cho nhánh này

- `ops` được tạo từ `main` (tạo 1 lần lúc đầu dự án, dùng lại lâu dài, không tạo lại mỗi đợt việc).
- Trước khi bắt đầu: `git checkout ops` rồi `git pull --rebase origin main`.
- Mọi thay đổi, dù nhỏ, commit ngay, không gộp nhiều việc rồi mới commit 1 lần (áp dụng cho toàn repo, xem `README.md` mục 4).
- Việc nhỏ: commit thẳng lên `ops`. Việc lớn hoặc còn thử nghiệm: tách `ops/ten-viec-ngan` từ `ops`, xong thì merge lại vào `ops` trước.
- Commit message bắt đầu bằng `[OPS] `.
- Đưa việc đã xong vào **`test`** (KHÔNG merge thẳng vào `main`): mở PR hoặc merge từ `ops` vào `test`. Nếu đụng phạm vi chung (actor, use case, entity, model, kiến trúc tổng, hoặc sửa `rule.md`), báo cho DEV/SEC biết trước khi merge. Nếu chỉ sửa trong phạm vi riêng OPS (ví dụ thêm 1 bước lint vào pipeline CI), tự merge vào `test` được.
- `test` -> `main` do 1 người đại diện nhóm phụ trách, OPS không tự ý merge `test` vào `main`.
- File `.docx` báo cáo là nhị phân, không merge được: trước khi mở sửa, báo cho DEV/SEC biết, sửa xong merge vào `test` trong ngày, không giữ nhánh mở nhiều ngày. Chi tiết đầy đủ ở `README.md` (`main`) mục 7.
- Không paste lại nguyên văn `rule.md`/`log.md` khi chỉ sửa 1 đoạn nhỏ, giữ diff gọn để dễ review.
- File cấu hình CI (`.github/workflows/*.yml`) và cấu trúc thư mục triển khai là của OPS; nếu DEV/SEC cần đổi, để OPS thực hiện hoặc duyệt lại trước khi merge vào `test`.
- Sau khi `main` được cập nhật (do merge `test` vào `main`), chạy lại `git pull --rebase origin main` trên `ops` để đồng bộ.

## 5. Checklist trước khi commit hoặc mở PR

1. Đã đọc đủ 5 file ở mục "ĐỌC TRƯỚC KHI LÀM" chưa.
2. Đã `git pull --rebase origin main` gần nhất chưa.
3. Đã ghi log vào `log_ops.md` (và `log.md` nếu đụng phạm vi chung) chưa.
4. Bước CI/CD hoặc giám sát mới thêm có dựa trên công cụ thật không, có đổi kiến trúc triển khai tổng không.
5. Có đang sửa file `.docx` không, nếu có đã báo trước cho DEV/SEC chưa.

## 6. Khi không chắc

Dừng lại và hỏi người dùng thay vì tự suy đoán rồi làm, đúng nguyên tắc "làm nhanh nhưng đúng phạm vi" của `rule.md` mục 4-5.
