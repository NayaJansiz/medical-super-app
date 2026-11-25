import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.audit import service as audit
from app.modules.audit.models import AuditLog
from app.modules.audit.schemas import AuditEntryOut
from app.modules.auth.deps import DbSession, require_roles
from app.modules.auth.models import User
from app.modules.auth.roles import Role
from app.modules.records.models import PatientProfile

router = APIRouter(prefix="/api/v1")

Limit = Annotated[int, Query(ge=1, le=200)]
Offset = Annotated[int, Query(ge=0)]


def _entries(
    db: Session,
    *,
    patient_id: uuid.UUID | None = None,
    actor_id: uuid.UUID | None = None,
    exclude_actor_id: uuid.UUID | None = None,
    limit: int,
    offset: int,
) -> list[AuditEntryOut]:
    stmt = select(AuditLog, User.full_name).outerjoin(
        User, User.id == AuditLog.actor_id
    )
    if patient_id is not None:
        stmt = stmt.where(AuditLog.patient_id == patient_id)
    if actor_id is not None:
        stmt = stmt.where(AuditLog.actor_id == actor_id)
    if exclude_actor_id is not None:
        stmt = stmt.where(AuditLog.actor_id != exclude_actor_id)
    stmt = stmt.order_by(AuditLog.at.desc(), AuditLog.id).limit(limit).offset(offset)
    return [
        AuditEntryOut(
            id=row.id,
            at=row.at,
            actor_id=row.actor_id,
            actor_name=name,
            action=row.action,
            resource_type=row.resource_type,
            resource_id=row.resource_id,
            patient_id=row.patient_id,
            outcome=row.outcome,
            detail=row.detail,
        )
        for row, name in db.execute(stmt).all()
    ]


@router.get("/audit-logs/me", response_model=list[AuditEntryOut])
def my_audit_log(
    patient: Annotated[User, Depends(require_roles(Role.PATIENT))],
    db: DbSession,
    limit: Limit = 50,
    offset: Offset = 0,
    others_only: bool = False,
) -> list[AuditEntryOut]:
    """Who accessed my record. Allowed: patient (own record only)."""
    profile = db.scalar(
        select(PatientProfile).where(PatientProfile.user_id == patient.id)
    )
    if profile is None:
        return []
    return _entries(
        db,
        patient_id=profile.id,
        exclude_actor_id=patient.id if others_only else None,
        limit=limit,
        offset=offset,
    )


@router.get("/audit-logs", response_model=list[AuditEntryOut])
def all_audit_logs(
    admin: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
    db: DbSession,
    patient_id: uuid.UUID | None = None,
    actor_id: uuid.UUID | None = None,
    limit: Limit = 50,
    offset: Offset = 0,
) -> list[AuditEntryOut]:
    """The whole audit log. Allowed: super_admin. Reading it is itself logged."""
    audit.log(db, actor_id=admin.id, action="audit.read", resource_type="audit_log")
    db.commit()
    return _entries(
        db, patient_id=patient_id, actor_id=actor_id, limit=limit, offset=offset
    )
