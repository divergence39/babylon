"""Data Transfer Objects for Rotate Credentials Use Cases."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserCommandDTO:
    """Input Data Transfer Object for registering a new user."""

    username_hash: str
    server_auth_hash: str
    salt: str
    kdf_memory_cost: int
    kdf_time_cost: int
    kdf_parallelism: int


@dataclass(frozen=True)
class RegisterUserResponseDTO:
    """Output Data Transfer Object for registering a new user."""

    user_id: str


@dataclass(frozen=True)
class GetLoginOptionsQueryDTO:
    """Input Data Transfer Object for retrieving login options."""

    username_hash: str


@dataclass(frozen=True)
class GetLoginOptionsResponseDTO:
    """Output Data Transfer Object for retrieving login options."""

    salt: str
    kdf_memory_cost: int
    kdf_time_cost: int
    kdf_parallelism: int
