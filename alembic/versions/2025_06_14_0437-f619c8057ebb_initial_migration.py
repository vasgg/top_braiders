"""initial_migration

Revision ID: f619c8057ebb
Revises:
Create Date: 2025-06-14 04:37:29.813195

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f619c8057ebb"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("fullname", sa.String(), nullable=False),
        sa.Column("username", sa.String(length=32), nullable=True),
        sa.Column("fio", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("experience", sa.String(), nullable=True),
        sa.Column("portfolio", sa.String(), nullable=True),
        sa.Column("essay", sa.String(), nullable=True),
        sa.Column("photo_id", sa.String(), nullable=True),
        sa.Column("screenshot", sa.String(), nullable=True),
        sa.Column("is_paid", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("users")
