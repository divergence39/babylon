"""SQLAlchemy Unit of Work implementation for transactional boundaries."""

from __future__ import annotations

import types
from collections.abc import Callable

from sqlalchemy.exc import OperationalError, TimeoutError
from sqlalchemy.ext.asyncio import AsyncSession

from babylon.auth.domain.ports import IUnitOfWork
from babylon.auth.infrastructure.database.repositories import (
    SqlAlchemyUserRepository,
)
from babylon.shared.infrastructure.database.exceptions import DatabaseUnavailableError


class UnitOfWorkSessionNotInitializedError(RuntimeError):
    """Raised when the Unit of Work session is accessed before initialization."""

    def __init__(self) -> None:
        super().__init__("Unit of work session is not initialized.")


class UnitOfWorkNotEnteredError(RuntimeError):
    """Raised when a Unit of Work repository is accessed before entry."""

    def __init__(self) -> None:
        super().__init__("Unit of work has not been entered.")


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """Async SQLAlchemy Unit of Work adapter."""

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._users: SqlAlchemyUserRepository | None = None
        self._committed: bool = False

    @property
    def users(self) -> SqlAlchemyUserRepository:
        """Access the user repository within the Unit of Work context."""
        if self._session is None or self._users is None:
            raise UnitOfWorkNotEnteredError()
        return self._users

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        self._session = self._session_factory()
        self._users = SqlAlchemyUserRepository(self._session)
        self._committed = False
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None or not self._committed:
                await self.rollback()
        finally:
            await self._close_session()

    async def commit(self) -> None:
        """Commit the active transaction."""
        try:
            await self._get_session().commit()
            self._committed = True
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
        if self._session is not None:
            await self._session.close()
            self._session = None
            self._users = None
