"""Application-level exception hierarchy for infrastructure failures."""

from babylon.shared.application.exceptions import (
    ResourceNotFoundError,
)


class UserNotFoundError(ResourceNotFoundError):
    """Raised when attempting to operate on a user ID that does not exist."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User with ID '{user_id}' not found.")
