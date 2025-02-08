from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime

from app.core.redis import redis_client

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for certain paths
        if request.url.path in ["/health", "/api/docs", "/api/redoc"]:
            return await call_next(request)
        
        # Get API key from header
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return await call_next(request)
        
        # Rate limit key includes API key and current minute
        current_minute = datetime.utcnow().strftime("%Y-%m-%d-%H-%M")
        rate_limit_key = f"rate_limit:{api_key}:{current_minute}"
        
        # Check rate limit (100 requests per minute)
        is_allowed = await redis_client.increment_and_check(
            rate_limit_key,
            ttl_seconds=60,
            max_requests=100
        )
        
        if not is_allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        return await call_next(request) 