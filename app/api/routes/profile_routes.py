from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.services.profile_service import ProfileService
from app.models.profile import ProfileUpdate, ProfileResponse
from app.models.user import UserResponse

router = APIRouter()

@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's profile"""
    profile_service = ProfileService(db)
    return await profile_service.get_profile(current_user.id)

@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile"""
    profile_service = ProfileService(db)
    return await profile_service.update_profile(current_user.id, profile_data) 