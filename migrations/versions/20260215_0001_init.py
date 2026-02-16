"""init

Revision ID: 20260215_0001
Revises: None
Create Date: 2026-02-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260215_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("language_code", sa.String(length=10), server_default="ru"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "bowel_movements",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False),
        sa.Column("time", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)
    op.create_index("ix_bowel_movements_date", "bowel_movements", ["date"])
    op.create_index("ix_bowel_movements_user_id", "bowel_movements", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_bowel_movements_user_id", table_name="bowel_movements")
    op.drop_index("ix_bowel_movements_date", table_name="bowel_movements")
    op.drop_table("bowel_movements")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
