from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.models.instance import Instance, InstanceCreate, InstanceUpdate
from app.models.database.instance import DBInstance
from app.core.exceptions import InstanceNotFoundException

class InstanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_instance(self, instance_data: InstanceCreate, user_id: UUID) -> Instance:
        db_instance = DBInstance(
            user_id=user_id,
            name=instance_data.name,
            website_url=instance_data.website_url,
            settings=instance_data.settings or {}
        )
        
        self.db.add(db_instance)
        await self.db.commit()
        await self.db.refresh(db_instance)
        
        return Instance.from_orm(db_instance)
    
    async def get_instance(self, instance_id: UUID) -> Instance:
        query = select(DBInstance).where(DBInstance.id == instance_id)
        result = await self.db.execute(query)
        db_instance = result.scalar_one_or_none()
        
        if not db_instance:
            raise InstanceNotFoundException(str(instance_id))
            
        return Instance.from_orm(db_instance)
    
    async def get_instance_by_api_key(
        self,
        api_key: str
    ) -> Optional[Instance]:
        query = select(DBInstance).where(
            DBInstance.api_key == api_key,
            DBInstance.is_active == True
        )
        result = await self.db.execute(query)
        db_instance = result.scalar_one_or_none()
        
        if db_instance:
            return Instance.from_orm(db_instance)
        return None
    
    async def update_instance(
        self,
        instance_id: UUID,
        instance_data: InstanceUpdate
    ) -> Instance:
        query = update(DBInstance).where(DBInstance.id == instance_id)
        values = instance_data.dict(exclude_unset=True)
        await self.db.execute(query.values(**values))
        await self.db.commit()
        return await self.get_instance(instance_id)
    
    async def delete_instance(self, instance_id: UUID):
        query = delete(DBInstance).where(DBInstance.id == instance_id)
        result = await self.db.execute(query)
        await self.db.commit()
        if result.rowcount == 0:
            raise InstanceNotFoundException(str(instance_id))
    
    async def list_instances(self, user_id: UUID) -> List[Instance]:
        query = select(DBInstance).where(DBInstance.user_id == user_id)
        result = await self.db.execute(query)
        return [Instance.from_orm(instance) for instance in result.scalars().all()]

    def _generate_api_key(self) -> str:
        return f"sk_{secrets.token_urlsafe(32)}" 