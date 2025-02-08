from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from typing import Optional

from app.core.database import get_db
from app.services.api_key_service import ApiKeyService
from app.models.api_key import ApiKeyResponse
from app.core.config import get_settings

settings = get_settings()
router = APIRouter()

@router.post("/generate", response_model=ApiKeyResponse)
async def generate_temporary_key(
    db: AsyncSession = Depends(get_db),
    admin_token: Optional[str] = Header(None, alias="X-Admin-Token")
):
    """Generate a temporary API key that expires in 1 hour. Requires admin token."""
    if not admin_token or admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(
            status_code=403,
            detail="Invalid admin token"
        )
    
    api_key_service = ApiKeyService(db)
    return await api_key_service.create_temporary_key() 