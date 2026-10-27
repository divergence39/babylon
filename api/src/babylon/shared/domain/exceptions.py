"""Base class for all shared domain exceptions."""


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
