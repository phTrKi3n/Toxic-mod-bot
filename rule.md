# RULE.md — Quy tắc làm việc cho đồ án "Hệ thống phát hiện bình luận độc hại"

Mục đích: giữ cho AI (Claude) và người làm đồ án đi đúng hướng, không lan man,
không tự sáng tạo ngoài phạm vi, và làm nhanh đúng deadline.

## 1. Phạm vi đề tài (KHÔNG được tự ý mở rộng)

- Tên đề tài: **Hệ thống phát hiện bình luận độc hại** (phân loại **tiếng Việt
  và tiếng Anh**).
- 4 chức năng chính, KHÔNG thêm/bớt: **Thu thập bình luận → Gắn nhãn →
  Kiểm duyệt → Khiếu nại**.
- Trọng tâm thiết kế: **Phân loại toxic/spam bằng NLP** — đây là phần được
  chấm kỹ nhất, đầu tư nhiều nhất.
- Các ý tưởng mở rộng (Active Learning Loop hoàn chỉnh, phân cấp kiểm duyệt
  viên, mở rộng đa nền tảng...) chỉ ghi là "hướng phát triển", KHÔNG thiết kế
  chi tiết, KHÔNG hiện thực.

## 2. Nguyên tắc dùng tri thức có sẵn (không tự sáng chế)

- Ưu tiên dùng kiến trúc, mô hình, quy trình đã được cộng đồng/học thuật dùng
  phổ biến: TextCNN / PhoBERT / mBERT cho phân loại văn bản, HITL
  (Human-in-the-Loop) cho kiểm duyệt, RBAC cho phân quyền, Precision-Recall
  threshold tuning cho hiệu chỉnh ngưỡng.
- Khi thiết kế pipeline NLP song ngữ (VI/EN): dùng cách tiếp cận đã có —
  detect ngôn ngữ trước (langdetect/fastText) → tách nhánh xử lý riêng
  (underthesea cho VI, spaCy/NLTK cho EN) → mô hình chung hoặc 2 mô hình
  riêng theo ngôn ngữ. Không bịa ra kỹ thuật mới.
- Nếu không chắc một kỹ thuật có thật/phổ biến hay không, ghi rõ trong
  `log.md` để kiểm tra lại, không tự tin trình bày như chân lý.

## 3. Công cụ

- Vẽ diagram (Use Case, ERD, Sequence, Activity...): dùng **Visual Paradigm**
  (visual-paradigm.com). Claude không vẽ trực tiếp trong VP được — Claude sẽ
  cung cấp **đặc tả rõ ràng** (danh sách actor, use case, entity, quan hệ,
  luồng) để người dùng tự vẽ trong VP, hoặc Claude phác thảo bằng
  Mermaid/Visualizer để hình dung trước.
- Báo cáo: Word (.docx). Slide: PowerPoint (.pptx).

## 4. Việc NÊN làm

- Bám sát 4 chức năng + trọng tâm NLP khi viết bất kỳ phần nào.
- Giữ văn phong báo cáo học thuật, ngắn gọn, có cấu trúc mục rõ ràng.
- Mỗi lần thay đổi định hướng quan trọng → ghi vào `log.md` (theo đúng luật
  ở mục "Quy tắc ghi log" trong chính file đó).
- Hỏi lại người dùng nếu một quyết định ảnh hưởng lớn đến phạm vi (ví dụ:
  đổi mô hình, đổi nguồn dữ liệu).
- Làm nhanh: ưu tiên hoàn thành bản đủ dùng (good enough, đúng hạn) hơn là
  hoàn hảo nhưng trễ.

## 5. Việc TRÁNH làm

- Không tự thêm chức năng ngoài 4 chức năng chính.
- Không thiết kế sâu các phần đã ghi "hướng phát triển".
- Không dùng thuật ngữ/kỹ thuật lạ, khó kiểm chứng, hoặc nghe "kêu" nhưng
  không có nguồn.
- Không viết lại toàn bộ tài liệu mỗi lần chỉ sửa một phần nhỏ — chỉ sửa
  đúng phần liên quan.
- Không để `log.md` phình to — tuân thủ luật xoay vòng log.

## 6. Nguyên tắc viết văn (áp dụng cho mọi phần văn xuôi trong báo cáo)

