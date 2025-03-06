from pydantic import BaseModel, HttpUrl, EmailStr
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    preferences: Optional[Dict] = None

class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
    job_title: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[HttpUrl]
    preferences: Dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 