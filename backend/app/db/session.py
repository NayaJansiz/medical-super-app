"""Database session dependency for FastAPI."""

from collections.abc import Iterator

from sqlalchemy.orm import Session

from app.core import database
from app.core.errors import AppError


def get_db() -> Iterator[Session]:
    engine = database.engine
    if engine is None:
        raise AppError(503, "SERVICE_UNAVAILABLE", "Database connection unavailable")
    with Session(engine) as session:
        yield session
