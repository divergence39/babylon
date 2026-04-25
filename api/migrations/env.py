"""Alembic environment configuration for online and offline migrations."""

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio.engine import async_engine_from_config

from babylon.infrastructure.database.models import Base


class MissingDatabaseUrlError(ValueError):
    """Raised when DATABASE_URL is not configured in the environment."""

    def __init__(self) -> None:
        super().__init__("DATABASE_URL environment variable is missing.")


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Read DATABASE_URL dynamically from the environment.
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    raise MissingDatabaseUrlError

# Inject the runtime URL into Alembic configuration.
config.set_main_option("sqlalchemy.url", db_url)

# Load aggregate metadata for autogeneration.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode using URL-only configuration."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations using a live SQLAlchemy connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and execute migrations with a live connection."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
