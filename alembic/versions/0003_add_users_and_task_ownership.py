"""Add users and task ownership.

Revision ID: 0003_users_task_owner
Revises: 0002_drop_redundant_task_id_index
Create Date: 2026-11-05
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_users_task_owner"
down_revision = "0002_drop_redundant_task_id_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # Preserve pre-existing tasks under a disabled legacy account. Its
    # unguessable placeholder hash means it cannot authenticate.
    op.execute(
        "INSERT INTO users (id, email, password_hash, created_at) "
        "VALUES (1, 'legacy-migration@invalid.local', "
        "'!account-disabled-by-migration!', CURRENT_TIMESTAMP)"
    )
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
    op.execute("UPDATE tasks SET user_id = 1 WHERE user_id IS NULL")
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.alter_column("user_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            "fk_tasks_user_id_users", "users", ["user_id"], ["id"], ondelete="CASCADE"
        )
        batch_op.create_index("ix_tasks_user_id", ["user_id"])


def downgrade() -> None:
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.drop_index("ix_tasks_user_id")
        batch_op.drop_constraint("fk_tasks_user_id_users", type_="foreignkey")
        batch_op.drop_column("user_id")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
