from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Type, Optional, Dict, Any
from fastapi import HTTPException, status

class ChatbotError(Exception):
    """Base exception for all chatbot errors"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(ChatbotError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )

class AuthenticationError(ChatbotError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class RateLimitError(ChatbotError):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

class LLMServiceException(ChatbotError):
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        details = {"original_error": str(original_error)} if original_error else None
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )

class InstanceNotFoundException(ChatbotError):
    """Raised when an instance is not found"""
    def __init__(self, message: str = "Instance not found"):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(ChatbotError)
    async def chatbot_exception_handler(request, exc: ChatbotError):
        from app.core.logging import logger
        
        logger.error(
            f"ChatbotError: {exc.message}",
            extra={
                "status_code": exc.status_code,
                "details": exc.details,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return {
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
                "details": exc.details
            }
        }
    
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred",
                "error": str(exc)
            }
        ) 