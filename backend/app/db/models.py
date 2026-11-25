"""Import every model module here so Alembic can see all tables."""

from app.modules.audit import models as audit_models
from app.modules.auth import models as auth_models
from app.modules.records import models as records_models

__all__ = ["audit_models", "auth_models", "records_models"]
