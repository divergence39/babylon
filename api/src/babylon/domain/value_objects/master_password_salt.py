"""Master-password salt value object with minimum entropy-related constraints."""

import re
from dataclasses import dataclass
from typing import Final

from babylon.domain.exceptions import MasterPasswordSaltValidationError

_MIN_SALT_LENGTH: Final[int] = 32
_BASE64_PATTERN = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")


@dataclass(frozen=True)
class MasterPasswordSalt:
    """Represents the persisted salt associated with master-password derivation.

    Attributes:
        value (str): The salt string value.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise MasterPasswordSaltValidationError(reason="must be a string.")

        if len(self.value) < _MIN_SALT_LENGTH:
            raise MasterPasswordSaltValidationError(
                reason=f"must have at least {_MIN_SALT_LENGTH} characters.",
            )

        if not _BASE64_PATTERN.fullmatch(self.value):
            raise MasterPasswordSaltValidationError(
                reason="must be a valid Base64 encoded string.",
            )
