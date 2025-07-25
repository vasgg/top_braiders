"""add_payment_id

Revision ID: 5a2fc1f897aa
Revises: f619c8057ebb
Create Date: 2025-06-17 13:45:10.782830

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5a2fc1f897aa"
down_revision: Union[str, None] = "f619c8057ebb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("payment_id", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "payment_id")
