"""
OAuth Service - Handles OAuth2 authentication with Google and GitHub
"""
import os
import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class OAuthService:
    """OAuth2 service for Google and GitHub authentication"""
    
    def __init__(self):
        # Google OAuth config
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.google_redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI", "http://localhost:3000/api/auth/callback/google"
        )
        
        # GitHub OAuth config
        self.github_client_id = os.getenv("GITHUB_CLIENT_ID")
        self.github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        self.github_redirect_uri = os.getenv(
            "GITHUB_REDIRECT_URI", "http://localhost:3000/api/auth/callback/github"
        )
    
    def get_google_oauth_client(self) -> AsyncOAuth2Client:
        """Create Google OAuth2 client"""
        return AsyncOAuth2Client(
            client_id=self.google_client_id,
            client_secret=self.google_client_secret,
            redirect_uri=self.google_redirect_uri,
            scope=["openid", "email", "profile"],
        )
    
    def get_github_oauth_client(self) -> AsyncOAuth2Client:
        """Create GitHub OAuth2 client"""
        return AsyncOAuth2Client(
            client_id=self.github_client_id,
            client_secret=self.github_client_secret,
            redirect_uri=self.github_redirect_uri,
            scope=["user:email"],
        )
    
    def get_google_authorization_url(self, state: str) -> str:
        """Get Google authorization URL"""
        client = self.get_google_oauth_client()
        uri, state = client.create_authorization_url(
            "https://accounts.google.com/o/oauth2/v2/auth",
            state=state,
            prompt="consent",
        )
        return uri
    
    def get_github_authorization_url(self, state: str) -> str:
        """Get GitHub authorization URL"""
        client = self.get_github_oauth_client()
        uri, state = client.create_authorization_url(
            "https://github.com/login/oauth/authorize",
            state=state,
        )
        return uri
    
    async def exchange_google_code(self, code: str) -> Dict[str, Any]:
        """Exchange Google authorization code for tokens"""
        client = self.get_google_oauth_client()
        
        async with httpx.AsyncClient() as http:
            token = await client.fetch_token(
                "https://oauth2.googleapis.com/token",
                authorization_response=f"{self.google_redirect_uri}?code={code}",
                http_client=http,
            )
            
            # Get user info
            async with http.stream('GET', 
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token['access_token']}"}
            ) as resp:
                user_info = await resp.aread()
                import json
                user_data = json.loads(user_info)
            
            return {
                "provider": "google",
                "provider_account_id": user_data.get("id"),
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "avatar_url": user_data.get("picture"),
                "email_verified": user_data.get("verified_email", False),
                "access_token": token.get("access_token"),
                "refresh_token": token.get("refresh_token"),
                "expires_at": datetime.utcnow() + timedelta(seconds=token.get("expires_in", 3600)),
            }
    
    async def exchange_github_code(self, code: str) -> Dict[str, Any]:
        """Exchange GitHub authorization code for tokens"""
        client = self.get_github_oauth_client()
        
        async with httpx.AsyncClient() as http:
            token = await client.fetch_token(
                "https://github.com/login/oauth/access_token",
                authorization_response=f"{self.github_redirect_uri}?code={code}",
                http_client=http,
            )
            
            # Get user info
            async with http.stream('GET',
                "https://api.github.com/user",
                headers={"Authorization": f"token {token['access_token']}"}
            ) as resp:
                user_info = await resp.aread()
                import json
                user_data = json.loads(user_info)
            
            # Get email if not in user data
            email = user_data.get("email")
            if not email:
                async with http.stream('GET',
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"token {token['access_token']}"}
                ) as email_resp:
                    email_data = await email_resp.aread()
                    import json
                    emails = json.loads(email_data)
                    # Get primary email
                    for e in emails:
                        if e.get("primary"):
                            email = e.get("email")
                            break
            
            return {
                "provider": "github",
                "provider_account_id": str(user_data.get("id")),
                "email": email,
                "name": user_data.get("name") or user_data.get("login"),
                "avatar_url": user_data.get("avatar_url"),
                "email_verified": True,  # GitHub emails are verified
                "access_token": token.get("access_token"),
                "refresh_token": None,  # GitHub doesn't provide refresh tokens
                "expires_at": None,  # GitHub tokens don't expire
            }
    
    async def refresh_google_token(
        self, refresh_token: str
    ) -> Optional[Dict[str, Any]]:
        """Refresh Google access token"""
        client = self.get_google_oauth_client()
        
        async with httpx.AsyncClient() as http:
            try:
                token = await client.refresh_token(
                    "https://oauth2.googleapis.com/token",
                    refresh_token=refresh_token,
                    http_client=http,
                )
                return {
                    "access_token": token.get("access_token"),
                    "refresh_token": token.get("refresh_token"),
                    "expires_at": datetime.utcnow() + timedelta(seconds=token.get("expires_in", 3600)),
                }
            except Exception:
                return None


# Global instance
oauth_service = OAuthService()
