"""Application-level exception hierarchy for infrastructure failures."""


class ApplicationError(Exception):
    """Base class for application-layer exceptions."""

    pass


class UsernameAlreadyExistsError(ApplicationError):
    """Raised when attempting to register a username that is already taken."""

    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(f"User with username '{username}' already exists.")


class InvalidCredentialsError(ApplicationError):
    """Raised when authentication fails due to incorrect username or password."""

    def __init__(self) -> None:
        super().__init__("Invalid username or password.")


class UserNotFoundError(ApplicationError):
    """Raised when attempting to operate on a user ID that does not exist."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User with ID '{user_id}' not found.")
