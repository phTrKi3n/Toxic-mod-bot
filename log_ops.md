# LOG_OPS.md — Nhật ký quyết định riêng của vai trò OPS

Áp dụng chung quy tắc ghi log ở `log.md` (tối đa 5 dòng/entry, entry mới
nhất trên cùng, xoay vòng khi vượt 20 entry). File này chỉ chứa quyết định
thuộc phạm vi OPS (xem `rule_ops.md`); quyết định ảnh hưởng phạm vi chung
được đồng thời ghi sang `log.md`.

## Active Log

| Ngày | Quyết định | Lý do | Ảnh hưởng |
|---|---|---|---|
| 2026-09-26 | Thêm mục "CI/CD" và "Giám sát vận hành & xử lý sự cố" vào Chương V (đổi tên chương thành "Kiểm thử, CI/CD và triển khai"): pipeline GitHub Actions (test, lint, build Docker image khi merge main, theo mẫu thực tế các bot discord.py mã nguồn mở); giám sát bằng health-check định kỳ cho Inference Service và cảnh báo khi tỉ lệ lỗi timeout tăng; kế hoạch rollback model bằng cờ is_current đã có trong bảng model_version | rule_ops.md yêu cầu CI/CD và giám sát nhưng bản cũ chỉ có kế hoạch kiểm thử + triển khai cơ bản; không dùng công nghệ/dịch vụ bịa, bám theo cách các bot Discord thật triển khai (Docker + GitHub Actions + health-check) | Không đổi nền tảng triển khai tổng (vẫn Discord/Telegram, Docker); chỉ thêm quy trình CI/CD và giám sát, không đổi kiến trúc 3 lớp đã chốt ở Chương IV |

## Archive

*(chưa có)*
