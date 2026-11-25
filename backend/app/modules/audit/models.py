import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, String, Uuid, event, func
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapped, Mapper, mapped_column

from app.core.timeutil import utcnow
from app.db.base import Base


class Outcome(StrEnum):
    SUCCESS = "success"
    DENIED = "denied"


class AuditLog(Base):
    """Append-only record of who did what. Never holds patient content.

    actor_id and patient_id are plain UUID columns (no foreign keys) so that
    denied attempts on unknown ids can still be recorded and rows outlive
    the records they describe. The table has no updated_at on purpose.
    """

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    action: Mapped[str] = mapped_column(String(64))
    resource_type: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True, index=True
    )
    outcome: Mapped[str] = mapped_column(String(16))
    detail: Mapped[str | None] = mapped_column(String(200), nullable=True)
    at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, server_default=func.now(), index=True
    )


@event.listens_for(AuditLog, "before_update")
def _block_update(
    mapper: Mapper[AuditLog], connection: Connection, target: AuditLog
) -> None:
    raise RuntimeError("audit_logs is append-only: rows cannot be updated")


@event.listens_for(AuditLog, "before_delete")
def _block_delete(
    mapper: Mapper[AuditLog], connection: Connection, target: AuditLog
) -> None:
    raise RuntimeError("audit_logs is append-only: rows cannot be deleted")
