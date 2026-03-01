# OAuth Implementation Guide

## Overview

KlyrSignals v1.6 now supports OAuth authentication with Google and GitHub. Users can sign in or register using their existing Google or GitHub accounts.

## Environment Configuration

To enable OAuth, set the following environment variables in your backend `.env` file:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/callback/google

# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:3000/api/auth/callback/github
```

## Getting OAuth Credentials

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Set application type to "Web application"
6. Add authorized redirect URI: `http://localhost:3000/api/auth/callback/google`
7. Copy Client ID and Client Secret

### GitHub OAuth

1. Go to [GitHub Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Set Application Name: "KlyrSignals"
4. Set Homepage URL: `http://localhost:3000`
5. Set Authorization Callback URL: `http://localhost:3000/api/auth/callback/github`
6. Click "Register application"
7. Copy Client ID and generate Client Secret

## OAuth Flow

1. User clicks "Sign in with Google/GitHub" button
2. Frontend calls `/api/v1/oauth/{provider}/init`
3. Backend returns authorization URL with state parameter
4. User is redirected to provider (Google/GitHub)
5. User authorizes the application
6. Provider redirects to callback URL with authorization code
7. Frontend callback handler exchanges code for tokens
8. Backend creates/updates user and OAuth account
9. JWT tokens issued and stored
10. User redirected to dashboard

## Account Linking

- OAuth accounts are linked to User model via Account table
- One OAuth account per provider per user (prevents duplicates)
- If email already exists, OAuth account is linked to existing user
- New users are created if email doesn't exist

## Security Features

- **State Parameter**: CSRF protection for OAuth flow
- **PKCE Flow**: Supported for public clients
- **Token Storage**: OAuth tokens stored securely in database
- **Email Verification**: Email marked as verified if OAuth provider verifies it
- **Avatar Sync**: User avatar URL synced from OAuth provider

## API Endpoints

### Initialize OAuth

```bash
GET /api/v1/oauth/google/init
GET /api/v1/oauth/github/init

Response:
{
  "authorization_url": "https://accounts.google.com/...",
  "state": "random_state_string"
}
```

### OAuth Callback

```bash
GET /api/v1/oauth/google/callback?code={code}&state={state}
GET /api/v1/oauth/github/callback?code={code}&state={state}

Response:
{
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "name": "User Name",
    "avatarUrl": "https://...",
    "emailVerified": "2026-03-01T08:00:00Z"
  }
}
```

### List Providers

```bash
GET /api/v1/oauth/providers

Response:
{
  "providers": [
    {"name": "google", "label": "Google", "enabled": true},
    {"name": "github", "label": "GitHub", "enabled": true}
  ]
}
```

## Database Schema

### Account Model

```python
@dataclass
class Account:
    id: str
    userId: str
    provider: str  # 'google' or 'github'
    providerAccountId: str  # User's ID on the OAuth provider
    accessToken: Optional[str]
    refreshToken: Optional[str]
    expiresAt: Optional[datetime]
    scope: Optional[str]
    tokenType: Optional[str]
    idToken: Optional[str]
    createdAt: datetime
    updatedAt: datetime
```

### User Model (Updated)

```python
@dataclass
class User:
    id: str
    email: str
    passwordHash: Optional[str] = None  # Optional for OAuth users
    name: str = ""
    avatarUrl: Optional[str] = None
    emailVerified: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime
```

## Testing

### Test OAuth Flow (Mock Mode)

Without credentials configured, endpoints return:
```json
{
  "detail": "Google OAuth not configured"
}
```

This confirms the OAuth infrastructure is in place and working.

### Test with Real Credentials

1. Configure environment variables
2. Start backend: `cd backend && source venv/bin/activate && python -m uvicorn app.main:app`
3. Start frontend: `cd frontend && npm run dev`
4. Navigate to `/login`
5. Click "Sign in with Google" or "Sign in with GitHub"
6. Complete OAuth flow
7. Verify redirect to dashboard with authenticated user

## Troubleshooting

### "OAuth not configured" Error

- Check environment variables are set correctly
- Restart backend server after setting variables
- Verify redirect URIs match exactly

### "Invalid state parameter" Error

- State parameter expired (timeout)
- Browser cookies blocked
- Try again with fresh login attempt

### "Already have a {provider} account linked" Error

- User already has OAuth account from this provider
- Sign in with the same provider instead of registering

## Production Deployment

For production, update redirect URIs:

```bash
GOOGLE_REDIRECT_URI=https://klyrsignals.com/api/auth/callback/google
GITHUB_REDIRECT_URI=https://klyrsignals.com/api/auth/callback/github
```

Add production domain to OAuth provider settings:
- Google Cloud Console: Add `https://klyrsignals.com` to authorized domains
- GitHub OAuth App: Update callback URL to production URL
