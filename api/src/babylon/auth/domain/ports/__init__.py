"""Domain port definitions."""

from .unit_of_work import IUnitOfWork
from .user_repository import IUserRepository

__all__ = [
    "IUnitOfWork",
    "IUserRepository",
]
