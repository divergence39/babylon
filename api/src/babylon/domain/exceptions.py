"""Domain-level exception hierarchy for business-rule validation failures."""


class DomainError(Exception):
    """Base class for all domain exceptions."""

    pass


class DomainValidationError(DomainError):
    """Raised when a value object violates a business rule."""

    def __init__(self, entity: str, reason: str) -> None:
        self.entity = entity
        self.reason = reason
        self.message = f"Validation failed for {entity}: {reason}"
        super().__init__(self.message)


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


class TokenValidationError(DomainValidationError):
    """Raised when a Token value object is given an invalid value."""

    def __init__(self, reason: str) -> None:
        super().__init__("Token", reason)
