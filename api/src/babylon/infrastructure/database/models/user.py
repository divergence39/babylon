"""SQLAlchemy ORM model for persisted users."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    FetchedValue,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from babylon.domain.value_objects.username import _HASHED_USERNAME_LENGTH
from babylon.infrastructure.database.base import Base


class UserModel(Base):
    """ORM mapping for the users table."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        CheckConstraint("version > 0", name="ck_users_version_positive"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column(
        String(length=_HASHED_USERNAME_LENGTH), nullable=False
    )
    salt: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    server_auth_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    kdf_configuration: Mapped[dict[str, int | str]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
    )
    last_modification_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("clock_timestamp()"),
        server_onupdate=FetchedValue(),
    )
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )

    @declared_attr.directive
    def __mapper_args__(cls) -> dict[str, Any]:
        return {
            "version_id_col": cls.version,
            "version_id_generator": False,
        }
