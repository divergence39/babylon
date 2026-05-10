"""Polyfactory-backed factories for integration tests."""

from dataclasses import dataclass

from polyfactory.factories import DataclassFactory

_DEFAULT_KEY = "probe-key"
_DEFAULT_PAYLOAD = "probe-payload"


@dataclass(frozen=True)
class ConnectionProbe:
    """Payload used to validate database round-trip operations."""

    key: str
    payload: str


class ConnectionProbeFactory(DataclassFactory[ConnectionProbe]):
    """Build deterministic connection probe payloads."""

    __model__ = ConnectionProbe

    key = _DEFAULT_KEY
    payload = _DEFAULT_PAYLOAD
