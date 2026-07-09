import uuid

import pytest

from babylon.application.exceptions import InvalidCredentialsError, UserNotFoundError
from babylon.application.use_cases.credential_rotation import (
    RotateCredentials,
    RotateCredentialsCommandDTO,
)


@pytest.fixture
def new_valid_phc_hash() -> str:
    """Fixture for a valid PHC hash."""
    return "$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$dmFsaWRoYXNoZm9ydGVzdGluZw=="


class TestRotateCredentials:
    @pytest.mark.asyncio
    async def test_rotate_credentials_happy_path(
        self, uow, user_factory, valid_phc_hash, new_valid_phc_hash
    ):
        existing_user = user_factory("test.user")
        original_version = existing_user.version.value
        await uow.users.save(existing_user)

        use_case = RotateCredentials(uow)

        dto = RotateCredentialsCommandDTO(
            user_id=str(existing_user.id.value),
            current_server_auth_hash=valid_phc_hash,
            new_salt="Y29ycmVjdF9zYWx0X3ZhbHVlX2hlcmU=",
            new_server_auth_hash=new_valid_phc_hash,
            new_kdf_memory_cost=100000,
            new_kdf_time_cost=4,
            new_kdf_parallelism=2,
        )

        await use_case(dto)
        assert uow.committed

        # Check updated user
        user = await uow.users.find_by_id(existing_user.id)
        assert user.salt.value == "Y29ycmVjdF9zYWx0X3ZhbHVlX2hlcmU="
        assert user.server_authentication_hash.value == new_valid_phc_hash
        assert user.kdf_configuration.memory_kb == 100000
        assert user.kdf_configuration.iterations == 4
        assert user.kdf_configuration.parallelism == 2
        assert user.version.value == original_version + 1

    @pytest.mark.asyncio
    async def test_rotate_credentials_user_not_found(self, uow, valid_phc_hash):
        use_case = RotateCredentials(uow)
        dto = RotateCredentialsCommandDTO(
            user_id=str(uuid.uuid7()),
            current_server_auth_hash=valid_phc_hash,
            new_salt="Y29ycmVjdF9zYWx0X3ZhbHVlX2hlcmU=",
            new_server_auth_hash=valid_phc_hash,
            new_kdf_memory_cost=100000,
            new_kdf_time_cost=4,
            new_kdf_parallelism=2,
        )

        with pytest.raises(UserNotFoundError):
            await use_case(dto)

        assert not uow.committed
        assert uow.rolled_back

    @pytest.mark.asyncio
    async def test_rotate_credentials_wrong_hash(
        self, uow, user_factory, valid_phc_hash, new_valid_phc_hash
    ):
        existing_user = user_factory("test.user")
        await uow.users.save(existing_user)

        use_case = RotateCredentials(uow)

        dto = RotateCredentialsCommandDTO(
            user_id=str(existing_user.id.value),
            current_server_auth_hash=new_valid_phc_hash,
            new_salt="Y29ycmVjdF9zYWx0X3ZhbHVlX2hlcmU=",
            new_server_auth_hash=valid_phc_hash,
            new_kdf_memory_cost=100000,
            new_kdf_time_cost=4,
            new_kdf_parallelism=2,
        )

        with pytest.raises(InvalidCredentialsError):
            await use_case(dto)

        assert not uow.committed
        assert uow.rolled_back
