# toxic-mod-bot

Bot kiểm duyệt bình luận độc hại song ngữ Việt-Anh cho Discord/Telegram. Đồ án môn Phân tích và thiết kế hệ thống thông tin, tổ chức theo mô hình Dev-Sec-Ops.

Đọc `rule.md` và `README.md` (quy trình Git) trước khi làm bất kỳ việc gì. Nếu đang ở nhánh `dev`/`sec`/`ops`, đọc `README.md` của đúng nhánh đó trước, file này chỉ mô tả cấu trúc thư mục.

## Cấu trúc thư mục

```
toxic-mod-bot/
├── README.md, README_dev.md, README_sec.md, README_ops.md   # quy trình, đổi tên README_<role>.md -> README.md khi đẩy lên nhánh role tương ứng
├── rule.md, rule_dev.md, rule_sec.md, rule_ops.md           # phạm vi và nguyên tắc
├── log.md, log_dev.md, log_sec.md, log_ops.md               # nhật ký quyết định
├── docs/
│   ├── BaoCao_DoAn_6Chuong_DevSecOps.docx   # báo cáo đầy đủ
│   └── diagrams/                            # xuất ảnh từ Visual Paradigm vào đây (use case, ERD, activity, kiến trúc, sequence)
├── bot/                    # DEV viết luồng, OPS phụ trách vận hành/CI cho phần này
│   ├── main.py             # khởi tạo discord.py client, đăng ký on_message (UC13)
│   ├── commands.py         # /appeal (UC03), /queue (UC04), /resolve (UC05, UC06), /config (UC09, UC10)
│   └── actions.py          # xoá tin, gửi DM, ghi log hành động (UC15)
├── inference_service/      # DEV
│   ├── app.py              # FastAPI: POST /classify (UC14), GET /health
│   └── model_loader.py     # load XLM-R fine-tuned + tokenizer, cache RAM, đổi model theo is_current
├── db/                     # DEV thiết kế schema, SEC review ràng buộc an toàn dữ liệu
│   ├── models.py           # SQLAlchemy ORM khớp ERD Chương III
│   └── migrations/         # Alembic migration scripts
├── training/               # DEV
│   ├── prepare_dataset.py  # gộp Jigsaw + ViHSD/UIT-ViCTSD, ánh xạ nhãn
│   └── finetune.py         # fine-tune XLM-R bằng Hugging Face Trainer
├── tests/                  # OPS
│   ├── test_bot.py
│   └── test_inference.py
├── .github/workflows/ci.yml    # OPS, pipeline test -> lint -> build Docker
├── .env.example                # SEC, mẫu biến môi trường, KHÔNG chứa giá trị thật
├── .gitignore
└── requirements.txt
```

## Trạng thái hiện tại

Đồ án đang ở giai đoạn phân tích và thiết kế (xem `rule.md` mục 8). Code trong `bot/`, `inference_service/`, `db/`, `training/` ở đây là khung khởi điểm (skeleton) khớp đúng thiết kế đã chốt trong báo cáo, chưa phải bản hiện thực đầy đủ. Ai nhận việc hiện thực phần nào, ghi quyết định vào đúng `log_<role>.md` của mình trước khi bắt đầu sửa.

## Khởi tạo 5 nhánh Git (làm 1 lần lúc đầu dự án)

Mô hình nhánh đầy đủ nằm ở `README.md` mục 3 (role -> test -> main). Các bước thực thi chi tiết, kèm kết quả mong đợi sau từng bước để agent tự kiểm tra, nằm ở `AGENT_SETUP_BRANCHES.md`. Nếu đang giao việc này cho một AI agent, trỏ agent đọc thẳng file đó, không cần tóm tắt lại.

