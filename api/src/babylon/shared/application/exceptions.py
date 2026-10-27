"""Base class for all application exceptions."""


class ApplicationError(Exception):
    """Base class for application-layer exceptions."""

    pass


class ResourceNotFoundError(ApplicationError):
    """Raised when a requested resource is not found."""

    pass


class ConflictError(ApplicationError):
    """Raised when a conflict occurs."""

    pass


class ConcurrencyError(ConflictError):
    """Raised when a concurrency conflict occurs."""

    pass
