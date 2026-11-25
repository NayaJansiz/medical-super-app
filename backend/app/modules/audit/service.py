"""Writing to the audit log.

log() only adds the row to the session. The caller commits, so the audit row
and the change it describes succeed or fail together. For reads and denials
the caller commits right after log(), before any data is returned.
"""

import uuid

from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog, Outcome


def log(
    db: Session,
    *,
    actor_id: uuid.UUID,
    action: str,
    resource_type: str,
    resource_id: uuid.UUID | None = None,
    patient_id: uuid.UUID | None = None,
    outcome: Outcome = Outcome.SUCCESS,
    detail: str | None = None,
) -> None:
    db.add(
        AuditLog(
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            patient_id=patient_id,
            outcome=outcome.value,
            detail=detail,
        )
    )
