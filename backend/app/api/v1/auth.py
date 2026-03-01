from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from app.services.database import db
from app.services.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    TokenData,
)
from datetime import timedelta, datetime

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """Register new user"""
    # Check if user exists
    existing = await db.user_find_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = await db.user_create(
        email=request.email,
        passwordHash=get_password_hash(request.password),
        name=request.name,
    )
    
    # Generate tokens
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.id, "email": user.email}
    )
    
    # Store refresh token in session
    await db.session_create(
        userId=user.id,
        token=refresh_token,
        expiresAt=datetime.utcnow() + timedelta(days=7),
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={"id": user.id, "email": user.email, "name": user.name}
    )

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login user"""
    # Find user
    user = await db.user_find_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not user.passwordHash or not verify_password(request.password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate tokens
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.id, "email": user.email}
    )
    
    # Store refresh token
    await db.session_create(
        userId=user.id,
        token=refresh_token,
        expiresAt=datetime.utcnow() + timedelta(days=7),
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={"id": user.id, "email": user.email, "name": user.name}
    )

@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    """Logout user (invalidate refresh token)"""
    # Delete all sessions for user
    await db.session_delete_many(current_user.user_id)
    return {"success": True}

@router.post("/refresh")
async def refresh_token(request: dict):
    """Refresh access token"""
    refresh_token = request.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )
    
    # Validate refresh token
    try:
        payload = decode_token(refresh_token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check session exists
    session = await db.session_find_by_token(refresh_token)
    if not session or session.expiresAt < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    
    # Generate new tokens
    new_access_token = create_access_token(
        data={"sub": payload.user_id, "email": payload.email}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": payload.user_id, "email": payload.email}
    )
    
    # Delete old session, create new one
    await db.session_delete_many(payload.user_id)
    await db.session_create(
        userId=payload.user_id,
        token=new_refresh_token,
        expiresAt=datetime.utcnow() + timedelta(days=7),
    )
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }

@router.get("/me")
async def get_me(current_user: TokenData = Depends(get_current_user)):
    """Get current user profile"""
    user = await db.user_find_by_id(current_user.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "avatarUrl": user.avatarUrl,
        "emailVerified": user.emailVerified.isoformat() if user.emailVerified else None,
        "oauthAccounts": []
    }
