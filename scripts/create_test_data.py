import asyncio
from uuid import uuid4
from app.core.database import AsyncSessionLocal
from app.models.database.instance import DBInstance
from app.core.security import api_key_manager

async def create_test_data():
    async with AsyncSessionLocal() as session:
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
        
        session.add(test_instance)
        await session.commit()
        
        print(f"Created test instance with API key: {test_instance.api_key}")

if __name__ == "__main__":
    asyncio.run(create_test_data()) 