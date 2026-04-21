from typing import cast

import pytest
from babylon.domain.exceptions import UsernameValidationError
from babylon.domain.value_objects import Username


class TestUsername:
    @pytest.mark.parametrize(
        "valid_user",
        [
            "spike@spiegel.com",
            "gintoki.sakata24@yorozuya.jp",
            "mark_knopfler@direstraits.net",
            "very-long_username-is_valid.32@email.com",
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
            "a@b.c",  # Too Short
            "invalid@name!",  # Invalid characters
            "alice in wonderlan",  # No whitespaces
        ],
    )
    def test_cannot_create_invalid_username(self, invalid_name: str | None) -> None:
        with pytest.raises(UsernameValidationError):
            Username(cast(str, invalid_name))

    def test_usernames_are_equatable_and_case_insensitive(self) -> None:
        user1 = Username("Spike@Spiegel.com")
        user2 = Username("spike@spiegel.com")

        assert user1 == user2

    def test_usernames_must_be_immutable(self) -> None:
        user = Username("Spike@Spiegel.com")

        with pytest.raises((AttributeError, UsernameValidationError)):
            user.value = "gintoki-sakata"
