import pytest

from babylon.application.exceptions import InvalidCredentialsError
from babylon.application.use_cases.authentication import (
    AuthenticateUser,
    AuthenticateUserQueryDTO,
    AuthenticateUserResponseDTO,
)


class TestAuthenticateUser:
    @pytest.mark.asyncio
    async def test_authenticate_user_happy_path(
        self, uow, user_factory, valid_phc_hash
    ):
        existing_user = user_factory("test.user")
        await uow.users.save(existing_user)

        use_case = AuthenticateUser(uow)
        dto = AuthenticateUserQueryDTO(
            username="test.user", server_auth_hash=valid_phc_hash
        )

        response = await use_case(dto)
        assert isinstance(response, AuthenticateUserResponseDTO)
        assert response.user_id == str(existing_user.id.value)
        assert not uow.committed
        assert not uow.rolled_back

    @pytest.mark.asyncio
    async def test_authenticate_user_sad_path_not_found(self, uow, valid_phc_hash):
        use_case = AuthenticateUser(uow)
        dto = AuthenticateUserQueryDTO(
            username="nonexistent.user", server_auth_hash=valid_phc_hash
        )

        with pytest.raises(InvalidCredentialsError):
            await use_case(dto)
        assert not uow.committed
        assert uow.rolled_back

    @pytest.mark.asyncio
    async def test_authenticate_user_sad_path_wrong_hash(self, uow, user_factory):
        existing_user = user_factory("test.user")
        await uow.users.save(existing_user)

        use_case = AuthenticateUser(uow)

        new_valid_phc_hash = "$argon2id$v=19$m=65536,\
t=3,p=4$c29tZXNhbHQ$d3Jvbmdhbndlcndyb25nYW53ZXJ3cm9uZ2Fud2Vyd3Jv"

        dto = AuthenticateUserQueryDTO(
            username="test.user", server_auth_hash=new_valid_phc_hash
        )

        with pytest.raises(InvalidCredentialsError):
            await use_case(dto)
        assert not uow.committed
        assert uow.rolled_back
