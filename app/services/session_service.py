from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.database.session import DBSession
from app.core.config import get_settings
from app.core.exceptions import AuthenticationError

settings = get_settings()

class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, user_id: UUID, token: str) -> DBSession:
        session = DBSession(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def validate_session(self, session_id: UUID) -> bool:
        query = select(DBSession).where(
            DBSession.id == session_id,
            DBSession.expires_at > datetime.utcnow()
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

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