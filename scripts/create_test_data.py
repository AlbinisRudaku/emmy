import asyncio
from uuid import uuid4
import hashlib
from datetime import datetime
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.database.instance import DBInstance
from app.core.security import api_key_manager

# Simple password hashing function
def simple_hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Check if we have a users table model and import it
try:
    from app.models.database.user import DBUser
    HAS_USER_MODEL = True
except ImportError:
    HAS_USER_MODEL = False
    print("Warning: DBUser model not found. Creating instance without user_id.")

async def create_test_data():
    async with AsyncSessionLocal() as session:
        user_id = None
        
        # Create or retrieve test user if the model exists
        if HAS_USER_MODEL:
            try:
                # Check if test user already exists
                test_email = "test@example.com"
                existing_user_query = select(DBUser).where(DBUser.email == test_email)
                existing_user = await session.execute(existing_user_query)
                existing_user = existing_user.scalars().first()
                
                if existing_user:
                    # Use existing test user
                    user_id = existing_user.id
                    print(f"Using existing test user with email: {test_email}")
                else:
                    # Create new test user
                    test_user = DBUser(
                        id=uuid4(),
                        email=test_email,
                        hashed_password=simple_hash_password("password123"),
                        is_active=True,
                        is_admin=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(test_user)
                    await session.flush()  # Flush to get the ID without committing
                    user_id = test_user.id
                    print(f"Created new test user with email: {test_email}")
            except Exception as e:
                print(f"Error handling test user: {e}")
                # Continue without user_id
        
        # Check if we already have a test instance
        try:
            existing_instance_query = select(DBInstance).where(DBInstance.name == "Test Instance")
            existing_instance = await session.execute(existing_instance_query)
            existing_instance = existing_instance.scalars().first()
            
            if existing_instance:
                print(f"Test instance already exists with API key: {existing_instance.api_key}")
                return
        except Exception as e:
            print(f"Error checking for existing instance: {e}")
        
        # Create test instance
        test_instance = DBInstance(
            id=uuid4(),
            api_key=api_key_manager.create_api_key(),
            name="Test Instance",
            website_url="https://test.com",
            settings={
                "welcome_message": "Hello! How can I help you today?",
                "language": "en"
            }
        )
        
        # Set user_id if available
        if user_id is not None:
            test_instance.user_id = user_id
        
        try:
            session.add(test_instance)
            await session.commit()
            print(f"Created test instance with API key: {test_instance.api_key}")
        except Exception as e:
            await session.rollback()
            print(f"Error creating test instance: {e}")

if __name__ == "__main__":
    asyncio.run(create_test_data()) 