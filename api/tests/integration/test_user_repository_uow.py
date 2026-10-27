import asyncio
import base64

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
)

from babylon.auth.domain.ports.user_repository import (
    UserAlreadyExistsError,
    UserConcurrencyError,
)
from babylon.auth.domain.value_objects import (
    AggregateVersion,
    KdfConfiguration,
    MasterPasswordSalt,
    ServerAuthHash,
)
from babylon.auth.infrastructure.database.models import UserModel
from babylon.auth.infrastructure.database.uow import SqlAlchemyUnitOfWork

from .factories import UserFactory


@pytest.fixture
def session_factory(connection: AsyncConnection) -> async_sessionmaker[AsyncSession]:
    """Factory per generare sessioni asincrone pulite agganciate all'engine di test."""
    return async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )


@pytest.fixture
def uow(session_factory: async_sessionmaker[AsyncSession]) -> SqlAlchemyUnitOfWork:
    """Fixture standard per i test che necessitano di una UoW ordinaria."""
    return SqlAlchemyUnitOfWork(session_factory=session_factory)


@pytest.mark.asyncio
async def test_save_and_find_user_returns_pure_domain_entity(
    uow: SqlAlchemyUnitOfWork,
    user_factory: type[UserFactory],
) -> None:
    """Asserts that a user can be saved and retrieved by ID as a pure Domain Entity."""
    user = user_factory.build()

    async with uow:
        await uow.users.add(user)
        await uow.commit()

    async with uow:
        retrieved_user = await uow.users.find_by_id(user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    assert retrieved_user.username_hash == user.username_hash
    assert retrieved_user.salt == user.salt
    assert retrieved_user.server_authentication_hash == user.server_authentication_hash
    assert retrieved_user.kdf_configuration == user.kdf_configuration
    assert retrieved_user.version == user.version


@pytest.mark.asyncio
async def test_last_modification_time_set_on_insert(
    uow: SqlAlchemyUnitOfWork,
    user_factory: type[UserFactory],
    db_session: AsyncSession,
) -> None:
    """Asserts inserts record a timezone-aware last modification timestamp."""
    user = user_factory.build()

    async with uow:
        await uow.users.add(user)
        await uow.commit()

    result = await db_session.execute(
        select(UserModel)
        .where(UserModel.id == user.id.value)
        .execution_options(populate_existing=True)
    )
    model = result.scalar_one()

    assert model.last_modification_time is not None
    assert model.last_modification_time.tzinfo is not None
    assert (
        model.last_modification_time.tzinfo.utcoffset(model.last_modification_time)
        is not None
    )


@pytest.mark.asyncio
async def test_last_modification_time_updates_on_change(
    uow: SqlAlchemyUnitOfWork,
    user_factory: type[UserFactory],
    db_session: AsyncSession,
) -> None:
    """Asserts updates bump the last modification timestamp."""
    user = user_factory.build()

    async with uow:
        await uow.users.add(user)
        await uow.commit()

    result = await db_session.execute(
        select(UserModel)
        .where(UserModel.id == user.id.value)
        .execution_options(populate_existing=True)
    )
    model = result.scalar_one()
    initial_time = model.last_modification_time

    await asyncio.sleep(0.01)

    user.rotate_credentials(
        current_server_auth_hash=user.server_authentication_hash,
        new_salt=MasterPasswordSalt(value="E" * 32),
        new_server_auth_hash=ServerAuthHash(
            value="$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$YQA4"
        ),
        new_kdf_configuration=KdfConfiguration(
            algorithm="argon2id", memory_kb=65536, iterations=3, parallelism=4
        ),
    )

    async with uow:
        await uow.users.update(user)
        await uow.commit()

    result = await db_session.execute(
        select(UserModel)
        .where(UserModel.id == user.id.value)
        .execution_options(populate_existing=True)
    )
    updated_model = result.scalar_one()

    assert updated_model.last_modification_time > initial_time


@pytest.mark.asyncio
async def test_save_without_commit_does_not_persist(
    uow: SqlAlchemyUnitOfWork,
    user_factory: type[UserFactory],
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Asserts data is not committed unless commit() is called explicitly."""
    user = user_factory.build()

    async with uow:
        await uow.users.add(user)

    verification_uow = SqlAlchemyUnitOfWork(session_factory=session_factory)
    async with verification_uow:
        retrieved_user = await verification_uow.users.find_by_id(user.id)

    assert retrieved_user is None


@pytest.mark.asyncio
async def test_unique_violation_rolls_back_and_allows_retry(
    uow: SqlAlchemyUnitOfWork,
    user_factory: type[UserFactory],
) -> None:
    """Asserts a deterministic unique-constraint failure rolls back cleanly."""
    test_username_hash = "MpY6dddb+ipakoYR7mxT69OdERLt+aocCgrztICn9X8="
    user = user_factory.build(
        user_id="018e6d2a-4f51-7000-8000-000000000010",
        username_hash=test_username_hash,
    )

    async with uow:
        await uow.users.add(user)
        await uow.commit()

    duplicate = user_factory.build(
        user_id="018e6d2a-4f51-7000-8000-000000000011",
        username_hash=user.username_hash.value,
    )

    with pytest.raises(UserAlreadyExistsError):  # noqa: PT012
        async with uow:
            await uow.users.add(duplicate)
            await uow.commit()

    test_username_hash_retry = "ziciPa56GT7tKXHt5xua255MCsQAAjsFQEQFfWcZyUU="

    retry_user = user_factory.build(
        user_id="018e6d2a-4f51-7000-8000-000000000012",
        username_hash=test_username_hash_retry,
    )

    async with uow:
        await uow.users.add(retry_user)
        await uow.commit()

    async with uow:
        retrieved = await uow.users.find_by_id(retry_user.id)

    assert retrieved is not None
    assert retrieved.id == retry_user.id


@pytest.mark.asyncio
async def test_find_by_username_returns_pure_domain_entity(
    uow: SqlAlchemyUnitOfWork,
    user_factory: type[UserFactory],
) -> None:
    """Asserts retrieval by canonical username_hash rehydrates the domain entity."""
    test_username_hash = "ziciPa56GT7tKXHt5xua255MCsQAAjsFQEQFfWcZyUU="
    user = user_factory.build(username_hash=test_username_hash)

    async with uow:
        await uow.users.add(user)
        await uow.commit()

    async with uow:
        retrieved_user = await uow.users.find_by_username_hash(user.username_hash)

    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    assert retrieved_user.version == user.version


@pytest.mark.asyncio
async def test_find_by_id_returns_none_if_not_found(
    uow: SqlAlchemyUnitOfWork,
    user_factory: type[UserFactory],
) -> None:
    """Asserts retrieving a missing User returns None."""
    user = user_factory.build()

    async with uow:
        retrieved_user = await uow.users.find_by_id(user.id)

    assert retrieved_user is None


@pytest.mark.asyncio
async def test_prevent_duplicate_canonical_usernames(
    uow: SqlAlchemyUnitOfWork,
    user_factory: type[UserFactory],
) -> None:
    """
    Asserts trying to persist two Users with identically canonicalized usernames
    translates raw IntegrityError into the clean domain UserAlreadyExistsError.
    """

    username_hash = "MpY6dddb+ipakoYR7mxT69OdERLt+aocCgrztICn9X8="

    user1 = user_factory.build(
        user_id="018e6d2a4f5170008000000000000001", username_hash=username_hash
    )
    user2 = user_factory.build(
        user_id="018e6d2a4f5170008000000000000002", username_hash=username_hash
    )

    async with uow:
        await uow.users.add(user1)
        await uow.commit()

    with pytest.raises(UserAlreadyExistsError):  # noqa: PT012
        async with uow:
            await uow.users.add(user2)
            await uow.commit()


@pytest.mark.asyncio
async def test_uow_rollback_prevents_persistence(
    uow: SqlAlchemyUnitOfWork,
    user_factory: type[UserFactory],
) -> None:
    """Asserts that raising an exception inside UOW rolls back the transaction."""
    user = user_factory.build()

    with pytest.raises(ValueError, match="fail"):  # noqa: PT012
        async with uow:
            await uow.users.add(user)
            raise ValueError("fail")

    async with uow:
        retrieved_user = await uow.users.find_by_id(user.id)

    assert retrieved_user is None


@pytest.mark.asyncio
async def test_update_existing_user(
    uow: SqlAlchemyUnitOfWork,
    user_factory: type[UserFactory],
) -> None:
    """Asserts that calling update on a persisted user updates their record."""
    user = user_factory.build()
    original_version = user.version

    async with uow:
        await uow.users.add(user)
        await uow.commit()

    new_salt = MasterPasswordSalt(
        value=base64.b64encode(b"CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC").decode()
    )
    new_auth_hash = ServerAuthHash(
        value="$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$YQNEW"
    )
    new_kdf = KdfConfiguration(
        algorithm="argon2id", memory_kb=128000, iterations=4, parallelism=4
    )

    user.rotate_credentials(
        current_server_auth_hash=user.server_authentication_hash,
        new_salt=new_salt,
        new_server_auth_hash=new_auth_hash,
        new_kdf_configuration=new_kdf,
    )

    assert user.version == original_version.next_version()

    async with uow:
        await uow.users.update(user)
        await uow.commit()

    async with uow:
        updated_user = await uow.users.find_by_id(user.id)

    assert updated_user is not None
    assert updated_user.salt == new_salt
    assert updated_user.server_authentication_hash == new_auth_hash
    assert updated_user.kdf_configuration == new_kdf
    assert updated_user.version == user.version


@pytest.mark.asyncio
async def test_concurrent_updates_raise_conflict(
    session_factory: async_sessionmaker[AsyncSession],
    user_factory: type[UserFactory],
) -> None:
    """Asserts concurrent updates surface as a UserConcurrencyError."""
    uow_setup = SqlAlchemyUnitOfWork(session_factory=session_factory)
    user = user_factory.build()
    async with uow_setup:
        await uow_setup.users.add(user)
        await uow_setup.commit()

    uow_a = SqlAlchemyUnitOfWork(session_factory=session_factory)
    uow_b = SqlAlchemyUnitOfWork(session_factory=session_factory)

    async with uow_a:
        user_a = await uow_a.users.find_by_id(user.id)

    async with uow_b:
        user_b = await uow_b.users.find_by_id(user.id)

    assert user_a is not None
    assert user_b is not None
    assert user_a.version == AggregateVersion(1)
    assert user_b.version == AggregateVersion(1)

    user_a.rotate_credentials(
        current_server_auth_hash=user_a.server_authentication_hash,
        new_salt=MasterPasswordSalt(value="C" * 32),
        new_server_auth_hash=ServerAuthHash(
            value="$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$YQA2"
        ),
        new_kdf_configuration=KdfConfiguration(
            algorithm="argon2id", memory_kb=65536, iterations=3, parallelism=4
        ),
    )

    async with uow_a:
        await uow_a.users.update(user_a)
        await uow_a.commit()

    user_b.rotate_credentials(
        current_server_auth_hash=user_b.server_authentication_hash,
        new_salt=MasterPasswordSalt(value="D" * 32),
        new_server_auth_hash=ServerAuthHash(
            value="$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$YQA3"
        ),
        new_kdf_configuration=KdfConfiguration(
            algorithm="argon2id", memory_kb=65536, iterations=3, parallelism=4
        ),
    )

    async def _test_update_b() -> None:
        async with uow_b:
            await uow_b.users.update(user_b)
            await uow_b.commit()

    with pytest.raises(UserConcurrencyError):
        await _test_update_b()
