"""add user timezone_offset"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "20260215_0004"
down_revision: Union[str, None] = "20260215_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("timezone_offset", sa.Integer(), nullable=True, server_default=sa.text("0"))
    )


def downgrade() -> None:
    op.drop_column("users", "timezone_offset")
