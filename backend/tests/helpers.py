import uuid
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog
from app.modules.auth.models import User
from app.modules.records.models import Consent
from tests.conftest import PASSWORD

LOGIN_URL = "/api/v1/auth/login"
CONSENTS_URL = "/api/v1/consents"
MY_PROFILE_URL = "/api/v1/patients/me/profile"
MY_AUDIT_URL = "/api/v1/audit-logs/me"
ALL_AUDIT_URL = "/api/v1/audit-logs"


def login(client: TestClient, user: User) -> None:
    response = client.post(LOGIN_URL, json={"email": user.email, "password": PASSWORD})
    assert response.status_code == 200


def in_days(days: float) -> str:
    return (datetime.now(UTC) + timedelta(days=days)).isoformat()


def profile_url(patient_id: str | uuid.UUID) -> str:
    return f"/api/v1/patients/{patient_id}/profile"


def create_profile(client: TestClient, text: str = "Synthetic note") -> str:
    """Log in first as a patient. Returns the new patient_id."""
    response = client.put(
        MY_PROFILE_URL,
        json={"allergies": text, "medical_history": "Synthetic history"},
    )
    assert response.status_code == 200
    return str(response.json()["id"])


def grant(
    client: TestClient,
    doctor: User,
    scope: str = "records:read",
    days: float = 30,
) -> str:
    """Log in as the patient first. Returns the consent id."""
    response = client.post(
        CONSENTS_URL,
        json={
            "grantee_email": doctor.email,
            "scope": scope,
            "expires_at": in_days(days),
        },
    )
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


def audit_rows(engine: Engine) -> list[AuditLog]:
    with Session(engine) as session:
        return list(session.scalars(select(AuditLog).order_by(AuditLog.at)).all())


def expire_consent(engine: Engine, consent_id: str) -> None:
    with Session(engine) as session:
        row = session.get(Consent, uuid.UUID(consent_id))
        assert row is not None
        row.expires_at = datetime.now(UTC) - timedelta(minutes=1)
        session.commit()
