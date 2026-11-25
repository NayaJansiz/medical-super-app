"""Authorization matrix for Day 3: every role against every endpoint."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.modules.auth.roles import ALL_ROLES
from tests.conftest import MakeUser
from tests.helpers import (
    ALL_AUDIT_URL,
    CONSENTS_URL,
    MY_AUDIT_URL,
    MY_PROFILE_URL,
    create_profile,
    grant,
    in_days,
    login,
    profile_url,
)

# endpoint key -> status per role. Every role not listed must get 403.
# 404 means "allowed to try, but this record is not yours".
EXPECTED: dict[str, dict[str, int]] = {
    "grant": {"patient": 201},
    "list_consents": {"patient": 200},
    "received": {"doctor": 200},
    "revoke": {"patient": 200},
    "my_profile_get": {"patient": 200},
    "my_profile_put": {"patient": 200},
    "profile_get_foreign": {"patient": 404, "doctor": 404},
    "profile_put_foreign": {"patient": 404, "doctor": 404},
    "audit_me": {"patient": 200},
    "audit_all": {"super_admin": 200},
}


def call(
    client: TestClient, key: str, foreign_id: str, consent_id: str, doctor_email: str
):
    match key:
        case "grant":
            return client.post(
                CONSENTS_URL,
                json={
                    "grantee_email": doctor_email,
                    "scope": "records:write",
                    "expires_at": in_days(3),
                },
            )
        case "list_consents":
            return client.get(CONSENTS_URL)
        case "received":
            return client.get(f"{CONSENTS_URL}/received")
        case "revoke":
            return client.post(f"{CONSENTS_URL}/{consent_id}/revoke")
        case "my_profile_get":
            return client.get(MY_PROFILE_URL)
        case "my_profile_put":
            return client.put(MY_PROFILE_URL, json={"allergies": "x"})
        case "profile_get_foreign":
            return client.get(profile_url(foreign_id))
        case "profile_put_foreign":
            return client.put(profile_url(foreign_id), json={})
        case "audit_me":
            return client.get(MY_AUDIT_URL)
        case "audit_all":
            return client.get(ALL_AUDIT_URL)
    raise AssertionError(key)


@pytest.mark.parametrize("key", list(EXPECTED))
@pytest.mark.parametrize("role", ALL_ROLES)
def test_role_by_endpoint_matrix(
    client: TestClient, make_user: MakeUser, role: str, key: str
) -> None:
    # An unrelated patient owns the foreign record; a second patient shares
    # with a doctor so that "revoke" and "received" have data to work on.
    owner = make_user("patient", email="owner@test.example")
    doctor = make_user("doctor", email="target-doctor@test.example")
    login(client, owner)
    foreign_id = create_profile(client)
    consent_id = grant(client, doctor)
    foreign_check = key.startswith("profile_")
    if role == "patient":
        # Consent endpoints use the owner; "foreign" checks use another patient.
        actor = (
            make_user("patient", email="other-patient@test.example")
            if foreign_check
            else owner
        )
    elif role == "doctor":
        # "foreign" checks use a doctor who holds NO consent on that record.
        actor = (
            make_user("doctor", email="no-consent@test.example")
            if foreign_check
            else doctor
        )
    else:
        actor = make_user(role, email=f"{role}@actor.example")
    login(client, actor)
    if role == "patient" and foreign_check:
        create_profile(client)
    response = call(client, key, foreign_id, consent_id, doctor.email)
    expected = EXPECTED[key].get(role, 403)
    assert response.status_code == expected, (role, key, response.text)
    if expected == 403:
        assert response.json()["error"]["code"] == "FORBIDDEN"


@pytest.mark.parametrize("key", list(EXPECTED))
def test_everything_requires_login(client: TestClient, key: str) -> None:
    response = call(client, key, str(uuid.uuid4()), str(uuid.uuid4()), "a@b.example")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "NOT_AUTHENTICATED"
