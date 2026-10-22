"""
tests/test_bot.py — khớp TC04, TC05, TC06 ở Chương V mục I.2 của báo cáo.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from bot import commands
from db.models import Appeal, Base, HardCase, Message, ModerationAction, Server, User


@pytest.fixture()
def db_url(tmp_path, monkeypatch):
    db_file = tmp_path / "bot_test.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.delenv("RBAC_DISCORD_ONLY", raising=False)

    engine = create_engine(url)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        srv = Server(
            server_id=1,
            guild_id="100",
            name="Test Guild",
            threshold_low=0.30,
            threshold_high=0.90,
            is_active=True,
        )
        member = User(user_id=1, discord_id="10", username="member_user", role="member")
        mod = User(user_id=2, discord_id="20", username="mod_user", role="mod")
        labeler = User(
            user_id=3, discord_id="30", username="labeler_user", role="labeler"
        )
        admin = User(user_id=4, discord_id="40", username="admin_user", role="admin")
        session.add_all([srv, member, mod, labeler, admin])
        session.flush()

        msg1 = Message(
            message_id=501,
            server_id=1,
            user_id=1,
            content="Tin nhắn nghi vấn cần duyệt",
            language="vi",
        )
        msg2 = Message(
            message_id=502,
            server_id=1,
            user_id=1,
            content="Tin nhắn bị xoá cần khiếu nại",
            language="vi",
        )
        session.add_all([msg1, msg2])
        session.flush()

        hc = HardCase(
            hardcase_id=1,
            message_id=501,
            original_score=0.55,
            status="pending",
        )
        session.add(hc)
        session.commit()

    return url


def _make_discord_msg(
    content: str, uid: str, uname: str, role: str, guild_id: str = "100"
):
    return SimpleNamespace(
        content=content,
        guild=SimpleNamespace(id=guild_id, name="Test Guild"),
        author=SimpleNamespace(
            id=uid,
            name=uname,
            bot=False,
            roles=[SimpleNamespace(name=role)],
            send=AsyncMock(),
        ),
        channel=SimpleNamespace(send=AsyncMock(), fetch_message=AsyncMock()),
    )


@pytest.mark.asyncio
async def test_mod_can_restore_flagged_message(db_url):
    """TC04: Mod gọi /resolve <id> restore cho tin nhắn trong hàng đợi."""
    msg = _make_discord_msg(
        "/resolve 501 restore", uid="20", uname="mod_user", role="mod"
    )
    await commands.handle_command(msg)

    engine = create_engine(db_url)
    with Session(engine) as session:
        action = session.scalar(
            select(ModerationAction).where(ModerationAction.message_id == 501)
        )
        assert action is not None
        assert action.action_type == "restore"
        assert action.decided_by == 2

        hc = session.scalar(select(HardCase).where(HardCase.message_id == 501))
        assert hc is not None
        assert hc.status == "labeled"
        assert hc.corrected_label == "not_toxic"


@pytest.mark.asyncio
async def test_appeal_creates_pending_record(db_url):
    """TC05: Thành viên gửi /appeal tạo bản ghi Appeal(status='pending') cho đúng tin nhắn của mình."""
    msg = _make_discord_msg(
        "/appeal 502 Em chỉ trích dẫn câu trong phim",
        uid="10",
        uname="member_user",
        role="member",
    )
    await commands.handle_command(msg)

    engine = create_engine(db_url)
    with Session(engine) as session:
        appeal = session.scalar(select(Appeal).where(Appeal.message_id == 502))
        assert appeal is not None
        assert appeal.status == "pending"
        assert appeal.user_id == 1
        assert "trích dẫn" in appeal.reason


@pytest.mark.asyncio
async def test_member_cannot_call_resolve_command(db_url):
    """TC06: Thành viên thường gọi /resolve bị từ chối quyền."""
    msg = _make_discord_msg(
        "/resolve 501 restore", uid="10", uname="member_user", role="member"
    )
    await commands.handle_command(msg)
    msg.channel.send.assert_awaited_once_with("Bạn không có quyền sử dụng lệnh này.")


@pytest.mark.asyncio
async def test_labeler_can_label_hardcase(db_url):
    """Kiểm tra lệnh /label cho phép labeler gắn nhãn HardCase trong cùng server."""
    msg = _make_discord_msg(
        "/label 1 toxic", uid="30", uname="labeler_user", role="labeler"
    )
    await commands.handle_command(msg)

    engine = create_engine(db_url)
    with Session(engine) as session:
        hc = session.get(HardCase, 1)
        assert hc is not None
        assert hc.status == "labeled"
        assert hc.corrected_label == "toxic"
        assert hc.labeled_by == 3
