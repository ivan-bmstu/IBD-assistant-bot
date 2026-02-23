from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260223_0007"
down_revision: Union[str, None] = "20260219_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'bowel_movements',
        sa.Column('is_false_urge', sa.Boolean(), nullable=False, server_default=sa.false())
    )

def downgrade() -> None:
    op.drop_column('bowel_movements', 'is_false_urge')
