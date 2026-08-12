"""Polyfactory-backed factories for integration tests."""

from __future__ import annotations

from typing import Any, TypeGuard
from uuid import UUID

from polyfactory.factories import BaseFactory, DataclassFactory
from polyfactory.field_meta import FieldMeta

from babylon.domain.entities import User
from babylon.domain.value_objects import (
    AggregateVersion,
    KdfConfiguration,
    MasterPasswordSalt,
    ServerAuthHash,
    UserId,
    UsernameHash,
)

_DEFAULT_USER_ID = UUID("018e6c4e-5e13-7fa3-aecd-8c4cc87ed165")
_DEFAULT_VERSION = AggregateVersion(1)
_DEFAULT_USERNAME_HASH = "MpY6dddb+ipakoYR7mxT69OdERLt+aocCgrztICn9X8="
_DEFAULT_SALT = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
_DEFAULT_SERVER_AUTH_HASH = "$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$YQ"
_DEFAULT_KDF_CONFIGURATION = KdfConfiguration(
    algorithm="argon2id", memory_kb=65536, iterations=3, parallelism=4
)


class UserIdFactory(DataclassFactory[UserId]):
    """Build valid UserId value objects for tests."""

    value = _DEFAULT_USER_ID


class UsernameHashFactory(DataclassFactory[UsernameHash]):
    """Build valid UsernameHash value objects for tests."""

    value = _DEFAULT_USERNAME_HASH


class MasterPasswordSaltFactory(DataclassFactory[MasterPasswordSalt]):
    """Build valid MasterPasswordSalt value objects for tests."""

    value = _DEFAULT_SALT


class ServerAuthHashFactory(DataclassFactory[ServerAuthHash]):
    """Build valid ServerAuthHash value objects for tests."""

    value = _DEFAULT_SERVER_AUTH_HASH


class KdfConfigurationFactory(DataclassFactory[KdfConfiguration]):
    """Build valid KdfConfiguration value objects for tests."""

    algorithm = _DEFAULT_KDF_CONFIGURATION.algorithm
    memory_kb = _DEFAULT_KDF_CONFIGURATION.memory_kb
    iterations = _DEFAULT_KDF_CONFIGURATION.iterations
    parallelism = _DEFAULT_KDF_CONFIGURATION.parallelism


class AggregateVersionFactory(DataclassFactory[AggregateVersion]):
    """Build valid AggregateVersion value objects for tests."""

    value = _DEFAULT_VERSION.value


class UserFactory(BaseFactory[User]):
    """Build User aggregate roots for integration tests."""

    __model__ = User

    id = UserIdFactory
    version = AggregateVersionFactory
    username_hash = UsernameHashFactory
    salt = MasterPasswordSaltFactory
    server_authentication_hash = ServerAuthHashFactory
    kdf_configuration = KdfConfigurationFactory

    @classmethod
    def is_supported_type(cls, value: Any) -> TypeGuard[type[User]]:
        """Return whether the provided type is supported by this factory."""
        return value is User

    @classmethod
    def get_model_fields(cls) -> list[FieldMeta]:
        """Describe the User fields used by the factory."""
        return [
            FieldMeta.from_type(annotation=UserId, name="id"),
            FieldMeta.from_type(annotation=AggregateVersion, name="version"),
            FieldMeta.from_type(annotation=UsernameHash, name="username_hash"),
            FieldMeta.from_type(annotation=MasterPasswordSalt, name="salt"),
            FieldMeta.from_type(
                annotation=ServerAuthHash, name="server_authentication_hash"
            ),
            FieldMeta.from_type(annotation=KdfConfiguration, name="kdf_configuration"),
        ]

    @classmethod
    def build(
        cls,
        *,
        user_id: str | UUID | UserId | None = None,
        version: int | AggregateVersion | None = None,
        username_hash: str | UsernameHash | None = None,
        **kwargs: Any,
    ) -> User:
        """Build a User aggregate, accepting raw ID, version, and username overrides."""
        if user_id is not None:
            kwargs["id"] = (
                user_id
                if isinstance(user_id, UserId)
                else UserIdFactory.build(value=_normalize_uuid(user_id))
            )
        if version is not None:
            kwargs["version"] = (
                version
                if isinstance(version, AggregateVersion)
                else AggregateVersionFactory.build(value=version)
            )
        if username_hash is not None:
            kwargs["username_hash"] = (
                username_hash
                if isinstance(username_hash, UsernameHash)
                else UsernameHashFactory.build(value=username_hash)
            )
        return super().build(**kwargs)


def _normalize_uuid(value: str | UUID) -> UUID:
    if isinstance(value, UUID):
        return value
    return UUID(value)
