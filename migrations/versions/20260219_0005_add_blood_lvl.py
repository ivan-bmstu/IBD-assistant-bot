from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260219_0005"
down_revision: Union[str, None] = "20260215_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'bowel_movements',
        sa.Column('blood_lvl', sa.Integer(), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('bowel_movements', 'blood_lvl')
