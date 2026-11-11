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
    # Normalize the placeholder address to a syntactically valid reserved example domain.
    op.execute(
        "UPDATE users SET email = 'legacy-migration@example.com', is_active = FALSE "
        "WHERE email = 'legacy-migration@invalid.local'"
    )

    # Earlier releases inserted the legacy user with an explicit ID. PostgreSQL
    # does not advance the SERIAL sequence for explicit IDs, so repair it before
    # the first real registration can collide with that row.
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            "SELECT setval("
            "pg_get_serial_sequence('users', 'id'), "
            "COALESCE((SELECT MAX(id) FROM users), 1), true)"
        )


def downgrade() -> None:
    op.execute(
        "UPDATE users SET email = 'legacy-migration@invalid.local' "
        "WHERE email = 'legacy-migration@example.com'"
    )
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("is_active")
