import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import uuid

from app.core.database import Base
from app.main import app
from app.core.database import get_db
from app.models.database.instance import DBInstance

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True
)

# Create test session factory
TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db_setup():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(
    test_db_setup
) -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
        await session.close()

@pytest.fixture
async def client(db_session: AsyncSession) -> Generator:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
async def test_instance(db_session: AsyncSession) -> DBInstance:
    instance = DBInstance(
        id=uuid.uuid4(),
        api_key="test_key",
        name="Test Instance",
        website_url="https://test.com",
        settings={}
    )
    db_session.add(instance)
    await db_session.commit()
    await db_session.refresh(instance)
    return instance 