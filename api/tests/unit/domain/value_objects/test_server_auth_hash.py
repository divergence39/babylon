import pytest
from babylon.domain.exceptions import ServerAuthHashValidationError
from babylon.domain.value_objects import ServerAuthHash


class TestAuthHash:
    @pytest.mark.parametrize(
        "valid_blob",
        [
            # Standard Argon2 output
            "$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$c29tZWhhc2g",
            "$argon2id$v=19$m=131072,t=4,p=4$YW5vdGhlcnNhbHQ$YW5vdGhlcmhhc2g",
        ],
    )
    def test_create_valid_auth_hash(self, valid_blob: str) -> None:
        blob = ServerAuthHash(valid_blob)

        assert blob.value == valid_blob

    @pytest.mark.parametrize(
        "invalid_blob",
        [
            "",  # Empty
            "just_a_random_string",
            "$pbkdf2$iterations=1000$salt$hash",  # Wrong algorithm format
            "$argon2id$v=19$m=65536$missing_parameters",
        ],
    )
    def test_cannot_create_invalid_blob(self, invalid_blob: str) -> None:
        with pytest.raises(ServerAuthHashValidationError):
            ServerAuthHash(invalid_blob)
