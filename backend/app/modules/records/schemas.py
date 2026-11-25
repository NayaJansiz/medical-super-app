import uuid
from datetime import datetime, timedelta
from typing import Annotated, Literal

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    StringConstraints,
    field_validator,
)

from app.core.timeutil import utcnow
from app.modules.auth.schemas import Email

MAX_CONSENT_DAYS = 365

ScopeName = Literal["records:read", "records:write"]
ProfileText = Annotated[str, StringConstraints(max_length=5000)]


class ProfileUpdate(BaseModel):
    """PUT replaces all four fields; leave a field out to clear it."""

    allergies: ProfileText | None = None
    surgeries: ProfileText | None = None
    medical_history: ProfileText | None = None
    medication_history: ProfileText | None = None


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    allergies: str | None
    surgeries: str | None
    medical_history: str | None
    medication_history: str | None
    updated_at: datetime


class ConsentCreate(BaseModel):
    grantee_email: Email
    scope: ScopeName
    expires_at: AwareDatetime

    @field_validator("expires_at")
    @classmethod
    def _check_expiry(cls, value: datetime) -> datetime:
        now = utcnow()
        if value <= now:
            raise ValueError("expires_at must be in the future")
        if value > now + timedelta(days=MAX_CONSENT_DAYS):
            raise ValueError(f"expires_at must be within {MAX_CONSENT_DAYS} days")
        return value


class ConsentOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    grantee_user_id: uuid.UUID
    grantee_name: str | None
    scope: str
    expires_at: datetime
    revoked_at: datetime | None
    status: Literal["active", "expired", "revoked"]


class ReceivedConsentOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    patient_name: str | None
    scope: str
    expires_at: datetime
