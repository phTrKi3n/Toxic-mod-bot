# README (nhánh `test`) — Nhánh tích hợp Dev-Sec-Ops, đồ án "Hệ thống phát hiện bình luận độc hại"

## ĐỌC TRƯỚC KHI LÀM BẤT KỲ VIỆC GÌ, KHÔNG NGOẠI LỆ

> Đây là yêu cầu bắt buộc cho mọi AI agent chạm vào nhánh `test`, kể cả khi chỉ merge hộ một nhánh role hoặc sửa một dòng nhỏ. Agent phải đọc đủ 5 file theo đúng thứ tự sau, trước khi merge, sửa, hoặc xoá bất kỳ file nào:
>
> 1. `README.md` (ở nhánh `main`) — quy trình Git chung, mô hình nhánh role -> test -> main.
> 2. `rule.md` — phạm vi chung của đồ án, KHÔNG được tự ý mở rộng.
> 3. `log.md` — lịch sử quyết định chung, đọc ít nhất 10 entry gần nhất để biết hiện trạng.
> 4. `log_dev.md`, `log_sec.md`, `log_ops.md` — lướt qua entry mới nhất của cả 3 file, vì `test` là nơi cả 3 role gặp nhau.
> 5. Kết quả CI lần chạy gần nhất trên `test` (tab Actions trên GitHub) — biết đang xanh hay đỏ trước khi merge thêm gì vào.
>
> Nếu thiếu bất kỳ file nào trong danh sách trên, hoặc không thấy lịch sử CI, agent phải **dừng lại và báo cho người dùng biết ngay**, không tự đoán trạng thái tích hợp hiện tại rồi merge liều.

## 1. `test` dùng để làm gì

`test` là nơi duy nhất cả 3 phần DEV, SEC, OPS gặp nhau trước khi vào `main`. Nhánh này không thuộc riêng vai trò nào, không ai "làm việc" trực tiếp trên `test` theo nghĩa viết code mới ở đây; việc duy nhất diễn ra trên `test` là:

- Merge nhánh `dev`, `sec`, `ops` vào khi từng role báo đã xong một phần việc.
- Chạy CI (`.github/workflows/ci.yml`) để xem 3 phần ghép lại có còn chạy được không.
- Sửa xung đột phát sinh khi merge nhiều nhánh role cùng lúc (đặc biệt ở `log.md`, `rule.md`, xem `README.md` mục 6).
- Khi ổn định, chuyển tiếp sang `main` (do 1 người đại diện duyệt, xem `README.md` mục 9), KHÔNG phải người vừa merge vào `test` tự ý đẩy tiếp sang `main`.

`test` là nhánh sống lâu dài, dùng xuyên suốt dự án, không xoá đi rồi tạo lại theo từng đợt.

## 2. Quy tắc merge nhánh role vào `test`

- Nhận merge từ `dev`, `sec`, `ops`, theo thứ tự role nào xong trước merge trước, không cần chờ cả 3 role cùng xong mới merge một lượt.
- Trước khi merge một nhánh role vào, đảm bảo nhánh đó đã `git pull --rebase origin main` gần nhất (tránh mang theo code cũ).
- Sau khi merge, chạy CI ngay. Nếu CI đỏ, xác định lỗi do phần nào (DEV/SEC/OPS) và báo lại đúng role đó sửa, không tự ý sửa code thay cho role khác nếu không chắc.
- Nếu merge một nhánh role vào `test` phát sinh conflict ở file chung (`rule.md`, `log.md`), xử lý theo đúng `README.md` mục 6 (giữ cả hai dòng log, không dùng `--ours`/`--theirs` tràn lan).
- Nếu merge phát sinh conflict ở file `.docx`, xử lý theo `README.md` mục 7 (không tự gộp tay trong Word, chọn bản mới nhất đã review rồi áp lại phần thiếu).

## 3. Điều kiện để coi `test` là "ổn định", sẵn sàng lên `main`

1. CI trên `test` đang xanh.
2. Không còn PR nào từ `dev`/`sec`/`ops` đang chờ merge mà 3 role dự định gộp vào đợt này.
3. Không còn conflict chưa giải quyết trong `rule.md`/`log.md`/`.docx`.

Khi đủ 3 điều kiện trên, báo cho người đại diện nhóm để họ duyệt merge `test` vào `main` theo checklist ở `README.md` mục 9. Agent không tự ý merge `test` vào `main` thay cho người đại diện.

## 4. Ghi log

Việc merge/tích hợp trên `test` không phải một "quyết định nội dung" nên không bắt buộc phải thêm entry mới vào `log.md`. Chỉ ghi log nếu trong lúc xử lý conflict, agent phải tự quyết định giữ bản nào/bỏ bản nào ở một chỗ có thể ảnh hưởng phạm vi chung (actor, use case, entity, kiến trúc, mô hình) — trường hợp đó dừng lại hỏi người dùng trước, không tự quyết rồi merge luôn.

## 5. Khi không chắc

Dừng lại và hỏi người dùng thay vì tự đoán trạng thái tích hợp hoặc tự ý sửa code của role khác để CI qua cho nhanh.
