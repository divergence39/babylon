"""Aggregate version value object enforcing optimistic concurrency sequencing."""

from dataclasses import dataclass
from typing import Final

from babylon.domain.exceptions import AggregateVersionValidationError

_MIN_VERSION: Final[int] = 1


@dataclass(frozen=True)
class AggregateVersion:
    """Represents the optimistic concurrency version for an aggregate.

    Attributes:
        value (int): The aggregate version number (must be > 0).
    """

    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int):
            raise AggregateVersionValidationError(reason="must be an integer.")

        if self.value < _MIN_VERSION:
            raise AggregateVersionValidationError(
                reason="must be greater than zero.",
            )

    def next_version(self) -> AggregateVersion:
        """Return the next sequential aggregate version."""
        return AggregateVersion(self.value + 1)
