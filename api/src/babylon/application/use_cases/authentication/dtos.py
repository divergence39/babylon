"""Data Transfer Objects for Authentication Use Cases."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticateUserQueryDTO:
    """Input Data Transfer Object for authenticating a user."""

    username_hash: str
    server_auth_hash: str


@dataclass(frozen=True)
class AuthenticateUserResponseDTO:
    """Output Data Transfer Object for authenticating a user."""

    user_id: str
