import pytest

from babylon.application.exceptions import UsernameAlreadyExistsError
from babylon.application.use_cases.registration import (
    RegisterUser,
    RegisterUserCommandDTO,
    RegisterUserResponseDTO,
)
from babylon.domain.exceptions import UsernameValidationError
from babylon.domain.value_objects import UsernameHash


class TestRegisterUser:
    @pytest.mark.asyncio
    async def test_register_user_happy_path(self, uow, valid_phc_hash):
        username_hash = "MpY6dddb+ipakoYR7mxT69OdERLt+aocCgrztICn9X8="

        use_case = RegisterUser(uow)
        dto = RegisterUserCommandDTO(
            username_hash=username_hash,
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
        user = await uow.users.find_by_username_hash(UsernameHash(username_hash))
        assert user is not None
        assert str(user.id.value) == response.user_id

    @pytest.mark.asyncio
    async def test_register_user_username_already_exists(
        self, uow, valid_phc_hash, user_factory
    ):
        existing_username_hash = "MpY6dddb+ipakoYR7mxT69OdERLt+aocCgrztICn9X8="
        existing_user = user_factory(existing_username_hash)
        await uow.users.save(existing_user)

        use_case = RegisterUser(uow)
        dto = RegisterUserCommandDTO(
            username_hash=existing_username_hash,
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
            username_hash="a",  # Invalid username hash length
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
