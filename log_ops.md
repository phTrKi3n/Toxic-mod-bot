# LOG_OPS.md — Nhật ký quyết định riêng của vai trò OPS

Áp dụng chung quy tắc ghi log ở `log.md` (tối đa 5 dòng/entry, entry mới
nhất trên cùng, xoay vòng khi vượt 20 entry). File này chỉ chứa quyết định
thuộc phạm vi OPS (xem `rule_ops.md`); quyết định ảnh hưởng phạm vi chung
được đồng thời ghi sang `log.md`.

## Active Log

| Ngày | Quyết định | Lý do | Ảnh hưởng |
|---|---|---|---|
| 2026-10-22 | Ghi nhận phương pháp và kết quả thực thi 58 test case trên nhánh tích hợp `test`: kết hợp Black-box phân hoạch tương đương & phân tích giá trị biên 3 vùng điểm (`<0.30`, `0.30-0.90`, `>=0.90`), White-box kiểm tra trạng thái ORM SQLite + Mock Discord/HTTP (`TC01`-`TC08`), kiểm thử bảo mật RBAC/Rate-limit (43 test) và đánh giá định lượng trên model Hugging Face XLM-R song ngữ thật (`MOCK_MODEL=false`) | Minh bạch hoá phương pháp kiểm thử thực nghiệm theo Chương V mục I.1-I.2 và đồng bộ sang `log.md` chung | 58/58 test PASSED ở cả chế độ model thật (~32ms/câu, F1=1.00) và chế độ CI/CD (`MOCK_MODEL=true`) |
| 2026-10-22 | Bổ sung `scikit-learn` vào `requirements-dev.txt`, cài PyTorch bản CPU trong CI/Dockerfile để tránh tràn ổ cứng runner và cho phép test đánh giá mô hình tôn trọng biến `MOCK_MODEL=true` trên GitHub Actions | Khắc phục lỗi `ModuleNotFoundError: No module named 'sklearn'` và tối ưu thời gian build Docker trên GitHub Actions CI/CD | Toàn bộ 2 job `Quality, Security Audit & Automated Tests` và `Build Docker Containers` trên GitHub Actions chạy xanh |
| 2026-10-22 | Bổ sung kiểm thử TC08 (hot-reload phiên bản mới sau chu kỳ fine-tune) và kiểm thử đo lường định lượng Precision/Recall/F1-score trên tập validation song ngữ Việt-Anh trong `tests/test_ops.py`; cập nhật CI/CD chạy toàn bộ `tests/` | Hoàn thiện đầy đủ mục I.1 (đánh giá định lượng mô hình) và mục I.2 (TC01-TC08) ở Chương V của báo cáo | Đảm bảo cả 8 ca kiểm thử chức năng (TC01-TC08) và đánh giá F1-score song ngữ đều được kiểm chứng tự động |
| 2026-09-29 | Bo sung ha tang Docker Compose (db, inference_service, bot), script benchmark SLA latency (<2s), monitoring webhook Discord, endpoint hot-rollback model (/ops/reload) va bo test test_ops.py; tich hop pip-audit vao CI/CD pipeline | Hoan thien toan bo cac hang muc ky thuat cua vai tro OPS theo Chuong V muc III-IV cua bao cao ma van dam bao tinh tuong thich va toan ven du lieu cho DEV va SEC | Dap ung day du tieu chi DevSecOps, khong pha vo ERD va ma nguon chung |
| 2026-09-26 | Thêm mục "CI/CD" và "Giám sát vận hành & xử lý sự cố" vào Chương V (đổi tên chương thành "Kiểm thử, CI/CD và triển khai"): pipeline GitHub Actions (test, lint, build Docker image khi merge main, theo mẫu thực tế các bot discord.py mã nguồn mở); giám sát bằng health-check định kỳ cho Inference Service và cảnh báo khi tỉ lệ lỗi timeout tăng; kế hoạch rollback model bằng cờ is_current đã có trong bảng model_version | rule_ops.md yêu cầu CI/CD và giám sát nhưng bản cũ chỉ có kế hoạch kiểm thử + triển khai cơ bản; không dùng công nghệ/dịch vụ bịa, bám theo cách các bot Discord thật triển khai (Docker + GitHub Actions + health-check) | Không đổi nền tảng triển khai tổng (vẫn Discord/Telegram, Docker); chỉ thêm quy trình CI/CD và giám sát, không đổi kiến trúc 3 lớp đã chốt ở Chương IV |

## Archive

*(chưa có)*
