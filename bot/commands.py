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


import os
from datetime import datetime

from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

from db.models import Appeal, HardCase, Message, ModerationAction, Server, User


async def _handle_appeal(message: discord.Message) -> None:
    # UC03: bất kỳ thành viên nào cũng gọi được, không cần RBAC
    # TODO(DEV): tạo bản ghi Appeal(message_id, user_id, reason, status='pending')
    parts = message.content.strip().split(maxsplit=2)
    if len(parts) < 3:
        await message.channel.send("Cú pháp: /appeal <message_id> <lý do>")
        return

    try:
        target_message_id = int(parts[1])
    except ValueError:
        await message.channel.send("message_id không hợp lệ.")
        return

    reason = parts[2]
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        await message.channel.send("Lỗi cấu hình CSDL.")
        return

    try:
        engine = create_engine(database_url)
        with Session(engine) as session:
            # Tìm hoặc tạo user
            stmt_user = select(User).where(User.discord_id == str(message.author.id))
            user = session.scalars(stmt_user).first()
            if not user:
                user = User(
                    discord_id=str(message.author.id),
                    username=message.author.name,
                    role="member",
                )
                session.add(user)
                session.flush()

            appeal = Appeal(
                message_id=target_message_id,
                user_id=user.user_id,
                reason=reason,
                status="pending",
            )
            session.add(appeal)
            session.commit()
            await message.channel.send(f"Đã gửi khiếu nại cho tin nhắn #{target_message_id} thành công.")
    except Exception as e:
        await message.channel.send(f"Lỗi khi gửi khiếu nại: {e}")


async def _handle_queue(message: discord.Message) -> None:
    # UC04: chỉ Mod/Admin. TODO(SEC): kiểm tra role trước khi cho xem hàng đợi
    # TODO(DEV): trả danh sách HardCase đang status='pending'
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        await message.channel.send("Lỗi cấu hình CSDL.")
        return

    try:
        engine = create_engine(database_url)
        with Session(engine) as session:
            stmt = select(HardCase).where(HardCase.status == "pending")
            hard_cases = session.scalars(stmt).all()
            if not hard_cases:
                await message.channel.send("Hàng đợi rỗng, không có trường hợp nghi vấn nào.")
                return

            lines = ["**Danh sách hàng đợi HardCase (pending):**"]
            for hc in hard_cases:
                lines.append(f"- ID: {hc.hardcase_id} | Message ID: {hc.message_id} | Score: {hc.original_score:.2f}")
            await message.channel.send("\n".join(lines))
    except Exception as e:
        await message.channel.send(f"Lỗi khi lấy hàng đợi: {e}")


async def _handle_resolve(message: discord.Message) -> None:
    # UC05, UC06: chỉ Mod/Admin. TODO(SEC): kiểm tra role trước khi cho ra quyết định
    # TODO(DEV): cập nhật ModerationAction/Appeal, ghi decided_by = người gọi lệnh
    parts = message.content.strip().split(maxsplit=2)
    if len(parts) < 3:
        await message.channel.send("Cú pháp: /resolve <message_id> <delete|restore|approve|reject>")
        return

    try:
        target_message_id = int(parts[1])
    except ValueError:
        await message.channel.send("message_id không hợp lệ.")
        return

    action = parts[2].lower()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        await message.channel.send("Lỗi cấu hình CSDL.")
        return

    try:
        engine = create_engine(database_url)
        with Session(engine) as session:
            stmt_user = select(User).where(User.discord_id == str(message.author.id))
            user = session.scalars(stmt_user).first()
            user_id = user.user_id if user else None

            if action in ["approve", "reject"]:
                new_status = "approved" if action == "approve" else "rejected"
                session.execute(
                    update(Appeal)
                    .where(Appeal.message_id == target_message_id)
                    .values(
                        status=new_status,
                        resolved_by=user_id,
                        resolved_at=datetime.utcnow(),
                    )
                )
                session.commit()
                await message.channel.send(f"Đã cập nhật Appeal cho tin nhắn #{target_message_id} thành {new_status}.")
            elif action in ["delete", "restore"]:
                mod_action = ModerationAction(
                    message_id=target_message_id,
                    action_type=action,
                    decided_by=user_id,
                    decided_at=datetime.utcnow(),
                )
                session.add(mod_action)
                session.commit()
                await message.channel.send(f"Đã ghi nhận ModerationAction '{action}' cho tin nhắn #{target_message_id}.")
            else:
                await message.channel.send("Hành động không hợp lệ. Chọn một trong: delete, restore, approve, reject.")
    except Exception as e:
        await message.channel.send(f"Lỗi khi xử lý resolve: {e}")


async def _handle_config(message: discord.Message) -> None:
    # UC09, UC10: chỉ Admin. TODO(SEC): kiểm tra role trước khi cho đổi ngưỡng/cấu hình
    # TODO(DEV): cập nhật threshold_low/threshold_high trong bảng server
    parts = message.content.strip().split(maxsplit=2)
    if len(parts) < 3:
        await message.channel.send("Cú pháp: /config <threshold_low|threshold_high> <giá trị>")
        return

    param_name = parts[1].lower()
    try:
        param_value = float(parts[2])
    except ValueError:
        await message.channel.send("Giá trị cấu hình phải là số thực.")
        return

    if param_name not in ["threshold_low", "threshold_high"]:
        await message.channel.send("Chỉ hỗ trợ cấu hình: threshold_low hoặc threshold_high.")
        return

    if not message.guild:
        await message.channel.send("Lệnh cấu hình chỉ dùng được trong server (guild).")
        return

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        await message.channel.send("Lỗi cấu hình CSDL.")
        return

    try:
        engine = create_engine(database_url)
        with Session(engine) as session:
            stmt = select(Server).where(Server.guild_id == str(message.guild.id))
            srv = session.scalars(stmt).first()
            if not srv:
                srv = Server(
                    guild_id=str(message.guild.id),
                    name=message.guild.name,
                    threshold_low=0.30,
                    threshold_high=0.90,
                )
                session.add(srv)
                session.flush()

            if param_name == "threshold_low":
                srv.threshold_low = param_value
            else:
                srv.threshold_high = param_value

            session.commit()
            await message.channel.send(f"Đã cập nhật {param_name} = {param_value:.2f} cho server.")
    except Exception as e:
        await message.channel.send(f"Lỗi khi cập nhật cấu hình: {e}")
