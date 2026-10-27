"""RotateCredentials Use Case."""

import uuid
from dataclasses import dataclass

from babylon.auth.application.exceptions import UserNotFoundError
from babylon.auth.domain.ports import IUnitOfWork
from babylon.auth.domain.value_objects import (
    KdfConfiguration,
    MasterPasswordSalt,
    ServerAuthHash,
    UserId,
)


@dataclass(frozen=True)
class RotateCredentialsCommandDTO:
    """Input Data Transfer Object for rotating user credentials."""

    user_id: str
    current_server_auth_hash: str
    new_salt: str
    new_server_auth_hash: str
    new_kdf_memory_cost: int
    new_kdf_time_cost: int
    new_kdf_parallelism: int


class RotateCredentials:
    """Use case for rotating user credentials."""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, dto: RotateCredentialsCommandDTO) -> None:
        """Rotate user credentials based on provided information."""
        user_id = UserId(uuid.UUID(dto.user_id))

        async with self._uow as uow:
            user = await uow.users.find_by_id(user_id)

            if user is None:
                raise UserNotFoundError(dto.user_id)

            current_auth_hash = ServerAuthHash(dto.current_server_auth_hash)
            new_salt = MasterPasswordSalt(dto.new_salt)
            new_auth_hash = ServerAuthHash(dto.new_server_auth_hash)
            new_kdf = KdfConfiguration(
                algorithm="argon2id",
                memory_kb=dto.new_kdf_memory_cost,
                iterations=dto.new_kdf_time_cost,
                parallelism=dto.new_kdf_parallelism,
            )

            user.rotate_credentials(current_auth_hash, new_salt, new_auth_hash, new_kdf)

            await uow.users.update(user)
            await uow.commit()
