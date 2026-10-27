"""Domain-level exception hierarchy for business-rule validation failures."""

from babylon.shared.domain.exceptions import DomainValidationError


class InvalidCredentialsError(DomainValidationError):
    """Raised when authentication fails due to incorrect username or password."""

    def __init__(self) -> None:
        super().__init__("User", "Invalid username or password.")


class UserValidationError(DomainValidationError):
    """Raised when a User entity is given an invalid value."""

    def __init__(self, reason: str) -> None:
        super().__init__("User", reason)


class UserIdValidationError(DomainValidationError):
    """Raised when a UserId value object is given an invalid value."""

    def __init__(self, reason: str) -> None:
        super().__init__("UserId", reason)


class UsernameValidationError(DomainValidationError):
    """Raised when a Username value object is given an invalid value."""

    def __init__(self, reason: str) -> None:
        super().__init__("Username", reason)


class MasterPasswordSaltValidationError(DomainValidationError):
    """Raised when a MasterPasswordSalt value object is given an invalid value."""

    def __init__(self, reason: str) -> None:
        super().__init__("MasterPasswordSalt", reason)


class ServerAuthHashValidationError(DomainValidationError):
    """Raised when a ServerAuthHash value object is given an invalid value."""

    def __init__(self, reason: str) -> None:
        super().__init__("ServerAuthHash", reason)


class KdfConfigurationValidationError(DomainValidationError):
    """Raised when a KdfConfiguration value object is given an invalid value."""

    def __init__(self, reason: str) -> None:
        super().__init__("KdfConfiguration", reason)


class AggregateVersionValidationError(DomainValidationError):
    """Raised when an AggregateVersion value object is given an invalid value."""

    def __init__(self, reason: str) -> None:
        super().__init__("AggregateVersion", reason)
