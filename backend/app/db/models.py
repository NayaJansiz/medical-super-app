"""Import every model module here so Alembic can see all tables."""

from app.modules.auth import models as auth_models

__all__ = ["auth_models"]
