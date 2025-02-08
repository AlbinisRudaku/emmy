from typing import Dict, Any
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AI Chatbot API",
        version="1.0.0",
        description="""
        # AI Chatbot Service API Documentation
        
        This service provides a sophisticated AI chatbot that can be integrated into any website.
        
        ## Key Features
        
        * Real-time chat via WebSocket connections
        * Multi-language support with automatic language detection
        * Context-aware responses based on website content
        * Secure authentication and rate limiting
        * Response caching for improved performance
        * User profiles and preferences management
        
        ## Authentication
        
        All endpoints (except API key generation) require an API key to be passed in the `X-API-Key` header.
        
        ### API Keys
        * API keys can be generated using the `/api/v1/api-keys/generate` endpoint
        * This endpoint requires an admin token in the `X-Admin-Token` header
        * Generated keys expire after 1 hour
        
        ## User Management
        
        ### Authentication Endpoints
        * `POST /api/v1/auth/register` - Register new user
        * `POST /api/v1/auth/login` - Login and get access token
        * `POST /api/v1/auth/logout` - Logout and invalidate session
        * `GET /api/v1/auth/me` - Get current user info
        
        ### Profile Management
        * `GET /api/v1/profiles/me` - Get user profile
        * `PUT /api/v1/profiles/me` - Update user profile
        
        ### Session Management
        * `GET /api/v1/auth/sessions` - List active sessions
        * `DELETE /api/v1/auth/sessions/{session_id}` - Revoke specific session
        * `DELETE /api/v1/auth/sessions` - Revoke all sessions
        
        ## Rate Limiting
        
        The API is rate-limited to:
        * 100 requests per minute per API key
        * 1000 requests per hour per API key
        
        ## Error Handling
        
        The API uses standard HTTP status codes and returns detailed error messages.
        
        ## WebSocket Usage
        
        For real-time chat, connect to the WebSocket endpoint with:
        ```
        ws://your-domain/ws/{instance_id}?token={access_token}
        ```
        """,
        routes=app.routes,
    )
    
    # Enhance security scheme documentation
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for authentication. Can be either a permanent key or a temporary key."
        }
    }
    
    # Add security requirement to all endpoints
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"ApiKeyAuth": []}]
    
    # Add response schemas
    openapi_schema["components"]["schemas"]["Error"] = {
        "type": "object",
        "properties": {
            "error": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "type": {"type": "string"},
                    "details": {"type": "object"}
                }
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

def setup_docs(app: FastAPI):
    app.openapi = lambda: custom_openapi(app) 