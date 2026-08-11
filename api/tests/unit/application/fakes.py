"""Fake implementations for Application Layer unit tests."""

from uuid import UUID

from babylon.application.ports.salt_generator import IFakeSaltGenerator
from babylon.domain.entities import User
from babylon.domain.ports.unit_of_work import UnitOfWork
from babylon.domain.ports.user_repository import UserRepository
from babylon.domain.value_objects import UserId, UsernameHash


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def save(self, user: User) -> None:
        self._users[user.id.value] = user

    async def find_by_id(self, id: UserId) -> User | None:
        return self._users.get(id.value)

    async def find_by_username_hash(self, username_hash: UsernameHash) -> User | None:
        for u in self._users.values():
            if u.username_hash == username_hash:
                return u
        return None


class FakeUnitOfWork(UnitOfWork):
    def __init__(self, repository: UserRepository | None = None) -> None:
        self.users = repository or FakeUserRepository()
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class FakeSaltGenerator(IFakeSaltGenerator):
    def generate_fallback_salt(self, username: str) -> str:
        return f"fake_salt_{username}"
