"""Create users table."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_create_users_table"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Apply the users table migration."""
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=32), nullable=False),
        sa.Column("salt", sa.LargeBinary(), nullable=False),
        sa.Column("server_auth_hash", sa.LargeBinary(), nullable=False),
        sa.Column("kdf_configuration", postgresql.JSONB(), nullable=False),
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.CheckConstraint("version > 0", name="ck_users_version_positive"),
    )


def downgrade() -> None:
    """Revert the users table migration."""
    op.drop_table("users")
