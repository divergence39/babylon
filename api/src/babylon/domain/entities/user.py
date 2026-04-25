"""User aggregate root entity for account-level domain operations."""

from typing import Any, Final

from babylon.domain.exceptions import UserValidationError
from babylon.domain.value_objects import (
    KdfConfiguration,
    MasterPasswordSalt,
    ServerAuthHash,
    UserId,
    Username,
)

_ID_TYPE_ERROR: Final[str] = "id must be a UserId"
_USERNAME_TYPE_ERROR: Final[str] = "username must be a Username"
_SALT_TYPE_ERROR: Final[str] = "salt must be a MasterPasswordSalt"
_AUTH_HASH_TYPE_ERROR: Final[str] = "the authentication hash must be a ServerAuthHash"
_KDF_CONFIGURATION_TYPE_ERROR: Final[str] = (
    "kdf_configuration must be a KdfConfiguration"
)


class User:
    """Registered user aggregate identified by immutable entity identity.

    Attributes:
        id (UserId): The user's unique identity.
        username (Username): The user's canonical username.
        salt (MasterPasswordSalt): The persisted salt for master-password derivation.
        server_authentication_hash (ServerAuthHash): The persisted server auth hash.
        kdf_configuration (KdfConfiguration): The active Argon2id configuration.
    """

    def __init__(
        self,
        id: UserId,
        username: Username,
        salt: MasterPasswordSalt,
        server_authentication_hash: ServerAuthHash,
        kdf_configuration: KdfConfiguration,
    ) -> None:
        if not isinstance(id, UserId):
            raise UserValidationError(_ID_TYPE_ERROR)
        if not isinstance(username, Username):
            raise UserValidationError(_USERNAME_TYPE_ERROR)
        if not isinstance(salt, MasterPasswordSalt):
            raise UserValidationError(_SALT_TYPE_ERROR)
        if not isinstance(server_authentication_hash, ServerAuthHash):
            raise UserValidationError(_AUTH_HASH_TYPE_ERROR)
        if not isinstance(kdf_configuration, KdfConfiguration):
            raise UserValidationError(_KDF_CONFIGURATION_TYPE_ERROR)

        self._id = id
        self._username = username
        self._salt = salt
        self._server_authentication_hash = server_authentication_hash
        self._kdf_configuration = kdf_configuration

    @property
    def id(self) -> UserId:
        """The user's unique identity."""
        return self._id

    @property
    def username(self) -> Username:
        """The user's canonical username."""
        return self._username

    @property
    def salt(self) -> MasterPasswordSalt:
        """The persisted salt for master-password derivation."""
        return self._salt

    @property
    def server_authentication_hash(self) -> ServerAuthHash:
        """The persisted server auth hash."""
        return self._server_authentication_hash

    @property
    def kdf_configuration(self) -> KdfConfiguration:
        """The active Argon2id configuration."""
        return self._kdf_configuration

    def rotate_credentials(
        self,
        new_salt: MasterPasswordSalt,
        new_server_auth_hash: ServerAuthHash,
        new_kdf_configuration: KdfConfiguration,
    ) -> None:
        """Rotate all credential-related attributes in a single state transition.

        Args:
            new_salt (MasterPasswordSalt): The newly derived master password salt.
            new_server_auth_hash (ServerAuthHash): The newly computed Argon2id PHC hash.
            new_kdf_configuration (KdfConfiguration):
                The newly selected KDF configuration.
        """
        if not isinstance(new_salt, MasterPasswordSalt):
            raise UserValidationError(_SALT_TYPE_ERROR)
        if not isinstance(new_server_auth_hash, ServerAuthHash):
            raise UserValidationError(_AUTH_HASH_TYPE_ERROR)
        if not isinstance(new_kdf_configuration, KdfConfiguration):
            raise UserValidationError(_KDF_CONFIGURATION_TYPE_ERROR)

        self._salt = new_salt
        self._server_authentication_hash = new_server_auth_hash
        self._kdf_configuration = new_kdf_configuration

    def __eq__(self, other: Any) -> bool:
        """Compare users by entity identity only.

        Args:
            other (Any): The other object to compare against.

        Returns:
            bool: True if other is a User with the same identity, otherwise False.
        """
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Return a stable hash based on user identity.

        Returns:
            int: The hash value of the user's ID.
        """
        return hash(self.id)
