"""GetLoginOptions Use Case."""

from dataclasses import dataclass

from babylon.auth.application.ports import IFakeSaltGenerator
from babylon.auth.domain.ports import IUnitOfWork
from babylon.auth.domain.value_objects import UsernameHash


@dataclass(frozen=True)
class GetLoginOptionsQueryDTO:
    """Input Data Transfer Object for retrieving login options."""

    username_hash: str


@dataclass(frozen=True)
class GetLoginOptionsResponseDTO:
    """Output Data Transfer Object for retrieving login options."""

    salt: str
    kdf_memory_cost: int
    kdf_time_cost: int
    kdf_parallelism: int


class GetLoginOptions:
    """Use case for retrieving login options for a given username."""

    def __init__(self, uow: IUnitOfWork, salt_generator: IFakeSaltGenerator):
        self._uow = uow
        self._salt_generator = salt_generator

    async def __call__(
        self, dto: GetLoginOptionsQueryDTO
    ) -> GetLoginOptionsResponseDTO:
        """Retrieve login options for a given username."""
        async with self._uow as uow:
            username_hash = UsernameHash(dto.username_hash)
            user = await uow.users.find_by_username_hash(username_hash)

            if user:
                return GetLoginOptionsResponseDTO(
                    salt=user.salt.value,
                    kdf_memory_cost=user.kdf_configuration.memory_kb,
                    kdf_time_cost=user.kdf_configuration.iterations,
                    kdf_parallelism=user.kdf_configuration.parallelism,
                )

            # Security requirement: Prevent user enumeration
            fake_salt = self._salt_generator.generate_fallback_salt(dto.username_hash)
            return GetLoginOptionsResponseDTO(
                salt=fake_salt,
                kdf_memory_cost=65536,
                kdf_time_cost=3,
                kdf_parallelism=4,
            )
