#!/usr/bin/env python
"""
Script to migrate instance settings to the new structured schema.
This script should be run after deploying the new code but before using the new settings features.
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, engine
from app.models.database.instance import DBInstance
from app.models.instance_settings import get_default_settings


async def migrate_instance_settings():
    """
    Update all existing instances with the new settings schema structure.
    """
    print("Starting instance settings migration...")
    
    # Get default settings
    default_settings = get_default_settings()
    
    # Create async session
    async with AsyncSession(engine) as session:
        # Get all instances
        result = await session.execute(select(DBInstance))
        instances = result.scalars().all()
        
        print(f"Found {len(instances)} instances to update.")
        
        for instance in instances:
            # Get current settings
            current_settings = instance.settings or {}
            
            # Create new settings based on default structure
            new_settings = default_settings.copy()
            
            # Set identity name from instance name if present
            if 'identity' in new_settings:
                new_settings['identity']['name'] = instance.name
            
            # Try to map existing settings to new structure
            for section in default_settings.keys():
                if section in current_settings and isinstance(current_settings[section], dict):
                    for key, value in current_settings[section].items():
                        if key in new_settings[section]:
                            new_settings[section][key] = value
            
            # Update instance
            instance.settings = new_settings
            session.add(instance)
            
            print(f"Updated settings for instance {instance.id}")
        
        # Commit all changes
        await session.commit()
    
    print("Instance settings migration completed successfully!")


if __name__ == "__main__":
    asyncio.run(migrate_instance_settings()) 