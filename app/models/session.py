from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict

class SessionInfo(BaseModel):
    id: UUID
    user_id: UUID
    expires_at: datetime
    session_data: Optional[Dict] = None
    created_at: datetime

    class Config:
        from_attributes = True 