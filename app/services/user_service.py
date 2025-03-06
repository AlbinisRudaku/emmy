from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import jwt
from passlib.context import CryptContext
import redis
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException
import logging

from app.models.database.user import DBUser
from app.models.database.profile import DBUserProfile
from app.models.user import UserCreate, UserResponse, Token
from app.core.config import get_settings
from app.core.exceptions import AuthenticationError
from app.models.database.session import DBSession
from app.services.session_service import SessionService

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger("chatbot")

# Redis client for session management
redis_client = redis.Redis.from_url(settings.REDIS_URL)

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        try:
            # Create user
            db_user = DBUser(
                email=user_data.email,
                hashed_password=self.get_password_hash(user_data.password)
            )
            self.db.add(db_user)
            await self.db.flush()  # Flush to get the user ID but don't commit yet

            # Create associated profile
            db_profile = DBUserProfile(
                user_id=db_user.id,
                email=user_data.email,  # Copy email from user
                preferences={}  # Empty preferences dict
            )
            self.db.add(db_profile)
            
            # Now commit both user and profile
            await self.db.commit()
            await self.db.refresh(db_user)
            
            return UserResponse.from_orm(db_user)
            
        except IntegrityError as e:
            await self.db.rollback()
            if isinstance(e.orig, UniqueViolationError):
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )
            raise HTTPException(
                status_code=500,
                detail="Database error occurred"
            )
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    async def authenticate_user(self, email: str, password: str) -> Token:
        query = select(DBUser).where(DBUser.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not self.verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid credentials")

        session_id = uuid4()
        logger.info(f"Generated session_id: {session_id} for user: {user.email}")
        
        access_token = self.create_access_token(
            data={"sub": str(user.id), "session": str(session_id)}
        )

        # Create session in database with the same session_id used in the token
        session_service = SessionService(self.db)
        try:
            await session_service.create_session(
                user_id=user.id,
                token=access_token,
                session_id=session_id
            )
            logger.info(f"Session created for user {user.email} with id {session_id}")
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise AuthenticationError(f"Failed to create session: {str(e)}")

        return Token(
            access_token=access_token,
            token_type="bearer",
            session_id=session_id,
            user_id=user.id
        )

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def get_user(self, user_id: UUID) -> Optional[UserResponse]:
        query = select(DBUser).where(DBUser.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if user:
            return UserResponse.from_orm(user)
        return None

    async def invalidate_session(self, session_id: UUID):
        """Invalidate a user session"""
        session_key = f"session:{str(session_id)}"
        redis_client.delete(session_key)

    async def create_session(self, user_id: UUID, session_id: UUID):
        """Create a new session"""
        session_key = f"session:{str(session_id)}"
        session_data = {
            "user_id": str(user_id),
            "created_at": datetime.utcnow().isoformat()
        }
        redis_client.hmset(session_key, session_data)
        redis_client.expire(session_key, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60) 