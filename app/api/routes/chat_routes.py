from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from uuid import UUID

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.core.security import verify_api_key

router = APIRouter()
chat_service = ChatService()

@router.post("/message", response_model=ChatResponse)
async def process_message(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    # If client doesn't provide session_id, it will be None and a new one will be generated
    try:
        response = await chat_service.process_message(
            instance_id=request.instance_id,
            message=request.message,
            session_id=request.session_id,  # Optional
            context=request.context
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 