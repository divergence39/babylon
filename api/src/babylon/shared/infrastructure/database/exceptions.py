"""Database-related exceptions for the Babylon backend."""


class DatabaseError(Exception):
    """Base class for database-related exceptions."""

    pass


class DatabaseUnavailableError(DatabaseError):
    """Raised when the database is unreachable or unavailable."""

    def __init__(self, message: str = "Database is unavailable.") -> None:
        super().__init__(message)
