"""Integration tests validating database connectivity."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from .factories import ConnectionProbeFactory


@pytest.mark.asyncio
async def test_database_round_trip(db_connection: AsyncConnection) -> None:
    """Confirm the test database accepts round-trip writes and reads."""
    probe = ConnectionProbeFactory.build()

    await db_connection.execute(
        text(
            "CREATE TEMP TABLE connection_probe ("
            "key TEXT PRIMARY KEY, "
            "payload TEXT NOT NULL"
            ")"
        )
    )
    await db_connection.execute(
        text("INSERT INTO connection_probe (key, payload) VALUES (:key, :payload)"),
        {"key": probe.key, "payload": probe.payload},
    )

    result = await db_connection.execute(
        text("SELECT key, payload FROM connection_probe WHERE key = :key"),
        {"key": probe.key},
    )
    row = result.one()

    assert row._mapping["key"] == probe.key
    assert row._mapping["payload"] == probe.payload
