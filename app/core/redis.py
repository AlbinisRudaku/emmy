from typing import Optional, Any
import json
from redis import asyncio as aioredis
from fastapi import HTTPException

from app.core.config import get_settings

settings = get_settings()

class RedisClient:
    def __init__(self):
        self.redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def set_with_ttl(
        self,
        key: str,
        value: Any,
        ttl_seconds: int
    ) -> None:
        serialized_value = (
            value if isinstance(value, str)
            else json.dumps(value)
        )
        await self.redis.setex(key, ttl_seconds, serialized_value)
    
    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)
    
    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
    
    async def increment_and_check(
        self,
        key: str,
        ttl_seconds: int,
        max_requests: int
    ) -> bool:
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, ttl_seconds)
        return current <= max_requests

redis_client = RedisClient() 