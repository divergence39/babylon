"""SQLAlchemy repository implementation for the User aggregate."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError, TimeoutError
from sqlalchemy.ext.asyncio import AsyncSession

from babylon.application import DatabaseUnavailableError
from babylon.domain.entities import User
from babylon.domain.exceptions import UserAlreadyExistsError
from babylon.domain.ports import UserRepository
from babylon.domain.value_objects import (
    KdfConfiguration,
    MasterPasswordSalt,
    ServerAuthHash,
    UserId,
    Username,
)
from babylon.infrastructure.database.models import UserModel

_UNIQUE_VIOLATION_CODE = "23505"


class SqlAlchemyUserRepository(UserRepository):
    """Async SQLAlchemy adapter for persisting User aggregates."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> None:
        """Persist a new or modified user entity."""
        try:
            model = UserModel(
                id=user.id.value,
                username=user.username.value,
                salt=user.salt.value.encode("utf-8"),
                server_auth_hash=user.server_authentication_hash.value.encode("utf-8"),
                kdf_configuration=_serialize_kdf(user.kdf_configuration),
            )

            await self._session.merge(model)
            await self._session.flush()
        except IntegrityError as exc:
            if _is_unique_violation(exc):
                raise UserAlreadyExistsError(user.username.value) from exc
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

    async def find_by_username(self, username: Username) -> User | None:
        """Find a single user by their canonical username."""
        try:
            statement = select(UserModel).where(UserModel.username == username.value)
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
        username=Username(value=model.username),
        salt=MasterPasswordSalt(value=model.salt.decode("utf-8")),
        server_authentication_hash=ServerAuthHash(
            value=model.server_auth_hash.decode("utf-8"),
        ),
        kdf_configuration=_deserialize_kdf(model.kdf_configuration),
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
