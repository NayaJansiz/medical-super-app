"""A consent works only while its holder is still a doctor."""

from fastapi.testclient import TestClient
from sqlalchemy import Engine

from tests.conftest import MakeUser
from tests.helpers import (
    audit_rows,
    create_profile,
    grant,
    login,
    profile_url,
)


def _demote(client: TestClient, admin: object, user_id: object, role: str) -> None:
    login(client, admin)  # type: ignore[arg-type]
    response = client.post(f"/api/v1/admin/users/{user_id}/role", json={"role": role})
    assert response.status_code == 200, response.text


def test_ex_doctor_made_patient_loses_read_and_write(
    client: TestClient, make_user: MakeUser, engine: Engine
) -> None:
    patient = make_user("patient", email="owner@test.example")
    doctor = make_user("doctor")
    admin = make_user("super_admin")
    login(client, patient)
    patient_id = create_profile(client, "Synthetic allergy")
    grant(client, doctor, "records:write")
    login(client, doctor)
    assert client.get(profile_url(patient_id)).status_code == 200

    _demote(client, admin, doctor.id, "patient")

    login(client, doctor)  # same person, now a patient
    assert client.get(profile_url(patient_id)).status_code == 404
    assert (
        client.put(profile_url(patient_id), json={"allergies": "x"}).status_code == 404
    )
    denied = [r for r in audit_rows(engine) if r.outcome == "denied"]
    assert [r.actor_id for r in denied] == [doctor.id, doctor.id]

    login(client, patient)
    assert (
        client.get("/api/v1/patients/me/profile").json()["allergies"]
        == "Synthetic allergy"
    )


def test_doctor_made_patient_then_doctor_again_regains_access(
    client: TestClient, make_user: MakeUser
) -> None:
    patient = make_user("patient", email="owner@test.example")
    doctor = make_user("doctor")
    admin = make_user("super_admin")
    login(client, patient)
    patient_id = create_profile(client)
    grant(client, doctor)
    _demote(client, admin, doctor.id, "patient")
    login(client, doctor)
    assert client.get(profile_url(patient_id)).status_code == 404
    _demote(client, admin, doctor.id, "doctor")
    login(client, doctor)
    assert client.get(profile_url(patient_id)).status_code == 200


def test_a_patient_never_gets_access_through_a_consent_row(
    client: TestClient, make_user: MakeUser
) -> None:
    """Another patient cannot read a record, whatever the consent table says."""
    owner = make_user("patient", email="owner@test.example")
    other = make_user("patient", email="other@test.example")
    login(client, owner)
    patient_id = create_profile(client)
    login(client, other)
    create_profile(client)
    assert client.get(profile_url(patient_id)).status_code == 404
