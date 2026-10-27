"""Unit of Work port definition."""

import types
from abc import ABC, abstractmethod
from typing import Self

from babylon.auth.domain.ports.user_repository import IUserRepository


class IUnitOfWork(ABC):
    """Abstract port defining the Unsit of Work for transactional boundaries."""

    @property
    @abstractmethod
    def users(self) -> IUserRepository:
        """Access the user repository within the Unit of Work context."""
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> Self:
        """Enter the Unit of Work context."""
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Exits the Unit of Work context, committing or rolling back as necessary."""
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        """Commits the active transaction."""
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Rolls back the active transaction."""
        raise NotImplementedError
