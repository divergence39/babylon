"""Server-side authentication hash value object encoded as Argon2id PHC."""

import re
from dataclasses import dataclass
from typing import Final

from babylon.domain.exceptions import ServerAuthHashValidationError

_ARGON2ID_PATTERN = re.compile(
    r"^\$argon2id\$v=19\$m=(?P<m>\d+),t=(?P<t>\d+),p=(?P<p>\d+)\$[A-Za-z0-9+/=_-]+\$[A-Za-z0-9+/=_-]+$"
)

# DoS Protection Bounds
_MIN_MEMORY_COST: Final[int] = 16_384
_MAX_MEMORY_COST: Final[int] = 262_144
_MIN_TIME_COST: Final[int] = 1
_MAX_TIME_COST: Final[int] = 10
_MIN_PARALLELISM_COST: Final[int] = 1
_MAX_PARALLELISM_COST: Final[int] = 16


@dataclass(frozen=True)
class ServerAuthHash:
    """Represents an Argon2id PHC hash used for server-side authentication.

    Attributes:
        value (str): The complete Argon2id PHC hash string.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise ServerAuthHashValidationError(reason="must be a string.")

        match = _ARGON2ID_PATTERN.fullmatch(self.value)
        if not match:
            raise ServerAuthHashValidationError(
                reason="must be a valid Argon2id v19 PHC string."
            )

        memory_cost = int(match.group("m"))
        time_cost = int(match.group("t"))
        parallelism = int(match.group("p"))

        if not (_MIN_MEMORY_COST <= memory_cost <= _MAX_MEMORY_COST):
            raise ServerAuthHashValidationError(
                reason=f"memory cost must be between "
                f"{_MIN_MEMORY_COST} and {_MAX_MEMORY_COST}.",
            )

        if not (_MIN_TIME_COST <= time_cost <= _MAX_TIME_COST):
            raise ServerAuthHashValidationError(
                reason=f"time cost must be between "
                f"{_MIN_TIME_COST} and {_MAX_TIME_COST}.",
            )

        if not (_MIN_PARALLELISM_COST <= parallelism <= _MAX_PARALLELISM_COST):
            raise ServerAuthHashValidationError(
                reason=f"parallelism cost must be between "
                f"{_MIN_PARALLELISM_COST} and {_MAX_PARALLELISM_COST}.",
            )
