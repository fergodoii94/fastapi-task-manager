"""Exercise the legacy-data ownership migration against a real PostgreSQL database."""

from datetime import datetime, timezone
import os

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text


def main() -> None:
    database_url = os.environ["DATABASE_URL"]
    config = Config("alembic.ini")

    # Build the exact pre-ownership schema, then seed a task as an existing
    # installation would have it before revision 0003.
    command.upgrade(config, "0002_drop_task_idx")

    engine = create_engine(database_url)
    now = datetime.now(timezone.utc)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO tasks
                    (title, description, status, priority, created_at, updated_at)
                VALUES
                    (:title, :description, :status, :priority, :created_at, :updated_at)
                """
            ),
            {
                "title": "Legacy task",
                "description": "Created before user ownership existed",
                "status": "pending",
                "priority": 3,
                "created_at": now,
                "updated_at": now,
            },
        )

    # Apply the ownership migration, then simulate the stale SERIAL sequence
    # left by the earlier release that inserted the legacy user with id=1.
    command.upgrade(config, "0003_users_task_owner")
    with engine.begin() as connection:
        connection.execute(
            text(
                "SELECT setval("
                "pg_get_serial_sequence('users', 'id'), "
                "COALESCE((SELECT MAX(id) FROM users), 1), false)"
            )
        )

    # The next migration must repair the sequence and disable the legacy user.
    command.upgrade(config, "head")
    with engine.begin() as connection:
        legacy_user = connection.execute(
            text("SELECT id, is_active FROM users WHERE email = :email"),
            {"email": "legacy-migration@example.com"},
        ).one()
        legacy_user_id = legacy_user.id
        assert legacy_user.is_active is False, "Legacy migration account must be inactive"
        task_owner_id = connection.execute(
            text("SELECT user_id FROM tasks WHERE title = :title"),
            {"title": "Legacy task"},
        ).scalar_one()

        assert task_owner_id == legacy_user_id, (
            f"Legacy task owner {task_owner_id} does not match "
            f"legacy user {legacy_user_id}"
        )

        # A normal insert must receive a fresh ID from PostgreSQL's sequence.
        new_user_id = connection.execute(
            text(
                """
                INSERT INTO users (email, password_hash, created_at)
                VALUES (:email, :password_hash, :created_at)
                RETURNING id
                """
            ),
            {
                "email": "sequence-check@example.com",
                "password_hash": "integration-test-hash",
                "created_at": now,
            },
        ).scalar_one()

        assert new_user_id != legacy_user_id, (
            "The next generated user ID collided with the legacy user ID"
        )
        assert new_user_id > legacy_user_id, (
            f"Expected generated ID > {legacy_user_id}, got {new_user_id}"
        )

    engine.dispose()
    print(
        "PostgreSQL migration verified: legacy task backfilled and "
        f"next user ID generated safely ({legacy_user_id} -> {new_user_id})."
    )


if __name__ == "__main__":
    main()
