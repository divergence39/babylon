"""Fake implementations for Application Layer unit tests."""

import copy
import types
from uuid import UUID

from babylon.auth.application.ports import IFakeSaltGenerator
from babylon.auth.domain.entities import User
from babylon.auth.domain.ports.unit_of_work import IUnitOfWork
from babylon.auth.domain.ports.user_repository import (
    IUserRepository,
    UserAlreadyExistsError,
    UserConcurrencyError,
)
from babylon.auth.domain.value_objects import UserId, UsernameHash


class FakeUserRepository(IUserRepository):
    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def add(self, user: User) -> None:
        if user.id.value in self._users:
            raise UserAlreadyExistsError(user.username_hash.value)
        for existing_id, existing_user in self._users.items():
            if (
                existing_user.username_hash == user.username_hash
                and existing_id != user.id.value
            ):
                raise UserAlreadyExistsError(user.username_hash.value)
        self._users[user.id.value] = copy.deepcopy(user)

    async def update(self, user: User) -> None:
        for existing_id, existing_user in self._users.items():
            if (
                existing_user.username_hash == user.username_hash
                and existing_id != user.id.value
            ):
                raise UserAlreadyExistsError(user.username_hash.value)
        existing_user = self._users[user.id.value]
        if existing_user.version.value != user.version.value - 1:
            raise UserConcurrencyError(str(user.id.value))
        self._users[user.id.value] = copy.deepcopy(user)

    async def find_by_id(self, id: UserId) -> User | None:
        return copy.deepcopy(self._users.get(id.value))

    async def find_by_username_hash(self, username_hash: UsernameHash) -> User | None:
        for u in self._users.values():
            if u.username_hash == username_hash:
                return copy.deepcopy(u)
        return None


class FakeUnitOfWork(IUnitOfWork):
    def __init__(self) -> None:
        self._users = FakeUserRepository()
        self.committed = False
        self.rolled_back = False

    @property
    def users(self) -> FakeUserRepository:
        return self._users

    async def __aenter__(self) -> FakeUnitOfWork:
        self.committed = False
        self.rolled_back = False
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        if exc_type is not None or not self.committed:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class FakeSaltGenerator(IFakeSaltGenerator):
    def generate_fallback_salt(self, username: str) -> str:
        return f"fake_salt_{username}"
