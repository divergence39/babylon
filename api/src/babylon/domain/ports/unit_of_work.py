"""Unit of Work port definition."""

import types
from abc import ABC, abstractmethod
from typing import Self

from babylon.domain.ports.user_repository import UserRepository


class UnitOfWork(ABC):
    """Abstract port defining the Unit of Work for transactional boundaries."""

    users: UserRepository

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        if exc_type:
            await self.rollback()
        # TODO: Revisit auto-commit vs explicit-commit; keeping explicit commits
        # avoids hidden writes and makes transaction boundaries obvious.

    @abstractmethod
    async def commit(self) -> None:
        """Commits the active transaction."""
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Rolls back the active transaction."""
        raise NotImplementedError
