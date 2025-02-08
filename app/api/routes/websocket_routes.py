from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict
from uuid import UUID
import json
import asyncio

from app.models.websocket import WebSocketMessage, WebSocketResponse
from app.services.chat_service import ChatService
from app.core.security import verify_websocket_token

router = APIRouter()
active_connections: Dict[UUID, WebSocket] = {}

@router.websocket("/ws/{instance_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    instance_id: UUID,
    token: str = Depends(verify_websocket_token)
):
    await websocket.accept()
    active_connections[instance_id] = websocket
    chat_service = ChatService()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = WebSocketMessage.parse_raw(data)
            
            # Send typing indicator
            await websocket.send_json(
                WebSocketResponse(
                    type="typing",
                    content="Assistant is typing..."
                ).dict()
            )
            
            # Process message
            response = await chat_service.process_message(
                instance_id=instance_id,
                message=message.content,
                session_id=message.session_id,
                context=message.metadata
            )
            
            # Send response
            await websocket.send_json(
                WebSocketResponse(
                    type="message",
                    content=response.response,
                    metadata={"session_id": str(response.session_id)}
                ).dict()
            )
            
    except WebSocketDisconnect:
        del active_connections[instance_id]
    except Exception as e:
        await websocket.send_json(
            WebSocketResponse(
                type="error",
                content=str(e)
            ).dict()
        ) 