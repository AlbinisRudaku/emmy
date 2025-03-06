"""add email to profiles

Revision ID: 007
Revises: 006
Create Date: 2024-02-09 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add email column to user_profiles table
    op.add_column('user_profiles', sa.Column('email', sa.String(), nullable=True))
    
    # Update existing profiles with email from users table
    op.execute("""
        UPDATE user_profiles
        SET email = users.email
        FROM users
        WHERE user_profiles.user_id = users.id
    """)
    
    # Make email column not nullable after populating data
    op.alter_column('user_profiles', 'email',
                    existing_type=sa.String(),
                    nullable=False)

def downgrade() -> None:
    op.drop_column('user_profiles', 'email') 