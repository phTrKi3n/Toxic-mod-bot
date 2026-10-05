"""Guild-scoped RBAC. Database role is an additional restriction, never a grant.

Discord roles are authoritative for guild membership; a configured database must
also agree. An absent/failed database denies administrative access (fail closed).
"""

import os
from functools import lru_cache

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from db.models import User, Server, Message, HardCase

DENIED = "Bạn không có quyền sử dụng lệnh này."
ROLE_PERMISSIONS = {
    "member": frozenset({"appeal"}),
    "labeler": frozenset({"appeal", "label"}),
    "mod": frozenset({"appeal", "label", "queue", "resolve"}),
    "admin": frozenset({"appeal", "label", "queue", "resolve", "config"}),
}


@lru_cache(maxsize=4)
def _engine(url):
    return create_engine(url, pool_pre_ping=True)


def _discord_role(message):
    if getattr(message, "guild", None) is None or getattr(message.author, "bot", False):
        return None
    # Never use display names or global administrator status as a grant.
    roles = {
        getattr(r, "name", "").casefold() for r in getattr(message.author, "roles", ())
    }
    return next(
        (r for r in ("admin", "mod", "labeler", "member") if r in roles), "member"
    )


def allowed(message, permission, *, session=None):
    """Deny unless the role AND (when configured) DB role permit the action."""
    role = _discord_role(message)
    if role is None or permission not in ROLE_PERMISSIONS[role]:
        return False
    if permission == "appeal":
        return True  # Public guild-member action; ownership checked on write.
    url = os.getenv("DATABASE_URL")
    if session is None and not url:
        # Explicit compatibility mode for deployments not yet using the DB.
        return os.getenv("RBAC_DISCORD_ONLY", "false").lower() == "true"
    try:
        if session is not None:
            return _db_allowed(message, permission, session)
        with Session(_engine(url)) as db:
            return _db_allowed(message, permission, db)
    except Exception:
        return False


def _db_allowed(message, permission, db):
    user = db.scalar(select(User).where(User.discord_id == str(message.author.id)))
    server = db.scalar(select(Server).where(Server.guild_id == str(message.guild.id)))
    return bool(
        user
        and server
        and server.is_active
        and permission in ROLE_PERMISSIONS.get(user.role, ())
        and permission in ROLE_PERMISSIONS[_discord_role(message)]
    )


def scoped_message(db, guild_id, message_id):
    """Return a message only if it belongs to the current guild."""
    return db.scalar(
        select(Message)
        .join(Server)
        .where(
            Message.message_id == message_id,
            Server.guild_id == str(guild_id),
            Server.is_active.is_(True),
        )
    )


def owned_appeal_target(db, guild_id, discord_id, message_id):
    """A user may appeal only their own message in the current guild."""
    msg = scoped_message(db, guild_id, message_id)
    user = db.scalar(select(User).where(User.discord_id == str(discord_id)))
    return (
        msg
        if msg is not None and user is not None and msg.user_id == user.user_id
        else None
    )


def scoped_hardcase(db, guild_id, case_id):
    return db.scalar(
        select(HardCase)
        .join(Message, HardCase.message_id == Message.message_id)
        .join(Server, Message.server_id == Server.server_id)
        .where(
            HardCase.hardcase_id == case_id,
            Server.guild_id == str(guild_id),
            Server.is_active.is_(True),
        )
    )
