"""add salary and is_active to employees

Revision ID: b06acfac470b
Revises: 
Create Date: 2026-10-16 09:14:00.240395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b06acfac470b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adding the new columns
    op.add_column(
        'employees', 
        sa.Column('salary', sa.Numeric(precision=10, scale=2), nullable=True)
    )
    op.add_column(
        'employees', 
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False)
    )
def downgrade() -> None:
    # Dropping the columns in case of rollback
    op.drop_column('employees', 'is_active')
    op.drop_column('employees', 'salary')
