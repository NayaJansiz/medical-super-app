import json
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.main import app
from app.modules.audit import service as audit_service
from app.modules.audit.models import AuditLog
from tests.conftest import MakeUser
from tests.helpers import (
    ALL_AUDIT_URL,
    CONSENTS_URL,
    MY_AUDIT_URL,
    MY_PROFILE_URL,
    audit_rows,
    create_profile,
    expire_consent,
    grant,
    login,
    profile_url,
)


def actions(engine: Engine) -> list[tuple[str, str]]:
    return [(row.action, row.outcome) for row in audit_rows(engine)]


def test_profile_lifecycle_is_audited(
    client: TestClient, make_user: MakeUser, engine: Engine
) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    patient_id = create_profile(client)
    grant(client, doctor, "records:write")
    login(client, doctor)
    client.get(profile_url(patient_id))
    client.put(profile_url(patient_id), json={"allergies": "x"})
    assert actions(engine) == [
        ("profile.create", "success"),
        ("consent.grant", "success"),
        ("profile.read", "success"),
        ("profile.update", "success"),
    ]
    rows = audit_rows(engine)
    assert rows[2].actor_id == doctor.id
    assert str(rows[2].patient_id) == patient_id


def test_owner_reads_are_audited_too(
    client: TestClient, make_user: MakeUser, engine: Engine
) -> None:
    login(client, make_user("patient"))
    create_profile(client)
    client.get(MY_PROFILE_URL)
    assert ("profile.read", "success") in actions(engine)


def test_denied_access_is_audited(
    client: TestClient, make_user: MakeUser, engine: Engine
) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    patient_id = create_profile(client)
    login(client, doctor)
    assert client.get(profile_url(patient_id)).status_code == 404
    assert client.put(profile_url(patient_id), json={}).status_code == 404
    denied = [row for row in audit_rows(engine) if row.outcome == "denied"]
    assert [row.action for row in denied] == ["profile.read", "profile.update"]
    assert all(row.actor_id == doctor.id for row in denied)
    assert all(str(row.patient_id) == patient_id for row in denied)


def test_probing_an_unknown_id_is_audited_without_error(
    client: TestClient, make_user: MakeUser, engine: Engine
) -> None:
    doctor = make_user("doctor")
    login(client, doctor)
    missing = uuid.uuid4()
    assert client.get(profile_url(missing)).status_code == 404
    rows = audit_rows(engine)
    assert len(rows) == 1
    assert rows[0].outcome == "denied"
    assert rows[0].patient_id == missing


def test_expired_consent_denial_is_audited(
    client: TestClient, make_user: MakeUser, engine: Engine
) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    login(client, patient)
    patient_id = create_profile(client)
    consent_id = grant(client, doctor)
    expire_consent(engine, consent_id)
    login(client, doctor)
    client.get(profile_url(patient_id))
    assert actions(engine)[-1] == ("profile.read", "denied")


def test_consent_revoke_and_role_change_are_audited(
    client: TestClient, make_user: MakeUser, engine: Engine
) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    admin = make_user("super_admin")
    login(client, patient)
    create_profile(client)
    consent_id = grant(client, doctor)
    client.post(f"{CONSENTS_URL}/{consent_id}/revoke")
    login(client, admin)
    client.post(f"/api/v1/admin/users/{patient.id}/role", json={"role": "student"})
    names = [name for name, _ in actions(engine)]
    assert "consent.revoke" in names
    role_row = next(r for r in audit_rows(engine) if r.action == "user.role_change")
    assert role_row.actor_id == admin.id
    assert role_row.resource_id == patient.id
    assert role_row.detail == "role=student"
    assert role_row.patient_id is None


def test_audit_rows_never_contain_patient_content(
    client: TestClient, make_user: MakeUser, engine: Engine
) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    secret = "SECRET-DIAGNOSIS-TEXT"
    login(client, patient)
    patient_id = create_profile(client, secret)
    grant(client, doctor)
    login(client, doctor)
    client.get(profile_url(patient_id))
    dump = json.dumps(
        [
            [str(v) for v in (r.action, r.resource_type, r.detail, r.outcome)]
            for r in audit_rows(engine)
        ]
    )
    assert secret not in dump
    login(client, patient)
    assert secret not in json.dumps(client.get(MY_AUDIT_URL).json())


