"""add stool_consistency

Revision ID: 20260215_0003
Revises: 20260215_0002
Create Date: 2026-02-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260215_0003"
down_revision: Union[str, None] = "20260215_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'bowel_movements',
        sa.Column('stool_consistency', sa.Integer(), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('bowel_movements', 'stool_consistency')
