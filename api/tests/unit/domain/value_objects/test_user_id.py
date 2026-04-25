import uuid
from typing import cast

import pytest

from babylon.domain.exceptions import UserIdValidationError
from babylon.domain.value_objects import UserId


class TestUserId:
    def test_valid_user_id_creation(self) -> None:
        raw_uuid = uuid.uuid7()
        user_id = UserId(raw_uuid)

        assert user_id.value == raw_uuid

    @pytest.mark.parametrize(
        "invalid_id",
        [
            "12345",
            "not-a-uuid",
            uuid.uuid1(),
            uuid.uuid3(uuid.NAMESPACE_DNS, "babylon.invalid"),
            uuid.uuid4(),
            uuid.uuid5(uuid.NAMESPACE_DNS, "babylon.invalid"),
            uuid.uuid6(),
            uuid.uuid8(),
        ],
    )
    def test_cannot_create_invalid_id(self, invalid_id: object) -> None:
        with pytest.raises(UserIdValidationError):
            UserId(cast(uuid.UUID, invalid_id))

    def test_user_ids_must_be_unique_and_equatable(self) -> None:
        base_uuid = uuid.uuid7()
        id_1 = UserId(base_uuid)
        id_2 = UserId(base_uuid)

        assert id_1 == id_2

    def test_user_ids_must_be_immutable(self) -> None:
        user_id = UserId(uuid.uuid7())

        with pytest.raises((AttributeError, UserIdValidationError)):
            user_id.value = uuid.uuid7()
