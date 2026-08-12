import pytest

from babylon.application.use_cases.registration import (
    GetLoginOptions,
    GetLoginOptionsQueryDTO,
    GetLoginOptionsResponseDTO,
)


class TestGetLoginOptions:
    @pytest.mark.asyncio
    async def test_get_login_options_user_exists(
        self, uow, salt_generator, user_factory
    ):
        valid_base64_salt = "UkVBTF9TQUxUX1ZBTFVFXzEyM19SRUFMX1NBTFRfMTI="
        existing_username_hash = "MpY6dddb+ipakoYR7mxT69OdERLt+aocCgrztICn9X8="
        existing_user = user_factory(
            existing_username_hash, salt=valid_base64_salt, kdf_mem=100000
        )
        await uow.users.save(existing_user)

        use_case = GetLoginOptions(uow, salt_generator)
        dto = GetLoginOptionsQueryDTO(username_hash=existing_username_hash)

        response = await use_case(dto)
        assert isinstance(response, GetLoginOptionsResponseDTO)
        assert response.salt == valid_base64_salt
        assert response.kdf_memory_cost == 100000
        assert response.kdf_time_cost == 3
        assert response.kdf_parallelism == 4
        assert not uow.committed
        assert not uow.rolled_back

    @pytest.mark.asyncio
    async def test_get_login_options_user_does_not_exist(self, uow, salt_generator):
        use_case = GetLoginOptions(uow, salt_generator)
        username_hash = "MpY6dddb+ipakoYR7mxT69OdERLt+aocCgrztICn9X8="

        dto = GetLoginOptionsQueryDTO(username_hash=username_hash)

        response = await use_case(dto)
        assert isinstance(response, GetLoginOptionsResponseDTO)
        # Should use the fake generator
        assert response.salt == "fake_salt_MpY6dddb+ipakoYR7mxT69OdERLt+aocCgrztICn9X8="
        # Should use some safe defaults
        assert response.kdf_memory_cost > 0
        assert response.kdf_time_cost > 0
        assert response.kdf_parallelism > 0
        assert not uow.committed
        assert not uow.rolled_back
