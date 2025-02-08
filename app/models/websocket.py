from pydantic import BaseModel
from typing import Optional, Dict, Literal
from uuid import UUID

class WebSocketMessage(BaseModel):
    type: Literal["message", "typing", "error"]
    content: str
    session_id: Optional[UUID] = None
    metadata: Optional[Dict] = None

class WebSocketResponse(BaseModel):
    type: Literal["message", "typing", "error"]
    content: str
    metadata: Optional[Dict] = None 