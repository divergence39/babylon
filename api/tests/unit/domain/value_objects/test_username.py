from typing import cast

import pytest

from babylon.domain.exceptions import UsernameValidationError
from babylon.domain.value_objects import Username


class TestUsername:
    @pytest.mark.parametrize(
        "valid_user",
        [
            "spike_spiegel",
            "gintoki.sakata24",
            "mark-knopfler",
            "val1d.user_n4me-32",
        ],
    )
    def test_create_valid_username(self, valid_user: str) -> None:
        username = Username(valid_user)

        assert username.value == valid_user.lower()

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "",  # empty
            None,
            "ab",  # Too Short (length 2)
            "invalid@name!",  # Invalid characters
            "alice in wonderlan",  # No whitespaces
            "a" * 33,  # Too Long (length 33)
        ],
    )
    def test_cannot_create_invalid_username(self, invalid_name: str | None) -> None:
        with pytest.raises(UsernameValidationError):
            Username(cast(str, invalid_name))

    def test_usernames_are_equatable_and_case_insensitive(self) -> None:
        user1 = Username("Spike_Spiegel")
        user2 = Username("spike_spiegel")

        assert user1 == user2

    def test_usernames_must_be_immutable(self) -> None:
        user = Username("Spike_Spiegel")

        with pytest.raises((AttributeError, UsernameValidationError)):
            user.value = "gintoki_sakata"
