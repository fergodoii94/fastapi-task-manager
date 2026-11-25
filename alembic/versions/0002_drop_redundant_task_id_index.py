"""Drop the redundant index on the tasks primary key.

Revision ID: 0002_drop_redundant_task_id_index
Revises: 0001_create_tasks
Create Date: 2026-11-04
"""

from alembic import op

revision = "0002_drop_redundant_task_id_index"
down_revision = "0001_create_tasks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_tasks_id", table_name="tasks")


def downgrade() -> None:
    op.create_index("ix_tasks_id", "tasks", ["id"], unique=False)
