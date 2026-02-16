"""add fsm_storage table

Revision ID: 20260215_0002
Revises: 20260215_0001
Create Date: 2026-02-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260215_0002"
down_revision: Union[str, None] = "20260215_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fsm_storage",
        sa.Column("key", sa.String(length=256), primary_key=True, nullable=False),
        sa.Column("state", sa.String(length=128), nullable=True),
        sa.Column(
            "data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("fsm_storage")
