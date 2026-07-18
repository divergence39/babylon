"""SQLAlchemy Unit of Work implementation for transactional boundaries."""

from __future__ import annotations

import types
from collections.abc import Callable

from sqlalchemy.exc import OperationalError, TimeoutError
from sqlalchemy.ext.asyncio import AsyncSession

from babylon.domain.entities import User
from babylon.domain.ports import UnitOfWork, UserRepository
from babylon.domain.value_objects import UserId, Username
from babylon.infrastructure.database.exceptions import DatabaseUnavailableError
from babylon.infrastructure.database.repositories.user_repository import (
    SqlAlchemyUserRepository,
)


class UnitOfWorkSessionNotInitializedError(RuntimeError):
    """Raised when the Unit of Work session is accessed before initialization."""

    def __init__(self) -> None:
        super().__init__("Unit of work session is not initialized.")


class UnitOfWorkNotEnteredError(RuntimeError):
    """Raised when a Unit of Work repository is accessed before entry."""

    def __init__(self) -> None:
        super().__init__("Unit of work has not been entered.")


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Async SQLAlchemy Unit of Work adapter."""

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
        *,
        owns_session: bool = True,
    ) -> None:
        self._session_factory = session_factory
        self._owns_session = owns_session
        self._session: AsyncSession | None = None
        self.users = _UninitializedUserRepository()

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        self._session = self._session_factory()
        self.users = SqlAlchemyUserRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        try:
            await super().__aexit__(exc_type, exc_val, exc_tb)
        finally:
            await self._close_session()

    async def commit(self) -> None:
        """Commit the active transaction."""
        try:
            await self._get_session().commit()
        except (OperationalError, TimeoutError) as exc:
            raise DatabaseUnavailableError() from exc

    async def rollback(self) -> None:
        """Rollback the active transaction."""
        try:
            await self._get_session().rollback()
        except (OperationalError, TimeoutError) as exc:
            raise DatabaseUnavailableError() from exc

    def _get_session(self) -> AsyncSession:
        if self._session is None:
            raise UnitOfWorkSessionNotInitializedError()
        return self._session

    async def _close_session(self) -> None:
        if self._session is None:
            return
        if self._owns_session:
            await self._session.close()
        self._session = None
        self.users = _UninitializedUserRepository()


class _UninitializedUserRepository(UserRepository):
    """Placeholder repository that fails fast before UoW activation."""

    async def save(self, user: User) -> None:
        _ = user
        raise UnitOfWorkNotEnteredError()

    async def find_by_id(self, id: UserId) -> User | None:
        _ = id
        raise UnitOfWorkNotEnteredError()

    async def find_by_username(self, username: Username) -> User | None:
        _ = username
        raise UnitOfWorkNotEnteredError()
