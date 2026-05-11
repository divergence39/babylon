"""SQLAlchemy ORM model for persisted users."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import LargeBinary, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from babylon.infrastructure.database.base import Base


class UserModel(Base):
    """ORM mapping for the users table."""

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("username", name="uq_users_username"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column(String(length=32), nullable=False)
    salt: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    server_auth_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    kdf_configuration: Mapped[dict[str, int | str]] = mapped_column(
        JSONB,
        nullable=False,
    )
