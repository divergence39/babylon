import os
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from tests.integration.factories import UserFactory

_TEST_DB_USER = os.getenv("TEST_DB_USER", "zk_admin")
_TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "local_development_password")
_TEST_DB_NAME = os.getenv("TEST_DB_NAME", "zk_vault_test")
ALEMBIC_INI_PATH = Path(__file__).resolve().parents[2] / "alembic.ini"
MIGRATIONS_PATH = Path(__file__).resolve().parents[2] / "migrations"


@pytest.fixture(scope="session")
def alembic_config() -> Config:
    """Provide a preconfigured Alembic Config for test migrations."""
    config = Config(str(ALEMBIC_INI_PATH))
    config.set_main_option("script_location", str(MIGRATIONS_PATH))
    return config


@pytest.fixture(scope="session")
def test_database_url() -> Generator[str]:
    """Provide a session-scoped Postgres test database URL."""
    with (
        PostgresContainer(
            image="postgres:18-alpine",
            username=_TEST_DB_USER,
            password=_TEST_DB_PASSWORD,
            dbname=_TEST_DB_NAME,
            driver="asyncpg",
        )
        .with_env("PGDATA", "/var/lib/postgresql/data/pgdata")
        .with_kwargs(tmpfs={"/var/lib/postgresql/data": "rw"}) as postgres
    ):
        yield postgres.get_connection_url(driver="asyncpg")


@pytest.fixture(scope="session", autouse=True, name="_apply_migrations")
def apply_migrations(
    alembic_config: Config,
    test_database_url: str,
) -> Generator[None]:
    """Apply and rollback migrations for the test database."""
    alembic_config.set_main_option("sqlalchemy.url", test_database_url)

    command.upgrade(alembic_config, "head")
    yield
    command.downgrade(alembic_config, "base")


@pytest.fixture(scope="session")
async def engine(
    test_database_url: str,
) -> AsyncGenerator[AsyncEngine]:
    """Creates a session-wide AsyncEngine using NullPool for pure isolation."""
    test_engine = create_async_engine(
        test_database_url,
        poolclass=NullPool,
        echo=False,
    )

    yield test_engine

    # Explicitly dispose to prevent connection hanging
    await test_engine.dispose()


@pytest.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    """Establishes a completely isolated SAVEPOINT (nested transaction) per test."""
    connection = await engine.connect()
    trans = await connection.begin()

    async_session = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    session = async_session()

    yield session

    await session.close()
    await trans.rollback()
    await connection.close()


@pytest.fixture
def user_factory() -> type[UserFactory]:
    """Expose the UserFactory for integration tests."""
    return UserFactory
