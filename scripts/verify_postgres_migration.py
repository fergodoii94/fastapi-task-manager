"""Verify ownership migration compatibility and PostgreSQL sequence recovery.

This script destructively resets the public schema. It refuses to run unless
DATABASE_URL points to the explicitly named disposable test database.
"""

from datetime import datetime, timezone
import os

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

BASE_REVISION = "0002_drop_redundant_task_id_index"
LEGACY_SENTINEL = "!account-disabled-by-migration!"
EXPECTED_DATABASE = os.getenv("POSTGRES_TEST_DATABASE_NAME", "task_manager_test")


def reset_schema(engine) -> None:
    with engine.begin() as connection:
        actual_database = connection.execute(text("SELECT current_database()")).scalar_one()
        if actual_database != EXPECTED_DATABASE:
            raise RuntimeError(
                f"Refusing to reset schema in {actual_database!r}; "
                f"expected disposable database {EXPECTED_DATABASE!r}"
            )
        connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        connection.execute(text("CREATE SCHEMA public AUTHORIZATION CURRENT_USER"))


def create_pre_ownership_database(config: Config, engine) -> datetime:
    reset_schema(engine)
    command.upgrade(config, BASE_REVISION)

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

    # Apply the exact, already-published ownership revision. It inserts the
    # legacy account with ID 1 without advancing PostgreSQL's SERIAL sequence.
    command.upgrade(config, "0003_users_task_owner")
    return now


def insert_user(connection, email: str, now: datetime) -> int:
    return connection.execute(
        text(
            """
            INSERT INTO users (email, password_hash, created_at)
            VALUES (:email, :password_hash, :created_at)
            RETURNING id
            """
        ),
        {
            "email": email,
            "password_hash": "integration-test-hash",
            "created_at": now,
        },
    ).scalar_one()


def verify_stale_sequence_and_email_collision(config: Config, engine) -> None:
    now = create_pre_ownership_database(config, engine)

    with engine.begin() as connection:
        # Allocate ID 2 to a legitimate account using the candidate address
        # that a previous migration attempted to assign to the legacy user.
        connection.execute(
            text("SELECT setval(pg_get_serial_sequence('users', 'id'), 1, TRUE)")
        )
        real_user_id = insert_user(connection, "legacy-migration@example.com", now)
        assert real_user_id == 2

        # Reproduce the stale sequence from the published explicit-ID migration.
        connection.execute(
            text("SELECT setval(pg_get_serial_sequence('users', 'id'), 1, FALSE)")
        )

    command.upgrade(config, "head")

    with engine.begin() as connection:
        legacy_user = connection.execute(
            text(
                "SELECT id, is_active FROM users "
                "WHERE password_hash = :sentinel"
            ),
            {"sentinel": LEGACY_SENTINEL},
        ).one()
        assert legacy_user.id == 1
        assert legacy_user.is_active is False

        existing_user = connection.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": "legacy-migration@example.com"},
        ).scalar_one()
        assert existing_user == real_user_id, "Migration must not rename over a real account"

        task_owner_id = connection.execute(
            text("SELECT user_id FROM tasks WHERE title = 'Legacy task'")
        ).scalar_one()
        assert task_owner_id == legacy_user.id

        next_user_id = insert_user(connection, "sequence-check@example.com", now)
        assert next_user_id > real_user_id, (
            f"Expected sequence to advance beyond {real_user_id}, got {next_user_id}"
        )

    print(
        "PostgreSQL stale-sequence scenario passed: legacy account disabled, "
        "existing email preserved, and generated ID advanced safely."
    )


def verify_sequence_is_never_rewound(config: Config, engine) -> None:
    now = create_pre_ownership_database(config, engine)

    with engine.begin() as connection:
        connection.execute(
            text("SELECT setval(pg_get_serial_sequence('users', 'id'), 50, TRUE)")
        )

    command.upgrade(config, "head")

    with engine.begin() as connection:
        next_user_id = insert_user(connection, "ahead-sequence-check@example.com", now)
        assert next_user_id == 51, (
            f"Expected sequence value 50 to be preserved, got {next_user_id}"
        )

    print("PostgreSQL sequence-ahead scenario passed: migration did not rewind the sequence.")


def main() -> None:
    database_url = os.environ["DATABASE_URL"]
    config = Config("alembic.ini")
    engine = create_engine(database_url)

    try:
        verify_stale_sequence_and_email_collision(config, engine)
        verify_sequence_is_never_rewound(config, engine)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
