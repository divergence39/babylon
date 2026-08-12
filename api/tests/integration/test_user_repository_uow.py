import asyncio

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from babylon.domain.exceptions import UserAlreadyExistsError, UserConcurrencyError
from babylon.domain.ports import UnitOfWork
from babylon.domain.value_objects import (
    AggregateVersion,
    KdfConfiguration,
    MasterPasswordSalt,
    ServerAuthHash,
)
from babylon.infrastructure.database.models import UserModel
from babylon.infrastructure.database.uow import SqlAlchemyUnitOfWork

from .factories import UserFactory


@pytest.fixture
def uow(db_session: AsyncSession) -> UnitOfWork:
    """Returns the SQLAlchemy UnitOfWork backed by the test session."""
    return SqlAlchemyUnitOfWork(
        session_factory=lambda: db_session,
        owns_session=False,
    )


@pytest.mark.asyncio
async def test_save_and_find_user_returns_pure_domain_entity(
    uow: UnitOfWork,
    user_factory: type[UserFactory],
) -> None:
    """Asserts that a user can be saved and retrieved by ID as a pure Domain Entity."""
    user = user_factory.build()

    async with uow:
        await uow.users.save(user)
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
    uow: UnitOfWork,
    user_factory: type[UserFactory],
    db_session: AsyncSession,
) -> None:
    """Asserts inserts record a timezone-aware last modification timestamp."""
    user = user_factory.build()

    async with uow:
        await uow.users.save(user)
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
    uow: UnitOfWork,
    user_factory: type[UserFactory],
    db_session: AsyncSession,
) -> None:
    """Asserts updates bump the last modification timestamp."""
    user = user_factory.build()

    async with uow:
        await uow.users.save(user)
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
        new_salt=MasterPasswordSalt(value="E" * 32),
        new_server_auth_hash=ServerAuthHash(
            value="$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$YQA4"
        ),
        new_kdf_configuration=KdfConfiguration(
            algorithm="argon2id", memory_kb=65536, iterations=3, parallelism=4
        ),
    )

    async with uow:
        await uow.users.save(user)
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
    uow: UnitOfWork,
    user_factory: type[UserFactory],
    engine: AsyncEngine,
) -> None:
    """Asserts data is not committed unless commit() is called explicitly."""
    user = user_factory.build()

    async with uow:
        await uow.users.save(user)

    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with async_session() as verification_session:
        verification_uow = SqlAlchemyUnitOfWork(
            session_factory=lambda: verification_session,
            owns_session=False,
        )
        async with verification_uow:
            retrieved_user = await verification_uow.users.find_by_id(user.id)

    assert retrieved_user is None


@pytest.mark.asyncio
async def test_unique_violation_rolls_back_and_allows_retry(
    uow: UnitOfWork,
    user_factory: type[UserFactory],
) -> None:
    """Asserts a deterministic unique-constraint failure rolls back cleanly."""
    test_username_hash = "MpY6dddb+ipakoYR7mxT69OdERLt+aocCgrztICn9X8="
    user = user_factory.build(
        user_id="018e6d2a-4f51-7000-8000-000000000010",
        username_hash=test_username_hash,
    )

    async with uow:
        await uow.users.save(user)
        await uow.commit()

    duplicate = user_factory.build(
        user_id="018e6d2a-4f51-7000-8000-000000000011",
        username_hash=user.username_hash.value,
    )

    with pytest.raises(UserAlreadyExistsError) as exc_info:  # noqa: PT012
        async with uow:
            await uow.users.save(duplicate)
            await uow.commit()

    assert exc_info.value.username_hash == user.username_hash.value

    test_username_hash_retry = "ziciPa56GT7tKXHt5xua255MCsQAAjsFQEQFfWcZyUU="

    retry_user = user_factory.build(
        user_id="018e6d2a-4f51-7000-8000-000000000012",
        username_hash=test_username_hash_retry,
    )

    async with uow:
        await uow.users.save(retry_user)
        await uow.commit()

    async with uow:
        retrieved = await uow.users.find_by_id(retry_user.id)

    assert retrieved is not None
    assert retrieved.id == retry_user.id


@pytest.mark.asyncio
async def test_find_by_username_returns_pure_domain_entity(
    uow: UnitOfWork,
    user_factory: type[UserFactory],
) -> None:
    """Asserts retrieval by canonical username_hash rehydrates the domain entity."""
    test_username_hash = "ziciPa56GT7tKXHt5xua255MCsQAAjsFQEQFfWcZyUU="
    user = user_factory.build(username_hash=test_username_hash)

    async with uow:
        await uow.users.save(user)
        await uow.commit()

    async with uow:
        retrieved_user = await uow.users.find_by_username_hash(user.username_hash)

    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    assert retrieved_user.version == user.version


@pytest.mark.asyncio
async def test_find_by_id_returns_none_if_not_found(
    uow: UnitOfWork,
    user_factory: type[UserFactory],
) -> None:
    """Asserts retrieving a missing User returns None."""
    user = user_factory.build()

    async with uow:
        retrieved_user = await uow.users.find_by_id(user.id)

    assert retrieved_user is None


