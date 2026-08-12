"""Username value object with normalization and allowed-character constraints."""

from dataclasses import dataclass
from typing import Final

from babylon.domain.exceptions import UsernameValidationError

_HASHED_USERNAME_LENGTH: Final[int] = 44  # Length of a SHA-256 hash in base64 encoding


@dataclass(frozen=True)
class UsernameHash:
    """Represents a hashed username identifier.

    Attributes:
        value (str): The hashed username value.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise UsernameValidationError(reason="must be a string.")

        if len(self.value) != _HASHED_USERNAME_LENGTH:
            raise UsernameValidationError(
                reason=f"must be a valid hashed username of exactly"
                f" {_HASHED_USERNAME_LENGTH} characters."
            )
