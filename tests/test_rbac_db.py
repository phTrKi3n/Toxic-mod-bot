from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from bot import rbac
from db.models import Base, HardCase, Message, Server, User


def msg(*roles, guild=10, uid=1, bot=False):
    return SimpleNamespace(
        guild=SimpleNamespace(id=guild) if guild else None,
        author=SimpleNamespace(
            id=uid, bot=bot, roles=[SimpleNamespace(name=r) for r in roles]
        ),
    )


def test_db_roles_and_tenant_scope(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("RBAC_DISCORD_ONLY", raising=False)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add_all(
            [
                User(user_id=1, discord_id="1", username="one", role="mod"),
                User(user_id=2, discord_id="2", username="two", role="member"),
                Server(server_id=10, guild_id="10", name="A", is_active=True),
                Server(server_id=20, guild_id="20", name="B", is_active=True),
            ]
        )
        db.flush()
        db.add_all(
            [
                Message(message_id=101, server_id=10, user_id=1, content="x"),
                Message(message_id=201, server_id=20, user_id=2, content="y"),
            ]
        )
        db.flush()
        db.add(HardCase(hardcase_id=5, message_id=201, original_score=0.5))
        db.commit()
        assert rbac.allowed(msg("mod"), "queue", session=db)
        assert not rbac.allowed(msg("admin"), "config", session=db)  # DB is mod
        assert not rbac.allowed(msg("mod", guild=99), "queue", session=db)
        assert not rbac.allowed(msg("mod", uid=2), "queue", session=db)
        assert not rbac.allowed(msg("mod", bot=True), "queue", session=db)
        assert not rbac.allowed(msg("mod", guild=None), "queue", session=db)
        assert rbac.scoped_message(db, 10, 101) is not None
        assert rbac.scoped_message(db, 10, 201) is None
        assert rbac.owned_appeal_target(db, 10, 1, 101) is not None
        assert rbac.owned_appeal_target(db, 10, 2, 101) is None
        assert rbac.scoped_hardcase(db, 10, 5) is None
        db.get(User, 1).role = "member"
        db.commit()
        assert not rbac.allowed(msg("mod"), "queue", session=db)


def test_fail_closed_without_db(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("RBAC_DISCORD_ONLY", raising=False)
    assert not rbac.allowed(msg("admin"), "config")
    assert rbac.allowed(msg("member"), "appeal")
    monkeypatch.setenv("RBAC_DISCORD_ONLY", "true")
    assert rbac.allowed(msg("mod"), "queue")
    assert not rbac.allowed(msg("mod"), "config")
