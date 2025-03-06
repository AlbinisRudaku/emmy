from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from uuid import UUID
from typing import Optional
import redis
import logging

from app.core.config import get_settings
from app.core.database import get_db
from app.services.user_service import UserService
from app.services.session_service import SessionService
from app.models.user import UserResponse

logger = logging.getLogger("chatbot")
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
        logger.info("Decoding JWT token")
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        session_id: str = payload.get("session")
        logger.info(f"Decoded token: user_id={user_id}, session_id={session_id}")
        
        if user_id is None or session_id is None:
            logger.error("Missing user_id or session_id in token")
            raise credentials_exception
            
        # Check if session is valid in the database
        logger.info(f"Validating session in database: {session_id}")
        session_service = SessionService(db)
        is_valid = await session_service.validate_session(UUID(session_id))
        logger.info(f"Session validation result: {is_valid}")
        
        if not is_valid:
            logger.error(f"Session {session_id} not found in database")
            raise credentials_exception
            
    except JWTError as e:
        logger.error(f"JWT Error: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        raise credentials_exception
        
    logger.info(f"Fetching user details for user_id: {user_id}")
    user_service = UserService(db)
    user = await user_service.get_user(UUID(user_id))
    if user is None:
        logger.error(f"User {user_id} not found in database")
        raise credentials_exception
    logger.info(f"User authenticated successfully: {user.email}")
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