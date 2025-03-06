from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

from app.models.instance_settings import InstanceSettings, get_default_settings

class Instance(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    api_key: str
    name: str
    website_url: str
    settings: Dict[str, Any] = Field(default_factory=get_default_settings)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True

class InstanceCreate(BaseModel):
    name: str
    website_url: str
    settings: Optional[Dict[str, Any]] = None

class InstanceUpdate(BaseModel):
    name: Optional[str] = None
    website_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class InstanceSettingsUpdate(BaseModel):
    """Model for partial updates to instance settings."""
    settings: Dict[str, Any] 