"""Integration test fixtures for database connectivity."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine
from testcontainers.postgres import PostgresContainer

_TEST_DB_USER = os.getenv("TEST_DB_USER", "zk_admin")
_TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "local_development_password")
_TEST_DB_NAME = os.getenv("TEST_DB_NAME", "zk_vault_test")


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


@pytest_asyncio.fixture
async def engine(test_database_url: str) -> AsyncGenerator[AsyncEngine]:
    """Create an async SQLAlchemy engine for integration tests."""
    test_engine = create_async_engine(
        test_database_url,
        poolclass=NullPool,
        echo=False,
    )
    try:
        yield test_engine
    finally:
        await test_engine.dispose()


@pytest_asyncio.fixture
async def db_connection(
    engine: AsyncEngine,
) -> AsyncGenerator[AsyncConnection]:
    """Provide a transactional connection for each test."""
    async with engine.connect() as connection:
        transaction = await connection.begin()
        try:
            yield connection
        finally:
            await transaction.rollback()
