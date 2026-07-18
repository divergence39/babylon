import pytest

from babylon.application.exceptions import UsernameAlreadyExistsError
from babylon.application.use_cases.registration import (
    RegisterUser,
    RegisterUserCommandDTO,
    RegisterUserResponseDTO,
)
from babylon.domain.exceptions import UsernameValidationError
from babylon.domain.value_objects import Username


class TestRegisterUser:
    @pytest.mark.asyncio
    async def test_register_user_happy_path(self, uow, valid_phc_hash):
        use_case = RegisterUser(uow)
        dto = RegisterUserCommandDTO(
            username="john.doe",
            server_auth_hash=valid_phc_hash,
            salt="Y29ycmVjdF9zYWx0X3ZhbHVlX2hlcmU=",
            kdf_memory_cost=65536,
            kdf_time_cost=3,
            kdf_parallelism=4,
        )
        response = await use_case(dto)
        assert isinstance(response, RegisterUserResponseDTO)
        assert response.user_id is not None
        assert uow.committed
        user = await uow.users.find_by_username(Username("john.doe"))
        assert user is not None
        assert str(user.id.value) == response.user_id

    @pytest.mark.asyncio
    async def test_register_user_username_already_exists(
        self, uow, valid_phc_hash, user_factory
    ):
        existing_user = user_factory("existing.user")
        await uow.users.save(existing_user)

        use_case = RegisterUser(uow)
        dto = RegisterUserCommandDTO(
            username="existing.user",
            server_auth_hash=valid_phc_hash,
            salt="Y29ycmVjdF9zYWx0X3ZhbHVlX2hlcmU=",
            kdf_memory_cost=65536,
            kdf_time_cost=3,
            kdf_parallelism=4,
        )

        with pytest.raises(UsernameAlreadyExistsError):
            await use_case(dto)

        assert not uow.committed
        assert uow.rolled_back

    @pytest.mark.asyncio
    async def test_register_user_invalid_domain_details(self, uow, valid_phc_hash):
        use_case = RegisterUser(uow)
        dto = RegisterUserCommandDTO(
            username="a",  # Invalid username length
            server_auth_hash=valid_phc_hash,
            salt="Y29ycmVjdF9zYWx0X3ZhbHVlX2hlcmU=",
            kdf_memory_cost=65536,
            kdf_time_cost=3,
            kdf_parallelism=4,
        )
        with pytest.raises(UsernameValidationError):
            await use_case(dto)
        assert not uow.committed
        assert uow.rolled_back
