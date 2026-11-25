import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.errors import AppError
from app.modules.auth.deps import DbSession, require_roles
from app.modules.auth.models import User
from app.modules.auth.roles import Role
from app.modules.records import service
from app.modules.records.schemas import (
    ConsentCreate,
    ConsentOut,
    ProfileOut,
    ProfileUpdate,
    ReceivedConsentOut,
)

router = APIRouter(prefix="/api/v1")

PatientOnly = Annotated[User, Depends(require_roles(Role.PATIENT))]
DoctorOnly = Annotated[User, Depends(require_roles(Role.DOCTOR))]
PatientOrDoctor = Annotated[User, Depends(require_roles(Role.PATIENT, Role.DOCTOR))]


@router.post("/consents", response_model=ConsentOut, status_code=201)
def grant_consent(
    payload: ConsentCreate, patient: PatientOnly, db: DbSession
) -> ConsentOut:
    """Allowed: patient, for their own record."""
    return service.create_consent(db, patient, payload)


@router.get("/consents", response_model=list[ConsentOut])
def my_consents(patient: PatientOnly, db: DbSession) -> list[ConsentOut]:
    """Allowed: patient. Everything I have shared, with its status."""
    return service.list_my_consents(db, patient)


@router.get("/consents/received", response_model=list[ReceivedConsentOut])
def received_consents(doctor: DoctorOnly, db: DbSession) -> list[ReceivedConsentOut]:
    """Allowed: doctor. Active access that patients have given me."""
    return service.list_received_consents(db, doctor)


@router.post("/consents/{consent_id}/revoke", response_model=ConsentOut)
def revoke_consent(
    consent_id: uuid.UUID, patient: PatientOnly, db: DbSession
) -> ConsentOut:
    """Allowed: the patient who owns the consent."""
    return service.revoke_consent(db, patient, consent_id)


@router.get("/patients/me/profile", response_model=ProfileOut)
def read_my_profile(patient: PatientOnly, db: DbSession) -> ProfileOut:
    """Allowed: patient (own profile)."""
    profile = service.get_profile_by_user(db, patient.id)
    if profile is None:
        raise AppError(404, "NOT_FOUND", "Profile not created yet.")
    return ProfileOut.model_validate(service.read_profile(db, patient, profile.id))


@router.put("/patients/me/profile", response_model=ProfileOut)
def save_my_profile(
    payload: ProfileUpdate, patient: PatientOnly, db: DbSession
) -> ProfileOut:
    """Allowed: patient. Creates the profile on first save."""
    return ProfileOut.model_validate(service.upsert_own_profile(db, patient, payload))


@router.get("/patients/{patient_id}/profile", response_model=ProfileOut)
def read_profile(
    patient_id: uuid.UUID, actor: PatientOrDoctor, db: DbSession
) -> ProfileOut:
    """Allowed: the owner, or a doctor with an active records:read consent."""
    return ProfileOut.model_validate(service.read_profile(db, actor, patient_id))


@router.put("/patients/{patient_id}/profile", response_model=ProfileOut)
def update_profile(
    patient_id: uuid.UUID,
    payload: ProfileUpdate,
    actor: PatientOrDoctor,
    db: DbSession,
) -> ProfileOut:
    """Allowed: the owner, or a doctor with an active records:write consent."""
    return ProfileOut.model_validate(
        service.update_profile(db, actor, patient_id, payload)
    )
