"""initial

Revision ID: 001
Revises: 
Create Date: 2023-11-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create instances table
    op.create_table(
        'instances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('api_key', sa.String(), nullable=False, unique=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('website_url', sa.String(), nullable=False),
        sa.Column('settings', postgresql.JSONB(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Create chat_sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('instance_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('messages', postgresql.ARRAY(postgresql.JSONB()), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['instance_id'], ['instances.id'], ondelete='CASCADE')
    )

def downgrade() -> None:
    op.drop_table('chat_sessions')
    op.drop_table('instances') 