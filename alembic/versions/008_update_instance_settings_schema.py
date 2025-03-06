"""update instance settings schema

Revision ID: 008
Revises: 007
Create Date: 2024-03-01 19:03:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add your schema update operations here
    # For example:
    # op.add_column('instance_settings', sa.Column('new_column', sa.String(), nullable=True))
    pass

def downgrade() -> None:
    # Add your downgrade operations here
    # For example:
    # op.drop_column('instance_settings', 'new_column')
    pass 