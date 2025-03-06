from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import logging

from app.models.database.session import DBSession
from app.core.config import get_settings
from app.core.exceptions import AuthenticationError

settings = get_settings()
logger = logging.getLogger("chatbot")

class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, user_id: UUID, token: str, session_id: Optional[UUID] = None) -> DBSession:
        """
        Create a new session for a user.
        If session_id is provided, use it as the session ID instead of auto-generating one.
        This is essential for matching the session_id in the JWT token.
        """
        logger.info(f"Creating session for user_id: {user_id}, session_id: {session_id}")
        
        session = DBSession(
            id=session_id,  # Use the provided session_id instead of auto-generating
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        self.db.add(session)
        try:
            await self.db.commit()
            await self.db.refresh(session)
            logger.info(f"Session created successfully: {session.id}")
            return session
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating session: {str(e)}")
            raise

    async def validate_session(self, session_id: UUID) -> bool:
        logger.info(f"Validating session: {session_id}")
        query = select(DBSession).where(
            DBSession.id == session_id,
            DBSession.expires_at > datetime.utcnow()
        )
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        is_valid = session is not None
        logger.info(f"Session validation result: {is_valid}")
        return is_valid

    async def invalidate_session(self, session_id: UUID):
        query = delete(DBSession).where(DBSession.id == session_id)
        await self.db.execute(query)
        await self.db.commit()

    async def cleanup_expired_sessions(self):
        query = delete(DBSession).where(DBSession.expires_at <= datetime.utcnow())
        await self.db.execute(query)
        await self.db.commit()

    async def get_user_sessions(self, user_id: UUID) -> List[DBSession]:
        query = select(DBSession).where(
            DBSession.user_id == user_id,
            DBSession.expires_at > datetime.utcnow()
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def invalidate_user_sessions(self, user_id: UUID):
        query = delete(DBSession).where(DBSession.user_id == user_id)
        await self.db.execute(query)
        await self.db.commit() 