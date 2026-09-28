"""
bot/actions.py — logic gọi Inference Service và hành động theo ngưỡng (UC15),
khớp sơ đồ tuần tự ca "điểm cao" ở Chương IV mục II. Timeout 2 giây và biện
pháp giới hạn tần suất là biện pháp giảm thiểu mối đe doạ spam/DoS ở Chương IV
mục V, không được bỏ khi hiện thực thật.
"""

import asyncio
import datetime
import logging
import os
import time
from typing import Any, Optional

import aiohttp
import discord

from bot.monitoring import error_tracker
from db.models import HardCase, ModerationAction

logger = logging.getLogger("bot.actions")

INFERENCE_TIMEOUT_SECONDS = float(os.getenv("INFERENCE_TIMEOUT_SECONDS", "2.0"))
INFERENCE_URL = os.getenv("INFERENCE_SERVICE_URL", "http://localhost:8000/classify")


async def classify_and_moderate(
    message: Any,
    server_config: Any,
    db_session: Any = None,
    discord_client: Any = None,
    session: Optional[aiohttp.ClientSession] = None,
) -> dict:
    """
    Hàm xử lý phân loại và kiểm duyệt với SLA timeout 2.0s và ghi nhận lỗi timeout giám sát.
    """
    msg_id = getattr(message, "id", None)
    msg_content = getattr(message, "content", "")
    author = getattr(message, "author", None)

    threshold_low = getattr(server_config, "threshold_low", 0.30)
    threshold_high = getattr(server_config, "threshold_high", 0.90)

    start_time = time.time()
    created_session = False

    if session is None:
        timeout = aiohttp.ClientTimeout(total=INFERENCE_TIMEOUT_SECONDS)
        session = aiohttp.ClientSession(timeout=timeout)
        created_session = True

    try:
        payload = {"text": msg_content}
        async with session.post(
            INFERENCE_URL,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=INFERENCE_TIMEOUT_SECONDS),
        ) as resp:
            elapsed = time.time() - start_time
            if resp.status != 200:
                err_msg = f"[HTTP_{resp.status}] message_id={msg_id}, duration={elapsed:.2f}s, action=bypass"
                logger.error(f"[TIMEOUT_ERROR] {err_msg}")
                error_tracker.record_error(err_msg)
                return {"action": "bypass", "reason": f"HTTP status {resp.status}"}

            data = await resp.json()
            score = float(data.get("score", 0.0))
            model_version_id = int(data.get("model_version_id", 1))

    except (asyncio.TimeoutError, aiohttp.ServerTimeoutError):
        elapsed = time.time() - start_time
        err_msg = f"[TIMEOUT_ERROR] message_id={msg_id}, duration > 2s ({elapsed:.2f}s), action=bypass"
        logger.error(err_msg)
        error_tracker.record_error(err_msg)
        return {"action": "bypass", "reason": "timeout"}

    except Exception as e:
        elapsed = time.time() - start_time
        err_msg = (
            f"[INFERENCE_EXCEPTION] message_id={msg_id}, error={str(e)}, action=bypass"
        )
        logger.error(f"[TIMEOUT_ERROR] {err_msg}")
        error_tracker.record_error(err_msg)
        return {"action": "bypass", "reason": str(e)}

    finally:
        if created_session and not session.closed:
            await session.close()

    if score >= threshold_high:
        action_taken = "delete"
        if hasattr(message, "delete") and callable(message.delete):
            try:
                await message.delete()
            except Exception:
                pass
        if author and hasattr(author, "send") and callable(author.send):
            try:
                await author.send(
                    f"⚠️ Tin nhắn của bạn đã bị xóa tự động do vi phạm quy chuẩn (Độ độc hại: {score:.2%})."
                )
            except Exception:
                pass
    elif threshold_low <= score < threshold_high:
        action_taken = "flag"
    else:
        action_taken = "ignore"

    return {
        "action": action_taken,
        "score": score,
        "model_version_id": model_version_id,
        "message_id": msg_id,
    }


async def classify_and_act(message: discord.Message) -> None:
    class DefaultServerConfig:
        threshold_low = 0.30
        threshold_high = 0.90

    await classify_and_moderate(message, DefaultServerConfig())


async def _delete_and_warn(message: discord.Message, score: float) -> None:
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


async def _flag_for_review(message: discord.Message, score: float) -> None:
    try:
        await message.author.send(
            f"Tin nhắn của bạn đang được chuyển đến đội ngũ kiểm duyệt để xem xét thêm (điểm: {score:.2f})."
        )
    except Exception:
        pass
