"""Token value object representing a generated authentication session token."""

from dataclasses import dataclass

from babylon.domain.exceptions import TokenValidationError


@dataclass(frozen=True)
class Token:
    """Represents an authentication session token.

    Attributes:
        value (str): The raw string token value.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TokenValidationError(reason="must be a string.")

        normalized = self.value.strip()
        if not normalized:
            raise TokenValidationError(reason="cannot be empty or whitespace.")

        object.__setattr__(self, "value", normalized)