def test_patient_sees_who_accessed_their_record(
    client: TestClient, make_user: MakeUser
) -> None:
    patient = make_user("patient")
    doctor = make_user("doctor")
    stranger = make_user("doctor", email="stranger@test.example")
    login(client, patient)
    patient_id = create_profile(client)
    grant(client, doctor)
    login(client, doctor)
    client.get(profile_url(patient_id))
    login(client, stranger)
    client.get(profile_url(patient_id))
    login(client, patient)
    entries = client.get(MY_AUDIT_URL).json()
    reads = [e for e in entries if e["action"] == "profile.read"]
    assert {(e["actor_name"], e["outcome"]) for e in reads} == {
        ("Test doctor", "success"),
        ("Test doctor", "denied"),
    }
    assert {e["actor_id"] for e in reads} == {str(doctor.id), str(stranger.id)}
    assert all(e["patient_id"] == patient_id for e in entries)
    others = client.get(MY_AUDIT_URL, params={"others_only": "true"}).json()
    assert all(e["actor_id"] != str(patient.id) for e in others)
    assert len(others) < len(entries)


def test_patient_never_sees_other_patients_audit_rows(
    client: TestClient, make_user: MakeUser
) -> None:
    alice = make_user("patient", email="alice@test.example")
    bob = make_user("patient", email="bob@test.example")
    login(client, alice)
    create_profile(client)
    login(client, bob)
    create_profile(client)
    entries = client.get(MY_AUDIT_URL).json()
    assert len(entries) == 1
    assert entries[0]["actor_id"] == str(bob.id)


def test_patient_without_profile_gets_empty_log(
    client: TestClient, make_user: MakeUser
) -> None:
    login(client, make_user("patient"))
    assert client.get(MY_AUDIT_URL).json() == []


def test_admin_sees_everything_and_can_filter(
    client: TestClient, make_user: MakeUser
) -> None:
    patient = make_user("patient")
    admin = make_user("super_admin")
    login(client, patient)
    patient_id = create_profile(client)
    login(client, admin)
    everything = client.get(ALL_AUDIT_URL)
    assert everything.status_code == 200
    assert {"profile.create", "audit.read"} <= {e["action"] for e in everything.json()}
    filtered = client.get(ALL_AUDIT_URL, params={"patient_id": patient_id}).json()
    assert [e["action"] for e in filtered] == ["profile.create"]


def test_admin_reading_the_log_is_itself_logged(
    client: TestClient, make_user: MakeUser, engine: Engine
) -> None:
    admin = make_user("super_admin")
    login(client, admin)
    client.get(ALL_AUDIT_URL)
    rows = [r for r in audit_rows(engine) if r.action == "audit.read"]
    assert len(rows) == 1
    assert rows[0].actor_id == admin.id


def test_audit_pagination_limits(client: TestClient, make_user: MakeUser) -> None:
    login(client, make_user("super_admin"))
    assert client.get(ALL_AUDIT_URL, params={"limit": 0}).status_code == 400
    assert client.get(ALL_AUDIT_URL, params={"limit": 201}).status_code == 400
    assert client.get(ALL_AUDIT_URL, params={"offset": -1}).status_code == 400
    assert client.get(ALL_AUDIT_URL, params={"limit": 1}).status_code == 200


def test_audit_log_is_append_only(engine: Engine) -> None:
    with Session(engine) as session:
        audit_service.log(
            session, actor_id=uuid.uuid4(), action="test", resource_type="x"
        )
        session.commit()
        row = session.query(AuditLog).one()
        row.action = "tampered"
        with pytest.raises(RuntimeError, match="append-only"):
            session.commit()
        session.rollback()
        session.delete(session.query(AuditLog).one())
        with pytest.raises(RuntimeError, match="append-only"):
            session.commit()


def test_no_endpoint_can_modify_the_audit_log(
    client: TestClient, make_user: MakeUser
) -> None:
    login(client, make_user("super_admin"))
    for method in ("put", "patch", "delete", "post"):
        response = getattr(client, method)(ALL_AUDIT_URL)
        assert response.status_code == 405


def test_read_fails_when_the_audit_write_fails(
    client: TestClient,
    make_user: MakeUser,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patient = make_user("patient")
    login(client, patient)
    patient_id = create_profile(client, "SECRET-DATA")

    def boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError("audit store down")

    monkeypatch.setattr(audit_service, "log", boom)
    with TestClient(app, raise_server_exceptions=False) as strict:
        strict.cookies.update(client.cookies)
        response = strict.get(profile_url(patient_id))
    assert response.status_code == 500
    assert "SECRET-DATA" not in response.text
