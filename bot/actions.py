"""
bot/actions.py — logic gọi Inference Service và hành động theo ngưỡng (UC15),
khớp sơ đồ tuần tự ca "điểm cao" ở Chương IV mục II. Timeout 2 giây và biện
pháp giới hạn tần suất là biện pháp giảm thiểu mối đe doạ spam/DoS ở Chương IV
mục V, không được bỏ khi hiện thực thật.
"""

import os
from datetime import datetime

import discord
import httpx
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from db.models import HardCase, ModerationAction, Server

INFERENCE_TIMEOUT_SECONDS = float(os.getenv("INFERENCE_TIMEOUT_SECONDS", "2.0"))
INFERENCE_SERVICE_URL = os.getenv("INFERENCE_SERVICE_URL", "http://localhost:8000")


def _get_server_thresholds(guild_id: str | None) -> tuple[float, float]:
    default_low = float(os.getenv("THRESHOLD_LOW", "0.30"))
    default_high = float(os.getenv("THRESHOLD_HIGH", "0.90"))
    if not guild_id:
        return default_low, default_high

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return default_low, default_high

    try:
        engine = create_engine(database_url)
        with Session(engine) as session:
            stmt = select(Server).where(Server.guild_id == str(guild_id))
            srv = session.scalars(stmt).first()
            if srv:
                return float(srv.threshold_low), float(srv.threshold_high)
    except Exception:
        pass
    return default_low, default_high


async def classify_and_act(message: discord.Message) -> None:
    # TODO(DEV): lấy threshold_low/threshold_high từ bảng server tương ứng
    guild_id = str(message.guild.id) if message.guild else None
    threshold_low, threshold_high = _get_server_thresholds(guild_id)

    try:
        async with httpx.AsyncClient(timeout=INFERENCE_TIMEOUT_SECONDS) as http_client:
            resp = await http_client.post(
                f"{INFERENCE_SERVICE_URL}/classify", json={"text": message.content}
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
    try:
        await message.delete()
    except Exception:
        pass

    try:
        await message.author.send(
            f"Tin nhắn của bạn đã bị xoá do vi phạm tiêu chuẩn cộng đồng (độ độc hại: {score:.2f})."
        )
    except Exception:
        pass

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        try:
            engine = create_engine(database_url)
            with Session(engine) as session:
                action = ModerationAction(
                    message_id=message.id,
                    action_type="delete",
                    decided_by=None,
                    decided_at=datetime.utcnow(),
                )
                session.add(action)
                session.commit()
        except Exception:
            pass


async def _flag_for_review(message: discord.Message, score: float) -> None:
    # TODO(DEV): tạo HardCase(status='pending'), thông báo nhẹ cho người gửi
    try:
        await message.author.send(
            f"Tin nhắn của bạn đang được chuyển đến đội ngũ kiểm duyệt để xem xét thêm (điểm: {score:.2f})."
        )
    except Exception:
        pass

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        try:
            engine = create_engine(database_url)
            with Session(engine) as session:
                hardcase = HardCase(
                    message_id=message.id,
                    original_score=score,
                    status="pending",
                )
                session.add(hardcase)
                session.commit()
        except Exception:
            pass
