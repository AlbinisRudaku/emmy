from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from uuid import UUID
from typing import Optional
import redis

from app.core.config import get_settings
from app.core.database import get_db
from app.services.user_service import UserService
from app.models.user import UserResponse

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Redis client for session management
redis_client = redis.Redis.from_url(settings.REDIS_URL)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        session_id: str = payload.get("session")
        if user_id is None or session_id is None:
            raise credentials_exception
            
        # Check if session is valid
        session_key = f"session:{session_id}"
        if not redis_client.exists(session_key):
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    user_service = UserService(db)
    user = await user_service.get_user(UUID(user_id))
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user 