"""
bot/commands.py — xử lý lệnh của người dùng qua bot, khớp UC03, UC04, UC05,
UC06, UC09, UC10 ở Chương III. RBAC (SEC) áp dụng ở đây: chỉ Mod/Admin mới
gọi được các lệnh quản trị, kiểm tra role trong bảng app_user trước khi chạy.
"""

import discord


async def handle_command(message: discord.Message) -> None:
    text = message.content.strip()

    if text.startswith("/appeal"):
        await _handle_appeal(message)
    elif text.startswith("/queue"):
        await _handle_queue(message)
    elif text.startswith("/resolve"):
        await _handle_resolve(message)
    elif text.startswith("/config"):
        await _handle_config(message)
    else:
        await message.channel.send("Lệnh không tồn tại.")


async def _handle_appeal(message: discord.Message) -> None:
    # UC03: bất kỳ thành viên nào cũng gọi được, không cần RBAC
    # TODO(DEV): tạo bản ghi Appeal(message_id, user_id, reason, status='pending')
    raise NotImplementedError


async def _handle_queue(message: discord.Message) -> None:
    # UC04: chỉ Mod/Admin. TODO(SEC): kiểm tra role trước khi cho xem hàng đợi
    # TODO(DEV): trả danh sách HardCase đang status='pending'
    raise NotImplementedError


async def _handle_resolve(message: discord.Message) -> None:
    # UC05, UC06: chỉ Mod/Admin. TODO(SEC): kiểm tra role trước khi cho ra quyết định
    # TODO(DEV): cập nhật ModerationAction/Appeal, ghi decided_by = người gọi lệnh
    raise NotImplementedError


async def _handle_config(message: discord.Message) -> None:
    # UC09, UC10: chỉ Admin. TODO(SEC): kiểm tra role trước khi cho đổi ngưỡng/cấu hình
    # TODO(DEV): cập nhật threshold_low/threshold_high trong bảng server
    raise NotImplementedError
