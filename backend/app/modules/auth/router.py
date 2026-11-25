import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from app.core.config import SESSION_COOKIE_NAME, cookie_secure, session_ttl
from app.modules.auth import service
from app.modules.auth.deps import CurrentUser, DbSession, require_roles
from app.modules.auth.models import User
from app.modules.auth.roles import Role
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    RoleUpdate,
    StatusOut,
    UserOut,
)

router = APIRouter(prefix="/api/v1")


@router.post("/auth/register", response_model=UserOut, status_code=201)
def register(payload: RegisterRequest, db: DbSession) -> User:
    return service.register_user(
        db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role=payload.role,
    )


@router.post("/auth/login", response_model=UserOut)
def login(payload: LoginRequest, response: Response, db: DbSession) -> User:
    user = service.authenticate(db, payload.email, payload.password)
    ttl = session_ttl()
    token = service.create_session(db, user, ttl)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=int(ttl.total_seconds()),
        httponly=True,
        samesite="lax",
        secure=cookie_secure(),
        path="/",
    )
    return user


@router.post("/auth/logout", response_model=StatusOut)
def logout(request: Request, response: Response, db: DbSession) -> StatusOut:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        service.revoke_session(db, token)
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return StatusOut(status="ok")


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser) -> User:
    return user


@router.post("/admin/users/{user_id}/role", response_model=UserOut)
def set_user_role(
    user_id: uuid.UUID,
    payload: RoleUpdate,
    admin: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
    db: DbSession,
) -> User:
    return service.change_role(
        db, actor=admin, user_id=user_id, role=Role(payload.role)
    )
