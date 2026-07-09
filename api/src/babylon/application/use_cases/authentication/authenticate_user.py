"""AuthenticateUser Use Case."""

from babylon.application.exceptions import InvalidCredentialsError
from babylon.domain.ports.unit_of_work import UnitOfWork
from babylon.domain.value_objects import ServerAuthHash, Username

from .dtos import AuthenticateUserQueryDTO, AuthenticateUserResponseDTO


class AuthenticateUser:
    """Use case for authenticating a user."""

    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def __call__(
        self, dto: AuthenticateUserQueryDTO
    ) -> AuthenticateUserResponseDTO:
        """Authenticate a user based on provided credentials."""
        async with self._uow as uow:
            username = Username(dto.username)
            user = await uow.users.find_by_username(username)

            if user is None:
                raise InvalidCredentialsError()

            provided_hash = ServerAuthHash(dto.server_auth_hash)

            # Using entity's value object exact match to verify the credentials.
            # Value Object comparison natively works if implemented appropriately.
            if user.server_authentication_hash != provided_hash:
                raise InvalidCredentialsError()

            return AuthenticateUserResponseDTO(user_id=str(user.id.value))
