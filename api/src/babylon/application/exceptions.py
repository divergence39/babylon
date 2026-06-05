"""Application-level exception hierarchy for infrastructure failures."""


class ApplicationError(Exception):
    """Base class for application-layer exceptions."""


class DatabaseUnavailableError(ApplicationError):
    """Raised when the database is unreachable or unavailable."""

    def __init__(self, message: str = "Database is unavailable.") -> None:
        super().__init__(message)
