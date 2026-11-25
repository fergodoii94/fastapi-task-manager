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

LEGACY_PASSWORD_SENTINEL = "!account-disabled-by-migration!"


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
    )

    # Identify only the account created by revision 0003. Do not rename its
    # email: a real user may already own any syntactically valid candidate.
    op.execute(
        sa.text(
            "UPDATE users SET is_active = FALSE WHERE password_hash = :sentinel"
        ).bindparams(sentinel=LEGACY_PASSWORD_SENTINEL)
    )

    # Revision 0003 was already published with an explicit legacy user ID.
    # Advance a stale PostgreSQL sequence to MAX(id), but never move a sequence
    # backwards if operators have already allocated IDs beyond the current rows.
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            """
            DO $$
            DECLARE
                user_id_sequence regclass;
                sequence_value bigint;
                max_user_id bigint;
            BEGIN
                user_id_sequence := pg_get_serial_sequence('users', 'id')::regclass;
                sequence_value := pg_sequence_last_value(user_id_sequence);
                SELECT COALESCE(MAX(id), 1) INTO max_user_id FROM users;

                PERFORM setval(
                    user_id_sequence,
                    GREATEST(COALESCE(sequence_value, 1), max_user_id),
                    TRUE
                );
            END
            $$;
            """
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("is_active")
