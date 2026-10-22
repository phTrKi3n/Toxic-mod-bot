from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from bot import commands, rbac


@pytest.fixture(autouse=True)
def discord_only_legacy_mode(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("RBAC_DISCORD_ONLY", "true")


def make_message(*roles, content="/queue", guild=True, bot=False):
    return SimpleNamespace(
        content=content,
        guild=SimpleNamespace(id=1, name="Guild 1") if guild else None,
        author=SimpleNamespace(
            id=99,
            name="tester",
            bot=bot,
            roles=[SimpleNamespace(name=role) for role in roles],
            send=AsyncMock(),
        ),
        channel=SimpleNamespace(send=AsyncMock()),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["queue", "resolve", "config"])
@pytest.mark.parametrize("roles", [(), ("member",), ("labeler",)])
async def test_member_cannot_run_administrative_command(name, roles):
    message = make_message(*roles, content=f"/{name} 123")
    await commands.handle_command(message)
    message.channel.send.assert_awaited_once_with(
        "Bạn không có quyền sử dụng lệnh này."
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["queue", "resolve", "config"])
async def test_direct_handler_call_is_protected(name):
    message = make_message("member")
    await getattr(commands, f"_handle_{name}")(message)
    message.channel.send.assert_awaited_once_with(
        "Bạn không có quyền sử dụng lệnh này."
    )


@pytest.mark.asyncio
async def test_mod_cannot_configure():
    message = make_message("mod", content="/config")
    await commands.handle_command(message)
    message.channel.send.assert_awaited_once_with(
        "Bạn không có quyền sử dụng lệnh này."
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role,name",
    [
        ("mod", "queue"),
        ("mod", "resolve"),
        ("admin", "queue"),
        ("admin", "resolve"),
        ("admin", "config"),
        ("Mod", "queue"),
    ],
)
async def test_authorized_user_passes_rbac_guard(role, name):
    message = make_message(role, content=f"/{name} 123")
    await commands.handle_command(message)
    message.channel.send.assert_awaited_once()
    sent_text = message.channel.send.await_args.args[0]
    assert sent_text != rbac.DENIED


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["queue", "resolve", "config"])
@pytest.mark.parametrize("guild,bot", [(False, False), (True, True)])
async def test_dm_and_bot_cannot_administrate(name, guild, bot):
    message = make_message("admin", content=f"/{name}", guild=guild, bot=bot)
    await commands.handle_command(message)
    message.channel.send.assert_awaited_once_with(
        "Bạn không có quyền sử dụng lệnh này."
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["queue", "resolve", "config", "appeal"])
async def test_similar_prefix_is_not_a_command(name):
    message = make_message("admin", content=f"/{name}fake")
    await commands.handle_command(message)
    message.channel.send.assert_awaited_once_with("Lệnh không tồn tại.")


@pytest.mark.asyncio
@pytest.mark.parametrize("role", ["member", "labeler", "mod", "admin"])
async def test_appeal_is_available_to_all_roles(role):
    message = make_message(role, content="/appeal 123 lý do")
    await commands.handle_command(message)
    message.channel.send.assert_awaited_once()
    sent_text = message.channel.send.await_args.args[0]
    assert sent_text != rbac.DENIED


@pytest.mark.asyncio
async def test_revoked_role_is_checked_again():
    message = make_message("admin", content="/config")
    await commands.handle_command(message)
    first_reply = message.channel.send.await_args.args[0]
    assert first_reply != rbac.DENIED

    message.channel.send.reset_mock()
    message.author.roles = []
    await commands.handle_command(message)
    message.channel.send.assert_awaited_once_with(
        "Bạn không có quyền sử dụng lệnh này."
    )


@pytest.mark.asyncio
async def test_whitespace_does_not_bypass_guard():
    message = make_message("member", content="  /resolve\t123  ")
    await commands.handle_command(message)
    message.channel.send.assert_awaited_once_with(
        "Bạn không có quyền sử dụng lệnh này."
    )


@pytest.mark.asyncio
async def test_empty_command_is_unknown():
    message = make_message("member", content="  ")
    await commands.handle_command(message)
    message.channel.send.assert_awaited_once_with("Lệnh không tồn tại.")
