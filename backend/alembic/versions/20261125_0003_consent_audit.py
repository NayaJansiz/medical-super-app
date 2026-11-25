"""Create patient_profiles, consents and audit_logs tables.

Revision ID: 20261125_0003
Revises: 20261125_0002
Create Date: 2026-11-25
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261125_0003"
down_revision: str | None = "20261125_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCOPES = ("records:read", "records:write")


def _timestamps() -> list[sa.Column[sa.DateTime]]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "patient_profiles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("allergies", sa.Text(), nullable=True),
        sa.Column("surgeries", sa.Text(), nullable=True),
        sa.Column("medical_history", sa.Text(), nullable=True),
        sa.Column("medication_history", sa.Text(), nullable=True),
        sa.Column(
            "is_synthetic", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        *_timestamps(),
    )
    op.create_index(
        "ix_patient_profiles_user_id", "patient_profiles", ["user_id"], unique=True
    )

    op.create_table(
        "consents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "patient_id",
            sa.Uuid(),
            sa.ForeignKey("patient_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "grantee_user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("scope", sa.String(32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "is_synthetic", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        *_timestamps(),
        sa.CheckConstraint(
            "scope IN ({})".format(", ".join(f"'{s}'" for s in SCOPES)),
            name="ck_consents_scope",
        ),
    )
    op.create_index("ix_consents_patient_id", "consents", ["patient_id"])
    op.create_index("ix_consents_grantee_user_id", "consents", ["grantee_user_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=False),
        sa.Column("resource_id", sa.Uuid(), nullable=True),
        sa.Column("patient_id", sa.Uuid(), nullable=True),
        sa.Column("outcome", sa.String(16), nullable=False),
        sa.Column("detail", sa.String(200), nullable=True),
        sa.Column(
            "at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_logs_patient_id", "audit_logs", ["patient_id"])
    op.create_index("ix_audit_logs_at", "audit_logs", ["at"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_patient_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_consents_grantee_user_id", table_name="consents")
    op.drop_index("ix_consents_patient_id", table_name="consents")
    op.drop_table("consents")
    op.drop_index("ix_patient_profiles_user_id", table_name="patient_profiles")
    op.drop_table("patient_profiles")
