import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar
from pythonjsonlogger import jsonlogger
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Context variables for request tracking
request_id_ctx = ContextVar("request_id", default=None)
user_id_ctx = ContextVar("user_id", default=None)

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any]
    ) -> None:
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name

class ContextualLogger:
    def __init__(self, logger_name: str = "chatbot"):
        self.logger = logging.getLogger(logger_name)
        self._setup_logger()
    
    def _setup_logger(self):
        handler = logging.StreamHandler()
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _get_context(self) -> Dict[str, Any]:
        return {
            "request_id": request_id_ctx.get(),
            "user_id": user_id_ctx.get(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log("info", message, extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log("error", message, extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log("warning", message, extra)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log("debug", message, extra)
    
    def _log(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None):
        context = self._get_context()
        if extra:
            context.update(extra)
        
        getattr(self.logger, level)(message, extra=context)

logger = ContextualLogger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request_id_ctx.set(request_id)
        
        # Extract user ID from token if available
        try:
            token = request.headers.get("Authorization", "").split(" ")[1]
            # Add token validation and user extraction here
            user_id = "example_user"  # Replace with actual user ID
            user_id_ctx.set(user_id)
        except:
            pass
        
        # Log request
        logger.info(
            "Incoming request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "headers": dict(request.headers),
                "query_params": dict(request.query_params)
            }
        )
        
        try:
            start_time = datetime.utcnow()
            response = await call_next(request)
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Log response
            logger.info(
                "Request completed",
                extra={
                    "status_code": response.status_code,
                    "duration_ms": duration
                }
            )
            
            return response
        except Exception as e:
            logger.error(
                "Request failed",
                extra={
                    "error": str(e),
                    "error_type": e.__class__.__name__
                }
            )
            raise 