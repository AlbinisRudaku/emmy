from typing import Optional, Any, Callable
from functools import wraps
import json
import hashlib
from datetime import timedelta

from app.core.redis import redis_client

class CacheManager:
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
    
    async def get_or_set(
        self,
        key: str,
        getter: Callable,
        ttl: Optional[int] = None
    ) -> Any:
        # Try to get from cache
        cached = await redis_client.get(key)
        if cached:
            return json.loads(cached)
        
        # Get fresh data
        data = await getter()
        
        # Cache the result
        await redis_client.set_with_ttl(
            key,
            json.dumps(data),
            ttl or self.default_ttl
        )
        
        return data
    
    def cache_response(
        self,
        prefix: str,
        ttl: Optional[int] = None,
        key_builder: Optional[Callable] = None
    ):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Build cache key
                if key_builder:
                    cache_key = f"{prefix}:{key_builder(*args, **kwargs)}"
                else:
                    # Default key builder uses arguments
                    key_parts = [
                        str(arg) for arg in args
                    ] + [
                        f"{k}={v}" for k, v in sorted(kwargs.items())
                    ]
                    cache_key = f"{prefix}:{hashlib.sha256(':'.join(key_parts).encode()).hexdigest()}"
                
                return await self.get_or_set(
                    cache_key,
                    lambda: func(*args, **kwargs),
                    ttl
                )
            return wrapper
        return decorator

cache_manager = CacheManager() 