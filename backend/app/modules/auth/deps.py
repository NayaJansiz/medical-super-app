"""FastAPI dependencies. Every protected endpoint uses these."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.config import SESSION_COOKIE_NAME
from app.core.errors import AppError
from app.db.session import get_db
from app.modules.auth import service
from app.modules.auth.models import User
from app.modules.auth.roles import Role

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(request: Request, db: DbSession) -> User:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    user = service.get_user_for_token(db, token) if token else None
    if user is None:
        raise AppError(401, "NOT_AUTHENTICATED", "You are not logged in.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: Role) -> Callable[[User], User]:
    """Allow only the listed roles. Usage: Depends(require_roles(Role.DOCTOR))."""
    allowed = {role.value for role in roles}

    def dependency(user: CurrentUser) -> User:
        if user.role not in allowed:
            raise AppError(403, "FORBIDDEN", "You do not have permission to do this.")
        return user

    return dependency
