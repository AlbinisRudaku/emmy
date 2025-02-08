"""add users table

Revision ID: 003
Revises: 002
Create Date: 2024-02-08 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Add user_id to instances table
    op.add_column('instances', sa.Column(
        'user_id',
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey('users.id'),
        nullable=True
    ))

def downgrade() -> None:
    op.drop_column('instances', 'user_id')
    op.drop_table('users') 