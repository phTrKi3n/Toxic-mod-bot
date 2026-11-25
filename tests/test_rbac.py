import pytest


@pytest.fixture(autouse=True)
def discord_only_legacy_mode(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("RBAC_DISCORD_ONLY", "true")


from types import SimpleNamespace

from bot.commands import has_role, is_admin, is_mod_or_admin


def make_message(*roles):
    discord_roles = [SimpleNamespace(name=role) for role in roles]

    author = SimpleNamespace(roles=discord_roles)

    return SimpleNamespace(author=author, guild=SimpleNamespace(id=1))


def test_member_has_no_mod_permission():
    message = make_message("member")

    assert not is_mod_or_admin(message)
    assert not is_admin(message)


def test_mod_has_mod_permission():
    message = make_message("member", "mod")

    assert is_mod_or_admin(message)
    assert not is_admin(message)


def test_admin_has_all_permissions():
    message = make_message("member", "admin")

    assert is_mod_or_admin(message)
    assert is_admin(message)


def test_role_check_is_case_insensitive():
    message = make_message("Mod")

    assert is_mod_or_admin(message)


def test_guild_owner_and_native_permissions_grant_roles():
    owner_msg = SimpleNamespace(
        guild=SimpleNamespace(id=1, owner_id=42),
        author=SimpleNamespace(id=42, bot=False, roles=[]),
    )
    assert is_admin(owner_msg)
    assert is_mod_or_admin(owner_msg)

    native_admin_msg = SimpleNamespace(
        guild=SimpleNamespace(id=1, owner_id=999),
        author=SimpleNamespace(
            id=10,
            bot=False,
            roles=[SimpleNamespace(name="member")],
            guild_permissions=SimpleNamespace(administrator=True),
        ),
    )
    assert is_admin(native_admin_msg)

    native_mod_msg = SimpleNamespace(
        guild=SimpleNamespace(id=1, owner_id=999),
        author=SimpleNamespace(
            id=11,
            bot=False,
            roles=[],
            guild_permissions=SimpleNamespace(
                administrator=False, manage_guild=False, manage_messages=True
            ),
        ),
    )
    assert is_mod_or_admin(native_mod_msg)
    assert not is_admin(native_mod_msg)
