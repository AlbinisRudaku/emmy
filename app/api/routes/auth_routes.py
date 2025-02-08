from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.services.user_service import UserService
from app.services.session_service import SessionService
from app.models.user import UserCreate, UserResponse, Token, UserLogin
from app.models.session import SessionInfo

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    try:
        user_service = UserService(db)
        return await user_service.create_user(user_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token"""
    user_service = UserService(db)
    session_service = SessionService(db)
    
    # Authenticate user
    token = await user_service.authenticate_user(form_data.email, form_data.password)
    
    # Create session in database
    await session_service.create_session(
        user_id=token.user_id,
        token=token.access_token
    )
    
    return token

@router.post("/logout")
async def logout(
    response: Response,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout and invalidate session"""
    session_service = SessionService(db)
    await session_service.invalidate_session(current_user.session_id)
    
    # Clear cookie if you're using cookie-based auth
    response.delete_cookie("session")
    
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user

@router.get("/sessions", response_model=List[SessionInfo])
async def list_sessions(
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all active sessions for the current user"""
    session_service = SessionService(db)
    return await session_service.get_user_sessions(current_user.id)

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: UUID,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke a specific session"""
    session_service = SessionService(db)
    await session_service.invalidate_session(session_id)
    return {"message": "Session revoked successfully"}

@router.delete("/sessions")
async def revoke_all_sessions(
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke all sessions for the current user"""
    session_service = SessionService(db)
    await session_service.invalidate_user_sessions(current_user.id)
    return {"message": "All sessions revoked successfully"} 