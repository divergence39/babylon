"""SQLAlchemy repository implementation for the User aggregate."""

from __future__ import annotations

import base64

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, OperationalError, TimeoutError
from sqlalchemy.ext.asyncio import AsyncSession

from babylon.auth.domain.entities import User
from babylon.auth.domain.ports.user_repository import (
    IUserRepository,
    UserAlreadyExistsError,
    UserConcurrencyError,
)
from babylon.auth.domain.value_objects import (
    AggregateVersion,
    KdfConfiguration,
    MasterPasswordSalt,
    ServerAuthHash,
    UserId,
    UsernameHash,
)
from babylon.auth.infrastructure.database.models import UserModel
from babylon.shared.infrastructure.database.exceptions import DatabaseUnavailableError

_UNIQUE_VIOLATION_CODE = "23505"


class SqlAlchemyUserRepository(IUserRepository):
    """Async SQLAlchemy adapter for persisting User aggregates."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user: User) -> None:
        """Add a new user entity to the repository."""
        model = _domain_to_model(user)
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            if _is_unique_violation(exc):
                raise UserAlreadyExistsError(user.username_hash.value) from exc
            raise
        except (OperationalError, TimeoutError) as exc:
            raise DatabaseUnavailableError() from exc

    async def update(self, user: User) -> None:
        """Update an existing user entity in the repository."""
        statement = (
            update(UserModel)
            .where(
                UserModel.id == user.id.value,
                UserModel.version == user.version.value - 1,
            )
            .values(
                username=user.username_hash.value,
                salt=base64.b64decode(user.salt.value),
                server_auth_hash=user.server_authentication_hash.value,
                kdf_configuration=_serialize_kdf(user.kdf_configuration),
                version=user.version.value,
            )
            .returning(UserModel.id)
        )
        try:
            result = await self._session.execute(statement)
            updated_id = result.scalar_one_or_none()

            if updated_id is None:
                raise UserConcurrencyError(str(user.id.value))

            await self._session.flush()
        except IntegrityError as exc:
            if _is_unique_violation(exc):
                raise UserAlreadyExistsError(user.username_hash.value) from exc
            raise
        except (OperationalError, TimeoutError) as exc:
            raise DatabaseUnavailableError() from exc

    async def find_by_id(self, id: UserId) -> User | None:
        """Find a single user by their unique identity."""
        try:
            model = await self._session.get(UserModel, id.value)
        except (OperationalError, TimeoutError) as exc:
            raise DatabaseUnavailableError() from exc
        if model is None:
            return None
        return _model_to_domain(model)

    async def find_by_username_hash(self, username_hash: UsernameHash) -> User | None:
        """Find a single user by their canonical username."""
        try:
            statement = select(UserModel).where(
                UserModel.username == username_hash.value
            )
            result = await self._session.execute(statement)
        except (OperationalError, TimeoutError) as exc:
            raise DatabaseUnavailableError() from exc
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return _model_to_domain(model)


def _model_to_domain(model: UserModel) -> User:
    """Rehydrate a domain User aggregate from a persisted ORM model."""
    return User(
        id=UserId(value=model.id),
        version=AggregateVersion(value=model.version),
        username_hash=UsernameHash(value=model.username),
        salt=MasterPasswordSalt(value=base64.b64encode(model.salt).decode()),
        server_authentication_hash=ServerAuthHash(
            value=model.server_auth_hash,
        ),
        kdf_configuration=_deserialize_kdf(model.kdf_configuration),
    )


def _domain_to_model(user: User) -> UserModel:
    """Convert a domain User aggregate into a persisted ORM model."""
    return UserModel(
        id=user.id.value,
        username=user.username_hash.value,
        salt=base64.b64decode(user.salt.value),
        server_auth_hash=user.server_authentication_hash.value,
        kdf_configuration=_serialize_kdf(user.kdf_configuration),
        version=user.version.value,
    )


def _serialize_kdf(config: KdfConfiguration) -> dict[str, int | str]:
    """Convert a KdfConfiguration into a JSON-compatible dictionary."""
    return {
        "algorithm": config.algorithm,
        "memory_kb": config.memory_kb,
        "iterations": config.iterations,
        "parallelism": config.parallelism,
    }


def _deserialize_kdf(config: dict[str, int | str]) -> KdfConfiguration:
    """Convert a JSON-compatible dictionary into a KdfConfiguration."""
    return KdfConfiguration(
        algorithm=str(config["algorithm"]),
        memory_kb=int(config["memory_kb"]),
        iterations=int(config["iterations"]),
        parallelism=int(config["parallelism"]),
    )


def _is_unique_violation(error: IntegrityError) -> bool:
    """Return True when the database raises a unique-constraint violation."""
    if error.orig is None:
        return False

    sqlstate = getattr(error.orig, "sqlstate", None) or getattr(
        error.orig, "pgcode", None
    )

    return sqlstate == _UNIQUE_VIOLATION_CODE
