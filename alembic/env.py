from logging.config import fileConfig

from alembic import context
from sqlalchemy import (
    Column,
    MetaData,
    String,
    Table,
    engine_from_config,
    inspect,
    pool,
)

from src.config import get_settings
from src.database import Base
import src.models  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", get_settings().database_url.replace("%", "%%"))


def ensure_version_table_capacity(connection) -> None:
    """Keep Alembic's version column wide enough for published revision IDs."""
    version_table = Table(
        "alembic_version",
        MetaData(),
        Column("version_num", String(length=64), primary_key=True, nullable=False),
    )
    version_table.create(connection, checkfirst=True)

    # Older Alembic-created PostgreSQL tables use VARCHAR(32). The published
    # revision 0002_drop_redundant_task_id_index is longer than that limit.
    if connection.dialect.name == "postgresql":
        version_column = next(
            column
            for column in inspect(connection).get_columns("alembic_version")
            if column["name"] == "version_num"
        )
        current_length = getattr(version_column["type"], "length", None)
        if current_length is not None and current_length < 64:
            connection.exec_driver_sql(
                "ALTER TABLE alembic_version "
                "ALTER COLUMN version_num TYPE VARCHAR(64)"
            )


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        ensure_version_table_capacity(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
