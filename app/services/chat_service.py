from typing import Optional, Dict, List
from uuid import UUID, uuid4
import asyncio
from datetime import datetime

from app.core.config import get_settings
from app.core.cache import cache_manager
from app.core.metrics import CHAT_MESSAGES, LLM_LATENCY
from app.models.chat import ChatSession, Message, ChatResponse
from app.services.llm_service import LLMService
from app.core.exceptions import ChatbotError
from app.core.redis import redis_client

settings = get_settings()

class ChatService:
    def __init__(self):
        self.llm_service = LLMService()
    
    @cache_manager.cache_response(
        prefix="chat_response",
        ttl=300,
        key_builder=lambda self, instance_id, message, **kwargs: f"{instance_id}:{message}"
    )
    async def process_message(
        self,
        instance_id: UUID,
        message: str,
        session_id: Optional[UUID] = None,
        context: Optional[Dict] = None
    ) -> ChatResponse:
        try:
            # If no session_id provided, create new one
            if not session_id:
                session_id = uuid4()
            
            with LLM_LATENCY.time():
                response = await self.llm_service.generate_response(
                    message,
                    await self._get_message_history(session_id),
                    context
                )
            
            CHAT_MESSAGES.labels(
                instance_id=str(instance_id),
                status="success"
            ).inc()
            
            return ChatResponse(
                session_id=session_id,
                response=response,
                context=context
            )
            
        except Exception as e:
            CHAT_MESSAGES.labels(
                instance_id=str(instance_id),
                status="error"
            ).inc()
            raise ChatbotError(f"Error processing message: {str(e)}")
    
    async def _get_message_history(
        self,
        session_id: Optional[UUID]
    ) -> List[Message]:
        if not session_id:
            return []
        
        # Get message history from database or cache
        return await cache_manager.get_or_set(
            f"chat_history:{session_id}",
            lambda: self._fetch_message_history(session_id),
            ttl=3600
        )
    
    def _get_or_create_session(
        self,
        instance_id: UUID,
        session_id: Optional[UUID] = None
    ) -> ChatSession:
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]
        
        new_session = ChatSession(instance_id=instance_id)
        self._sessions[new_session.id] = new_session 

    async def create_session(
        self,
        instance_id: UUID,
        metadata: Optional[Dict] = None
    ) -> ChatSession:
        session = ChatSession(
            id=uuid4(),  # Generate new session ID
            instance_id=instance_id,
            metadata=metadata or {}
        )
        
        # Save to database if needed
        return session 