"""add_is_published

Revision ID: 5630e84c7523
Revises: 5a2fc1f897aa
Create Date: 2025-06-20 16:28:34.653224

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5630e84c7523"
down_revision: Union[str, None] = "5a2fc1f897aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_published", sa.Boolean(), server_default="false", nullable=False))


def downgrade() -> None:
    op.drop_column("users", "is_published")
