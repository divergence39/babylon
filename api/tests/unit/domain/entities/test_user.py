import uuid

import pytest
from babylon.domain.entities import User
from babylon.domain.value_objects import (
    KdfConfiguration,
    MasterPasswordSalt,
    ServerAuthHash,
    UserId,
    Username,
)


class TestUserEntity:
    @pytest.fixture
    def base_id(self) -> UserId:
        return UserId(uuid.uuid7())

    @pytest.fixture
    def valid_username(self) -> Username:
        return Username("spike.spiegel@example.com")

    @pytest.fixture
    def valid_salt(self) -> MasterPasswordSalt:
        return MasterPasswordSalt("a" * 32)

    @pytest.fixture
    def valid_hash(self) -> ServerAuthHash:
        return ServerAuthHash("$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$c29tZWhhc2g")

    @pytest.fixture
    def valid_kdf(self) -> KdfConfiguration:
        return KdfConfiguration("argon2id", 65536, 3, 4)

    # --- Tests ---

    def test_create_valid_user_entity(
        self,
        base_id: UserId,
        valid_username: Username,
        valid_salt: MasterPasswordSalt,
        valid_hash: ServerAuthHash,
        valid_kdf: KdfConfiguration,
    ) -> None:
        """Ensure entity creation wires value objects correctly."""
        user = User(
            id=base_id,
            username=valid_username,
            salt=valid_salt,
            server_authentication_hash=valid_hash,
            kdf_configuration=valid_kdf,
        )

        assert user.id == base_id
        assert user.username == valid_username
        assert user.kdf_configuration == valid_kdf
        assert user.salt == valid_salt
        assert user.server_authentication_hash == valid_hash

    def test_entities_are_compared_by_identity_only(
        self,
        base_id: UserId,
        valid_username: Username,
        valid_salt: MasterPasswordSalt,
        valid_hash: ServerAuthHash,
        valid_kdf: KdfConfiguration,
    ) -> None:
        """DDD Rule: Two entities with the same ID are the exact same entity,
        even if their attributes differ (e.g., the user changed their username).
        """
        user_1 = User(
            id=base_id,
            username=valid_username,
            salt=valid_salt,
            server_authentication_hash=valid_hash,
            kdf_configuration=valid_kdf,
        )

        user_2 = User(
            id=base_id,  # SAME ID
            username=Username("faye.valentine@example.com"),  # DIFFERENT USERNAME
            salt=valid_salt,
            server_authentication_hash=valid_hash,
            kdf_configuration=valid_kdf,
        )

        assert user_1 == user_2

    def test_entities_with_different_ids_are_not_equal(
        self,
        valid_username: Username,
        valid_salt: MasterPasswordSalt,
        valid_hash: ServerAuthHash,
        valid_kdf: KdfConfiguration,
    ) -> None:
        user_1 = User(
            id=UserId(uuid.uuid7()),
            username=valid_username,
            salt=valid_salt,
            server_authentication_hash=valid_hash,
            kdf_configuration=valid_kdf,
        )

        user_2 = User(
            id=UserId(uuid.uuid7()),  # DIFFERENT ID
            username=valid_username,  # SAME USERNAME
            salt=valid_salt,
            server_authentication_hash=valid_hash,
            kdf_configuration=valid_kdf,
        )

        assert user_1 != user_2

    def test_rotate_authentication_credentials(
        self,
        base_id: UserId,
        valid_username: Username,
        valid_salt: MasterPasswordSalt,
        valid_hash: ServerAuthHash,
        valid_kdf: KdfConfiguration,
    ) -> None:
        """Tests domain behavior. A password change requires updating the salt,
        hash, and potentially the KDF config all at once.
        """
        user = User(
            id=base_id,
            username=valid_username,
            salt=valid_salt,
            server_authentication_hash=valid_hash,
            kdf_configuration=valid_kdf,
        )

        new_salt = MasterPasswordSalt("b" * 64)
        new_hash = ServerAuthHash(
            "$argon2id$v=19$m=131072,t=4,p=4$bmV3c2FsdA$bmV3aGFzaA"
        )
        new_kdf = KdfConfiguration("argon2id", 131072, 4, 4)

        user.rotate_credentials(new_salt, new_hash, new_kdf)

        assert user.salt == new_salt
        assert user.server_authentication_hash == new_hash
        assert user.kdf_configuration == new_kdf
