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
