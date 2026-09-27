# HƯỚNG DẪN CHO AI AGENT — Dựng nhánh Git đúng mô hình Dev-Sec-Ops

Tài liệu này viết cho một AI agent (không phải người) thực thi trực tiếp bằng lệnh Git. Làm đúng thứ tự, đúng từng bước, kiểm tra kết quả sau mỗi bước trước khi sang bước tiếp theo. Gặp bất kỳ kết quả nào khác với "Kết quả mong đợi" nêu trong bước đó, DỪNG LẠI và báo người dùng, không tự đoán tiếp.

## Mục tiêu cuối cùng

Từ một khung xương thư mục duy nhất (`toxic-mod-bot/`), dựng ra 5 nhánh trên GitHub: `main`, `test`, `dev`, `sec`, `ops`. Cả 5 nhánh có cấu trúc thư mục giống hệt nhau (để merge dễ), chỉ khác nhau ở file `README.md` tại gốc (mỗi nhánh có bản README đúng vai trò của nó). Mô hình nhánh đầy đủ: xem `README.md` (bản ở `main`) mục 3.

## Điều kiện cần trước khi bắt đầu

Agent kiểm tra đủ 3 điều sau, nếu thiếu điều nào thì dừng lại hỏi người dùng:

1. Đã có sẵn thư mục khung xương `toxic-mod-bot/` đầy đủ file (rule*.md, log*.md, README*.md, docs/, bot/, inference_service/, db/, training/, tests/, .github/).
2. Lệnh `git` chạy được trong môi trường hiện tại (`git --version` không lỗi).
3. Người dùng đã cho biết URL của repo GitHub trống để push vào, hoặc xác nhận agent được phép tạo repo hộ (nếu agent có quyền gọi GitHub API/CLI). Nếu không có URL và agent không tự tạo được repo, dừng lại hỏi người dùng URL trước khi chạy bước 2.

## Bước 0 — Xác nhận đang đứng đúng chỗ

```bash
cd toxic-mod-bot
ls
```

Kết quả mong đợi: thấy đủ `README.md`, `README_dev.md`, `README_sec.md`, `README_ops.md`, `README_test.md`, `rule.md`, `log.md`, `docs/`, `bot/`, v.v. Nếu thiếu file nào trong danh sách này, dừng lại, không tự tạo file thay thế.

## Bước 1 — Khởi tạo Git và commit khung xương lên `main`

```bash
git init
git add .
git status
```

Kết quả mong đợi: `git status` liệt kê toàn bộ file trong khung xương ở mục "Changes to be committed", không có file nào bị thiếu bất thường (ví dụ thiếu cả thư mục `bot/`).

```bash
git commit -m "[CHUNG] khoi tao khung repo dung chung cho ca 3 role"
git branch -M main
```

## Bước 2 — Gắn remote và push `main`

```bash
git remote add origin <URL_REPO_GITHUB>
git push -u origin main
```

Thay `<URL_REPO_GITHUB>` bằng URL người dùng đã cung cấp ở "Điều kiện cần trước khi bắt đầu". Nếu `git push` báo lỗi xác thực (authentication), dừng lại, báo người dùng tự cấu hình quyền truy cập GitHub (SSH key hoặc token), agent không tự tạo hay đoán thông tin xác thực.

Kết quả mong đợi: push thành công, `main` xuất hiện trên GitHub với đúng cấu trúc thư mục của khung xương.

## Bước 3 — Tạo nhánh `test` (nhánh tích hợp, sống lâu dài)

```bash
git checkout -b test
mv README_test.md README.md
git add README.md README_test.md
git commit -m "[TEST] dung README rieng cho nhanh test"
git push -u origin test
```

Kết quả mong đợi: nhánh `test` trên GitHub có `README.md` là nội dung của `README_test.md` cũ (mở đầu bằng khối "ĐỌC TRƯỚC KHI LÀM BẤT KỲ VIỆC GÌ" dành riêng cho `test`), file `README_test.md` không còn tồn tại trên nhánh này nữa (đã đổi tên), các file khác giữ nguyên như `main`.

## Bước 4 — Tạo nhánh `dev`

```bash
git checkout main
git checkout -b dev
mv README_dev.md README.md
git add README.md README_dev.md
git commit -m "[DEV] dung README rieng cho nhanh dev"
git push -u origin dev
```

