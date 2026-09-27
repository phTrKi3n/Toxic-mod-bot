"""
bot/actions.py — logic gọi Inference Service và hành động theo ngưỡng (UC15),
khớp sơ đồ tuần tự ca "điểm cao" ở Chương IV mục II. Timeout 2 giây và biện
pháp giới hạn tần suất là biện pháp giảm thiểu mối đe doạ spam/DoS ở Chương IV
mục V, không được bỏ khi hiện thực thật.
"""

import discord
import httpx

INFERENCE_TIMEOUT_SECONDS = 2.0


async def classify_and_act(message: discord.Message) -> None:
    # TODO(DEV): lấy threshold_low/threshold_high từ bảng server tương ứng
    threshold_low, threshold_high = 0.30, 0.90

    try:
        async with httpx.AsyncClient(timeout=INFERENCE_TIMEOUT_SECONDS) as http_client:
            resp = await http_client.post(
                "http://localhost:8000/classify", json={"text": message.content}
            )
            score = resp.json()["score"]
    except httpx.TimeoutException:
        # Luồng ngoại lệ đã chốt ở Chương III: bỏ qua tin nhắn lần này, ghi log lỗi,
        # không chặn để tránh treo trải nghiệm chat.
        # TODO(OPS): ghi log lỗi timeout có cấu trúc, phục vụ giám sát Chương V mục IV
        return

    if score >= threshold_high:
        await _delete_and_warn(message, score)
    elif score >= threshold_low:
        await _flag_for_review(message, score)
    # else: không hành động


async def _delete_and_warn(message: discord.Message, score: float) -> None:
    # TODO(DEV): xoá tin nhắn, gửi DM cảnh báo, ghi ModerationAction(action_type='delete')
    raise NotImplementedError


async def _flag_for_review(message: discord.Message, score: float) -> None:
    # TODO(DEV): tạo HardCase(status='pending'), thông báo nhẹ cho người gửi
    raise NotImplementedError
