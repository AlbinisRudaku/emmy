from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.database.profile import DBUserProfile
from app.models.profile import ProfileUpdate, ProfileResponse
from app.core.exceptions import NotFoundException

class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile(self, user_id: UUID) -> ProfileResponse:
        query = select(DBUserProfile).where(DBUserProfile.user_id == user_id)
        result = await self.db.execute(query)
        profile = result.scalar_one_or_none()
        
        if not profile:
            profile = await self.create_profile(user_id)
        
        return ProfileResponse.from_orm(profile)

    async def create_profile(self, user_id: UUID) -> DBUserProfile:
        profile = DBUserProfile(user_id=user_id)
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def update_profile(
        self,
        user_id: UUID,
        profile_data: ProfileUpdate
    ) -> ProfileResponse:
        query = select(DBUserProfile).where(DBUserProfile.user_id == user_id)
        result = await self.db.execute(query)
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise NotFoundException("Profile not found")
        
        # Update only provided fields
        update_data = profile_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(profile, key, value)
        
        try:
            await self.db.commit()
            await self.db.refresh(profile)
            return ProfileResponse.from_orm(profile)
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            ) 