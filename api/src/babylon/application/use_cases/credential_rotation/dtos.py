"""Data Transfer Objects for Rotate Credentials Use Cases."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RotateCredentialsCommandDTO:
    """Input Data Transfer Object for rotating user credentials."""

    user_id: str
    current_server_auth_hash: str
    new_salt: str
    new_server_auth_hash: str
    new_kdf_memory_cost: int
    new_kdf_time_cost: int
    new_kdf_parallelism: int
