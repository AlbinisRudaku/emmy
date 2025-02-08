from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID, uuid4

class Instance(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    api_key: str
    name: str
    website_url: str
    settings: Dict = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class InstanceCreate(BaseModel):
    name: str
    website_url: str
    settings: Optional[Dict] = None

class InstanceUpdate(BaseModel):
    name: Optional[str] = None
    website_url: Optional[str] = None
    settings: Optional[Dict] = None
    is_active: Optional[bool] = None 