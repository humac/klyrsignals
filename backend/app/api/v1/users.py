from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.services.database import db
from app.services.auth import get_current_user, TokenData, get_password_hash

router = APIRouter()

class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    avatarUrl: Optional[str] = None

@router.get("/me")
async def get_current_user_profile(current_user: TokenData = Depends(get_current_user)):
    """Get current user profile"""
    user = await db.user.find_unique(
        where={"id": current_user.user_id},
        include={"accounts": True}
    )
    
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
        "emailVerified": user.emailVerified,
        "oauthAccounts": [
            {"provider": acc.provider, "providerAccountId": acc.providerAccountId}
            for acc in user.accounts
        ]
    }

@router.patch("/me")
async def update_current_user(
    request: UpdateUserRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """Update current user profile"""
    update_data = {}
    
    if request.name is not None:
        update_data["name"] = request.name
    if request.avatarUrl is not None:
        update_data["avatarUrl"] = request.avatarUrl
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    user = await db.user.update(
        where={"id": current_user.user_id},
        data=update_data
    )
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "avatarUrl": user.avatarUrl,
    }

@router.delete("/me")
async def delete_current_user(
    current_user: TokenData = Depends(get_current_user)
):
    """Delete current user account (GDPR right to deletion)"""
    # Delete all sessions
    await db.session.delete_many(where={"userId": current_user.user_id})
    
    # Delete all OAuth accounts
    await db.account.delete_many(where={"userId": current_user.user_id})
    
    # Delete all portfolios (cascade will delete holdings)
    await db.portfolio.delete_many(where={"userId": current_user.user_id})
    
    # Delete user
    await db.user.delete(where={"id": current_user.user_id})
    
    # Log audit event
    await db.auditlog.create(
        data={
            "userId": current_user.user_id,
            "action": "user_deleted",
            "resource": "User",
            "resourceId": current_user.user_id,
        }
    )
    
    return {"success": True, "message": "Account deleted successfully"}
