import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()


def _database_url() -> str | None:
    url = os.getenv("DATABASE_URL")
    if url is None:
        return None
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def _create_engine() -> Engine | None:
    url = _database_url()
    if url is None:
        return None
    return create_engine(url, pool_pre_ping=True)


engine = _create_engine()


def check_database_connection() -> bool:
    if engine is None:
        return False

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return False
    return True
