import asyncio
import datetime
import logging
import os
import time

import aiohttp
import discord

from bot.monitoring import error_tracker
from db.models import Classification, HardCase, ModerationAction

logger = logging.getLogger("bot.actions")

INFERENCE_TIMEOUT_SECONDS = float(os.getenv("INFERENCE_TIMEOUT_SECONDS", "2.0"))
INFERENCE_URL = os.getenv(
    "INFERENCE_SERVICE_URL", "http://inference_service:8000/classify"
)


async def classify_and_moderate(
    message, server_config, db_session=None, discord_client=None, session=None
):
    msg_id = getattr(message, "id", 123456789)
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

    score = None
    model_version_id = 1
    action_taken = "bypass"

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

    if db_session is not None:
        try:
            cls_record = Classification(
                message_id=msg_id,
                model_version_id=model_version_id,
                score=score,
                created_at=datetime.datetime.utcnow(),
            )
            db_session.add(cls_record)
            db_session.flush()
        except Exception as db_err:
            logger.error(f"Failed to insert classification record: {db_err}")

    if score >= threshold_high:
        action_taken = "delete"
        try:
            if hasattr(message, "delete") and callable(message.delete):
                await message.delete()
                logger.info(f"Deleted toxic message {msg_id} (score={score:.4f})")
        except Exception as del_err:
            logger.error(f"Failed to delete message {msg_id}: {del_err}")

        try:
            if author and hasattr(author, "send") and callable(author.send):
                await author.send(
                    f"⚠️ Tin nhắn của bạn đã bị xóa tự động do vi phạm quy chuẩn cộng đồng "
                    f"(Độ độc hại: {score:.2%})."
                )
        except Exception as dm_err:
            logger.warning(f"Could not send DM to user {author}: {dm_err}")

        if db_session is not None:
            mod_action = ModerationAction(
                message_id=msg_id,
                action_type="delete",
                decided_by=None,
                decided_at=datetime.datetime.utcnow(),
            )
            db_session.add(mod_action)

    elif threshold_low <= score < threshold_high:
        action_taken = "flag"
        if db_session is not None:
            hard_case = HardCase(
                message_id=msg_id,
                original_score=score,
                status="pending",
            )
            db_session.add(hard_case)

            mod_action = ModerationAction(
                message_id=msg_id,
                action_type="flag",
                decided_by=None,
                decided_at=datetime.datetime.utcnow(),
            )
            db_session.add(mod_action)

    else:
        action_taken = "ignore"
        if db_session is not None:
            mod_action = ModerationAction(
                message_id=msg_id,
                action_type="ignore",
                decided_by=None,
                decided_at=datetime.datetime.utcnow(),
            )
            db_session.add(mod_action)

    if db_session is not None:
        try:
            db_session.commit()
        except Exception as commit_err:
            db_session.rollback()
            logger.error(f"Failed to commit moderation action: {commit_err}")

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

    db = None
    try:
        from db.session import SessionLocal

        db = SessionLocal()
    except Exception:
        pass

    try:
        await classify_and_moderate(message, DefaultServerConfig(), db_session=db)
    finally:
        if db is not None:
            db.close()


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
