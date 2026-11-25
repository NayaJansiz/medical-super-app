"""Settings read from environment variables at call time."""

import os
from datetime import timedelta

SESSION_COOKIE_NAME = "session"
DEFAULT_SESSION_DAYS = 7


def session_ttl() -> timedelta:
    raw = os.getenv("SESSION_TTL_DAYS", str(DEFAULT_SESSION_DAYS))
    try:
        days = int(raw)
    except ValueError:
        days = DEFAULT_SESSION_DAYS
    return timedelta(days=days if days > 0 else DEFAULT_SESSION_DAYS)


def cookie_secure() -> bool:
    """Cookies are Secure everywhere except local development."""
    return os.getenv("APP_ENV", "development").strip().lower() != "development"
