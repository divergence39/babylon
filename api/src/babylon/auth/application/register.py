"""RegisterUser Use Case."""

import uuid
from dataclasses import dataclass

from babylon.auth.domain.entities import User
from babylon.auth.domain.ports import IUnitOfWork
from babylon.auth.domain.value_objects import (
    AggregateVersion,
    KdfConfiguration,
    MasterPasswordSalt,
    ServerAuthHash,
    UserId,
    UsernameHash,
)


@dataclass(frozen=True)
class RegisterUserCommandDTO:
    """Input Data Transfer Object for registering a new user."""

    username_hash: str
    server_auth_hash: str
    salt: str
    kdf_memory_cost: int
    kdf_time_cost: int
    kdf_parallelism: int


@dataclass(frozen=True)
class RegisterUserResponseDTO:
    """Output Data Transfer Object for registering a new user."""

    user_id: str


class RegisterUser:
    """Use case for registering a new user."""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, dto: RegisterUserCommandDTO) -> RegisterUserResponseDTO:
        """Register a new user based on provided information."""
        user = User(
            id=UserId(uuid.uuid7()),
            version=AggregateVersion(1),
            username_hash=UsernameHash(dto.username_hash),
            salt=MasterPasswordSalt(dto.salt),
            server_authentication_hash=ServerAuthHash(dto.server_auth_hash),
            kdf_configuration=KdfConfiguration(
                algorithm="argon2id",
                memory_kb=dto.kdf_memory_cost,
                iterations=dto.kdf_time_cost,
                parallelism=dto.kdf_parallelism,
            ),
        )

        async with self._uow as uow:
            await uow.users.add(user)
            await uow.commit()

        return RegisterUserResponseDTO(user_id=str(user.id.value))
