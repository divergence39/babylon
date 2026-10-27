"""Interfaces requiring external implementations."""

from abc import ABC, abstractmethod


class IFakeSaltGenerator(ABC):
    """Generates deterministic fake salts to prevent User Enumeration."""

    @abstractmethod
    def generate_fallback_salt(self, username_hash: str) -> str:
        """Generate a fake salt deterministically based on the username hash."""
        pass
