import uuid

from fastapi.testclient import TestClient

from tests.conftest import MakeUser
from tests.helpers import (
    CONSENTS_URL,
    create_profile,
    grant,
    in_days,
    login,
    profile_url,
)


def test_patient_grants_and_lists_consent(
    client: TestClient, make_user: MakeUser
) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    patient_id = create_profile(client)
    consent_id = grant(client, doctor, "records:read")
    listed = client.get(CONSENTS_URL).json()
    assert len(listed) == 1
    assert listed[0]["id"] == consent_id
    assert listed[0]["patient_id"] == patient_id
    assert listed[0]["status"] == "active"
    assert listed[0]["scope"] == "records:read"


def test_grant_requires_profile(client: TestClient, make_user: MakeUser) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    response = client.post(
        CONSENTS_URL,
        json={
            "grantee_email": doctor.email,
            "scope": "records:read",
            "expires_at": in_days(5),
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PROFILE_REQUIRED"


def test_grant_to_non_doctor_or_unknown_is_404(
    client: TestClient, make_user: MakeUser
) -> None:
    patient = make_user("patient")
    pharmacist = make_user("pharmacist")
    login(client, patient)
    create_profile(client)
    for email in (pharmacist.email, "nobody@test.example"):
        response = client.post(
            CONSENTS_URL,
            json={
                "grantee_email": email,
                "scope": "records:read",
                "expires_at": in_days(5),
            },
        )
        assert response.status_code == 404


def test_grant_validation(client: TestClient, make_user: MakeUser) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    create_profile(client)
    base = {"grantee_email": doctor.email, "scope": "records:read"}
    bad_bodies = [
        {**base, "expires_at": in_days(-1)},  # in the past
        {**base, "expires_at": in_days(400)},  # too far away
        {**base, "expires_at": "2030-01-01T00:00:00"},  # no timezone
        {**base, "expires_at": in_days(5), "scope": "records:delete"},
        {**base, "expires_at": in_days(5), "grantee_email": "not-an-email"},
        {"grantee_email": doctor.email, "scope": "records:read"},  # no expiry
    ]
    for body in bad_bodies:
        response = client.post(CONSENTS_URL, json=body)
        assert response.status_code == 400, body
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_double_grant_is_409(client: TestClient, make_user: MakeUser) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    create_profile(client)
    grant(client, doctor, "records:read")
    response = client.post(
        CONSENTS_URL,
        json={
            "grantee_email": doctor.email,
            "scope": "records:read",
            "expires_at": in_days(5),
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONSENT_EXISTS"


def test_regrant_after_revoke_is_allowed(
    client: TestClient, make_user: MakeUser
) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    create_profile(client)
    consent_id = grant(client, doctor)
    assert client.post(f"{CONSENTS_URL}/{consent_id}/revoke").status_code == 200
    grant(client, doctor)


def test_revoke_twice_is_409(client: TestClient, make_user: MakeUser) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    create_profile(client)
    consent_id = grant(client, doctor)
    first = client.post(f"{CONSENTS_URL}/{consent_id}/revoke")
    assert first.status_code == 200
    assert first.json()["status"] == "revoked"
    second = client.post(f"{CONSENTS_URL}/{consent_id}/revoke")
    assert second.status_code == 409


def test_revoke_unknown_consent_is_404(client: TestClient, make_user: MakeUser) -> None:
    patient = make_user("patient")
    login(client, patient)
    create_profile(client)
    response = client.post(f"{CONSENTS_URL}/{uuid.uuid4()}/revoke")
    assert response.status_code == 404


def test_patient_cannot_revoke_someone_elses_consent(
    client: TestClient, make_user: MakeUser
) -> None:
    alice = make_user("patient", email="alice@test.example")
    mallory = make_user("patient", email="mallory@test.example")
    doctor = make_user("doctor")
    login(client, alice)
    create_profile(client)
    consent_id = grant(client, doctor)
    login(client, mallory)
    create_profile(client)
    response = client.post(f"{CONSENTS_URL}/{consent_id}/revoke")
    assert response.status_code == 404
    # Alice's consent is still active.
    login(client, alice)
    assert client.get(CONSENTS_URL).json()[0]["status"] == "active"


def test_patient_only_sees_their_own_consents(
    client: TestClient, make_user: MakeUser
) -> None:
    alice = make_user("patient", email="alice@test.example")
    bob = make_user("patient", email="bob@test.example")
    doctor = make_user("doctor")
    login(client, alice)
    create_profile(client)
    grant(client, doctor)
    login(client, bob)
    create_profile(client)
    assert client.get(CONSENTS_URL).json() == []


def test_doctor_sees_received_consents_until_revoked(
    client: TestClient, make_user: MakeUser
) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    patient_id = create_profile(client)
    consent_id = grant(client, doctor)
    login(client, doctor)
    received = client.get(f"{CONSENTS_URL}/received").json()
    assert [item["patient_id"] for item in received] == [patient_id]
    assert received[0]["patient_name"] == "Test patient"
    login(client, patient)
    client.post(f"{CONSENTS_URL}/{consent_id}/revoke")
    login(client, doctor)
    assert client.get(f"{CONSENTS_URL}/received").json() == []
    assert client.get(profile_url(patient_id)).status_code == 404
