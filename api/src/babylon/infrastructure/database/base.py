"""Shared SQLAlchemy declarative base for all persistence models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """The foundational SQLAlchemy Declarative Base.

    All domain models will inherit from this class to register their metadata.
    """

    pass
