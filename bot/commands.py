"""
bot/commands.py — xử lý lệnh của người dùng qua bot, khớp UC03, UC04, UC05,
UC06, UC09, UC10 ở Chương III. RBAC (SEC) áp dụng ở đây: chỉ Mod/Admin mới
gọi được các lệnh quản trị, đồng thời kiểm tra ownership và guild scope.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    import discord
from bot import rbac
from bot.actions import sync_discord_context
from db.models import Appeal, HardCase, Message, ModerationAction, Server, User


def has_role(message: discord.Message, allowed_roles: set[str]) -> bool:
    """Check whether the command author has one of the allowed roles."""
    if getattr(message, "guild", None) is None:
        return False
    if getattr(message.author, "bot", False):
        return False

    user_roles = {role.name.lower() for role in getattr(message.author, "roles", [])}

    return bool(user_roles & allowed_roles)


def _sync_if_db_configured(message: discord.Message) -> None:
    url = os.getenv("DATABASE_URL")
    if not url:
        return
    try:
        with Session(rbac._engine(url)) as db:
            sync_discord_context(message, db)
            db.commit()
    except Exception:
        pass


def is_mod_or_admin(message: discord.Message) -> bool:
    return rbac.allowed(message, "queue")


def is_admin(message: discord.Message) -> bool:
    return rbac.allowed(message, "config")


def _can_label(message: discord.Message) -> bool:
    return rbac.allowed(message, "label")


async def handle_command(message: discord.Message) -> None:
    text = message.content.strip()
    command = text.split(maxsplit=1)[0] if text else ""

    if command in ("/appeal", "/queue", "/resolve", "/config", "/label"):
        _sync_if_db_configured(message)

    if command == "/appeal":
        await _handle_appeal(message)
    elif command == "/queue":
        await _handle_queue(message)
    elif command == "/resolve":
        await _handle_resolve(message)
    elif command == "/config":
        await _handle_config(message)
    elif command == "/label":
        await _handle_label(message)
    else:
        await message.channel.send("Lệnh không tồn tại.")


async def _handle_appeal(message: discord.Message) -> None:
    if not rbac.allowed(message, "appeal"):
        await message.channel.send(rbac.DENIED)
        return

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
            _, user = sync_discord_context(message, session)
            target_msg = rbac.owned_appeal_target(
                session, message.guild.id, message.author.id, target_message_id
            )
            if target_msg is None or user is None:
                await message.channel.send(
                    "Không tìm thấy tin nhắn của bạn trong server này để khiếu nại."
                )
                return

            existing = session.scalar(
                select(Appeal).where(Appeal.message_id == target_message_id)
            )
            if existing is not None:
                await message.channel.send(
                    "Tin nhắn này đã được gửi khiếu nại trước đó."
                )
                return

            appeal = Appeal(
                message_id=target_message_id,
                user_id=user.user_id,
                reason=reason,
                status="pending",
            )
            session.add(appeal)
            session.commit()
            await message.channel.send(
                f"Đã gửi khiếu nại cho tin nhắn #{target_message_id} thành công."
            )
    except Exception as e:
        await message.channel.send(f"Lỗi khi gửi khiếu nại: {e}")


async def _send_private_or_channel(message: discord.Message, content: str) -> None:
    author_send = getattr(getattr(message, "author", None), "send", None)
    if callable(author_send):
        try:
            await author_send(content)
            await message.channel.send(
                "Đã gửi danh sách hàng đợi qua tin nhắn riêng (DM)."
            )
            return
        except Exception:
            pass
    await message.channel.send(content)


async def _handle_queue(message: discord.Message) -> None:
    if not is_mod_or_admin(message):
        await message.channel.send("Bạn không có quyền sử dụng lệnh này.")
        return

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        await message.channel.send("Lỗi cấu hình CSDL.")
        return

    try:
        engine = create_engine(database_url)
        with Session(engine) as session:
            stmt = (
                select(HardCase)
                .join(Message, HardCase.message_id == Message.message_id)
                .join(Server, Message.server_id == Server.server_id)
                .where(
                    HardCase.status == "pending",
                    Server.guild_id == str(message.guild.id),
                    Server.is_active.is_(True),
                )
            )
            hard_cases = session.scalars(stmt).all()
            if not hard_cases:
                await message.channel.send(
                    "Hàng đợi rỗng, không có trường hợp nghi vấn nào."
                )
                return

            lines = ["**Danh sách hàng đợi HardCase (pending):**"]
            for hc in hard_cases:
                lines.append(
                    f"- ID: {hc.hardcase_id} | Message ID: {hc.message_id} | Score: {hc.original_score:.2f}"
                )
            await _send_private_or_channel(message, "\n".join(lines))
    except Exception as e:
        await message.channel.send(f"Lỗi khi lấy hàng đợi: {e}")


async def _handle_resolve(message: discord.Message) -> None:
    if not is_mod_or_admin(message):
        await message.channel.send("Bạn không có quyền sử dụng lệnh này.")
        return

    parts = message.content.strip().split(maxsplit=2)
    if len(parts) < 3:
        await message.channel.send(
            "Cú pháp: /resolve <message_id> <delete|keep|restore|approve|reject>"
        )
        return

    try:
        target_message_id = int(parts[1])
    except ValueError:
        await message.channel.send("message_id không hợp lệ.")
        return

    action = parts[2].lower()
    if action not in ("delete", "keep", "restore", "approve", "reject"):
        await message.channel.send(
            "Hành động không hợp lệ. Chọn một trong: delete, keep, restore, approve, reject."
        )
        return

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        await message.channel.send("Lỗi cấu hình CSDL.")
        return

    try:
        engine = create_engine(database_url)
        with Session(engine) as session:
            _, user = sync_discord_context(message, session)
            user_id = user.user_id if user else None

            target_msg = rbac.scoped_message(
                session, message.guild.id, target_message_id
            )
            if target_msg is None:
                await message.channel.send("Không tìm thấy tin nhắn thuộc server này.")
                return

            if action in ("approve", "reject"):
                appeal = session.scalar(
                    select(Appeal).where(Appeal.message_id == target_message_id)
                )
                if appeal is None:
                    await message.channel.send(
                        "Không tìm thấy khiếu nại cho tin nhắn này."
                    )
                    return

                new_status = "approved" if action == "approve" else "rejected"
                appeal.status = new_status
                appeal.resolved_by = user_id
                appeal.resolved_at = datetime.utcnow()

                if action == "approve":
                    session.add(
                        ModerationAction(
                            message_id=target_message_id,
                            action_type="restore",
                            decided_by=user_id,
                            decided_at=datetime.utcnow(),
                        )
                    )
                session.commit()
                await message.channel.send(
                    f"Đã cập nhật Appeal cho tin nhắn #{target_message_id} thành {new_status}."
                )
            else:
                mod_action = ModerationAction(
                    message_id=target_message_id,
                    action_type=action,
                    decided_by=user_id,
                    decided_at=datetime.utcnow(),
                )
                session.add(mod_action)

                hc = session.scalar(
                    select(HardCase).where(
                        HardCase.message_id == target_message_id,
                        HardCase.status == "pending",
                    )
                )
                if hc is not None:
                    hc.corrected_label = (
                        "toxic" if action in ("delete", "keep") else "not_toxic"
                    )
                    hc.labeled_by = user_id
                    hc.status = "labeled"

                if action == "delete":
                    fetch_msg = getattr(message.channel, "fetch_message", None)
                    if callable(fetch_msg):
                        try:
                            discord_msg = await fetch_msg(target_message_id)
                            await discord_msg.delete()
                        except Exception:
                            pass

                session.commit()
                await message.channel.send(
                    f"Đã ghi nhận ModerationAction '{action}' cho tin nhắn #{target_message_id}."
                )
    except Exception as e:
        await message.channel.send(f"Lỗi khi xử lý resolve: {e}")


async def _handle_label(message: discord.Message) -> None:
    if not _can_label(message):
        await message.channel.send(rbac.DENIED)
        return

    parts = message.content.strip().split(maxsplit=2)
    if len(parts) < 3:
        await message.channel.send("Cú pháp: /label <hardcase_id> <toxic|not_toxic>")
        return

    try:
        hardcase_id = int(parts[1])
    except ValueError:
        await message.channel.send("hardcase_id không hợp lệ.")
        return

    label_val = parts[2].lower()
    if label_val not in ("toxic", "not_toxic"):
        await message.channel.send("Nhãn không hợp lệ. Chọn: toxic hoặc not_toxic.")
        return

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        await message.channel.send("Lỗi cấu hình CSDL.")
        return

    try:
        engine = create_engine(database_url)
        with Session(engine) as session:
            _, user = sync_discord_context(message, session)
            hc = rbac.scoped_hardcase(session, message.guild.id, hardcase_id)
            if hc is None:
                await message.channel.send("Không tìm thấy HardCase thuộc server này.")
                return

            hc.corrected_label = label_val
            hc.labeled_by = user.user_id if user else None
            hc.status = "labeled"
            session.commit()
            await message.channel.send(
                f"Đã gắn nhãn '{label_val}' cho HardCase #{hardcase_id}."
            )
    except Exception as e:
        await message.channel.send(f"Lỗi khi gắn nhãn: {e}")


async def _handle_config(message: discord.Message) -> None:
    if not is_admin(message):
        await message.channel.send("Bạn không có quyền sử dụng lệnh này.")
        return

    parts = message.content.strip().split(maxsplit=2)
    if len(parts) < 3:
        await message.channel.send(
            "Cú pháp: /config <threshold_low|threshold_high> <giá trị>"
        )
        return

    param_name = parts[1].lower()
    try:
        param_value = float(parts[2])
    except ValueError:
        await message.channel.send("Giá trị cấu hình phải là số thực.")
        return

    if param_name not in ("threshold_low", "threshold_high"):
        await message.channel.send(
            "Chỉ hỗ trợ cấu hình: threshold_low hoặc threshold_high."
        )
        return

    if not (0.0 <= param_value <= 1.0):
        await message.channel.send("Giá trị ngưỡng phải nằm trong khoảng 0.0 đến 1.0.")
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
            srv, _ = sync_discord_context(message, session)
            if srv is None:
                await message.channel.send("Không thể khởi tạo cấu hình server.")
                return

            new_low = (
                param_value if param_name == "threshold_low" else srv.threshold_low
            )
            new_high = (
                param_value if param_name == "threshold_high" else srv.threshold_high
            )
            if new_low >= new_high:
                await message.channel.send(
                    "Ngưỡng không hợp lệ: threshold_low phải nhỏ hơn threshold_high."
                )
                return

            srv.threshold_low = new_low
            srv.threshold_high = new_high
            session.commit()
            await message.channel.send(
                f"Đã cập nhật {param_name} = {param_value:.2f} cho server."
            )
    except Exception as e:
        await message.channel.send(f"Lỗi khi cập nhật cấu hình: {e}")
