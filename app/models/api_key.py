from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class ApiKey(BaseModel):
    id: UUID
    key: str
    expires_at: datetime
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ApiKeyResponse(BaseModel):
    key: str
    expires_at: datetime 