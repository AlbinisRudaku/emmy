"""
Script to add user_id column to instances table.
"""
import asyncio
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

# Database connection string from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

async def add_user_id_column():
    """Add user_id column to instances table."""
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL environment variable not set")
        return
    
    # Create async engine
    engine = create_async_engine(DATABASE_URL)
    
    # SQL to add user_id column if it doesn't exist
    sql = """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name='instances' AND column_name='user_id'
        ) THEN
            ALTER TABLE instances ADD COLUMN user_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
            ALTER TABLE instances ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id);
        END IF;
    END $$;
    """
    
    async with engine.begin() as conn:
        print("Adding user_id column to instances table...")
        await conn.execute(text(sql))
        print("Column added successfully.")

if __name__ == "__main__":
    asyncio.run(add_user_id_column()) 