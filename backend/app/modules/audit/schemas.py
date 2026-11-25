import uuid
from datetime import datetime

from pydantic import BaseModel


class AuditEntryOut(BaseModel):
    id: uuid.UUID
    at: datetime
    actor_id: uuid.UUID
    actor_name: str | None
    action: str
    resource_type: str
    resource_id: uuid.UUID | None
    patient_id: uuid.UUID | None
    outcome: str
    detail: str | None
