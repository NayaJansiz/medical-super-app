from collections.abc import Callable, Iterator

import pytest
from argon2 import PasswordHasher
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core import security
from app.core.security import hash_password
from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.modules.auth.models import User

PASSWORD = "correct-horse-battery"

MakeUser = Callable[..., User]


@pytest.fixture(autouse=True)
def fast_password_hashing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests use cheap argon2id settings. Production keeps the defaults."""
    monkeypatch.setattr(
        security, "_hasher", PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)
    )
    security._dummy_hash.cache_clear()


@pytest.fixture
def engine() -> Iterator[Engine]:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def client(engine: Engine) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(engine: Engine) -> MakeUser:
    def _make_user(
        role: str = "patient",
        email: str | None = None,
        password: str = PASSWORD,
        is_active: bool = True,
    ) -> User:
        with Session(engine) as session:
            user = User(
                email=email or f"{role}@test.example",
                password_hash=hash_password(password),
                full_name=f"Test {role}",
                role=role,
                is_active=is_active,
                is_synthetic=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    return _make_user
