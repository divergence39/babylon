"""User repository port definitions."""

from abc import ABC, abstractmethod

from babylon.auth.domain.entities import User
from babylon.auth.domain.value_objects import UserId, UsernameHash
from babylon.shared.domain.exceptions import DomainError


class UserRepositoryError(DomainError):
    """Base class for user repository errors."""

    pass


class UserAlreadyExistsError(UserRepositoryError):
    """Raised when attempting to register a user with an already taken username."""

    def __init__(self, username_hash: str) -> None:
        super().__init__(f"User with username {username_hash} already exists.")


class UserConcurrencyError(UserRepositoryError):
    """Raised when a user update conflicts with a concurrent write."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User '{user_id}' was updated concurrently.")


class IUserRepository(ABC):
    """Mapping between the domain User aggregate root and persistent storage."""

    @abstractmethod
    async def add(self, user: User) -> None:
        """Add a new user entity to the repository.

        Args:
            user (User): The user entity to add.
        """
        pass

    @abstractmethod
    async def update(self, user: User) -> None:
        """Update an existing user entity in the repository.

        Args:
            user (User): The user entity to update.
        """
        pass

    @abstractmethod
    async def find_by_id(self, id: UserId) -> User | None:
        """Find a single user by their unique identity.

        Args:
            id (UserId): The unique identifier.

        Returns:
            User | None: The user entity if found, None otherwise.
        """
        pass

    @abstractmethod
    async def find_by_username_hash(self, username_hash: UsernameHash) -> User | None:
        """Find a single user by their canonical username hash..

        Args:
            username_hash (UsernameHash): The canonical username hash to search by.

        Returns:
            User | None: The user entity if found, None otherwise.
        """
        pass
