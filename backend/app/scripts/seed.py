"""Create one fake user per role, a demo patient profile and one consent
(all is_synthetic = true).

Run from the repo root:
    SEED_PASSWORD='choose-a-long-password' PYTHONPATH=backend \
        uv run python -m app.scripts.seed

The password comes from the environment, never from code. Safe to run twice.
"""

import os
import sys
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import database
from app.core.timeutil import utcnow
from app.db import models  # noqa: F401
from app.modules.auth.roles import Role
from app.modules.auth.service import get_user_by_email, register_user
from app.modules.records.models import Consent, PatientProfile, Scope

DEMO_DOMAIN = "demo.example"


def seed_users(db: Session, password: str) -> int:
    """Create missing demo users. Returns how many were created."""
    created = 0
    for role in Role:
        email = f"{role.value.replace('_', '-')}@{DEMO_DOMAIN}"
        if get_user_by_email(db, email) is not None:
            continue
        register_user(
            db,
            email=email,
            password=password,
            full_name=f"Demo {role.value.replace('_', ' ').title()}",
            role=role.value,
            is_synthetic=True,
        )
        created += 1
    return created


def seed_records(db: Session) -> int:
    """Give the demo patient a fake profile and share it with the demo doctor."""
    patient = get_user_by_email(db, f"patient@{DEMO_DOMAIN}")
    doctor = get_user_by_email(db, f"doctor@{DEMO_DOMAIN}")
    if patient is None or doctor is None:
        return 0
    created = 0
    profile = db.scalar(
        select(PatientProfile).where(PatientProfile.user_id == patient.id)
    )
    if profile is None:
        profile = PatientProfile(
            user_id=patient.id,
            allergies="Synthetic demo allergy: none known",
            surgeries="Synthetic demo: none",
            medical_history="Synthetic demo record. Not a real patient.",
            medication_history="Synthetic demo: none",
            is_synthetic=True,
        )
        db.add(profile)
        db.flush()
        created += 1
    has_consent = db.scalar(
        select(Consent).where(
            Consent.patient_id == profile.id, Consent.grantee_user_id == doctor.id
        )
    )
    if has_consent is None:
        db.add(
            Consent(
                patient_id=profile.id,
                grantee_user_id=doctor.id,
                scope=Scope.READ.value,
                expires_at=utcnow() + timedelta(days=30),
                is_synthetic=True,
            )
        )
        created += 1
    db.commit()
    return created


def main() -> None:
    password = os.getenv("SEED_PASSWORD", "")
    if len(password) < 8:
        sys.exit("Set SEED_PASSWORD (at least 8 characters) before seeding.")
    if database.engine is None:
        sys.exit("DATABASE_URL is not set.")
    with Session(database.engine) as db:
        created = seed_users(db, password)
        records = seed_records(db)
    print(f"Seeded {created} synthetic user(s) and {records} record item(s).")


if __name__ == "__main__":
    main()
