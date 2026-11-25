"""Consent and patient-record logic.

The only way to reach a patient profile is authorize_access(). It allows the
owner, or a user holding an active consent with a sufficient scope, and it
writes an audit row for every decision, including denials. A denied caller
gets 404, so the API never confirms that a record exists.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.timeutil import as_utc, utcnow
from app.modules.audit import service as audit
from app.modules.audit.models import Outcome
from app.modules.auth.models import User
from app.modules.auth.roles import Role
from app.modules.auth.service import get_user_by_email
from app.modules.records.models import Consent, PatientProfile, Scope
from app.modules.records.schemas import (
    ConsentCreate,
    ConsentOut,
    ProfileUpdate,
    ReceivedConsentOut,
)

_ALLOWED_SCOPES = {
    Scope.READ: {Scope.READ.value, Scope.WRITE.value},
    Scope.WRITE: {Scope.WRITE.value},
}


def consent_status(consent: Consent) -> str:
    if consent.revoked_at is not None:
        return "revoked"
    if as_utc(consent.expires_at) <= utcnow():
        return "expired"
    return "active"


def _has_active_consent(
    db: Session, *, patient_id: uuid.UUID, grantee_id: uuid.UUID, scope: Scope
) -> bool:
    rows = db.scalars(
        select(Consent).where(
            Consent.patient_id == patient_id,
            Consent.grantee_user_id == grantee_id,
            Consent.revoked_at.is_(None),
            Consent.scope.in_(_ALLOWED_SCOPES[scope]),
        )
    ).all()
    return any(consent_status(row) == "active" for row in rows)


def authorize_access(
    db: Session,
    actor: User,
    patient_id: uuid.UUID,
    scope: Scope,
    action: str,
) -> PatientProfile:
    profile = db.get(PatientProfile, patient_id)
    allowed = profile is not None and (
        profile.user_id == actor.id
        or _has_active_consent(
            db, patient_id=patient_id, grantee_id=actor.id, scope=scope
        )
    )
    if profile is None or not allowed:
        audit.log(
            db,
            actor_id=actor.id,
            action=action,
            resource_type="patient_profile",
            resource_id=patient_id,
            patient_id=patient_id,
            outcome=Outcome.DENIED,
        )
        db.commit()
        raise AppError(404, "NOT_FOUND", "Patient record not found.")
    return profile


def get_profile_by_user(db: Session, user_id: uuid.UUID) -> PatientProfile | None:
    return db.scalar(select(PatientProfile).where(PatientProfile.user_id == user_id))


def read_profile(db: Session, actor: User, patient_id: uuid.UUID) -> PatientProfile:
    profile = authorize_access(db, actor, patient_id, Scope.READ, "profile.read")
    audit.log(
        db,
        actor_id=actor.id,
        action="profile.read",
        resource_type="patient_profile",
        resource_id=profile.id,
        patient_id=profile.id,
    )
    db.commit()  # the audit row is saved before any data is returned
    return profile


def update_profile(
    db: Session, actor: User, patient_id: uuid.UUID, data: ProfileUpdate
) -> PatientProfile:
    profile = authorize_access(db, actor, patient_id, Scope.WRITE, "profile.update")
    _apply(profile, data)
    audit.log(
        db,
        actor_id=actor.id,
        action="profile.update",
        resource_type="patient_profile",
        resource_id=profile.id,
        patient_id=profile.id,
    )
    db.commit()
    db.refresh(profile)
    return profile


def upsert_own_profile(
    db: Session, patient: User, data: ProfileUpdate
) -> PatientProfile:
    profile = get_profile_by_user(db, patient.id)
    if profile is not None:
        return update_profile(db, patient, profile.id, data)
    profile = PatientProfile(user_id=patient.id, is_synthetic=patient.is_synthetic)
    _apply(profile, data)
    db.add(profile)
    db.flush()
    audit.log(
        db,
        actor_id=patient.id,
        action="profile.create",
        resource_type="patient_profile",
        resource_id=profile.id,
        patient_id=profile.id,
    )
    db.commit()
    db.refresh(profile)
    return profile


def _apply(profile: PatientProfile, data: ProfileUpdate) -> None:
    profile.allergies = data.allergies
    profile.surgeries = data.surgeries
    profile.medical_history = data.medical_history
    profile.medication_history = data.medication_history


def _consent_out(consent: Consent, grantee_name: str | None) -> ConsentOut:
    return ConsentOut(
        id=consent.id,
        patient_id=consent.patient_id,
        grantee_user_id=consent.grantee_user_id,
        grantee_name=grantee_name,
        scope=consent.scope,
        expires_at=consent.expires_at,
        revoked_at=consent.revoked_at,
        status=consent_status(consent),  # type: ignore[arg-type]
    )


def create_consent(db: Session, patient: User, payload: ConsentCreate) -> ConsentOut:
    profile = get_profile_by_user(db, patient.id)
    if profile is None:
        raise AppError(
            409, "PROFILE_REQUIRED", "Create your profile before sharing it."
        )
    grantee = get_user_by_email(db, payload.grantee_email)
    if grantee is None or grantee.role != Role.DOCTOR.value or not grantee.is_active:
        raise AppError(404, "NOT_FOUND", "Doctor not found.")
    existing = db.scalars(
        select(Consent).where(
            Consent.patient_id == profile.id,
            Consent.grantee_user_id == grantee.id,
            Consent.scope == payload.scope,
            Consent.revoked_at.is_(None),
        )
    ).all()
    if any(consent_status(row) == "active" for row in existing):
        raise AppError(409, "CONSENT_EXISTS", "This doctor already has this access.")
    consent = Consent(
        patient_id=profile.id,
        grantee_user_id=grantee.id,
        scope=payload.scope,
        expires_at=payload.expires_at,
        is_synthetic=patient.is_synthetic,
    )
    db.add(consent)
    db.flush()
    audit.log(
        db,
        actor_id=patient.id,
        action="consent.grant",
        resource_type="consent",
        resource_id=consent.id,
        patient_id=profile.id,
        detail=f"scope={payload.scope}; grantee={grantee.id}",
    )
    db.commit()
    db.refresh(consent)
    return _consent_out(consent, grantee.full_name)


def list_my_consents(db: Session, patient: User) -> list[ConsentOut]:
    profile = get_profile_by_user(db, patient.id)
    if profile is None:
        return []
    rows = db.execute(
        select(Consent, User.full_name)
        .join(User, User.id == Consent.grantee_user_id)
        .where(Consent.patient_id == profile.id)
        .order_by(Consent.created_at.desc(), Consent.id)
    ).all()
    return [_consent_out(consent, name) for consent, name in rows]


def revoke_consent(db: Session, patient: User, consent_id: uuid.UUID) -> ConsentOut:
    profile = get_profile_by_user(db, patient.id)
    consent = db.get(Consent, consent_id)
    # Someone else's consent looks exactly like a missing one.
    if profile is None or consent is None or consent.patient_id != profile.id:
        raise AppError(404, "NOT_FOUND", "Consent not found.")
    if consent.revoked_at is not None:
        raise AppError(
            409, "CONSENT_ALREADY_REVOKED", "This consent is already revoked."
        )
    consent.revoked_at = utcnow()
    audit.log(
        db,
        actor_id=patient.id,
        action="consent.revoke",
        resource_type="consent",
        resource_id=consent.id,
        patient_id=profile.id,
        detail=f"scope={consent.scope}; grantee={consent.grantee_user_id}",
    )
    db.commit()
    db.refresh(consent)
    grantee = db.get(User, consent.grantee_user_id)
    return _consent_out(consent, grantee.full_name if grantee else None)


def list_received_consents(db: Session, doctor: User) -> list[ReceivedConsentOut]:
    """Active consents granted to this doctor: how a doctor finds patient ids."""
    rows = db.execute(
        select(Consent, User.full_name)
        .join(PatientProfile, PatientProfile.id == Consent.patient_id)
        .join(User, User.id == PatientProfile.user_id)
        .where(Consent.grantee_user_id == doctor.id, Consent.revoked_at.is_(None))
        .order_by(Consent.created_at.desc(), Consent.id)
    ).all()
    return [
        ReceivedConsentOut(
            id=consent.id,
            patient_id=consent.patient_id,
            patient_name=name,
            scope=consent.scope,
            expires_at=consent.expires_at,
        )
        for consent, name in rows
        if consent_status(consent) == "active"
    ]
