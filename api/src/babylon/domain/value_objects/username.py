"""Username value object with normalization and allowed-character constraints."""

import re
from dataclasses import dataclass
from typing import Final

from babylon.domain.exceptions import UsernameValidationError

_MIN_USERNAME_LEN: Final[int] = 3
_MAX_USERNAME_LEN: Final[int] = 32
_USERNAME_PATTERN = re.compile(r"^[a-z0-9._-]+$")


@dataclass(frozen=True)
class Username:
    """Represents a canonical, case-normalized username identifier.

    Attributes:
        value (str): The canonicalized username value.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise UsernameValidationError(reason="must be a string.")

        normalized = self.value.strip().lower()
        if (
            not _USERNAME_PATTERN.fullmatch(normalized)
            or len(normalized) < _MIN_USERNAME_LEN
            or len(normalized) > _MAX_USERNAME_LEN
        ):
            raise UsernameValidationError(
                reason=f"must be a valid username containing only "
                f"alphanumeric characters, dots, underscores, or hyphens "
                f"between {_MIN_USERNAME_LEN} and {_MAX_USERNAME_LEN} characters.",
            )

        object.__setattr__(self, "value", normalized)
