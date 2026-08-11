from typing import cast

import pytest

from babylon.domain.exceptions import UsernameValidationError
from babylon.domain.value_objects import UsernameHash


class TestUsername:
    @pytest.mark.parametrize(
        "valid_user",
        [
            "MpY6dddb+ipakoYR7mxT69OdERLt+aocCgrztICn9X8=",
            "ziciPa56GT7tKXHt5xua255MCsQAAjsFQEQFfWcZyUU=",
        ],
    )
    def test_create_valid_username(self, valid_user: str) -> None:
        username_hash = UsernameHash(valid_user)

        assert username_hash.value == valid_user

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "",  # empty
            None,
            "ab",  # Too Short (length 2)
            "invalid@name!",  # Invalid characters
            "alice in wonderlan",  # No whitespaces
            "a" * 33,  # Too Long (length 33)
            "Spike_Spiegel",  # Not hashed
        ],
    )
    def test_cannot_create_invalid_username(self, invalid_name: str | None) -> None:
        with pytest.raises(UsernameValidationError):
            UsernameHash(cast(str, invalid_name))

    def test_usernames_are_equatable(self) -> None:
        user1 = UsernameHash("MpY6dddb+ipakoYR7mxT69OdERLt+aocCgrztICn9X8=")
        user2 = UsernameHash("MpY6dddb+ipakoYR7mxT69OdERLt+aocCgrztICn9X8=")

        assert user1 == user2

    def test_usernames_must_be_immutable(self) -> None:
        username = UsernameHash("MpY6dddb+ipakoYR7mxT69OdERLt+aocCgrztICn9X8=")

        with pytest.raises((AttributeError, UsernameValidationError)):
            username.value = "ziciPa56GT7tKXHt5xua255MCsQAAjsFQEQFfWcZyUU="
