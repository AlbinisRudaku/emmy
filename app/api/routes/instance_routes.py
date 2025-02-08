from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.instance import Instance, InstanceCreate, InstanceUpdate
from app.models.user import UserResponse
from app.services.instance_service import InstanceService

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