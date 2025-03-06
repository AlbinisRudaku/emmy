"""update user profiles

Revision ID: 006
Revises: 005
Create Date: 2024-02-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add new columns to user_profiles table
    op.add_column('user_profiles', sa.Column('job_title', sa.String(), nullable=True))
    op.add_column('user_profiles', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('user_profiles', sa.Column('location', sa.String(), nullable=True))
    op.add_column('user_profiles', sa.Column('bio', sa.String(), nullable=True))

def downgrade() -> None:
    # Remove the new columns
    op.drop_column('user_profiles', 'bio')
    op.drop_column('user_profiles', 'location')
    op.drop_column('user_profiles', 'phone')
    op.drop_column('user_profiles', 'job_title') 