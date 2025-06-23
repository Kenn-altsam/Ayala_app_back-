from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from src.core.database import get_db
from .service import AuthService
from .schemas import (
    Token,
    UserLogin,
    UserCreate,
    UserResponse,
    PasswordReset,
    PasswordResetRequest,
    ResetPasswordRequest
)
from .dependencies import get_current_user
from .models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login timestamp
    await auth_service.update_last_login(user)
    
    return {
        "access_token": auth_service.create_access_token(user.id),
        "token_type": "bearer"
    }


@router.post("/login", response_model=Token)
async def login_json(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    JSON-based login for mobile apps.
    """
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive"
        )
    
    # Update last login timestamp
    await auth_service.update_last_login(user)
    
    return {
        "access_token": auth_service.create_access_token(user.id),
        "token_type": "bearer"
    }


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    """
    auth_service = AuthService(db)
    
    # Check if user already exists
    existing_user = await auth_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = await auth_service.create_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        google_id=user_data.google_id
    )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at
    )


@router.post("/password-reset-request")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request a password reset token.
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_email(reset_request.email)
    
    if user:
        token = await auth_service.create_password_reset_token(user)
        # Here you would typically send this token via email
        # For development, we'll return it directly
        return {"message": "Password reset token created", "token": token}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@router.post("/password-reset")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Reset password using token"""
    auth_service = AuthService(db)
    success = await auth_service.reset_password(db, request.token, request.new_password)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token"
        )
    
    return {"message": "Password reset successfully"}


@router.post("/google/verify")
async def verify_google_token(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify Google ID token from iOS app and create/login user.
    
    For SwiftUI iOS app:
    1. User signs in with Google using GoogleSignIn SDK
    2. iOS app gets Google ID token
    3. iOS app sends token to this endpoint
    4. Backend verifies token with Google and returns JWT
    """
    try:
        from google.auth.transport import requests
        from google.oauth2 import id_token
        from src.core.config import settings
        
        # Verify the Google ID token
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        
        # Extract user information
        google_user_id = idinfo['sub']
        email = idinfo['email']
        full_name = idinfo.get('name', '')
        
        # Check if user exists
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_email(email)
        
        if not user:
            # Create new user
            user = await auth_service.create_user(
                email=email,
                password="",  # No password for Google users
                full_name=full_name,
                google_id=google_user_id
            )
        
        # Generate JWT token
        access_token = auth_service.create_access_token(user.id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "is_verified": True  # Google users are automatically verified
            }
        }
        
    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=401,
            detail="Invalid Google token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Authentication failed"
        )


@router.get("/google/config")
async def get_google_config():
    """
    Get Google OAuth configuration for iOS app.
    Returns the Google Client ID needed for iOS GoogleSignIn SDK.
    """
    from src.core.config import settings
    
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured"
        )
    
    return {
        "google_client_id": settings.GOOGLE_CLIENT_ID,
        "configured": True
    } 