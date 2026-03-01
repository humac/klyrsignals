"""
OAuth API Routes - Google and GitHub authentication
"""
import secrets
from fastapi import APIRouter, HTTPException, status, Query, Request
from pydantic import BaseModel
from typing import Optional
from app.services.database import db
from app.services.auth import create_access_token, create_refresh_token
from app.services.oauth_service import oauth_service
from datetime import timedelta, datetime

router = APIRouter()

# Store state parameters temporarily (in production, use Redis)
oauth_states: dict = {}


class OAuthInitResponse(BaseModel):
    """Response for OAuth initialization"""
    authorization_url: str
    state: str


class OAuthCallbackResponse(BaseModel):
    """Response for OAuth callback"""
    access_token: str
    refresh_token: str
    user: dict


@router.get("/google/init", response_model=OAuthInitResponse)
async def init_google_oauth():
    """Initialize Google OAuth flow"""
    if not oauth_service.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured"
        )
    
    # Generate state parameter for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"provider": "google", "created_at": datetime.utcnow()}
    
    # Get authorization URL
    auth_url = oauth_service.get_google_authorization_url(state)
    
    return OAuthInitResponse(authorization_url=auth_url, state=state)


@router.get("/github/init", response_model=OAuthInitResponse)
async def init_github_oauth():
    """Initialize GitHub OAuth flow"""
    if not oauth_service.github_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth not configured"
        )
    
    # Generate state parameter for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"provider": "github", "created_at": datetime.utcnow()}
    
    # Get authorization URL
    auth_url = oauth_service.get_github_authorization_url(state)
    
    return OAuthInitResponse(authorization_url=auth_url, state=state)


@router.get("/google/callback", response_model=OAuthCallbackResponse)
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
):
    """Handle Google OAuth callback"""
    # Validate state
    if state not in oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    state_data = oauth_states.pop(state)
    if state_data["provider"] != "google":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    # Exchange code for tokens and user info
    try:
        oauth_data = await oauth_service.exchange_google_code(code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google OAuth failed: {str(e)}"
        )
    
    # Find or create user
    return await _handle_oauth_login(oauth_data)


@router.get("/github/callback", response_model=OAuthCallbackResponse)
async def github_callback(
    code: str = Query(...),
    state: str = Query(...),
):
    """Handle GitHub OAuth callback"""
    # Validate state
    if state not in oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    state_data = oauth_states.pop(state)
    if state_data["provider"] != "github":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    # Exchange code for tokens and user info
    try:
        oauth_data = await oauth_service.exchange_github_code(code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub OAuth failed: {str(e)}"
        )
    
    # Find or create user
    return await _handle_oauth_login(oauth_data)


async def _handle_oauth_login(oauth_data: dict) -> OAuthCallbackResponse:
    """
    Handle OAuth login - find existing user or create new one
    
    This function:
    1. Checks if OAuth account exists
    2. If yes, returns tokens for linked user
    3. If no, checks if email exists
    4. If email exists, links OAuth account to existing user
    5. If email doesn't exist, creates new user and links OAuth account
    """
    provider = oauth_data["provider"]
    provider_account_id = oauth_data["provider_account_id"]
    
    # Check if OAuth account already exists
    existing_account = await db.account_find_by_provider_and_id(
        provider, provider_account_id
    )
    
    if existing_account:
        # User already has this OAuth account linked
        user = await db.user_find_by_id(existing_account.userId)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update tokens
        await db.account_update_tokens(
            existing_account.id,
            access_token=oauth_data["access_token"],
            refresh_token=oauth_data["refresh_token"],
            expires_at=oauth_data["expires_at"],
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
        
        return OAuthCallbackResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "avatarUrl": user.avatarUrl,
                "emailVerified": user.emailVerified.isoformat() if user.emailVerified else None,
            }
        )
    
    # OAuth account doesn't exist, check if user with this email exists
    user = await db.user_find_by_email(oauth_data["email"])
    
    if user:
        # Link OAuth account to existing user
        # Prevent duplicate OAuth accounts for same provider
        existing_accounts = await db.account_find_by_user(user.id)
        if any(acc.provider == provider for acc in existing_accounts):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Already have a {provider} account linked"
            )
        
        # Create OAuth account link
        await db.account_create(
            userId=user.id,
            provider=provider,
            providerAccountId=provider_account_id,
            accessToken=oauth_data["access_token"],
            refreshToken=oauth_data["refresh_token"],
            expiresAt=oauth_data["expires_at"],
        )
        
        # Update user's email verification if OAuth provider verified it
        if oauth_data["email_verified"] and not user.emailVerified:
            user.emailVerified = datetime.utcnow()
        
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
        
        return OAuthCallbackResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "avatarUrl": user.avatarUrl,
                "emailVerified": user.emailVerified.isoformat() if user.emailVerified else None,
            }
        )
    
    # Create new user
    user = await db.user_create(
        email=oauth_data["email"],
        passwordHash=None,  # No password for OAuth users
        name=oauth_data["name"] or oauth_data["email"].split("@")[0],
    )
    
    # Update avatar URL if provided
    if oauth_data["avatar_url"]:
        user.avatarUrl = oauth_data["avatar_url"]
    
    # Set email as verified if OAuth provider verified it
    if oauth_data["email_verified"]:
        user.emailVerified = datetime.utcnow()
    
    # Create OAuth account link
    await db.account_create(
        userId=user.id,
        provider=provider,
        providerAccountId=provider_account_id,
        accessToken=oauth_data["access_token"],
        refreshToken=oauth_data["refresh_token"],
        expiresAt=oauth_data["expires_at"],
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
    
    return OAuthCallbackResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "avatarUrl": user.avatarUrl,
            "emailVerified": user.emailVerified.isoformat() if user.emailVerified else None,
        }
    )


@router.get("/providers")
async def get_oauth_providers():
    """Get available OAuth providers"""
    providers = []
    
    if oauth_service.google_client_id:
        providers.append({
            "name": "google",
            "label": "Google",
            "enabled": True,
        })
    
    if oauth_service.github_client_id:
        providers.append({
            "name": "github",
            "label": "GitHub",
            "enabled": True,
        })
    
    return {"providers": providers}
