# Dockerfile khởi điểm, đủ để bước "build" trong .github/workflows/ci.yml chạy được.
# OPS tinh chỉnh thêm khi hiện thực thật (ví dụ tách 2 image riêng cho bot và
# inference_service thay vì gộp chung, theo đúng hướng đã nêu ở Chương IV mục IV).
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "bot.main"]
