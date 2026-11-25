import uuid

from fastapi.testclient import TestClient
from sqlalchemy import Engine

from tests.conftest import MakeUser
from tests.helpers import (
    CONSENTS_URL,
    MY_PROFILE_URL,
    create_profile,
    expire_consent,
    grant,
    login,
    profile_url,
)


def test_patient_creates_reads_and_updates_own_profile(
    client: TestClient, make_user: MakeUser
) -> None:
    login(client, make_user("patient"))
    assert client.get(MY_PROFILE_URL).status_code == 404  # none yet
    patient_id = create_profile(client, "Penicillin (synthetic)")
    body = client.get(MY_PROFILE_URL).json()
    assert body["id"] == patient_id
    assert body["allergies"] == "Penicillin (synthetic)"
    updated = client.put(MY_PROFILE_URL, json={"allergies": "None"})
    assert updated.json()["id"] == patient_id
    assert updated.json()["allergies"] == "None"
    assert updated.json()["medical_history"] is None  # PUT replaces


def test_profile_validation(client: TestClient, make_user: MakeUser) -> None:
    login(client, make_user("patient"))
    too_long = client.put(MY_PROFILE_URL, json={"allergies": "x" * 5001})
    assert too_long.status_code == 400
    wrong_type = client.put(MY_PROFILE_URL, json={"allergies": ["a"]})
    assert wrong_type.status_code == 400


def test_response_never_exposes_user_internals(
    client: TestClient, make_user: MakeUser
) -> None:
    login(client, make_user("patient"))
    create_profile(client)
    body = client.get(MY_PROFILE_URL).json()
    assert set(body) == {
        "id",
        "allergies",
        "surgeries",
        "medical_history",
        "medication_history",
        "updated_at",
    }


def test_doctor_without_consent_gets_404(
    client: TestClient, make_user: MakeUser
) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    patient_id = create_profile(client)
    login(client, doctor)
    assert client.get(profile_url(patient_id)).status_code == 404
    assert client.put(profile_url(patient_id), json={}).status_code == 404


def test_unknown_and_foreign_ids_look_identical(
    client: TestClient, make_user: MakeUser
) -> None:
    alice = make_user("patient", email="alice@test.example")
    bob = make_user("patient", email="bob@test.example")
    login(client, alice)
    alice_id = create_profile(client)
    login(client, bob)
    create_profile(client)
    foreign = client.get(profile_url(alice_id))
    unknown = client.get(profile_url(uuid.uuid4()))
    assert foreign.status_code == unknown.status_code == 404
    assert foreign.json() == unknown.json()


def test_read_consent_allows_read_but_not_write(
    client: TestClient, make_user: MakeUser
) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    patient_id = create_profile(client, "Synthetic allergy")
    grant(client, doctor, "records:read")
    login(client, doctor)
    read = client.get(profile_url(patient_id))
    assert read.status_code == 200
    assert read.json()["allergies"] == "Synthetic allergy"
    write = client.put(profile_url(patient_id), json={"allergies": "changed"})
    assert write.status_code == 404
    login(client, patient)
    assert client.get(MY_PROFILE_URL).json()["allergies"] == "Synthetic allergy"


def test_write_consent_allows_read_and_write(
    client: TestClient, make_user: MakeUser
) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    patient_id = create_profile(client)
    grant(client, doctor, "records:write")
    login(client, doctor)
    assert client.get(profile_url(patient_id)).status_code == 200
    write = client.put(profile_url(patient_id), json={"allergies": "Doctor note"})
    assert write.status_code == 200
    login(client, patient)
    assert client.get(MY_PROFILE_URL).json()["allergies"] == "Doctor note"


def test_consent_for_patient_a_does_not_open_patient_b(
    client: TestClient, make_user: MakeUser
) -> None:
    alice = make_user("patient", email="alice@test.example")
    bob = make_user("patient", email="bob@test.example")
    doctor = make_user("doctor")
    login(client, alice)
    create_profile(client)
    grant(client, doctor, "records:write")
    login(client, bob)
    bob_id = create_profile(client)
    login(client, doctor)
    assert client.get(profile_url(bob_id)).status_code == 404
    assert client.put(profile_url(bob_id), json={}).status_code == 404


def test_consent_for_another_doctor_does_not_help(
    client: TestClient, make_user: MakeUser
) -> None:
    patient = make_user("patient")
    allowed = make_user("doctor", email="allowed@test.example")
    other = make_user("doctor", email="other@test.example")
    login(client, patient)
    patient_id = create_profile(client)
    grant(client, allowed)
    login(client, other)
    assert client.get(profile_url(patient_id)).status_code == 404


def test_expired_consent_stops_working(
    client: TestClient, make_user: MakeUser, engine: Engine
) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    patient_id = create_profile(client)
    consent_id = grant(client, doctor)
    login(client, doctor)
    assert client.get(profile_url(patient_id)).status_code == 200
    expire_consent(engine, consent_id)
    assert client.get(profile_url(patient_id)).status_code == 404
    login(client, patient)
    assert client.get(CONSENTS_URL).json()[0]["status"] == "expired"


def test_revoke_takes_effect_on_the_next_request(
    client: TestClient, make_user: MakeUser
) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    patient_id = create_profile(client)
    consent_id = grant(client, doctor)
    login(client, doctor)
    assert client.get(profile_url(patient_id)).status_code == 200
    login(client, patient)
    client.post(f"{CONSENTS_URL}/{consent_id}/revoke")
    login(client, doctor)
    assert client.get(profile_url(patient_id)).status_code == 404


def test_patient_can_use_the_id_route_for_own_profile_only(
    client: TestClient, make_user: MakeUser
) -> None:
    alice = make_user("patient", email="alice@test.example")
    bob = make_user("patient", email="bob@test.example")
    login(client, alice)
    alice_id = create_profile(client)
    assert client.get(profile_url(alice_id)).status_code == 200
    login(client, bob)
    create_profile(client)
    assert client.get(profile_url(alice_id)).status_code == 404
