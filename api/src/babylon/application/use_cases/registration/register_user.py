"""RegisterUser Use Case."""

import uuid

from babylon.application.exceptions import UsernameAlreadyExistsError
from babylon.domain.entities import User
from babylon.domain.ports.unit_of_work import UnitOfWork
from babylon.domain.value_objects import (
    AggregateVersion,
    KdfConfiguration,
    MasterPasswordSalt,
    ServerAuthHash,
    UserId,
    UsernameHash,
)

from .dtos import RegisterUserCommandDTO, RegisterUserResponseDTO


class RegisterUser:
    """Use case for registering a new user."""

    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def __call__(self, dto: RegisterUserCommandDTO) -> RegisterUserResponseDTO:
        """Register a new user based on provided information."""
        async with self._uow as uow:
            username_hash = UsernameHash(dto.username_hash)
            existing_user = await uow.users.find_by_username_hash(username_hash)
            if existing_user is not None:
                raise UsernameAlreadyExistsError(dto.username_hash)

            user = User(
                id=UserId(uuid.uuid7()),
                version=AggregateVersion(1),
                username_hash=username_hash,
                salt=MasterPasswordSalt(dto.salt),
                server_authentication_hash=ServerAuthHash(dto.server_auth_hash),
                kdf_configuration=KdfConfiguration(
                    algorithm="argon2id",
                    memory_kb=dto.kdf_memory_cost,
                    iterations=dto.kdf_time_cost,
                    parallelism=dto.kdf_parallelism,
                ),
            )

            await uow.users.save(user)
            await uow.commit()

            return RegisterUserResponseDTO(user_id=str(user.id.value))
