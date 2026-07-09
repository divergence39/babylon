"""GetLoginOptions Use Case."""

from babylon.application.ports.salt_generator import IFakeSaltGenerator
from babylon.domain.ports.unit_of_work import UnitOfWork
from babylon.domain.value_objects import Username

from .dtos import GetLoginOptionsQueryDTO, GetLoginOptionsResponseDTO


class GetLoginOptions:
    """Use case for retrieving login options for a given username."""

    def __init__(self, uow: UnitOfWork, salt_generator: IFakeSaltGenerator):
        self._uow = uow
        self._salt_generator = salt_generator

    async def __call__(
        self, dto: GetLoginOptionsQueryDTO
    ) -> GetLoginOptionsResponseDTO:
        """Retrieve login options for a given username."""
        async with self._uow as uow:
            username = Username(dto.username)
            user = await uow.users.find_by_username(username)

            if user:
                return GetLoginOptionsResponseDTO(
                    salt=user.salt.value,
                    kdf_memory_cost=user.kdf_configuration.memory_kb,
                    kdf_time_cost=user.kdf_configuration.iterations,
                    kdf_parallelism=user.kdf_configuration.parallelism,
                )

            # Security requirement: Prevent user enumeration
            fake_salt = self._salt_generator.generate_fallback_salt(dto.username)
            return GetLoginOptionsResponseDTO(
                salt=fake_salt,
                kdf_memory_cost=65536,
                kdf_time_cost=3,
                kdf_parallelism=4,
            )
