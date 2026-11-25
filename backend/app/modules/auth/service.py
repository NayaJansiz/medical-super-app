"""Auth business logic. No HTTP here."""

import uuid
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import (
    burn_password_check,
    hash_password,
    hash_token,
    new_session_token,
    verify_password,
)
from app.core.timeutil import as_utc, utcnow
from app.modules.auth.models import User, UserSession
from app.modules.auth.roles import Role

INVALID_CREDENTIALS = AppError(401, "INVALID_CREDENTIALS", "Wrong email or password.")


def _invalid_credentials() -> AppError:
    return AppError(
        INVALID_CREDENTIALS.status_code,
        INVALID_CREDENTIALS.code,
        INVALID_CREDENTIALS.message,
    )


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def register_user(
    db: Session,
    *,
    email: str,
    password: str,
    full_name: str,
    role: str,
    is_synthetic: bool = False,
) -> User:
    if get_user_by_email(db, email) is not None:
        raise AppError(409, "EMAIL_TAKEN", "This email is already registered.")
    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=role,
        is_synthetic=is_synthetic,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AppError(
            409, "EMAIL_TAKEN", "This email is already registered."
        ) from None
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    """Return the user or raise the same error for every kind of failure."""
    user = get_user_by_email(db, email)
    if user is None:
        burn_password_check(password)
        raise _invalid_credentials()
    if not verify_password(user.password_hash, password) or not user.is_active:
        raise _invalid_credentials()
    return user


def create_session(db: Session, user: User, ttl: timedelta) -> str:
    token = new_session_token()
    db.add(
        UserSession(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=utcnow() + ttl,
        )
    )
    db.commit()
    return token


def get_user_for_token(db: Session, token: str) -> User | None:
    row = db.scalar(
        select(UserSession).where(UserSession.token_hash == hash_token(token))
    )
    if row is None or row.revoked_at is not None:
        return None
    if as_utc(row.expires_at) <= utcnow():
        return None
    user = db.get(User, row.user_id)
    if user is None or not user.is_active:
        return None
    return user


def revoke_session(db: Session, token: str) -> None:
    row = db.scalar(
        select(UserSession).where(UserSession.token_hash == hash_token(token))
    )
    if row is not None and row.revoked_at is None:
        row.revoked_at = utcnow()
        db.commit()


def change_role(db: Session, *, actor: User, user_id: uuid.UUID, role: Role) -> User:
    if actor.id == user_id:
        raise AppError(
            409, "CANNOT_CHANGE_OWN_ROLE", "You cannot change your own role."
        )
    user = db.get(User, user_id)
    if user is None:
        raise AppError(404, "NOT_FOUND", "User not found.")
    user.role = role.value
    db.commit()
    db.refresh(user)
    return user
