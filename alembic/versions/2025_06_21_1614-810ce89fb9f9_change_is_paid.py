"""change_is_paid

Revision ID: 810ce89fb9f9
Revises: 5630e84c7523
Create Date: 2025-06-21 16:14:26.885563

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "810ce89fb9f9"
down_revision: Union[str, None] = "5630e84c7523"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text("UPDATE users SET is_paid = FALSE WHERE is_paid IS NULL")
    )
    op.alter_column("users", "is_paid", existing_type=sa.BOOLEAN(), nullable=False)


def downgrade() -> None:
    op.alter_column("users", "is_paid", existing_type=sa.BOOLEAN(), nullable=True)
