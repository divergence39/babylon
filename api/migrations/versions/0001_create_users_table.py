"""Create users table."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from babylon.domain.value_objects.username import _HASHED_USERNAME_LENGTH

revision: str = "0001_create_users_table"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Apply the users table migration."""
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "username", sa.String(length=_HASHED_USERNAME_LENGTH), nullable=False
        ),
        sa.Column("salt", sa.LargeBinary(), nullable=False),
        sa.Column("server_auth_hash", sa.LargeBinary(), nullable=False),
        sa.Column("kdf_configuration", postgresql.JSONB(), nullable=False),
        sa.Column(
            "last_modification_time",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("clock_timestamp()"),
        ),
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

    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_users_last_modification_time()
        RETURNS trigger AS $$
        BEGIN
            NEW.last_modification_time = clock_timestamp();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_users_last_modification_time
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION set_users_last_modification_time();
        """
    )


def downgrade() -> None:
    """Revert the users table migration."""
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_users_last_modification_time ON users;
        """
    )
    op.execute(
        """
        DROP FUNCTION IF EXISTS set_users_last_modification_time;
        """
    )
    op.drop_table("users")
