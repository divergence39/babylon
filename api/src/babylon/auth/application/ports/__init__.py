"""Application-level ports for the authentication domain."""

from babylon.auth.application.ports.salt_generator import IFakeSaltGenerator

__all__ = ["IFakeSaltGenerator"]
