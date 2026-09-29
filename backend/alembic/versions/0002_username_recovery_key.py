"""username instead of email, recovery key

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-29
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=20), nullable=True))
    op.add_column("users", sa.Column("username_key", sa.String(length=20), nullable=True))
    op.add_column("users", sa.Column("recovery_key_hash", sa.String(length=255), nullable=True))
    # Accounts from before this change get a placeholder name and no recovery key.
    op.execute("UPDATE users SET username = 'user' || id, username_key = 'user' || id")
    op.alter_column("users", "username", nullable=False)
    op.alter_column("users", "username_key", nullable=False)
    op.create_unique_constraint(op.f("uq_users_username_key"), "users", ["username_key"])
    op.drop_constraint(op.f("uq_users_email"), "users", type_="unique")
    op.drop_column("users", "email")


def downgrade() -> None:
    op.add_column("users", sa.Column("email", sa.String(length=254), nullable=True))
    op.execute("UPDATE users SET email = username_key || '@invalid'")
    op.alter_column("users", "email", nullable=False)
    op.create_unique_constraint(op.f("uq_users_email"), "users", ["email"])
    op.drop_constraint(op.f("uq_users_username_key"), "users", type_="unique")
    op.drop_column("users", "recovery_key_hash")
    op.drop_column("users", "username_key")
    op.drop_column("users", "username")
