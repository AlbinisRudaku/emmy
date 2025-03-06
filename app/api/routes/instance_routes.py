from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.instance import Instance, InstanceCreate, InstanceUpdate, InstanceSettingsUpdate
from app.models.user import UserResponse
from app.services.instance_service import InstanceService
from app.core.settings_validation import validate_settings, validate_settings_section, get_section_schema

router = APIRouter()

@router.post("", response_model=Instance)
async def create_instance(
    instance_data: InstanceCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new instance"""
    instance_service = InstanceService(db)
    return await instance_service.create_instance(instance_data, current_user.id)

@router.get("", response_model=List[Instance])
async def list_instances(
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all instances for the current user"""
    instance_service = InstanceService(db)
    return await instance_service.list_instances(current_user.id)

@router.get("/{instance_id}", response_model=Instance)
async def get_instance(
    instance_id: UUID,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific instance"""
    instance_service = InstanceService(db)
    return await instance_service.get_instance(instance_id)

@router.put("/{instance_id}", response_model=Instance)
async def update_instance(
    instance_id: UUID,
    instance_data: InstanceUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an instance"""
    instance_service = InstanceService(db)
    return await instance_service.update_instance(instance_id, instance_data)

@router.patch("/{instance_id}/settings", response_model=Instance)
async def update_instance_settings(
    instance_id: UUID,
    settings_data: Dict[str, Any] = Body(...),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update instance settings with partial updates"""
    # Validate settings before updating
    errors = validate_settings(settings_data)
    if errors:
        raise HTTPException(
            status_code=422,
            detail={"message": "Invalid settings data", "errors": errors}
        )
    
    instance_service = InstanceService(db)
    return await instance_service.update_instance_settings(instance_id, settings_data)

@router.patch("/{instance_id}/settings/{section}", response_model=Instance)
async def update_settings_section(
    instance_id: UUID,
    section: str,
    section_data: Dict[str, Any] = Body(...),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a specific section of instance settings"""
    # Validate section data before updating
    errors = validate_settings_section(section, section_data)
    if errors:
        raise HTTPException(
            status_code=422,
            detail={"message": f"Invalid {section} settings", "errors": errors}
        )
    
    instance_service = InstanceService(db)
    return await instance_service.update_settings_section(instance_id, section, section_data)

@router.get("/{instance_id}/settings/schema")
async def get_settings_schema(
    instance_id: UUID,
    section: str = None,
    current_user: UserResponse = Depends(get_current_active_user),
):
    """Get JSON schema for instance settings or a specific section"""
    return get_section_schema(section)

@router.post("/{instance_id}/settings/reset", response_model=Instance)
async def reset_settings(
    instance_id: UUID,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Reset instance settings to default values"""
    instance_service = InstanceService(db)
    return await instance_service.reset_settings_to_default(instance_id)

@router.delete("/{instance_id}")
async def delete_instance(
    instance_id: UUID,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an instance"""
    instance_service = InstanceService(db)
    await instance_service.delete_instance(instance_id)
    return {"message": "Instance deleted successfully"} 