Mục tiêu: đọc như một báo cáo/paper do người viết, không đọc như văn bản AI
sinh ra. Áp dụng 7 nguyên tắc sau mỗi khi viết mới hoặc viết lại nội dung:

1. **Bỏ giọng marketing** — không dùng hype, buzzword, câu nghe như quảng cáo
   ("giải pháp đột phá", "mạnh mẽ", "toàn diện"...).
2. **Có góc nhìn cá nhân** — viết với quan điểm rõ ràng (vì sao chọn A bỏ B),
   tránh trung lập kiểu liệt kê ưu/nhược chung chung, tránh lời khuyên sáo rỗng.
3. **Trộn nhịp câu** — xen câu ngắn, vừa, dài; không để mọi câu dài đều như
   nhau, không để văn bản đọc "quá hoàn hảo, quá đều".
4. **Cụ thể, có dẫn chứng** — thay ý mơ hồ bằng số liệu, tên công cụ, tình
   huống thật, dòng lệnh, ví dụ cụ thể thay vì mô tả trừu tượng.
5. **Viết như đang nói chuyện với người trong ngành** — từ đơn giản, tự
   nhiên, như giải thích cho một nghiên cứu sinh/đồng nghiệp, không sách vở.
6. **Xoá dấu hiệu AI** — bỏ mở bài chung chung/filler, bỏ câu chuyển ý lặp
   khuôn ("Điều quan trọng cần lưu ý là...", "Bên cạnh đó, không thể không
   nhắc đến..."), bỏ kết luận thừa nhắc lại y nguyên phần mở.
7. **Bám giọng các paper mẫu trong project** — trước khi viết, xem lại cách
   dùng từ, nhịp câu, cách nêu trade-off của các bài báo khoa học đã có trong
   project, rồi viết theo tinh thần đó thay vì giọng báo cáo sinh viên mặc định.

Quy tắc định dạng đi kèm (áp dụng luôn, không chỉ khi được nhắc):

- Không dùng dấu gạch ngang dài "—" trong câu văn; dùng dấu phẩy, dấu hai
  chấm, hoặc tách câu.
- Không dùng dấu "=" để nối ý trong câu văn xuôi; "=" chỉ dùng trong công
  thức toán hoặc code/SQL.
- Tên biến, tên trường dữ liệu, tên bảng dùng dấu gạch dưới "_" (ví dụ
  user_id, model_version), không viết cách hoặc dùng CamelCase tuỳ tiện.

## 7. Cơ cấu vai trò Dev - Sec - Ops và đồng bộ log

Từ 2026-09-25, dự án chia công việc theo 3 vai trò. Cả 3 role đều bám phạm vi
ở mục 1 và các nguyên tắc chung ở mục 2-3-6 — không role nào được tự ý đổi
phạm vi chung của đề tài.

- **DEV** (`rule_dev.md`, `log_dev.md`): pipeline NLP, ERD/entity, use case
  chức năng — phần lõi Chương I-III.
- **SEC** (`rule_sec.md`, `log_sec.md`): threat model, RBAC/phân quyền, an
  toàn dữ liệu người dùng, rủi ro khi bot tự xoá/cảnh báo tin nhắn — Chương
  III-IV.
- **OPS** (`rule_ops.md`, `log_ops.md`): triển khai, giám sát, CI/CD, xử lý
  sự cố, hiệu năng, kiểm thử — Chương IV-V.

Quy tắc log 2 tầng:

1. Mỗi role ghi **mọi** quyết định trong phạm vi của mình vào log riêng
   (`log_<role>.md`), theo đúng khuôn 5 trường như `log.md`. Ghi **ngay khi
   có quyết định**, không giữ tạm chờ gộp — tránh mất quyết định nếu hết
   token hoặc phiên chat kết thúc giữa chừng.
2. Quyết định nào đụng đến phạm vi chung (4 chức năng chính, mô hình, actor,
   kiến trúc tổng, hoặc thay đổi chính `rule.md`) thì **đồng thời** thêm 1
   dòng tóm tắt vào `log.md` chung, ghi rõ nguồn ở đầu cột Quyết định (ví dụ
   `[DEV] ...`, `[SEC] ...`, `[OPS] ...`).
3. Quyết định chỉ nằm trong phạm vi riêng của 1 role (không ảnh hưởng role
   khác hay phạm vi chung) thì chỉ cần nằm trong `log_<role>.md`. Định kỳ
   (mỗi khi 1 role log đạt 5 entry mới, hoặc khi người dùng yêu cầu "đồng bộ
   log" / "chốt log") rà lại các entry đó và đẩy 1 dòng tóm tắt tối thiểu
   sang `log.md` để `log.md` vẫn là bức tranh tổng quan toàn dự án.
4. `log.md` chung KHÔNG chứa toàn bộ chi tiết của từng role — chi tiết đầy
   đủ nằm ở `log_<role>.md`, `log.md` chỉ giữ phần ảnh hưởng chung/tóm tắt.

## 8. Trạng thái hiện tại (cập nhật lần cuối: xem log.md)

- Bản báo cáo hiện hành: `BaoCao_DoAn_6Chuong_DevSecOps.docx` (thay thế
  `BaoCao_DoAn_6Chuong.docx` cũ, file cũ vẫn giữ làm bản lưu trữ). Tổ chức lại
  toàn bộ 6 chương theo tư tưởng Dev-Sec-Ops xuyên suốt, Chương IV đổi tên
  thành "Thiết kế kiến trúc và an toàn hệ thống" (thêm Mô hình mối đe doạ -
  SEC), Chương V đổi tên thành "Kiểm thử, CI/CD và triển khai" (thêm CI/CD và
  Giám sát vận hành - OPS). 5 sơ đồ (kiến trúc, use case, activity, ERD,
  sequence) giữ nguyên, dùng lại từ bản cũ vì đã có màu DEV/OP/SEC sẵn.
- Đội hình: đủ 3 thành viên khớp 3 vai trò Dev/Sec/Ops (xem mục 1); tên/MSSV
  thành viên thứ 3 và việc gán cụ thể ai vào vai trò nào đang để trống dạng
  placeholder trong báo cáo, cần điền tay.
- Từ 2026-09-25: dự án chia 3 role Dev/Sec/Ops, mỗi role có rule và log riêng
  (xem mục 7). `log.md` chung chỉ giữ quyết định ảnh hưởng phạm vi chung.
- Cần bổ sung khi có thời gian: slide thuyết trình, số liệu thật sau khi
  hiện thực (F1-score trên tập validation trộn Anh-Việt), tên/MSSV thành
  viên thứ 3 và phân công vai trò cụ thể.

## 9. Nguyên tắc làm việc khi code (áp dụng cả 3 role)

Áp dụng cho mọi agent (AI hoặc người) khi viết hoặc sửa code trong repo này,
không riêng vai trò nào.

- Suy nghĩ trước khi code: nếu yêu cầu chưa rõ, nêu rõ giả định đang dùng
  hoặc hỏi lại người dùng, không tự chọn một cách hiểu rồi làm luôn. Có nhiều
  cách làm khả thi thì trình bày ngắn gọn đánh đổi trước khi chọn, không im
  lặng chọn một phương án.
- Ưu tiên đơn giản: chỉ viết đúng phần cần cho yêu cầu đang có, không thêm
  tính năng, không thêm lớp trừu tượng, không thêm cấu hình linh hoạt cho
  trường hợp chưa ai yêu cầu. Đoạn nào rút gọn được mà vẫn đúng thì rút gọn.
- Sửa đúng phạm vi: khi sửa file có sẵn, chỉ đổi đúng phần liên quan tới yêu
  cầu, không tiện tay sửa định dạng, comment, hay đoạn code khác. Giữ nguyên
  style code hiện có trong file dù thấy cách khác hợp lý hơn. Thấy code chết
  không liên quan thì báo lại cho người dùng, không tự xoá.
- Nêu tiêu chí hoàn thành trước khi làm việc nhiều bước: với việc lớn, agent
  liệt kê ngắn từng bước kèm cách kiểm tra bước đó đã đúng (ví dụ viết test
  trước rồi coi test pass là xong), thay vì chỉ nhận việc chung chung.

Khi không chắc điều nào ở trên có mâu thuẫn với phạm vi đã chốt ở mục 1-2 hay
không, dừng lại hỏi người dùng, không tự quyết.
