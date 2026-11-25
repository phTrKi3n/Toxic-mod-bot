"""Security hardening regression tests verified during v1.0.1 audit remediation."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from bot import commands
from db.models import Base, HardCase, Message, Server, User
from inference_service.app import app


@pytest.fixture()
def hardened_db(tmp_path, monkeypatch):
    db_file = tmp_path / "hardened_test.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.delenv("RBAC_DISCORD_ONLY", raising=False)
    monkeypatch.delenv("RBAC_AUTO_SYNC_ROLES", raising=False)

    engine = create_engine(url)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(Server(server_id=1, guild_id="100", name="G100", is_active=True))
        session.add(
            User(user_id=1, discord_id="50", username="restricted_mod", role="mod")
        )
        session.flush()
        session.add(
            Message(
                message_id=777,
                server_id=1,
                user_id=1,
                content="borderline content",
                language="vi",
            )
        )
        session.flush()
        session.add(
            HardCase(
                hardcase_id=1,
                message_id=777,
                original_score=0.65,
                status="pending",
            )
        )
        session.commit()
    return url


@pytest.mark.asyncio
async def test_queue_does_not_leak_to_public_channel_when_dm_fails(hardened_db):
    msg = SimpleNamespace(
        content="/queue",
        guild=SimpleNamespace(id="100", name="G100"),
        author=SimpleNamespace(
            id="50",
            name="restricted_mod",
            bot=False,
            roles=[SimpleNamespace(name="mod")],
            send=AsyncMock(side_effect=RuntimeError("Forbidden")),
        ),
        channel=SimpleNamespace(send=AsyncMock()),
    )
    await commands.handle_command(msg)
    sent = msg.channel.send.await_args.args[0]
    assert "HardCase" not in sent
    assert "777" not in sent
    assert "DM" in sent


@pytest.mark.asyncio
async def test_sync_does_not_promote_restricted_db_role(hardened_db):
    msg = SimpleNamespace(
        content="/config threshold_high 0.85",
        guild=SimpleNamespace(id="100", name="G100", owner_id="50"),
        author=SimpleNamespace(
            id="50",
            name="restricted_mod",
            bot=False,
            roles=[SimpleNamespace(name="admin")],
            send=AsyncMock(),
        ),
        channel=SimpleNamespace(send=AsyncMock()),
    )
    await commands.handle_command(msg)
    assert msg.channel.send.await_args.args[0] == "Bạn không có quyền sử dụng lệnh này."

    engine = create_engine(hardened_db)
    with Session(engine) as session:
        user = session.get(User, 1)
        assert user is not None
        assert user.role == "mod"


@pytest.mark.asyncio
async def test_command_sanitizes_internal_db_exceptions(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "invalid://bad_url")
    msg = SimpleNamespace(
        content="/appeal 777 test reason",
        guild=SimpleNamespace(id="100", name="G100"),
        author=SimpleNamespace(
            id="50",
            name="member",
            bot=False,
            roles=[SimpleNamespace(name="member")],
            send=AsyncMock(),
        ),
        channel=SimpleNamespace(send=AsyncMock()),
    )
    await commands.handle_command(msg)
    sent = msg.channel.send.await_args.args[0]
    assert "sqlalchemy" not in sent.lower()
    assert "bad_url" not in sent.lower()


def test_inference_ops_reload_requires_api_key_and_rejects_oversized_input(
    monkeypatch,
):
    client = TestClient(app)

    oversized = client.post("/classify", json={"text": "x" * 4001})
    assert oversized.status_code == 422

    monkeypatch.setenv("OPS_API_KEY", "top-secret-ops-key")
    unauth = client.post("/ops/reload")
    assert unauth.status_code == 403

    wrong = client.post("/ops/reload", headers={"X-Ops-Api-Key": "wrong-key"})
    assert wrong.status_code == 403

    ok = client.post("/ops/reload", headers={"X-Ops-Api-Key": "top-secret-ops-key"})
    assert ok.status_code == 200
