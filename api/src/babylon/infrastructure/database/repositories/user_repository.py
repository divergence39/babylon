"""SQLAlchemy repository implementation for the User aggregate."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError, TimeoutError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import StaleDataError

from babylon.domain.entities import User
from babylon.domain.exceptions import UserAlreadyExistsError, UserConcurrencyError
from babylon.domain.ports import UserRepository
from babylon.domain.value_objects import (
    AggregateVersion,
    KdfConfiguration,
    MasterPasswordSalt,
    ServerAuthHash,
    UserId,
    UsernameHash,
)
from babylon.infrastructure.database.exceptions import DatabaseUnavailableError
from babylon.infrastructure.database.models import UserModel

_UNIQUE_VIOLATION_CODE = "23505"


class SqlAlchemyUserRepository(UserRepository):
    """Async SQLAlchemy adapter for persisting User aggregates."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> None:
        """Persist a new or modified user entity."""
        try:
            salt_bytes = user.salt.value.encode("utf-8")
            auth_hash_bytes = user.server_authentication_hash.value.encode("utf-8")
            existing = await self._session.get(UserModel, user.id.value)
            if existing is None:
                model = UserModel(
                    id=user.id.value,
                    username=user.username_hash.value,
                    salt=salt_bytes,
                    server_auth_hash=auth_hash_bytes,
                    kdf_configuration=_serialize_kdf(user.kdf_configuration),
                    version=user.version.value,
                )
                self._session.add(model)
            else:
                _ensure_expected_version(user, existing.version)
                existing.username = user.username_hash.value
                existing.salt = salt_bytes
                existing.server_auth_hash = auth_hash_bytes
                existing.kdf_configuration = _serialize_kdf(user.kdf_configuration)
                existing.version = user.version.value

            await self._session.flush()
        except IntegrityError as exc:
            if _is_unique_violation(exc):
                raise UserAlreadyExistsError(user.username_hash.value) from exc
            raise
        except StaleDataError as exc:
            raise UserConcurrencyError(str(user.id.value)) from exc
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
        salt=MasterPasswordSalt(value=model.salt.decode("utf-8")),
        server_authentication_hash=ServerAuthHash(
            value=model.server_auth_hash.decode("utf-8"),
        ),
        kdf_configuration=_deserialize_kdf(model.kdf_configuration),
    )


def _ensure_expected_version(user: User, current_version: int) -> None:
    """Validate the user version aligns with the persisted version."""
    expected_version = user.version.value - 1
    if expected_version != current_version:
        raise UserConcurrencyError(str(user.id.value))


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
