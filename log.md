# LOG.md — Nhật ký quyết định dự án

## Quy tắc ghi log (đọc trước khi thêm entry mới)

1. Mỗi entry tối đa **5 dòng**: Ngày | Quyết định | Lý do ngắn | Ảnh hưởng.
2. Chỉ ghi **quyết định/thay đổi định hướng**, KHÔNG ghi lại toàn bộ nội dung
   đã viết (nội dung nằm trong file báo cáo/slide, không lặp ở đây).
3. Giới hạn **tối đa 20 entry đang hoạt động**. Khi vượt quá:
   - Chuyển các entry cũ hơn (không còn ảnh hưởng tới quyết định hiện tại)
     xuống mục "Archive" ở cuối file, gộp thành 1 dòng tóm tắt mỗi 5 entry cũ.
4. Không copy-paste đoạn văn dài từ báo cáo vào log — chỉ tham chiếu tên mục
   (ví dụ: "Chương I mục 2").
5. Entry mới nhất nằm **trên cùng** của bảng "Active Log".
6. Từ 2026-09-25, mỗi role (Dev/Sec/Ops) có log riêng (`log_dev.md`,
   `log_sec.md`, `log_ops.md`) cho quyết định trong phạm vi role đó. File
   này (`log.md`) chỉ ghi quyết định ảnh hưởng phạm vi chung dự án — xem
   `rule.md` mục 7 về đồng bộ 2 tầng.

## Active Log

