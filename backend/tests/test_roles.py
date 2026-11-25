"""Authorization matrix: every role against every protected endpoint."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.roles import ALL_ROLES
from tests.conftest import PASSWORD, MakeUser

LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/me"


def login_as(client: TestClient, make_user: MakeUser, role: str) -> User:
    user = make_user(role)
    response = client.post(LOGIN_URL, json={"email": user.email, "password": PASSWORD})
    assert response.status_code == 200
    return user


def role_url(user_id: uuid.UUID) -> str:
    return f"/api/v1/admin/users/{user_id}/role"


# endpoint -> roles allowed. Add every new endpoint here.
@pytest.mark.parametrize("role", ALL_ROLES)
def test_me_is_open_to_every_logged_in_role(
    client: TestClient, make_user: MakeUser, role: str
) -> None:
    login_as(client, make_user, role)
    assert client.get(ME_URL).status_code == 200


@pytest.mark.parametrize("role", ALL_ROLES)
def test_set_role_matrix(client: TestClient, make_user: MakeUser, role: str) -> None:
    login_as(client, make_user, role)
    target = make_user("patient", email="target@test.example")
    response = client.post(role_url(target.id), json={"role": "doctor"})
    expected = 200 if role == "super_admin" else 403
    assert response.status_code == expected
    if expected == 403:
        assert response.json()["error"]["code"] == "FORBIDDEN"


def test_set_role_requires_login(client: TestClient, make_user: MakeUser) -> None:
    target = make_user("patient")
    response = client.post(role_url(target.id), json={"role": "doctor"})
    assert response.status_code == 401


def test_set_role_actually_changes_the_role(
    client: TestClient, make_user: MakeUser, engine: Engine
) -> None:
    login_as(client, make_user, "super_admin")
    target = make_user("patient", email="target@test.example")
    client.post(role_url(target.id), json={"role": "pharmacist"})
    with Session(engine) as session:
        refreshed = session.scalar(select(User).where(User.id == target.id))
        assert refreshed is not None
        assert refreshed.role == "pharmacist"


def test_admin_cannot_change_their_own_role(
    client: TestClient, make_user: MakeUser
) -> None:
    admin = login_as(client, make_user, "super_admin")
    response = client.post(role_url(admin.id), json={"role": "patient"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CANNOT_CHANGE_OWN_ROLE"


def test_set_role_unknown_user_is_404(client: TestClient, make_user: MakeUser) -> None:
    login_as(client, make_user, "super_admin")
    response = client.post(role_url(uuid.uuid4()), json={"role": "doctor"})
    assert response.status_code == 404


def test_set_role_rejects_invalid_role(client: TestClient, make_user: MakeUser) -> None:
    login_as(client, make_user, "super_admin")
    target = make_user("patient", email="target@test.example")
    response = client.post(role_url(target.id), json={"role": "wizard"})
    assert response.status_code == 400
