from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from typing import Optional, List
import jwt
from datetime import datetime, timedelta
import secrets
import hashlib
from pydantic import BaseModel

from app.core.config import get_settings
from app.models.instance import Instance
from app.services.instance_service import InstanceService

settings = get_settings()

class SecurityConfig:
    API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=True)
    ALLOWED_HOSTS = ["*"]  # Configure this appropriately in production
    MAX_REQUEST_SIZE = 1024 * 1024  # 1MB
    RATE_LIMIT_WINDOW = 60  # seconds
    RATE_LIMIT_MAX_REQUESTS = 100
    JWT_ALGORITHM = "HS256"
    PASSWORD_HASH_ALGORITHM = "argon2"

class APIKeyManager:
    def __init__(self):
        self.key_hash_cache = {}
    
    def create_api_key(self) -> str:
        api_key = f"sk_{secrets.token_urlsafe(32)}"
        self.key_hash_cache[self._hash_key(api_key)] = True
        return api_key
    
    def verify_api_key(self, api_key: str) -> bool:
        return self._hash_key(api_key) in self.key_hash_cache
    
    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()

api_key_manager = APIKeyManager()

async def verify_api_key(
    api_key: str = Security(SecurityConfig.API_KEY_HEADER)
) -> str:
    if not api_key_manager.verify_api_key(api_key):
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return api_key

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=SecurityConfig.JWT_ALGORITHM
    ) 