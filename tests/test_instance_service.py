import pytest
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.instance_service import InstanceService
from app.models.instance import InstanceCreate, InstanceUpdate
from app.core.exceptions import InstanceNotFoundException

@pytest.mark.asyncio
async def test_create_instance(db_session: AsyncSession):
    service = InstanceService(db_session)
    instance_data = InstanceCreate(
        name="Test Instance",
        website_url="https://test.com"
    )
    
    instance = await service.create_instance(instance_data)
    
    assert instance.name == "Test Instance"
    assert instance.website_url == "https://test.com"
    assert instance.api_key.startswith("sk_")
    assert instance.is_active == True

@pytest.mark.asyncio
async def test_get_instance(db_session: AsyncSession, test_instance):
    service = InstanceService(db_session)
    
    instance = await service.get_instance(test_instance.id)
    
    assert instance.id == test_instance.id
    assert instance.name == test_instance.name
    assert instance.website_url == test_instance.website_url

@pytest.mark.asyncio
async def test_get_instance_not_found(db_session: AsyncSession):
    service = InstanceService(db_session)
    
    with pytest.raises(InstanceNotFoundException):
        await service.get_instance(UUID('00000000-0000-0000-0000-000000000000'))

@pytest.mark.asyncio
async def test_update_instance(db_session: AsyncSession, test_instance):
    service = InstanceService(db_session)
    update_data = InstanceUpdate(name="Updated Name")
    
    updated_instance = await service.update_instance(
        test_instance.id,
        update_data
    )
    
    assert updated_instance.name == "Updated Name"
    assert updated_instance.website_url == test_instance.website_url 