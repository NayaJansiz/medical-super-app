from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app.core.security import hash_token
from app.core.timeutil import utcnow
from app.modules.auth.models import User, UserSession
from tests.conftest import PASSWORD, MakeUser

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
LOGOUT_URL = "/api/v1/auth/logout"
ME_URL = "/api/v1/me"


def register_payload(**overrides: str) -> dict[str, str]:
    payload = {
        "email": "new.user@test.example",
        "password": PASSWORD,
        "full_name": "New User",
        "role": "patient",
    }
    payload.update(overrides)
    return payload


def assert_error_shape(body: dict[str, object], code: str) -> None:
    assert set(body) == {"error"}
    error = body["error"]
    assert isinstance(error, dict)
    assert error["code"] == code
    assert isinstance(error["message"], str)
    assert "details" in error


# ---------- register ----------


def test_register_creates_user_without_leaking_secrets(client: TestClient) -> None:
    response = client.post(REGISTER_URL, json=register_payload())
    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "email", "full_name", "role"}
    assert isinstance(body["id"], str) and len(body["id"]) == 36
    assert body["role"] == "patient"
    assert "password" not in response.text.lower()


def test_register_lowercases_and_trims_email(client: TestClient) -> None:
    response = client.post(
        REGISTER_URL, json=register_payload(email="  Mixed.Case@Test.Example ")
    )
    assert response.status_code == 201
    assert response.json()["email"] == "mixed.case@test.example"


def test_register_duplicate_email_is_conflict_case_insensitive(
    client: TestClient,
) -> None:
    assert client.post(REGISTER_URL, json=register_payload()).status_code == 201
    response = client.post(
        REGISTER_URL, json=register_payload(email="NEW.USER@test.example")
    )
    assert response.status_code == 409
    assert_error_shape(response.json(), "EMAIL_TAKEN")


@pytest.mark.parametrize("role", ["doctor", "super_admin", "clinic_admin", "wizard"])
def test_register_rejects_privileged_roles(client: TestClient, role: str) -> None:
    response = client.post(REGISTER_URL, json=register_payload(role=role))
    assert response.status_code == 400
    assert_error_shape(response.json(), "VALIDATION_ERROR")


def test_register_student_is_allowed(client: TestClient) -> None:
    response = client.post(REGISTER_URL, json=register_payload(role="student"))
    assert response.status_code == 201
    assert response.json()["role"] == "student"


def test_register_validation_errors_do_not_echo_the_password(
    client: TestClient,
) -> None:
    response = client.post(REGISTER_URL, json=register_payload(password="Sh0rt!"))
    assert response.status_code == 400
    assert_error_shape(response.json(), "VALIDATION_ERROR")
    assert "Sh0rt!" not in response.text


@pytest.mark.parametrize(
    "overrides",
    [{"email": "not-an-email"}, {"full_name": "   "}, {"password": "x" * 200}],
)
def test_register_rejects_bad_input(
    client: TestClient, overrides: dict[str, str]
) -> None:
    response = client.post(REGISTER_URL, json=register_payload(**overrides))
    assert response.status_code == 400
    assert_error_shape(response.json(), "VALIDATION_ERROR")


def test_register_stores_a_hash_not_the_password(
    client: TestClient, engine: Engine
) -> None:
    client.post(REGISTER_URL, json=register_payload())
    with Session(engine) as session:
        user = session.scalar(select(User))
        assert user is not None
        assert user.password_hash != PASSWORD
        assert user.password_hash.startswith("$argon2")
        assert user.is_synthetic is False


# ---------- login ----------


def test_login_sets_a_safe_cookie_and_returns_user(
    client: TestClient, make_user: MakeUser
) -> None:
    make_user("patient")
    response = client.post(
        LOGIN_URL, json={"email": "patient@test.example", "password": PASSWORD}
    )
    assert response.status_code == 200
    assert response.json()["role"] == "patient"
    cookie = response.headers["set-cookie"].lower()
    assert "session=" in cookie
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "path=/" in cookie


