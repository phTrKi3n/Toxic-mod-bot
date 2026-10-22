import asyncio
import datetime
import logging
import os
import time

import aiohttp
import discord
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from bot import rbac
from bot.monitoring import error_tracker
from db.models import (
    Classification,
    HardCase,
    Message,
    ModelVersion,
    ModerationAction,
    Server,
    User,
)

logger = logging.getLogger("bot.actions")

INFERENCE_TIMEOUT_SECONDS = float(os.getenv("INFERENCE_TIMEOUT_SECONDS", "2.0"))
_raw_url = os.getenv(
    "INFERENCE_SERVICE_URL", "http://inference_service:8000/classify"
).rstrip("/")
INFERENCE_URL = _raw_url if _raw_url.endswith("/classify") else f"{_raw_url}/classify"


def _detect_language(text: str) -> str:
    vi_chars = set(
        "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
    )
    if any(ch in vi_chars for ch in text.lower()):
        return "vi"
    return "en"


def sync_discord_context(message, db: Session) -> tuple[Server | None, User | None]:
    default_low = float(os.getenv("THRESHOLD_LOW", "0.30"))
    default_high = float(os.getenv("THRESHOLD_HIGH", "0.90"))

    srv = None
    guild = getattr(message, "guild", None)
    if guild is not None and getattr(guild, "id", None) is not None:
        guild_id = str(guild.id)
        srv = db.scalar(select(Server).where(Server.guild_id == guild_id))
        if srv is None:
            srv = Server(
                guild_id=guild_id,
                name=getattr(guild, "name", None) or f"Guild {guild_id}",
                threshold_low=default_low,
                threshold_high=default_high,
                is_active=True,
            )
            db.add(srv)
            db.flush()

    usr = None
    author = getattr(message, "author", None)
    if author is not None and getattr(author, "id", None) is not None:
        discord_id = str(author.id)
        inferred_role = rbac._discord_role(message) or "member"
        usr = db.scalar(select(User).where(User.discord_id == discord_id))
        if usr is None:
            usr = User(
                discord_id=discord_id,
                username=getattr(author, "name", None) or f"user_{discord_id}",
                role=inferred_role,
            )
            db.add(usr)
            db.flush()
        else:
            if getattr(author, "name", None):
                usr.username = author.name
            if guild is not None:
                usr.role = inferred_role
            db.flush()

    return srv, usr


def _ensure_message_and_model(
    message, db: Session, model_version_id: int
) -> tuple[int, int]:
    msg_id = int(getattr(message, "id", 123456789))
    msg_content = getattr(message, "content", "") or ""
    srv, usr = sync_discord_context(message, db)

    if srv is None:
        srv = db.scalar(select(Server).where(Server.guild_id == "default_guild"))
        if srv is None:
            srv = Server(
                guild_id="default_guild",
                name="Default Guild",
                threshold_low=0.30,
                threshold_high=0.90,
                is_active=True,
            )
            db.add(srv)
            db.flush()

    if usr is None:
        usr = db.scalar(select(User).where(User.discord_id == "default_user"))
        if usr is None:
            usr = User(
                discord_id="default_user",
                username="DefaultUser",
                role="member",
            )
            db.add(usr)
            db.flush()

    msg_row = db.get(Message, msg_id)
    if msg_row is None:
        msg_row = Message(
            message_id=msg_id,
            server_id=srv.server_id,
            user_id=usr.user_id,
            content=msg_content,
            language=_detect_language(msg_content),
            created_at=datetime.datetime.utcnow(),
        )
        db.add(msg_row)
        db.flush()

    mv = db.get(ModelVersion, model_version_id)
    if mv is None:
        mv = db.scalar(select(ModelVersion).where(ModelVersion.is_current.is_(True)))
    if mv is None:
        mv = ModelVersion(
            model_version_id=model_version_id,
            version_tag=f"v1.0.0-auto-{model_version_id}",
            trained_at=datetime.datetime.utcnow(),
            is_current=True,
        )
        db.add(mv)
        db.flush()

    return msg_row.message_id, mv.model_version_id


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
            msg_id, model_version_id = _ensure_message_and_model(
                message, db_session, model_version_id
            )
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
        await _delete_and_warn(message, score)

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
        await _flag_for_review(message, score)

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


def _open_db_session() -> Session | None:
    url = os.getenv("DATABASE_URL")
    try:
        if url:
            engine = create_engine(url, pool_pre_ping=True)
            return Session(engine)
        from db.session import SessionLocal

        return SessionLocal()
    except Exception:
        return None


async def classify_and_act(message: discord.Message) -> None:
    class DefaultServerConfig:
        threshold_low = float(os.getenv("THRESHOLD_LOW", "0.30"))
        threshold_high = float(os.getenv("THRESHOLD_HIGH", "0.90"))

    db = _open_db_session()
    server_cfg = DefaultServerConfig()
    try:
        if db is not None:
            srv, _ = sync_discord_context(message, db)
            db.commit()
            if srv is not None:
                server_cfg = srv
        await classify_and_moderate(message, server_cfg, db_session=db)
    finally:
        if db is not None:
            db.close()


async def _delete_and_warn(message: discord.Message, score: float) -> None:
    msg_id = getattr(message, "id", None)
    author = getattr(message, "author", None)
    try:
        if hasattr(message, "delete") and callable(message.delete):
            await message.delete()
            logger.info(f"Deleted toxic message {msg_id} (score={score:.4f})")
    except Exception as del_err:
        logger.error(f"Failed to delete message {msg_id}: {del_err}")

    try:
        if author and hasattr(author, "send") and callable(author.send):
            await author.send(
                f"⚠️ Tin nhắn của bạn (#{msg_id}) đã bị xóa tự động do vi phạm quy chuẩn cộng đồng "
                f"(Độ độc hại: {score:.2%}). Bạn có thể khiếu nại bằng lệnh `/appeal {msg_id} <lý do>`."
            )
    except Exception as dm_err:
        logger.warning(f"Could not send DM to user {author}: {dm_err}")


async def _flag_for_review(message: discord.Message, score: float) -> None:
    author = getattr(message, "author", None)
    try:
        if author and hasattr(author, "send") and callable(author.send):
            await author.send(
                f"Tin nhắn của bạn đang được chuyển đến đội ngũ kiểm duyệt để xem xét thêm (điểm: {score:.2f})."
            )
    except Exception:
        pass
