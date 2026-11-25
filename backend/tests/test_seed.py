import pytest
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.roles import ALL_ROLES
from app.scripts import seed


def test_seed_creates_one_synthetic_user_per_role(engine: Engine) -> None:
    with Session(engine) as session:
        assert seed.seed_users(session, "a-long-demo-password") == len(ALL_ROLES)
        users = session.scalars(select(User)).all()
    assert sorted(u.role for u in users) == sorted(ALL_ROLES)
    assert all(u.is_synthetic for u in users)
    assert all(u.password_hash.startswith("$argon2") for u in users)


def test_seed_is_idempotent(engine: Engine) -> None:
    with Session(engine) as session:
        seed.seed_users(session, "a-long-demo-password")
        assert seed.seed_users(session, "a-long-demo-password") == 0


def test_seed_refuses_without_a_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SEED_PASSWORD", raising=False)
    with pytest.raises(SystemExit):
        seed.main()
