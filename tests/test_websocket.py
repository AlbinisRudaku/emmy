import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.models.websocket import WebSocketMessage

def test_websocket_connection():
    client = TestClient(app)
    
    with client.websocket_connect("/ws/123") as websocket:
        data = WebSocketMessage(
            type="message",
            content="Hello"
        ).json()
        websocket.send_text(data)
        
        response = websocket.receive_json()
        assert response["type"] == "typing"
        
        response = websocket.receive_json()
        assert response["type"] == "message"
        assert "content" in response

def test_websocket_error_handling():
    client = TestClient(app)
    
    with client.websocket_connect("/ws/123") as websocket:
        websocket.send_text("invalid json")
        
        response = websocket.receive_json()
        assert response["type"] == "error" 