def test_cookie_is_secure_outside_development(
    client: TestClient, make_user: MakeUser, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    make_user("patient")
    response = client.post(
        LOGIN_URL, json={"email": "patient@test.example", "password": PASSWORD}
    )
    assert "secure" in response.headers["set-cookie"].lower()


def test_wrong_password_and_unknown_email_give_the_same_error(
    client: TestClient, make_user: MakeUser
) -> None:
    make_user("patient")
    wrong = client.post(
        LOGIN_URL, json={"email": "patient@test.example", "password": "nope-nope-nope"}
    )
    unknown = client.post(
        LOGIN_URL, json={"email": "ghost@test.example", "password": PASSWORD}
    )
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()
    assert_error_shape(wrong.json(), "INVALID_CREDENTIALS")
    assert "set-cookie" not in wrong.headers


def test_inactive_user_cannot_log_in(client: TestClient, make_user: MakeUser) -> None:
    make_user("patient", is_active=False)
    response = client.post(
        LOGIN_URL, json={"email": "patient@test.example", "password": PASSWORD}
    )
    assert response.status_code == 401
    assert_error_shape(response.json(), "INVALID_CREDENTIALS")


def test_session_token_is_stored_hashed(
    client: TestClient, make_user: MakeUser, engine: Engine
) -> None:
    make_user("patient")
    client.post(LOGIN_URL, json={"email": "patient@test.example", "password": PASSWORD})
    cookie_value = client.cookies.get("session")
    assert cookie_value
    with Session(engine) as session:
        row = session.scalar(select(UserSession))
        assert row is not None
        assert row.token_hash != cookie_value
        assert row.token_hash == hash_token(cookie_value)


# ---------- /me, logout, expiry ----------


def login(client: TestClient, email: str = "patient@test.example") -> None:
    response = client.post(LOGIN_URL, json={"email": email, "password": PASSWORD})
    assert response.status_code == 200


def test_me_requires_login(client: TestClient) -> None:
    response = client.get(ME_URL)
    assert response.status_code == 401
    assert_error_shape(response.json(), "NOT_AUTHENTICATED")


def test_me_returns_the_logged_in_user(client: TestClient, make_user: MakeUser) -> None:
    make_user("doctor")
    login(client, "doctor@test.example")
    response = client.get(ME_URL)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "doctor@test.example"
    assert body["role"] == "doctor"
    assert set(body) == {"id", "email", "full_name", "role"}


def test_me_rejects_a_forged_cookie(client: TestClient) -> None:
    client.cookies.set("session", "totally-made-up-token")
    assert client.get(ME_URL).status_code == 401


def test_logout_ends_the_session_even_if_the_cookie_is_reused(
    client: TestClient, make_user: MakeUser
) -> None:
    make_user("patient")
    login(client)
    old_cookie = client.cookies.get("session")
    assert old_cookie

    response = client.post(LOGOUT_URL)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert client.get(ME_URL).status_code == 401

    client.cookies.set("session", old_cookie)
    assert client.get(ME_URL).status_code == 401


def test_logout_without_login_is_harmless(client: TestClient) -> None:
    assert client.post(LOGOUT_URL).status_code == 200


def test_expired_session_is_rejected(
    client: TestClient, make_user: MakeUser, engine: Engine
) -> None:
    make_user("patient")
    login(client)
    with Session(engine) as session:
        row = session.scalar(select(UserSession))
        assert row is not None
        row.expires_at = utcnow() - timedelta(minutes=1)
        session.commit()
    assert client.get(ME_URL).status_code == 401


def test_deactivated_user_loses_access_immediately(
    client: TestClient, make_user: MakeUser, engine: Engine
) -> None:
    make_user("patient")
    login(client)
    with Session(engine) as session:
        user = session.scalar(select(User))
        assert user is not None
        user.is_active = False
        session.commit()
    assert client.get(ME_URL).status_code == 401


def test_unknown_route_uses_the_error_shape(client: TestClient) -> None:
    response = client.get("/api/v1/nope")
    assert response.status_code == 404
    assert_error_shape(response.json(), "NOT_FOUND")
