from typing import List, Optional, Dict, Any
from uuid import UUID
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
import copy

from app.models.instance import Instance, InstanceCreate, InstanceUpdate, InstanceSettingsUpdate
from app.models.database.instance import DBInstance
from app.models.instance_settings import get_default_settings, InstanceSettings
from app.core.exceptions import InstanceNotFoundException

class InstanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_instance(self, instance_data: InstanceCreate, user_id: UUID) -> Instance:
        # Use default settings if none provided
        settings = instance_data.settings or get_default_settings()
        
        # Set the name in identity settings if not already set
        if "identity" in settings and "name" not in settings["identity"]:
            settings["identity"]["name"] = instance_data.name

        db_instance = DBInstance(
            user_id=user_id,
            api_key=self._generate_api_key(),
            name=instance_data.name,
            website_url=instance_data.website_url,
            settings=settings
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
    
    async def update_instance_settings(
        self,
        instance_id: UUID,
        settings_data: Dict[str, Any]
    ) -> Instance:
        """Update instance settings with deep merge capability."""
        # Get current instance
        instance = await self.get_instance(instance_id)
        
        # Deep merge settings
        updated_settings = self._deep_merge_settings(
            instance.settings, 
            settings_data
        )
        
        # Update instance with merged settings
        query = update(DBInstance).where(DBInstance.id == instance_id)
        await self.db.execute(query.values(settings=updated_settings))
        await self.db.commit()
        
        return await self.get_instance(instance_id)
    
    async def update_settings_section(
        self,
        instance_id: UUID,
        section: str,
        section_data: Dict[str, Any]
    ) -> Instance:
        """Update a specific section of instance settings."""
        # Get current instance
        instance = await self.get_instance(instance_id)
        
        # Create updated settings by copying current settings
        updated_settings = copy.deepcopy(instance.settings)
        
        # If section doesn't exist, create it
        if section not in updated_settings:
            updated_settings[section] = {}
            
        # Update section with deep merge
        updated_settings[section] = self._deep_merge_settings(
            updated_settings.get(section, {}),
            section_data
        )
        
        # Update instance with new settings
        query = update(DBInstance).where(DBInstance.id == instance_id)
        await self.db.execute(query.values(settings=updated_settings))
        await self.db.commit()
        
        return await self.get_instance(instance_id)
    
    async def reset_settings_to_default(
        self,
        instance_id: UUID
    ) -> Instance:
        """Reset instance settings to default values."""
        query = update(DBInstance).where(DBInstance.id == instance_id)
        await self.db.execute(query.values(settings=get_default_settings()))
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
        
    def _deep_merge_settings(
        self,
        original: Dict[str, Any],
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries, with updates taking precedence."""
        result = copy.deepcopy(original)
        
        for key, value in updates.items():
            # If both are dictionaries, merge them recursively
            if (
                key in result and 
                isinstance(result[key], dict) and 
                isinstance(value, dict)
            ):
                result[key] = self._deep_merge_settings(result[key], value)
            else:
                # Otherwise just update the value
                result[key] = value
                
        return result 