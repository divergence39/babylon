import uuid
from collections.abc import Callable

import pytest

from babylon.domain.entities import User
from babylon.domain.value_objects import (
    AggregateVersion,
    KdfConfiguration,
    MasterPasswordSalt,
    ServerAuthHash,
    UserId,
    Username,
)

from .fakes import FakeSaltGenerator, FakeUnitOfWork

VALID_PHC_HASH_CONSTANT = (
    "$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$bm90YWhhc2h0aGF0aXNsb25nZW5vdWdoMTIzNA"
)


@pytest.fixture
def valid_phc_hash() -> str:
    return VALID_PHC_HASH_CONSTANT


@pytest.fixture
def uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def salt_generator() -> FakeSaltGenerator:
    return FakeSaltGenerator()


@pytest.fixture
def user_factory(valid_phc_hash: str) -> Callable[[str, str, int], User]:
    def _create_user(username: str, salt: str = "B" * 32, kdf_mem: int = 65536) -> User:
        return User(
            id=UserId(uuid.uuid7()),
            version=AggregateVersion(1),
            username=Username(username),
            salt=MasterPasswordSalt(salt),
            server_authentication_hash=ServerAuthHash(valid_phc_hash),
            kdf_configuration=KdfConfiguration("argon2id", kdf_mem, 3, 4),
        )

    return _create_user
