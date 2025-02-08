from datetime import datetime, timedelta
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database.api_key import DBApiKey
from app.models.api_key import ApiKey, ApiKeyResponse

class ApiKeyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_temporary_key(self, duration: timedelta = timedelta(hours=1)) -> ApiKeyResponse:
        api_key = DBApiKey(
            key=f"tmp_{secrets.token_urlsafe(32)}",
            expires_at=datetime.utcnow() + duration
        )
        
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        
        return ApiKeyResponse(
            key=api_key.key,
            expires_at=api_key.expires_at
        )

    async def validate_key(self, key: str) -> bool:
        query = select(DBApiKey).where(
            DBApiKey.key == key,
            DBApiKey.is_active == True,
            DBApiKey.expires_at > datetime.utcnow()
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None 