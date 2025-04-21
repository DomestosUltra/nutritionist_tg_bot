"""Create user_interactions table

Revision ID: initial_migration
Revises: 
Create Date: 2024-07-09

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'initial_migration'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_interactions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False, index=True),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('user_query', sa.Text(), nullable=False),
        sa.Column('bot_response', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('user_interactions') 