Kết quả mong đợi: nhánh `dev` có `README.md` là bản dành cho DEV, các file khác giống `main`.

## Bước 5 — Tạo nhánh `sec`

```bash
git checkout main
git checkout -b sec
mv README_sec.md README.md
git add README.md README_sec.md
git commit -m "[SEC] dung README rieng cho nhanh sec"
git push -u origin sec
```

Kết quả mong đợi: nhánh `sec` có `README.md` là bản dành cho SEC, các file khác giống `main`.

## Bước 6 — Tạo nhánh `ops`

```bash
git checkout main
git checkout -b ops
mv README_ops.md README.md
git add README.md README_ops.md
git commit -m "[OPS] dung README rieng cho nhanh ops"
git push -u origin ops
```

Kết quả mong đợi: nhánh `ops` có `README.md` là bản dành cho OPS, các file khác giống `main`.

## Bước 7 — Xác nhận lại toàn bộ (bắt buộc, không bỏ qua)

```bash
git checkout main
git branch -a
```

Kết quả mong đợi: thấy đủ `main`, `test`, `dev`, `sec`, `ops` (và các bản `remotes/origin/...` tương ứng).

Kiểm tra từng nhánh có đúng README riêng, không cần checkout qua lại, dùng `git show`:

```bash
git show origin/main:README.md | head -3
git show origin/test:README.md | head -3
git show origin/dev:README.md | head -3
git show origin/sec:README.md | head -3
git show origin/ops:README.md | head -3
```

Kết quả mong đợi: dòng đầu tiên của mỗi lệnh khác nhau, khớp đúng tiêu đề từng file gốc:

- `origin/main` -> `# README — Quy trình làm việc Dev-Sec-Ops & Git...`
- `origin/test` -> `# README (nhánh \`test\`) — Nhánh tích hợp Dev-Sec-Ops...`
- `origin/dev` -> `# README (nhánh \`dev\`) — Vai trò DEV...`
- `origin/sec` -> `# README (nhánh \`sec\`) — Vai trò SEC...`
- `origin/ops` -> `# README (nhánh \`ops\`) — Vai trò OPS...`

Nếu bất kỳ nhánh nào cho ra tiêu đề sai (ví dụ `dev` lại hiện tiêu đề của `sec`), dừng lại, báo người dùng, không tự sửa bằng cách đoán, vì rất có thể đã `mv` nhầm file ở bước trước.

## Bước 8 — Kiểm tra khung xương giống nhau giữa các nhánh

```bash
git diff main dev -- . ':!README.md' ':!README_dev.md'
git diff main sec -- . ':!README.md' ':!README_sec.md'
git diff main ops -- . ':!README.md' ':!README_ops.md'
git diff main test -- . ':!README.md' ':!README_test.md'
```

Kết quả mong đợi: cả 4 lệnh trên đều không in ra gì (không có khác biệt nào ngoài file README), xác nhận 5 nhánh dùng chung đúng 1 khung xương như người dùng yêu cầu.

## Sau khi setup xong

- Báo lại cho người dùng: đã tạo xong 5 nhánh, mỗi nhánh có README riêng, khung xương giống nhau.
- Không tự ý làm thêm việc gì khác (ví dụ không tự viết code vào `dev`) trừ khi người dùng yêu cầu tiếp.
- Từ đây, mọi AI agent nhận việc trên nhánh `dev`/`sec`/`ops`/`test` phải đọc đúng `README.md` của nhánh đó trước (khối "ĐỌC TRƯỚC KHI LÀM BẤT KỲ VIỆC GÌ"), theo đúng quy trình đã mô tả trong các file đó.

## Việc agent KHÔNG được tự ý làm trong lúc setup

- Không tự đổi nội dung `rule.md`, `rule_dev.md`, `rule_sec.md`, `rule_ops.md` để "cho hợp lý hơn".
- Không tự xoá hay gộp bớt nhánh nếu thấy "thừa".
- Không tự tạo thêm nhánh ngoài 5 nhánh trên nếu người dùng không yêu cầu.
- Không tự quyết định URL repo hay quyền truy cập GitHub, luôn hỏi người dùng nếu thiếu thông tin này.
