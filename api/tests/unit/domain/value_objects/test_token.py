"""Unit tests for the Token value object."""

from typing import cast

import pytest

from babylon.domain.exceptions import TokenValidationError
from babylon.domain.value_objects import Token


class TestToken:
    @pytest.mark.parametrize(
        "valid_token",
        [
            "valid-token-string-123",
            "abc.def.ghi",
            "BearerLikeTokenWithMixedChars_123-XYZ",
        ],
    )
    def test_create_valid_token(self, valid_token: str) -> None:
        token = Token(valid_token)

        assert token.value == valid_token

    def test_token_with_whitespace_should_normalize(self) -> None:
        raw_value = "basic-token-value"

        token = Token("  " + raw_value + "  ")

        assert token.value == raw_value

    @pytest.mark.parametrize("invalid_token", ["", "   "])
    def test_cannot_create_empty_or_whitespace_token(self, invalid_token: str) -> None:
        with pytest.raises(TokenValidationError, match="cannot be empty or whitespace"):
            Token(invalid_token)

    @pytest.mark.parametrize(
        "invalid_token", [None, 123, 12.5, b"token-bytes", object()]
    )
    def test_cannot_create_token_with_non_string_input(
        self, invalid_token: object
    ) -> None:
        with pytest.raises(TokenValidationError, match="must be a string"):
            Token(cast(str, invalid_token))

    def test_tokens_are_equatable_by_normalized_value(self) -> None:
        token_1 = Token("token-value")
        token_2 = Token("  token-value  ")

        assert token_1 == token_2

    def test_tokens_must_be_immutable(self) -> None:
        token = Token("stable-token")

        with pytest.raises((AttributeError, TokenValidationError)):
            token.value = "new-token"