| Ngày | Quyết định | Lý do | Ảnh hưởng |
|---|---|---|---|
| 2026-09-27 | [CHUNG] Thêm mục 9 vào rule.md: 4 nguyên tắc làm việc khi code (suy nghĩ trước khi code, ưu tiên đơn giản, sửa đúng phạm vi, nêu tiêu chí hoàn thành), áp dụng cho cả 3 role | Người dùng muốn áp dụng nguyên tắc từ skill andrej-karpathy-skills để giảm lỗi thường gặp khi AI agent code (tự đoán, làm phức tạp hoá, sửa lan ra ngoài phạm vi) | Không đổi 4 chức năng chính hay phạm vi đề tài; 3 role không cần sửa file riêng, chỉ cần đọc mục 9 rule.md như các mục chung khác |
| 2026-09-27 | Chốt mô hình nhánh Git 2 tầng: `dev`/`sec`/`ops` đều tạo từ `main`, mỗi role tự làm rồi merge việc đã xong vào nhánh tích hợp `test` (sống lâu dài, không xoá giữa chừng); `test` ổn định (CI xanh) thì 1 người đại diện nhóm duyệt merge `test` vào `main`, không cần cả 3 role duyệt; mọi thay đổi dù nhỏ đều phải commit ngay, áp dụng toàn repo | Người dùng muốn 3 role làm việc thật sự độc lập trên nhánh riêng, có một bước tích hợp/kiểm tra chung trước khi vào `main`, và merge cuối cùng do 1 người quyết định thay vì chờ đồng thuận cả 3 | Viết lại `README.md` chung (mục 3, 4, 6-9) và thêm `README_test.md`; cập nhật `README_dev.md`/`README_sec.md`/`README_ops.md` mục 4 (đích merge đổi từ `main` sang `test`); cập nhật khung repo (`STRUCTURE.md` thêm lệnh khởi tạo 5 nhánh, `.github/workflows/ci.yml` thêm nhánh `test`); không đổi `rule.md` vì đây là quy trình Git, không phải phạm vi đề tài |
| 2026-09-26 | Viết lại báo cáo thành file mới `BaoCao_DoAn_6Chuong_DevSecOps.docx` (không sửa đè bản cũ): tổ chức lại toàn bộ 6 chương theo tư tưởng Dev-Sec-Ops xuyên suốt (trước đó chỉ 3 sơ đồ Chương III-IV có màu DEV/OP/SEC, phần văn bản chưa theo kịp); đổi tên Chương IV thành "Thiết kế kiến trúc và an toàn hệ thống" (thêm mục Mô hình mối đe doạ - SEC) và Chương V thành "Kiểm thử, CI/CD và triển khai" (thêm mục CI/CD và Giám sát vận hành - OPS); thêm bảng phân công vai trò Dev/Sec/Ops đầu báo cáo | Bản cũ chưa hoàn thiện theo đúng tư tưởng dev-sec-op dù sơ đồ đã làm trước; nhóm không muốn tạo tính năng bot mới, chỉ hệ thống hoá lại phần đã có và bổ sung đúng phần còn thiếu (threat model, CI/CD) dựa trên thực tế các bot Discord kiểm duyệt thật (Discord AutoMod, RaidProtect...), không bịa kỹ thuật | Không đổi actor/use case/entity/kiến trúc cốt lõi đã chốt (dùng lại nguyên 5 sơ đồ cũ image1-6); không đổi 4 chức năng chính hay phạm vi đề tài; đồng thời cập nhật `log_dev.md`, `log_sec.md`, `log_ops.md` |
| 2026-09-26 | Đội hình cập nhật đủ 3 thành viên (khớp 3 vai trò Dev/Sec/Ops), thay vì 2 thành viên như bản cũ | Người dùng xác nhận nhóm đã có thành viên mới | Cập nhật bìa báo cáo và bảng phân công vai trò; tên/MSSV thành viên thứ 3 và việc gán ai vào vai trò nào để trống dạng placeholder, chờ người dùng điền |
| 2026-09-25 | Chia dự án thành 3 vai trò Dev/Sec/Ops: tách `rule_dev.md`, `rule_sec.md`, `rule_ops.md` (quy tắc riêng từng role) và `log_dev.md`, `log_sec.md`, `log_ops.md` (log riêng từng role); `log.md` chung chỉ giữ quyết định ảnh hưởng phạm vi chung | Người dùng muốn 3 role làm việc riêng nhưng đồng bộ hệ thống chung; cần ghi log ngay khi quyết định, không giữ tạm, để tránh mất quyết định khi hết token giữa chừng | Thêm mục 7 vào `rule.md` (đổi mục "Trạng thái hiện tại" thành mục 8); không đổi 4 chức năng chính hay phạm vi đề tài ở mục 1 |
| 2026-09-14 | Đồng bộ `BaoCao_DoAn_6Chuong.docx` với diagram code đã tạo: sửa `model_version` thành `model_version_id` và bổ sung `restore` vào action_type trong bảng Entity Chương III.III.1; nối thêm câu khép vòng fine-tune (UC07-UC08-UC11) vào cuối luồng Activity Chương III.II | Cross-check 5 ảnh diagram render từ code PlantUML với docx phát hiện 2 chỗ lệch (bảng entity thiếu hậu tố _id và thiếu giá trị restore) và 1 chỗ activity diagram mở rộng hơn câu chữ gốc | Chỉ sửa câu/từ tại đúng 3 vị trí, không đổi cấu trúc chương; không đổi rule.md vì không phải thay đổi phạm vi |
| 2026-09-14 | Gán khung tư tưởng DEV-OP-SEC lên các sơ đồ Chương III-IV (Use case, ERD, Activity swimlane, kiến trúc), không đổi actor/use case/entity/thành phần đã có | Người dùng yêu cầu sửa file .docx theo tư tưởng dev-sec-op | Sửa trực tiếp 5 đoạn trong `BaoCao_DoAn_6Chuong.docx` (chỉ thêm đoạn giải thích, không viết lại chương); không đổi rule.md vì không phải thay đổi phạm vi đề tài |
| 2026-09-13 | Viết lại toàn bộ `BaoCao_DoAn_6Chuong.docx` theo văn phong bám paper mẫu (7 nguyên tắc), bỏ dấu "—" và "=" trong câu văn | Người dùng chê bản trước đọc như văn AI, yêu cầu bám giọng paper trong project | Thêm mục 6 "Nguyên tắc viết văn" vào `rule.md`; file docx đã build lại và kiểm tra render qua PDF |
| 2026-09-13 | Đổi phạm vi: viết đầy đủ 6 chương ngay (I-VI) làm bản mẫu thử, không còn hoãn Chương III-VI lại như trước | Người dùng yêu cầu bản mẫu đủ 6 chương để gửi thử | File mới `BaoCao_DoAn_6Chuong.docx` thay `BaoCao_DoAn_Chuong1-2_Bot.docx`; thêm Chương III (Use-case, ERD, SQL), IV (Kiến trúc/phát triển), V (Kiểm thử/triển khai), VI (Kết luận) |
| 2026-09-13 | Đổi lại: dùng 1 model song ngữ gộp chung (backbone XLM-R, fine-tune trên Jigsaw+ViHSD gộp lại) thay vì 2 model tách riêng; đổi khung ứng dụng thành bot kiểm duyệt kiểu Discord/Telegram (đọc tin nhắn realtime, tự xoá/cảnh báo) thay vì web platform; bỏ hẳn chi tiết ERD/CSDL/workflow ra khỏi Chương I-II — đã được thay thế bởi entry trên (ERD/SQL nay đưa vào Chương III cùng bản) | Người dùng chỉnh lại: muốn model gộp không tách nhánh; muốn hình dung là bot chat | Xem entry mới nhất |
| 2026-09-13 | Bỏ khung "song ngữ 1 model", đổi thành 2 nhánh riêng — đã bị thay thế bởi entry trên | Hiểu sai ý người dùng ở bước trước | Xem entry mới nhất |
| 2026-09-13 | Viết lại hoàn chỉnh Chương I-II lần 1 (docx) theo hướng song ngữ — đã bị thay thế bởi entry trên | Bản đầu chưa đúng ý (v thiếu dùng model có sẵn, viết văn phong AI) | Xem entry mới nhất |
| 2026-09-13 | Mở rộng phạm vi phân loại từ chỉ tiếng Việt sang **song ngữ Việt + Anh** | Đề bài yêu cầu rõ "phân loại tiếng Việt, tiếng Anh" | Cần thêm bước phát hiện ngôn ngữ (language detection) trước khi vào pipeline NLP; cập nhật Chương I mục 2-3 |
| 2026-09-13 | Chốt phạm vi chức năng = 4 khối: Thu thập, Gắn nhãn, Kiểm duyệt, Khiếu nại (bỏ chi tiết hoá Active Learning Loop hoàn chỉnh) | Theo tiêu chí đề bài đưa ra, tránh lan man | Chương II chỉ cần mô tả 4 khối này ở mức đủ, phần mở rộng ghi là "hướng phát triển" |
| 2026-09-13 | Trọng tâm thiết kế = Phân loại toxic/spam bằng NLP | Theo tiêu chí đề bài | Đầu tư kỹ nhất vào mô tả pipeline NLP (tiền xử lý → embedding → mô hình → ngưỡng phân loại) trong Chương I và II |
| 2026-09-13 | Dùng Visual Paradigm để vẽ Use Case/ERD, Claude chỉ cung cấp đặc tả | VP là công cụ người dùng chỉ định, Claude không thao tác trực tiếp trên web đó | Chương III có mô tả actor/use case/entity dạng text để đưa vào VP |
| 2026-09-13 | Tạo `rule.md` + `log.md` làm nền quản lý dự án | Yêu cầu người dùng, để tránh lan man và giữ tiến độ | Mọi quyết định lớn từ nay ghi vào log này, không lặp lại trong chat |
| 2026-09-13 | Ưu tiên làm slide ý tưởng trước, hoãn hoàn thiện toàn văn Chương I-II đầy đủ — đã bị thay thế bởi entry mới nhất (nay làm đủ 6 chương luôn) | Deadline gấp: thuyết trình ý tưởng vào ngày mai | Xem entry mới nhất |

## Archive

*(chưa có — sẽ chuyển entry cũ xuống đây khi Active Log vượt 20 dòng)*