@pytest.mark.asyncio
async def test_prevent_duplicate_canonical_usernames(
    uow: UnitOfWork,
    user_factory: type[UserFactory],
) -> None:
    """
    Asserts trying to persist two Users with identically canonicalized usernames
    translates raw IntegrityError into the clean domain UserAlreadyExistsError.
    """

    username_hash = "MpY6dddb+ipakoYR7mxT69OdERLt+aocCgrztICn9X8="

    user1 = user_factory.build(
        user_id="018e6d2a-4f51-7000-8000-000000000001", username_hash=username_hash
    )
    user2 = user_factory.build(
        user_id="018e6d2a-4f51-7000-8000-000000000002", username_hash=username_hash
    )

    async with uow:
        await uow.users.save(user1)
        await uow.commit()

    with pytest.raises(UserAlreadyExistsError) as exc_info:  # noqa: PT012
        async with uow:
            await uow.users.save(user2)
            await uow.commit()

    assert exc_info.value.username_hash == username_hash


@pytest.mark.asyncio
async def test_uow_rollback_prevents_persistence(
    uow: UnitOfWork,
    user_factory: type[UserFactory],
) -> None:
    """Asserts that raising an exception inside UOW rolls back the transaction."""
    user = user_factory.build()

    with pytest.raises(ValueError, match="fail"):  # noqa: PT012
        async with uow:
            await uow.users.save(user)
            raise ValueError("fail")

    async with uow:
        retrieved_user = await uow.users.find_by_id(user.id)

    assert retrieved_user is None


@pytest.mark.asyncio
async def test_save_updates_existing_user(
    uow: UnitOfWork,
    user_factory: type[UserFactory],
) -> None:
    """Asserts that calling save on an already persisted user updates their record."""
    user = user_factory.build()
    original_version = user.version

    async with uow:
        await uow.users.save(user)
        await uow.commit()

    # Mutate aggregate data correctly using the domain method
    new_salt = MasterPasswordSalt(value="BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=")
    new_auth_hash = ServerAuthHash(
        value="$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$YQNEW"
    )
    new_kdf = KdfConfiguration(
        algorithm="argon2id", memory_kb=128000, iterations=4, parallelism=4
    )

    user.rotate_credentials(
        new_salt=new_salt,
        new_server_auth_hash=new_auth_hash,
        new_kdf_configuration=new_kdf,
    )

    assert user.version == original_version.next_version()

    async with uow:
        await uow.users.save(user)
        await uow.commit()

    async with uow:
        updated_user = await uow.users.find_by_id(user.id)

    assert updated_user is not None
    assert updated_user.salt == new_salt
    assert updated_user.server_authentication_hash == new_auth_hash
    assert updated_user.kdf_configuration == new_kdf
    assert updated_user.version == user.version


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
async def test_concurrent_updates_raise_conflict(
    uow: UnitOfWork,
    user_factory: type[UserFactory],
    db_session: AsyncSession,
) -> None:
    """Asserts concurrent updates surface as a UserConcurrencyError."""
    user = user_factory.build()

    async with uow:
        await uow.users.save(user)
        await uow.commit()

    engine = db_session.bind
    async_session = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
    async with async_session() as session_a, async_session() as session_b:
        uow_a = SqlAlchemyUnitOfWork(
            session_factory=lambda: session_a,
            owns_session=False,
        )
        uow_b = SqlAlchemyUnitOfWork(
            session_factory=lambda: session_b,
            owns_session=False,
        )

        async with uow_a:
            user_a = await uow_a.users.find_by_id(user.id)

        async with uow_b:
            user_b = await uow_b.users.find_by_id(user.id)

        assert user_a is not None
        assert user_b is not None
        assert user_a.version == AggregateVersion(1)
        assert user_b.version == AggregateVersion(1)

        user_a.rotate_credentials(
            new_salt=MasterPasswordSalt(value="C" * 32),
            new_server_auth_hash=ServerAuthHash(
                value="$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$YQA2"
            ),
            new_kdf_configuration=KdfConfiguration(
                algorithm="argon2id", memory_kb=65536, iterations=3, parallelism=4
            ),
        )

        async with uow_a:
            await uow_a.users.save(user_a)
            await uow_a.commit()

        user_b.rotate_credentials(
            new_salt=MasterPasswordSalt(value="D" * 32),
            new_server_auth_hash=ServerAuthHash(
                value="$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$YQA3"
            ),
            new_kdf_configuration=KdfConfiguration(
                algorithm="argon2id", memory_kb=65536, iterations=3, parallelism=4
            ),
        )

        async def _commit_conflicting_update() -> None:
            async with uow_b:
                await uow_b.users.save(user_b)
                await uow_b.commit()

        with pytest.raises(UserConcurrencyError):
            await _commit_conflicting_update()
