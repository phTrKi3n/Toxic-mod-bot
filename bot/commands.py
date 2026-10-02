"""
bot/commands.py — xử lý lệnh của người dùng qua bot, khớp UC03, UC04, UC05,
UC06, UC09, UC10 ở Chương III. RBAC (SEC) áp dụng ở đây: chỉ Mod/Admin mới
gọi được các lệnh quản trị, adapter hiện kiểm tra role Discord của người gửi trong server.
TODO(DEV/SEC): thống nhất ánh xạ với app_user khi tích hợp DB.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import discord
from bot import rbac


def has_role(message: discord.Message, allowed_roles: set[str]) -> bool:
    """Check whether the command author has one of the allowed roles."""
    # Administrative commands are only valid for human guild members.
    if getattr(message, "guild", None) is None:
        return False
    if getattr(message.author, "bot", False):
        return False

    user_roles = {role.name.lower() for role in getattr(message.author, "roles", [])}

    return bool(user_roles & allowed_roles)


def is_mod_or_admin(message: discord.Message) -> bool:
    return rbac.allowed(message, "queue")


def is_admin(message: discord.Message) -> bool:
    return rbac.allowed(message, "config")


async def handle_command(message: discord.Message) -> None:
    text = message.content.strip()
    command = text.split(maxsplit=1)[0] if text else ""

    if command == "/appeal":
        await _handle_appeal(message)
    elif command == "/queue":
        await _handle_queue(message)
    elif command == "/resolve":
        await _handle_resolve(message)
    elif command == "/config":
        await _handle_config(message)
    else:
        await message.channel.send("Lệnh không tồn tại.")


async def _handle_appeal(message: discord.Message) -> None:
    if not rbac.allowed(message, "appeal"):
        await message.channel.send(rbac.DENIED)
        return
    # UC03: member may appeal; enforce ownership using owned_appeal_target before write
    # TODO(DEV): tạo bản ghi Appeal(message_id, user_id, reason, status='pending')
    raise NotImplementedError


async def _handle_queue(message: discord.Message) -> None:
    if not is_mod_or_admin(message):
        await message.channel.send("Bạn không có quyền sử dụng lệnh này.")
        return

    # UC04: chỉ Mod/Admin. kiểm tra quyền ở trên trước khi đọc hàng đợi
    # TODO(DEV): trả danh sách HardCase đang status='pending'
    raise NotImplementedError


async def _handle_resolve(message: discord.Message) -> None:
    if not is_mod_or_admin(message):
        await message.channel.send("Bạn không có quyền sử dụng lệnh này.")
        return

    # UC05, UC06: chỉ Mod/Admin. kiểm tra quyền ở trên trước khi ra quyết định
    # TODO(DEV): cập nhật ModerationAction/Appeal, ghi decided_by = người gọi lệnh
    raise NotImplementedError


async def _handle_config(message: discord.Message) -> None:
    if not is_admin(message):
        await message.channel.send("Bạn không có quyền sử dụng lệnh này.")
        return

    # UC09, UC10: chỉ Admin. kiểm tra quyền ở trên trước khi đổi cấu hình
    # TODO(DEV): cập nhật threshold_low/threshold_high trong bảng server
    raise NotImplementedError
