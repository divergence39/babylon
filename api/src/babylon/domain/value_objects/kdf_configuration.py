"""KDF parameter value object constrained to secure Argon2id settings."""

from dataclasses import dataclass
from typing import Final

from babylon.domain.exceptions import KdfConfigurationValidationError

_MIN_MEMORY_KB: Final[int] = 65_536
_MAX_MEMORY_KB: Final[int] = 2_097_152
_MIN_ITERATIONS: Final[int] = 3
_MAX_ITERATIONS: Final[int] = 1_000
_MIN_PARALLELISM: Final[int] = 1
_MAX_PARALLELISM: Final[int] = 16
_SUPPORTED_ALGO: Final[str] = "argon2id"


@dataclass(frozen=True)
class KdfConfiguration:
    """Safe Argon2id work-factor configuration for password derivation.

    Attributes:
        algorithm (str): The hashing algorithm name. Must be ``argon2id``.
        memory_kb (int): The memory cost parameter in kibibytes.
        iterations (int): The time cost parameter as iteration count.
        parallelism (int): The degree of parallelism used by the KDF.
    """

    algorithm: str
    memory_kb: int
    iterations: int
    parallelism: int

    def __post_init__(self) -> None:
        if self.algorithm != _SUPPORTED_ALGO:
            raise KdfConfigurationValidationError(
                reason=f"Only '{_SUPPORTED_ALGO}' is supported.",
            )

        if not (_MIN_MEMORY_KB <= self.memory_kb <= _MAX_MEMORY_KB):
            raise KdfConfigurationValidationError(
                reason=f"KDF memory must be between "
                f"{_MIN_MEMORY_KB} and {_MAX_MEMORY_KB} KiB.",
            )

        if not (_MIN_ITERATIONS <= self.iterations <= _MAX_ITERATIONS):
            raise KdfConfigurationValidationError(
                reason=f"KDF iterations must be between "
                f"{_MIN_ITERATIONS} and {_MAX_ITERATIONS}.",
            )

        if not (_MIN_PARALLELISM <= self.parallelism <= _MAX_PARALLELISM):
            raise KdfConfigurationValidationError(
                reason=f"KDF parallelism must be between "
                f"{_MIN_PARALLELISM} and {_MAX_PARALLELISM}.",
            )
