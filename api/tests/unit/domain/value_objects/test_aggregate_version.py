from typing import cast

import pytest

from babylon.domain.exceptions import AggregateVersionValidationError
from babylon.domain.value_objects import AggregateVersion


class TestAggregateVersion:
    def test_create_valid_version(self) -> None:
        version = AggregateVersion(1)

        assert version.value == 1

    def test_increment_version(self) -> None:
        version = AggregateVersion(1)

        assert version.next_version().value == 2

    @pytest.mark.parametrize(
        "invalid_version",
        [
            0,
            None,
            "1",
        ],
    )
    def test_cannot_create_invalid_version(self, invalid_version: object) -> None:
        with pytest.raises(AggregateVersionValidationError):
            AggregateVersion(cast(int, invalid_version))

    def test_versions_must_be_immutable(self) -> None:
        version = AggregateVersion(1)

        with pytest.raises((AttributeError, AggregateVersionValidationError)):
            version.value = 2
