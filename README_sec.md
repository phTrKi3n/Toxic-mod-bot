# README (nhánh `sec`) — Vai trò SEC, đồ án "Hệ thống phát hiện bình luận độc hại"

## ĐỌC TRƯỚC KHI LÀM BẤT KỲ VIỆC GÌ, KHÔNG NGOẠI LỆ

> Đây là yêu cầu bắt buộc cho mọi AI agent nhận việc trên nhánh `sec`, kể cả khi nhiệm vụ được giao nghe rất nhỏ (ví dụ "thêm 1 dòng threat model", "sửa 1 câu"). Agent phải đọc đủ 5 file theo đúng thứ tự sau, trước khi tạo, sửa, hoặc xoá bất kỳ file nào:
>
> 1. `README.md` (ở nhánh `main`) — quy trình Git chung, cách tránh conflict.
> 2. `rule.md` — phạm vi chung của đồ án, KHÔNG được tự ý mở rộng.
> 3. `rule_sec.md` — phạm vi riêng của vai trò SEC.
> 4. `log.md` — lịch sử quyết định chung, đọc ít nhất các entry từ lần gần nhất có nhãn `[SEC]` hoặc `[CHUNG]`.
> 5. `log_sec.md` — toàn bộ lịch sử quyết định riêng của SEC.
>
> Nếu thiếu bất kỳ file nào trong 5 file trên, agent phải **dừng lại và báo cho người dùng biết ngay**, không tự đoán nội dung, không tự tạo file thay thế, không tự suy diễn phạm vi. Sau khi đọc xong, agent tự tóm tắt lại trong đầu (không cần viết ra) 3 điều: đề tài đang giới hạn ở 4 chức năng nào, SEC đang phụ trách đúng phần gì, quyết định gần nhất liên quan tới phần mình sắp sửa là gì (ví dụ threat model đã liệt kê những mối đe doạ nào rồi, tránh thêm trùng).

## 1. SEC phụ trách gì

- Threat model cho bot kiểm duyệt Discord/Telegram: giả mạo, spam tấn công model, injection vào input, và các mối đe doạ tương tự (ví dụ khả năng kết nối C2 nếu máy chủ bị xâm nhập, nếu đã được người dùng xác nhận đưa vào phạm vi).
- RBAC/phân quyền giữa người dùng, kiểm duyệt viên, admin.
- An toàn dữ liệu người dùng khi thu thập/lưu bình luận; rủi ro khi bot tự động xoá/cảnh báo tin nhắn (sai dương tính/sai âm tính).
- Nội dung bảo mật ở Chương III-IV của báo cáo.

Chi tiết đầy đủ nằm ở `rule_sec.md`, không lặp lại ở đây; file này chỉ tóm tắt để agent định hướng nhanh.

## 2. Việc SEC không được tự quyết

Thêm cơ chế bảo mật làm đổi luồng Activity/Use case đã chốt ở Chương III. Gặp trường hợp này, agent dừng lại, báo người dùng, không tự quyết rồi merge. Threat model chỉ được **thêm mục mô tả và biện pháp giảm thiểu**, không được tự ý vẽ lại sơ đồ Activity/Use case đã có.

## 3. Ghi log ngay khi có quyết định

Mọi quyết định trong phạm vi SEC ghi ngay vào `log_sec.md`, đúng khuôn 5 trường (Ngày, Quyết định, Lý do, Ảnh hưởng) như `log.md`, entry mới nhất nằm trên cùng. Quyết định nào đụng phạm vi chung thì đồng thời thêm 1 dòng tóm tắt vào `log.md`, nhãn `[SEC] ...` ở đầu cột Quyết định. Không giữ quyết định trong đầu chờ gộp lại cuối phiên, ghi ngay để không mất nếu phiên làm việc kết thúc giữa chừng.

Lưu ý riêng cho SEC: mỗi mối đe doạ thêm vào bảng Threat Model phải kèm biện pháp giảm thiểu dựa trên cơ chế có thật (Discord AutoMod, rate limit, ORM/parameterized query, biến môi trường, audit log...), không bịa kỹ thuật, đúng nguyên tắc `rule.md` mục 2.

## 4. Quy tắc Git riêng cho nhánh này

- `sec` được tạo từ `main` (tạo 1 lần lúc đầu dự án, dùng lại lâu dài, không tạo lại mỗi đợt việc).
- Trước khi bắt đầu: `git checkout sec` rồi `git pull --rebase origin main`.
- Mọi thay đổi, dù nhỏ, commit ngay, không gộp nhiều việc rồi mới commit 1 lần (áp dụng cho toàn repo, xem `README.md` mục 4).
- Việc nhỏ: commit thẳng lên `sec`. Việc lớn hoặc còn thử nghiệm: tách `sec/ten-viec-ngan` từ `sec`, xong thì merge lại vào `sec` trước.
- Commit message bắt đầu bằng `[SEC] `.
- Đưa việc đã xong vào **`test`** (KHÔNG merge thẳng vào `main`): mở PR hoặc merge từ `sec` vào `test`. Nếu đụng phạm vi chung (actor, use case, entity, model, kiến trúc tổng, hoặc sửa `rule.md`), báo cho DEV/OPS biết trước khi merge. Nếu chỉ sửa trong phạm vi riêng SEC (ví dụ thêm 1 dòng threat model không đổi luồng), tự merge vào `test` được.
- `test` -> `main` do 1 người đại diện nhóm phụ trách, SEC không tự ý merge `test` vào `main`.
- File `.docx` báo cáo là nhị phân, không merge được: trước khi mở sửa, báo cho DEV/OPS biết, sửa xong merge vào `test` trong ngày, không giữ nhánh mở nhiều ngày. Chi tiết đầy đủ ở `README.md` (`main`) mục 7.
- Không paste lại nguyên văn `rule.md`/`log.md` khi chỉ sửa 1 đoạn nhỏ, giữ diff gọn để dễ review.
- Sau khi `main` được cập nhật (do merge `test` vào `main`), chạy lại `git pull --rebase origin main` trên `sec` để đồng bộ.

## 5. Checklist trước khi commit hoặc mở PR

1. Đã đọc đủ 5 file ở mục "ĐỌC TRƯỚC KHI LÀM" chưa.
2. Đã `git pull --rebase origin main` gần nhất chưa.
3. Đã ghi log vào `log_sec.md` (và `log.md` nếu đụng phạm vi chung) chưa.
4. Mối đe doạ mới thêm có biện pháp giảm thiểu dựa trên cơ chế có thật không, có làm đổi luồng Activity/Use case đã chốt không.
5. Có đang sửa file `.docx` không, nếu có đã báo trước cho DEV/OPS chưa.

## 6. Khi không chắc

Dừng lại và hỏi người dùng thay vì tự suy đoán rồi làm, đúng nguyên tắc "làm nhanh nhưng đúng phạm vi" của `rule.md` mục 4-5. Đặc biệt: nếu một mối đe doạ nghe có vẻ giống một tính năng tấn công thật (ví dụ dựng kênh điều khiển từ xa) thay vì mô tả rủi ro phòng thủ, dừng lại và hỏi rõ ý người dùng trước khi viết.
