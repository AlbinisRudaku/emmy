from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID, uuid4

class Message(BaseModel):
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    instance_id: UUID
    messages: List[Message] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
class ChatRequest(BaseModel):
    instance_id: UUID
    message: str
    session_id: Optional[UUID] = None
    context: Optional[Dict] = None

class ChatResponse(BaseModel):
    session_id: UUID
    response: str
    context: Optional[Dict] = None 