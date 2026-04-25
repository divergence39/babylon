from typing import cast

import pytest

from babylon.domain.exceptions import MasterPasswordSaltValidationError
from babylon.domain.value_objects import MasterPasswordSalt


class TestMasterPasswordSalt:
    @pytest.mark.parametrize(
        "valid_salt",
        [
            "a" * 32,  # Assuming 32-byte hex or base64 representation
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz012345/+" + "==",
            "b" * 64,
        ],
    )
    def test_create_valid_salt(self, valid_salt: str) -> None:
        salt = MasterPasswordSalt(valid_salt)

        assert salt.value == valid_salt

    @pytest.mark.parametrize(
        "invalid_salt",
        [
            "",  # Empty
            "short",  # Too short to be cryptographically secure
            None,
            "!" * 32,
        ],
    )
    def test_cannot_create_invalid_salt(self, invalid_salt: str | None) -> None:
        with pytest.raises(MasterPasswordSaltValidationError):
            MasterPasswordSalt(cast(str, invalid_salt))
