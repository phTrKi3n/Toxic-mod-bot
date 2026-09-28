import asyncio
import datetime
import logging
import os
import time

import aiohttp

from bot.monitoring import error_tracker
from db.models import Classification, HardCase, ModerationAction

logger = logging.getLogger("bot.actions")

INFERENCE_URL = os.getenv(
    "INFERENCE_SERVICE_URL", "http://inference_service:8000/classify"
)


async def classify_and_moderate(
    message, server_config, db_session, discord_client=None, session=None
):
    msg_id = getattr(message, "id", 123456789)
    msg_content = getattr(message, "content", "")
    author = getattr(message, "author", None)

    threshold_low = getattr(server_config, "threshold_low", 0.30)
    threshold_high = getattr(server_config, "threshold_high", 0.90)

    start_time = time.time()
    created_session = False

    if session is None:
        timeout = aiohttp.ClientTimeout(total=2.0)
        session = aiohttp.ClientSession(timeout=timeout)
        created_session = True

    score = None
    model_version_id = 1
    action_taken = "bypass"

    try:
        payload = {"text": msg_content}
        async with session.post(
            INFERENCE_URL, json=payload, timeout=aiohttp.ClientTimeout(total=2.0)
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

        mod_action = ModerationAction(
            message_id=msg_id,
            action_type="delete",
            decided_by=None,
            decided_at=datetime.datetime.utcnow(),
        )
        db_session.add(mod_action)

    elif threshold_low <= score < threshold_high:
        action_taken = "flag"
        hard_case = HardCase(
            message_id=msg_id,
            text=msg_content,
            score=score,
            status="pending",
            created_at=datetime.datetime.utcnow(),
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
        mod_action = ModerationAction(
            message_id=msg_id,
            action_type="ignore",
            decided_by=None,
            decided_at=datetime.datetime.utcnow(),
        )
        db_session.add(mod_action)

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
