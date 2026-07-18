"""RotateCredentials Use Case."""

import uuid

from babylon.application.exceptions import InvalidCredentialsError, UserNotFoundError
from babylon.domain.ports.unit_of_work import UnitOfWork
from babylon.domain.value_objects import (
    KdfConfiguration,
    MasterPasswordSalt,
    ServerAuthHash,
    UserId,
)

from .dtos import RotateCredentialsCommandDTO


class RotateCredentials:
    """Use case for rotating user credentials."""

    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def __call__(self, dto: RotateCredentialsCommandDTO) -> None:
        """Rotate user credentials based on provided information."""
        async with self._uow as uow:
            # Domain exception will automatically raise if UUID is malformed
            user_id = UserId(uuid.UUID(dto.user_id))
            user = await uow.users.find_by_id(user_id)

            if user is None:
                raise UserNotFoundError(dto.user_id)

            current_hash = ServerAuthHash(dto.current_server_auth_hash)
            if user.server_authentication_hash != current_hash:
                raise InvalidCredentialsError()

            new_salt = MasterPasswordSalt(dto.new_salt)
            new_hash = ServerAuthHash(dto.new_server_auth_hash)
            new_kdf = KdfConfiguration(
                algorithm="argon2id",
                memory_kb=dto.new_kdf_memory_cost,
                iterations=dto.new_kdf_time_cost,
                parallelism=dto.new_kdf_parallelism,
            )

            user.rotate_credentials(new_salt, new_hash, new_kdf)

            await uow.users.save(user)
            await uow.commit()
