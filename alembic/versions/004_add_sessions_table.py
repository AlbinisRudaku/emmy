"""add sessions table

Revision ID: 004
Revises: 003
Create Date: 2024-02-08 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('session_data', postgresql.JSONB(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('ix_sessions_token', 'sessions', ['token'])

def downgrade() -> None:
    op.drop_index('ix_sessions_token')
    op.drop_index('ix_sessions_user_id')
    op.drop_table('sessions') 