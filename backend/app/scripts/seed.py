"""Create one fake user per role (is_synthetic = true).

Run from the repo root:
    SEED_PASSWORD='choose-a-long-password' PYTHONPATH=backend \
        uv run python -m app.scripts.seed

The password comes from the environment, never from code. Safe to run twice.
"""

import os
import sys

from sqlalchemy.orm import Session

from app.core import database
from app.modules.auth.roles import Role
from app.modules.auth.service import get_user_by_email, register_user

DEMO_DOMAIN = "demo.example"


def seed_users(db: Session, password: str) -> int:
    """Create missing demo users. Returns how many were created."""
    created = 0
    for role in Role:
        email = f"{role.value.replace('_', '-')}@{DEMO_DOMAIN}"
        if get_user_by_email(db, email) is not None:
            continue
        register_user(
            db,
            email=email,
            password=password,
            full_name=f"Demo {role.value.replace('_', ' ').title()}",
            role=role.value,
            is_synthetic=True,
        )
        created += 1
    return created


def main() -> None:
    password = os.getenv("SEED_PASSWORD", "")
    if len(password) < 8:
        sys.exit("Set SEED_PASSWORD (at least 8 characters) before seeding.")
    if database.engine is None:
        sys.exit("DATABASE_URL is not set.")
    with Session(database.engine) as db:
        created = seed_users(db, password)
    print(f"Seeded {created} synthetic user(s).")


if __name__ == "__main__":
    main()
