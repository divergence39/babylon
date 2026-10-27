"""AuthenticateUser Use Case."""

from dataclasses import dataclass

from babylon.auth.domain.exceptions import InvalidCredentialsError
from babylon.auth.domain.ports import IUnitOfWork
from babylon.auth.domain.value_objects import ServerAuthHash, UsernameHash


@dataclass(frozen=True)
class AuthenticateUserQueryDTO:
    """Input Data Transfer Object for authenticating a user."""

    username_hash: str
    server_auth_hash: str


@dataclass(frozen=True)
class AuthenticateUserResponseDTO:
    """Output Data Transfer Object for authenticating a user."""

    user_id: str


class AuthenticateUser:
    """Use case for authenticating a user."""

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(
        self, dto: AuthenticateUserQueryDTO
    ) -> AuthenticateUserResponseDTO:
        """Authenticate a user based on provided credentials."""
        async with self._uow as uow:
            username_hash = UsernameHash(dto.username_hash)
            user = await uow.users.find_by_username_hash(username_hash)

            if user is None:
                raise InvalidCredentialsError()

            provided_hash = ServerAuthHash(dto.server_auth_hash)

            if user.server_authentication_hash != provided_hash:
                raise InvalidCredentialsError()

            return AuthenticateUserResponseDTO(user_id=str(user.id.value))
