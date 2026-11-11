"""Add an explicit active flag for user accounts.

Revision ID: 0004_user_is_active
Revises: 0003_users_task_owner
Create Date: 2026-11-11
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_user_is_active"
down_revision = "0003_users_task_owner"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
    )
    op.execute(
        "UPDATE users SET is_active = FALSE "
        "WHERE email = 'legacy-migration@invalid.local'"
    )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("is_active")
