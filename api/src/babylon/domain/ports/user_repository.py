"""User repository port definitions."""

from abc import ABC, abstractmethod

from babylon.domain.entities import User
from babylon.domain.value_objects import UserId, UsernameHash


class UserRepository(ABC):
    """Mapping between the domain User aggregate root and persistent storage."""

    @abstractmethod
    async def save(self, user: User) -> None:
        """Persist a new or modified user entity.

        Args:
            user (User): The user entity to persist.
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
