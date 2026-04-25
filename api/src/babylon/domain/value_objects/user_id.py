"""User identity value object constrained to UUIDv7 values."""

from dataclasses import dataclass
from typing import Final
from uuid import UUID

from babylon.domain.exceptions import UserIdValidationError

_REQUIRED_UUID_VERSION: Final[int] = 7


@dataclass(frozen=True)
class UserId:
    """Represents the immutable identity of a user entity.

    Attributes:
        value (UUID): The underlying UUID instance.
    """

    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise UserIdValidationError(reason="must be a UUID instance.")

        if self.value.version != _REQUIRED_UUID_VERSION:
            raise UserIdValidationError(
                reason=f"must be a UUIDv{_REQUIRED_UUID_VERSION} value.",
            )
