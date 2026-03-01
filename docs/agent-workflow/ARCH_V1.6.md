# KlyrSignals v1.6 - Authentication & Authorization Architecture

**Version:** 1.6.0  
**Status:** Design Complete  
**Date:** 2026-03-01  
**Author:** Tony (Lead Architect)  

---

## Executive Summary

KlyrSignals v1.6 introduces full authentication, authorization, database persistence, and user management to transform the client-side-only v1.5 into a production-ready, multi-user SaaS application. This architecture document defines the complete system design for secure user authentication, data persistence, and authorization.

### Key Changes from v1.5

| Aspect | v1.5 (Current) | v1.6 (Target) |
|--------|----------------|---------------|
| **Data Storage** | Browser localStorage | PostgreSQL database |
| **User Accounts** | None | Full user management |
| **Authentication** | None | Email/password + OAuth (Google, GitHub) |
| **Authorization** | N/A (single user) | JWT-based, user-scoped |
| **Multi-Device** | No | Yes (cloud sync) |
| **Security** | Client-side only | bcrypt, JWT, rate limiting, CORS |
| **Password Reset** | N/A | Email-based reset flow |
| **Session Management** | N/A | Refresh tokens, session tracking |
| **Audit Logging** | None | Comprehensive audit trail |

---

## 1. Requirements Analysis

### 1.1 User Stories

#### End User Requirements

**As a user, I want to:**

1. ✅ Create an account with email/password
2. ✅ Login with my credentials
3. ✅ Login with OAuth (Google, GitHub)
4. ✅ Have my portfolio saved to the cloud
5. ✅ Access my portfolio from any device
6. ✅ Reset my password if I forget it
7. ✅ Update my profile settings
8. ✅ Logout securely
9. ✅ Delete my account and data (GDPR compliance)

#### System Requirements

**As the system, I need to:**

1. ✅ Securely store user passwords (bcrypt hashing, 12+ rounds)
2. ✅ Issue JWT tokens for authenticated sessions
3. ✅ Validate tokens on every API request
4. ✅ Encrypt sensitive portfolio data at rest
5. ✅ Rate limit API endpoints (prevent abuse)
6. ✅ Log authentication events (login, logout, failed attempts)
7. ✅ Enforce authorization (users can only access their own data)
8. ✅ Support password reset via email
9. ✅ Handle session expiration and refresh

### 1.2 Security Requirements

| Security Control | Implementation | Specification |
|-----------------|----------------|---------------|
| **Password Storage** | bcrypt | 12 rounds minimum, unique salt per password |
| **Access Tokens** | JWT (HS256 or RS256) | 15-minute expiry, signed with secret/key |
| **Refresh Tokens** | JWT + Database | 7-day expiry, stored as hash, revocable |
| **Data Encryption** | AES-256 | For sensitive data at rest (future enhancement) |
| **Transport Security** | HTTPS/TLS 1.3 | Required for all production traffic |
| **CORS** | Whitelist | Restrict to allowed origins only |
| **Rate Limiting** | Redis-backed | 100 req/hour per user, 1000 req/hour per IP |
| **Input Validation** | Pydantic + Zod | All inputs validated on client and server |

### 1.3 Privacy & Compliance

**GDPR Requirements:**

- ✅ Right to access (data export)
- ✅ Right to deletion (account + all data)
- ✅ Right to rectification (profile updates)
- ✅ Data minimization (only collect what's needed)
- ✅ Consent management (explicit opt-in for PII)
- ✅ Data retention policy (define retention periods)
- ✅ Privacy policy (clear, accessible documentation)

**Data Retention Policy:**

| Data Type | Retention Period | Deletion Trigger |
|-----------|------------------|------------------|
| User accounts | Until user deletion | Account deletion request |
| Session tokens | 7 days | Expiry or logout |
| Audit logs | 90 days | Automatic purge |
| Deleted accounts | 30 days (backup) | Permanent purge after 30 days |

---

## 2. Database Schema Design

### 2.1 Technology Stack

- **Database:** PostgreSQL 15
- **ORM:** Prisma ORM
- **Hosting:** Railway or Supabase (managed PostgreSQL)
- **Connection Pooling:** Built-in (Railway/Supabase) or pgBouncer

### 2.2 Prisma Schema

```prisma
// schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// User Model - Core authentication entity
model User {
  id            String    @id @default(uuid())
  email         String    @unique
  passwordHash  String?   // Null for OAuth-only users
  name          String?
  avatarUrl     String?
  emailVerified DateTime?
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
  
  // Relations
  accounts      Account[]
  sessions      Session[]
  portfolios    Portfolio[]
  auditLogs     AuditLog[]
  
  @@index([email])
}

// OAuth Account Model - Links OAuth providers to users
model Account {
  id                String  @id @default(uuid())
  userId            String
  type              String  // "oauth2" | "oidc"
  provider          String  // "google" | "github"
  providerAccountId String
  refresh_token     String?
  access_token      String?
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String?
  
  user              User    @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  @@unique([provider, providerAccountId])
  @@index([userId])
}

// Session Model - Manages refresh tokens and active sessions
model Session {
  id           String   @id @default(uuid())
  userId       String
  token        String   @unique // Hashed refresh token
  expiresAt    DateTime
  createdAt    DateTime @default(now())
  userAgent    String?
  ipAddress    String?
  
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  @@index([userId])
  @@index([token])
}

// Portfolio Model - User's investment portfolio
model Portfolio {
  id          String   @id @default(uuid())
  userId      String
  name        String   @default("My Portfolio")
  description String?
  isPublic    Boolean  @default(false)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  
  // Relations
  user        User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  holdings    Holding[]
  
  @@index([userId])
}

// Holding Model - Individual investment in a portfolio
model Holding {
  id            String   @id @default(uuid())
  portfolioId   String
  symbol        String
  quantity      Float
  purchasePrice Float
  purchaseDate  DateTime?
  assetClass    String   @default("stock") // stock, etf, crypto, mutual_fund
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
  
  // Relations
  portfolio     Portfolio @relation(fields: [portfolioId], references: [id], onDelete: Cascade)
  
  @@unique([portfolioId, symbol])
  @@index([portfolioId])
}

// Audit Log Model - Security and activity tracking
model AuditLog {
  id        String   @id @default(uuid())
  userId    String?
  action    String   // "login", "logout", "portfolio.create", etc.
  resource  String?  // "Portfolio", "Holding"
  resourceId String?
  ipAddress String?
  userAgent String?
  timestamp DateTime @default(now())
  metadata  Json?
  
  @@index([userId])
  @@index([timestamp])
  @@index([action])
}
```

### 2.3 Entity Relationship Diagram

```mermaid
erDiagram
  USER ||--o{ ACCOUNT : "has OAuth accounts"
  USER ||--o{ SESSION : "has active sessions"
  USER ||--o{ PORTFOLIO : "owns"
  PORTFOLIO ||--o{ HOLDING : "contains"
  USER ||--o{ AUDIT_LOG : "generates"
  
  USER {
    uuid id PK
    string email UK
    string passwordHash
    string name
    datetime emailVerified
    datetime createdAt
    datetime updatedAt
  }
  
  ACCOUNT {
    uuid id PK
    uuid userId FK
    string type
    string provider
    string providerAccountId
    string access_token
    string refresh_token
    datetime expires_at
  }
  
  SESSION {
    uuid id PK
    uuid userId FK
    string token UK
    datetime expiresAt
    datetime createdAt
    string userAgent
    string ipAddress
  }
  
  PORTFOLIO {
    uuid id PK
    uuid userId FK
    string name
    string description
    boolean isPublic
    datetime createdAt
    datetime updatedAt
  }
  
  HOLDING {
    uuid id PK
    uuid portfolioId FK
    string symbol
    float quantity
    float purchasePrice
    datetime purchaseDate
    string assetClass
  }
  
  AUDIT_LOG {
    uuid id PK
    uuid userId FK
    string action
    string resource
    string resourceId
    string ipAddress
    datetime timestamp
    json metadata
  }
```

### 2.4 Database Indexes & Performance

**Indexes:**

| Table | Index | Purpose |
|-------|-------|---------|
| User | `email` | Fast lookup by email (login) |
| Account | `provider, providerAccountId` | OAuth account lookup |
| Account | `userId` | Fetch all OAuth accounts for user |
| Session | `userId` | Fetch all sessions for user |
| Session | `token` | Refresh token validation |
| Portfolio | `userId` | Fetch user's portfolios |
| Holding | `portfolioId` | Fetch portfolio holdings |
| Holding | `portfolioId, symbol` | Unique constraint + fast lookup |
| AuditLog | `userId` | User activity history |
| AuditLog | `timestamp` | Time-based queries |
| AuditLog | `action` | Filter by action type |

**Performance Considerations:**

- All foreign keys indexed for JOIN performance
- Composite indexes on frequently queried columns
- UUID primary keys for distributed ID generation
- Soft deletes not implemented (hard delete for GDPR compliance)

---

## 3. API Design

### 3.1 Base URL Structure

```
Production: https://api.klyrsignals.com/api/v1/
Development: http://localhost:8000/api/v1/
```

### 3.2 Authentication Endpoints

#### POST /api/v1/auth/register

Create a new user account with email/password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

**Validation:**
- Email: Valid email format, unique
- Password: Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
- Name: Optional, max 100 chars

**Response (201 Created):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": null
  },
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Errors:**
- `400 Bad Request` - Invalid input
- `409 Conflict` - Email already exists

---

#### POST /api/v1/auth/login

Authenticate user with email/password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials
- `429 Too Many Requests` - Rate limit exceeded

**Rate Limiting:** Max 5 login attempts per minute per IP

---

#### POST /api/v1/auth/oauth/:provider

Initiate OAuth login flow.

**Providers:** `google`, `github`

**Request:** Redirect to this endpoint

**Response (302 Found):**
```
Location: https://accounts.google.com/o/oauth2/v2/auth?...
```

**Flow:**
1. User clicks "Login with Google/GitHub"
2. Redirect to OAuth provider
3. User authorizes app
4. Provider redirects to `/api/v1/auth/oauth/:provider/callback`
5. Backend exchanges code for tokens
6. Redirect to frontend with tokens

---

#### GET /api/v1/auth/oauth/:provider/callback

OAuth callback handler.

**Query Parameters:**
- `code` - Authorization code from provider
- `state` - CSRF protection token

**Response (302 Found):**
```
Location: https://klyrsignals.com/auth/callback?accessToken=...&refreshToken=...
```

**Errors:**
- `400 Bad Request` - Invalid state or code
- `401 Unauthorized` - OAuth provider error

---

#### POST /api/v1/auth/refresh

Refresh access token using refresh token.

**Request:**
```json
{
  "refreshToken": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Response (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "bmV3IHJlZnJlc2ggdG9rZW4..."
}
```

**Errors:**
- `401 Unauthorized` - Invalid or expired refresh token
- `403 Forbidden` - Token revoked

---

#### POST /api/v1/auth/logout

Logout user and invalidate refresh token.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "refreshToken": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Response (200 OK):**
```json
{
  "success": true
}
```

**Side Effects:**
- Refresh token deleted from database
- Access token blacklisted (optional, for immediate invalidation)

---

#### POST /api/v1/auth/password/reset

Request password reset email.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "If email exists, reset link sent"
}
```

**Security Note:** Always return success message to prevent email enumeration attacks.

**Email Template:**
```
Subject: Reset Your KlyrSignals Password

Hi,

You requested a password reset for your KlyrSignals account.

Click here to reset your password: https://klyrsignals.com/reset-password?token=RESET_TOKEN

This link expires in 1 hour.

If you didn't request this, you can safely ignore this email.

- The KlyrSignals Team
```

---

#### POST /api/v1/auth/password/reset/:token

Reset password with token.

**Request:**
```json
{
  "token": "reset_token_from_email",
  "newPassword": "NewSecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "success": true
}
```

**Errors:**
- `400 Bad Request` - Invalid password
- `401 Unauthorized` - Invalid or expired token

**Token Expiry:** 1 hour

---

### 3.3 Protected Endpoints (Require Authentication)

All existing v1.5 endpoints move under `/api/v1/protected/` and require valid JWT access token.

**Headers Required:**
```
Authorization: Bearer <access_token>
```

#### GET /api/v1/protected/portfolio

Get user's portfolio with holdings.

**Response (200 OK):**
```json
{
  "portfolio": {
    "id": "uuid",
    "name": "My Portfolio",
    "description": null,
    "isPublic": false,
    "holdings": [
      {
        "id": "uuid",
        "symbol": "AAPL",
        "quantity": 10,
        "purchasePrice": 150.00,
        "purchaseDate": "2024-01-15",
        "assetClass": "stock"
      }
    ]
  }
}
```

**Errors:**
- `401 Unauthorized` - Missing or invalid token
- `404 Not Found` - No portfolio exists (create one first)

---

#### POST /api/v1/protected/portfolio/import

Import holdings (WealthSimple, manual, etc.).

**Request:**
```json
{
  "holdings": [
    {
      "symbol": "AAPL",
      "quantity": 10,
      "purchasePrice": 150.00,
      "purchaseDate": "2024-01-15",
      "assetClass": "stock"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "portfolioId": "550e8400-e29b-41d4-a716-446655440000",
  "importedCount": 10
}
```

---

#### GET /api/v1/protected/analysis

Get portfolio analysis with AI insights.

**Response (200 OK):**
```json
{
  "analysis": {
    "totalValue": 15000.00,
    "totalGainLoss": 2500.00,
    "totalGainLossPercent": 20.0,
    "assetAllocation": {
      "stock": 70,
      "etf": 20,
      "crypto": 10
    },
    "insights": [
      "Your portfolio is heavily weighted towards tech stocks",
      "Consider diversifying into international markets"
    ]
  }
}
```

---

### 3.4 User Management Endpoints

#### GET /api/v1/users/me

Get current user profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "avatarUrl": "https://...",
    "emailVerified": "2024-01-01T00:00:00Z",
    "createdAt": "2024-01-01T00:00:00Z"
  }
}
```

---

#### PATCH /api/v1/users/me

Update current user profile.

**Request:**
```json
{
  "name": "New Name",
  "avatarUrl": "https://..."
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "New Name",
    "avatarUrl": "https://..."
  }
}
```

---

#### DELETE /api/v1/users/me

Delete user account and all associated data.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "confirmation": "DELETE_MY_ACCOUNT"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Account deleted successfully"
}
```

**Side Effects (Cascade Delete):**
- All portfolios deleted
- All holdings deleted
- All sessions invalidated
- All OAuth accounts disconnected
- Audit log entry created (for compliance)

**Errors:**
- `400 Bad Request` - Confirmation text missing
- `401 Unauthorized` - Invalid token

---

### 3.5 API Error Response Format

**Standard Error Response:**
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": {}
  }
}
```

**Common Error Codes:**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_INPUT` | 400 | Validation failed |
| `INVALID_CREDENTIALS` | 401 | Wrong email/password |
| `TOKEN_EXPIRED` | 401 | JWT expired |
| `TOKEN_INVALID` | 401 | JWT malformed |
| `UNAUTHORIZED` | 401 | Missing auth header |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## 4. Security Architecture

### 4.1 JWT Token Structure

#### Access Token (Short-lived)

**Payload:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "iat": 1709337600,
  "exp": 1709338500,
  "type": "access"
}
```

**Claims:**
- `sub` - User ID (subject)
- `email` - User email (for convenience)
- `iat` - Issued at (Unix timestamp)
- `exp` - Expiration (Unix timestamp, 15 minutes from iat)
- `type` - Token type ("access")

**Algorithm:** HS256 or RS256  
**Expiry:** 15 minutes  
**Storage:** Memory (frontend), not persisted

---

#### Refresh Token (Long-lived)

**Payload:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "sessionId": "session_uuid",
  "iat": 1709337600,
  "exp": 1709942400,
  "type": "refresh"
}
```

**Claims:**
- `sub` - User ID
- `sessionId` - Session ID (links to database)
- `iat` - Issued at
- `exp` - Expiration (7 days from iat)
- `type` - Token type ("refresh")

**Algorithm:** HS256 or RS256  
**Expiry:** 7 days  
**Storage:** HttpOnly cookie (secure, sameSite=strict)

---

### 4.2 Password Hashing

**Algorithm:** bcrypt  
**Rounds:** 12 (minimum)  
**Library:** passlib[bcrypt] or bcrypt

**Implementation:**
```python
import bcrypt

def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        password_hash.encode('utf-8')
    )
```

**Security Notes:**
- Never store plain text passwords
- Use constant-time comparison (bcrypt.checkpw does this)
- Salt is automatically generated and stored with hash

---

### 4.3 Rate Limiting

**Implementation:** FastAPI-Limiter with Redis backend

**Configuration:**
```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# Initialize on startup
@app.on_event("startup")
async def startup():
    redis = await aioredis.create_redis_pool("redis://localhost")
    await FastAPILimiter.init(redis)

# Apply to endpoints
@app.post("/auth/login", dependencies=[Depends(RateLimiter(times=5, minutes=1))])
async def login(...):
    # Max 5 login attempts per minute
```

**Rate Limits:**

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/auth/login` | 5 requests | 1 minute |
| `/auth/register` | 3 requests | 1 hour |
| `/auth/password/reset` | 3 requests | 1 hour |
| All other endpoints | 100 requests | 1 hour (per user) |
| Global IP limit | 1000 requests | 1 hour (per IP) |

**Response on Rate Limit:**
```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests. Please try again later.",
    "retryAfter": 60
  }
}
```

---

### 4.4 CORS Configuration

**Implementation:** FastAPI CORS middleware

**Configuration:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://klyrsignals.com",
        "https://www.klyrsignals.com",
        "http://localhost:3000",  # Development only
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
)
```

**Security Notes:**
- Never use `allow_origins=["*"]` in production
- Explicitly list allowed origins
- Use environment variables for configuration

---

### 4.5 Input Validation

**Backend:** Pydantic models

```python
from pydantic import BaseModel, EmailStr, validator
import re

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v
```

**Frontend:** Zod schema

```typescript
import { z } from 'zod';

export const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase letter')
    .regex(/[a-z]/, 'Must contain lowercase letter')
    .regex(/\d/, 'Must contain number')
    .regex(/[!@#$%^&*(),.?":{}|<>]/, 'Must contain special character'),
  name: z.string().max(100).optional(),
});
```

---

### 4.6 Audit Logging

**Purpose:** Track security-relevant events for compliance and debugging.

**Logged Events:**
- `user.register` - New account created
- `user.login` - Successful login
- `user.login.failed` - Failed login attempt
- `user.logout` - User logged out
- `user.password.reset.requested` - Password reset requested
- `user.password.reset.completed` - Password reset completed
- `user.deleted` - Account deleted
- `portfolio.created` - New portfolio created
- `portfolio.imported` - Holdings imported
- `holding.created` - New holding added
- `holding.updated` - Holding modified
- `holding.deleted` - Holding removed

**Implementation:**
```python
from fastapi import Request
from datetime import datetime

async def log_audit(
    db: Session,
    user_id: Optional[str],
    action: str,
    resource: Optional[str] = None,
    resource_id: Optional[str] = None,
    request: Optional[Request] = None,
    metadata: Optional[dict] = None
):
    audit_log = AuditLog(
        userId=user_id,
        action=action,
        resource=resource,
        resourceId=resource_id,
        ipAddress=request.client.host if request else None,
        userAgent=request.headers.get("user-agent") if request else None,
        timestamp=datetime.utcnow(),
        metadata=metadata
    )
    db.add(audit_log)
    db.commit()
```

---

## 5. Frontend Architecture

### 5.1 New Pages Required

#### 5.1.1 Login Page (`/login`)

**Purpose:** Authenticate existing users.

**Components:**
- Email input field
- Password input field (with show/hide toggle)
- "Remember me" checkbox
- "Forgot password?" link
- OAuth buttons (Google, GitHub)
- "Don't have an account? Register" link
- Form validation (client-side)
- Error message display

**Wireframe:**
```
┌────────────────────────────────────┐
│         KlyrSignals                │
│                                    │
│        Welcome Back                │
│                                    │
│  ┌────────────────────────────┐   │
│  │ Email                      │   │
│  │ user@example.com           │   │
│  └────────────────────────────┘   │
│                                    │
│  ┌────────────────────────────┐   │
│  │ Password          👁        │   │
│  │ •••••••••••••••            │   │
│  └────────────────────────────┘   │
│                                    │
│  ☐ Remember me      Forgot password?│
│                                    │
│  ┌────────────────────────────┐   │
│  │         Login              │   │
│  └────────────────────────────┘   │
│                                    │
│  ──────── Or continue with ───────│
│                                    │
│  ┌──────┐      ┌──────┐          │
│  │  G   │      │  ⌂  │          │
│  │Google│      │GitHub│          │
│  └──────┘      └──────┘          │
│                                    │
│  Don't have an account? Register  │
└────────────────────────────────────┘
```

---

#### 5.1.2 Register Page (`/register`)

**Purpose:** Create new user account.

**Components:**
- Name input field (optional)
- Email input field
- Password input field (with strength indicator)
- Confirm password field
- Terms of service checkbox (required)
- Privacy policy link
- OAuth buttons (Google, GitHub)
- "Already have an account? Login" link
- Real-time password validation
- Password strength meter

**Password Strength Indicator:**
```
Weak:    [██░░░░░░░░] Red
Fair:    [████░░░░░░] Orange
Good:    [██████░░░░] Yellow
Strong:  [██████████] Green
```

---

#### 5.1.3 Forgot Password Page (`/forgot-password`)

**Purpose:** Request password reset email.

**Components:**
- Email input field
- Submit button
- Success message (after submission)
- "Back to login" link

**Flow:**
1. User enters email
2. System sends reset email (if email exists)
3. Display success message (generic, don't reveal if email exists)
4. User receives email with reset link

---

#### 5.1.4 Reset Password Page (`/reset-password`)

**Purpose:** Set new password using reset token.

**URL:** `/reset-password?token=RESET_TOKEN`

**Components:**
- New password input field
- Confirm password field
- Password strength indicator
- Submit button
- Validation (password requirements)
- Error handling (expired/invalid token)

---

#### 5.1.5 Profile Page (`/profile`)

**Purpose:** View and update user profile.

**Components:**
- Avatar display (with upload/change option)
- Name input field
- Email display (read-only, or change with verification)
- Email verification status
- Account creation date
- "Change password" section
- "Delete account" section (with confirmation)
- Save button
- Cancel button

---

#### 5.1.6 Settings Page (`/settings`)

**Purpose:** Manage account settings and preferences.

**Sections:**

**Notification Preferences:**
- Email notifications toggle
- Marketing emails toggle
- Security alerts toggle (always on)

**Privacy Settings:**
- Portfolio visibility (public/private)
- Data sharing preferences
- Analytics opt-out

**Connected Accounts:**
- List of connected OAuth providers
- Connect/disconnect buttons
- Last connected date

**Session Management:**
- List of active sessions (device, location, last active)
- "Logout from all devices" button
- Individual session logout

**Security:**
- Two-factor authentication (future)
- Login history
- Security recommendations

---

### 5.2 Auth Context (React)

**File:** `frontend/context/AuthContext.tsx`

```typescript
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/router';

interface User {
  id: string;
  email: string;
  name?: string;
  avatarUrl?: string;
  emailVerified?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => Promise<void>;
  loginWithOAuth: (provider: 'google' | 'github') => void;
  resetPassword: (token: string, newPassword: string) => Promise<void>;
  requestPasswordReset: (email: string) => Promise<void>;
  updateUser: (data: Partial<User>) => Promise<void>;
  deleteAccount: (confirmation: string) => Promise<void>;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Check for existing session on mount
  useEffect(() => {
    async function checkAuth() {
      try {
        const response = await fetch('/api/v1/users/me', {
          credentials: 'include', // Include httpOnly cookies
        });
        if (response.ok) {
          const data = await response.json();
          setUser(data.user);
        }
      } catch (err) {
        console.error('Auth check failed:', err);
      } finally {
        setIsLoading(false);
      }
    }
    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
        credentials: 'include',
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error.message);
      }
      
      const data = await response.json();
      setUser(data.user);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  };

  const register = async (email: string, password: string, name?: string) => {
    try {
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name }),
        credentials: 'include',
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error.message);
      }
      
      const data = await response.json();
      setUser(data.user);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  };

  const logout = async () => {
    try {
      await fetch('/api/v1/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
    } catch (err) {
      console.error('Logout failed:', err);
    } finally {
      setUser(null);
      router.push('/login');
    }
  };

  const loginWithOAuth = (provider: 'google' | 'github') => {
    // Redirect to OAuth endpoint
    window.location.href = `/api/v1/auth/oauth/${provider}`;
  };

  const resetPassword = async (token: string, newPassword: string) => {
    const response = await fetch('/api/v1/auth/password/reset/' + token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, newPassword }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error.message);
    }
    
    router.push('/login?reset=success');
  };

  const requestPasswordReset = async (email: string) => {
    const response = await fetch('/api/v1/auth/password/reset', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error.message);
    }
  };

  const updateUser = async (data: Partial<User>) => {
    const response = await fetch('/api/v1/users/me', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'include',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error.message);
    }
    
    const result = await response.json();
    setUser(result.user);
  };

  const deleteAccount = async (confirmation: string) => {
    const response = await fetch('/api/v1/users/me', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ confirmation }),
      credentials: 'include',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error.message);
    }
    
    setUser(null);
    router.push('/');
  };

  const clearError = () => setError(null);

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    loginWithOAuth,
    resetPassword,
    requestPasswordReset,
    updateUser,
    deleteAccount,
    error,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

---

### 5.3 Protected Route Component

**File:** `frontend/components/ProtectedRoute.tsx`

```typescript
import { useAuth } from '../context/AuthContext';
import { useRouter } from 'next/router';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to login, but save the intended destination
    router.replace(`/login?redirect=${encodeURIComponent(router.asPath)}`);
    return null;
  }

  return <>{children}</>;
}
```

**Usage:**
```typescript
// In app/dashboard/page.tsx
import { ProtectedRoute } from '@/components/ProtectedRoute';

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  );
}
```

---

### 5.4 Token Storage Strategy

**Security Best Practice:** Use httpOnly cookies, NOT localStorage.

**Why httpOnly cookies?**
- ✅ Not accessible via JavaScript (XSS protection)
- ✅ Automatically sent with requests (convenient)
- ✅ Can be marked secure (HTTPS only)
- ✅ Can be marked sameSite (CSRF protection)

**Implementation:**

**Backend (Set Cookie):**
```python
from fastapi import Response
from datetime import datetime, timedelta

def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str
):
    # Access token (short-lived, in memory on frontend)
    # Not stored in cookie - frontend keeps in memory
    
    # Refresh token (long-lived, httpOnly cookie)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="strict",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/",
    )
```

**Frontend:**
```typescript
// Access token: Keep in memory (React state)
// Refresh token: Automatically sent via httpOnly cookie

// No need to manually store tokens
// Just use credentials: 'include' in fetch requests
```

---

## 6. Migration Strategy (v1.5 → v1.6)

### 6.1 Migration Timeline

**Total Estimated Time:** 6 weeks

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1 | Database Setup | PostgreSQL, Prisma, migrations |
| 2 | Backend Auth | User model, auth endpoints, OAuth |
| 3 | Frontend Auth | Login/register pages, AuthContext |
| 4 | Portfolio Migration | localStorage → database migration |
| 5 | QA & Security | Penetration testing, security audit |
| 6 | Deployment | Staging → production rollout |

---

### 6.2 Phase 1: Database Setup (Week 1)

**Tasks:**

- [ ] Set up PostgreSQL database (Railway or Supabase)
  - Create database instance
  - Configure connection string
  - Set up environment variables
- [ ] Install and configure Prisma ORM
  - `npm install prisma @prisma/client`
  - Initialize Prisma: `npx prisma init`
  - Define schema (Section 2.2)
- [ ] Run initial migration
  - `npx prisma migrate dev --name init`
  - Verify tables created
- [ ] Test database connection
  - Write simple query test
  - Verify Prisma Client generation

**Success Criteria:**
- ✅ Database accessible from backend
- ✅ All tables created with correct schema
- ✅ Prisma Client generated and working

---

### 6.3 Phase 2: Backend Auth (Week 2)

**Tasks:**

- [ ] Implement User model and repository
  - CRUD operations for User
  - Password hashing utilities
- [ ] Implement auth endpoints
  - POST /auth/register
  - POST /auth/login
  - POST /auth/logout
  - POST /auth/refresh
- [ ] Implement OAuth (Google, GitHub)
  - Register OAuth apps with providers
  - Implement OAuth flow
  - Handle callbacks
- [ ] Implement JWT token generation/validation
  - Access token generation
  - Refresh token generation
  - Token validation middleware
- [ ] Add rate limiting
  - Redis setup
  - Apply rate limits to auth endpoints
- [ ] Write unit tests
  - Test auth endpoints
  - Test token validation
  - Test OAuth flow (mocked)

**Success Criteria:**
- ✅ Users can register and login
- ✅ OAuth login works (Google, GitHub)
- ✅ JWT tokens issued and validated
- ✅ Rate limiting active
- ✅ Unit tests passing (>80% coverage)

---

### 6.4 Phase 3: Frontend Auth (Week 3)

**Tasks:**

- [ ] Create AuthContext
  - Implement all auth methods
  - Handle token storage (httpOnly cookies)
  - Manage user state
- [ ] Build login page
  - Email/password form
  - OAuth buttons
  - Error handling
- [ ] Build register page
  - Form with validation
  - Password strength indicator
  - Terms checkbox
- [ ] Build forgot/reset password pages
  - Request reset flow
  - Reset password form
- [ ] Build profile/settings pages
  - User profile display
  - Edit functionality
  - Delete account flow
- [ ] Add protected route wrapper
  - ProtectedRoute component
  - Apply to existing pages
- [ ] Update existing pages
  - Add auth checks
  - Show user-specific data

**Success Criteria:**
- ✅ All auth pages functional
- ✅ Protected routes redirect to login
- ✅ User data displayed correctly
- ✅ No console errors

---

### 6.5 Phase 4: Portfolio Migration (Week 4)

**Tasks:**

- [ ] Add migration flow for localStorage data
  - Detect existing localStorage data
  - Prompt user: "Import your local portfolio?"
- [ ] Implement migration endpoint
  - POST /protected/portfolio/migrate
  - Accept localStorage data
  - Save to database
- [ ] Build migration UI
  - Modal/prompt on first login
  - Progress indicator
  - Success/error messages
- [ ] Verify data integrity
  - Compare before/after
  - Validate all holdings migrated
- [ ] Clear localStorage after migration
  - Only after successful migration
  - Confirm with user

**Migration Flow:**
```
1. User logs in for first time
2. Frontend checks localStorage for existing portfolio
3. If found: Show migration modal
   "We found a local portfolio. Import it to your account?"
4. User clicks "Import"
5. Frontend sends localStorage data to backend
6. Backend saves to database
7. Frontend verifies migration success
8. Frontend clears localStorage
9. User redirected to dashboard with migrated data
```

**Success Criteria:**
- ✅ Existing v1.5 users can migrate data
- ✅ No data loss during migration
- ✅ localStorage cleared after migration
- ✅ User can continue using app seamlessly

---

### 6.6 Phase 5: QA & Security Audit (Week 5)

**Tasks:**

- [ ] Penetration testing
  - Test for OWASP Top 10 vulnerabilities
  - SQL injection testing
  - XSS testing
  - CSRF testing
- [ ] Security audit
  - Review auth implementation
  - Check password hashing
  - Verify token handling
  - Audit rate limiting
- [ ] Load testing
  - Test with 100 concurrent users
  - Measure response times
  - Identify bottlenecks
- [ ] User acceptance testing
  - Test all user stories
  - Verify edge cases
  - Collect feedback
- [ ] Bug fixes
  - Address all critical/high issues
  - Document known issues

**Security Checklist:**
- [ ] Passwords hashed with bcrypt (12+ rounds)
- [ ] JWT tokens properly signed and validated
- [ ] httpOnly cookies for refresh tokens
- [ ] CORS configured correctly
- [ ] Rate limiting active on all auth endpoints
- [ ] Input validation on all endpoints
- [ ] SQL injection prevented (Prisma ORM)
- [ ] XSS prevented (React escapes by default)
- [ ] CSRF protection (sameSite cookies)
- [ ] HTTPS enforced in production

**Success Criteria:**
- ✅ No critical/high security vulnerabilities
- ✅ All user stories verified
- ✅ Performance acceptable (<500ms response time)
- ✅ Ready for production deployment

---

### 6.7 Phase 6: Deployment (Week 6)

**Tasks:**

- [ ] Deploy to staging
  - Deploy backend to Railway/Render
  - Deploy frontend to Vercel/Netlify
  - Configure environment variables
- [ ] Final testing on staging
  - Smoke tests
  - Integration tests
- [ ] Deploy to production
  - Update DNS records
  - Enable HTTPS (Let's Encrypt)
  - Configure CDN (optional)
- [ ] Monitor for issues
  - Set up Sentry (error tracking)
  - Set up LogRocket (session replay)
  - Monitor logs for errors

**Deployment Checklist:**
- [ ] Database backups enabled
- [ ] Environment variables set
- [ ] HTTPS enabled
- [ ] CORS configured for production domain
- [ ] Rate limiting configured
- [ ] Monitoring tools active
- [ ] Rollback plan documented

**Success Criteria:**
- ✅ Production deployment successful
- ✅ No downtime during deployment
- ✅ Monitoring active
- ✅ Users can access app

---

### 6.8 Backwards Compatibility

**v1.5 Users (localStorage):**

| Scenario | Behavior |
|----------|----------|
| **No account, using localStorage** | Can continue using app without account (local mode) |
| **Creates account, first login** | Prompted to migrate localStorage data |
| **After migration** | Can use cloud mode (data synced across devices) |
| **Chooses not to migrate** | Can continue using local mode |
| **Both modes simultaneously** | Supported (toggle between local/cloud) |

**UI Indicators:**
- Show "Local Mode" badge when using localStorage
- Show "Cloud Mode" badge when using account
- Clear indication of which mode is active

---

## 7. Technology Stack

### 7.1 Backend (Python/FastAPI)

**Core Dependencies:**

```txt
# requirements.txt

# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Authentication
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4            # Password hashing
bcrypt==4.1.2

# OAuth
authlib==1.3.0                    # OAuth client
httpx==0.26.0                     # HTTP client for OAuth

# Database
prisma==0.11.0                    # ORM
psycopg2-binary==2.9.9            # PostgreSQL driver

# Rate Limiting
fastapi-limiter==0.1.6
redis==5.0.1                      # For rate limiting storage

# Email (password reset)
sendgrid==6.11.0                  # Email service

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0                     # Test client

# Development
python-dotenv==1.0.0              # Environment variables
black==23.12.1                    # Code formatting
ruff==0.1.9                       # Linting
```

---

### 7.2 Frontend (Next.js)

**Core Dependencies:**

```json
{
  "dependencies": {
    "next": "^14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    
    "next-auth": "^4.24.0",  // Auth library for Next.js
    "jose": "^5.2.0",        // JWT utilities
    "zod": "^3.22.0",        // Form validation
    
    "@tanstack/react-query": "^5.17.0",  // Data fetching
    "axios": "^1.6.0",                   // HTTP client
    
    "tailwindcss": "^3.4.0",  // Styling
    "@headlessui/react": "^1.7.0",  // UI components
    
    "react-hook-form": "^7.49.0",  // Form handling
    "@hookform/resolvers": "^3.3.0"  // Zod resolver
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.3.0",
    "eslint": "^8.56.0",
    "prettier": "^3.1.0"
  }
}
```

---

### 7.3 Infrastructure

**Database:**
- **Provider:** Railway or Supabase
- **Version:** PostgreSQL 15
- **Features:**
  - Connection pooling (built-in)
  - Daily automated backups
  - Point-in-time recovery
  - Read replicas (future scaling)

**Email:**
- **Provider:** SendGrid
- **Plan:** Free tier (100 emails/day)
- **Templates:**
  - Password reset email
  - Welcome email
  - Email verification (future)

**Hosting:**
- **Backend:** Railway or Render
  - Auto-deploy from GitHub
  - Environment variables
  - SSL/TLS termination
- **Frontend:** Vercel or Netlify
  - Auto-deploy from GitHub
  - Edge caching
  - Preview deployments

**Monitoring:**
- **Error Tracking:** Sentry (free tier: 5K errors/month)
  - Backend error tracking
  - Frontend error tracking
  - Performance monitoring
- **Session Replay:** LogRocket (free tier: 1K sessions/month)
  - User session recording
  - Debugging tool
- **Uptime Monitoring:** UptimeRobot (free tier: 50 monitors)
  - Ping every 5 minutes
  - Email/SMS alerts

---

## 8. Diagrams

### 8.1 Authentication Flow Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database
    participant OAuth

    %% Email/Password Login
    User->>Frontend: Enter email/password
    Frontend->>Backend: POST /auth/login
    Backend->>Database: Find user by email
    Database-->>Backend: User record
    Backend->>Backend: Verify password (bcrypt)
    Backend->>Backend: Generate JWT tokens
    Backend->>Database: Create session (refresh token)
    Backend-->>Frontend: Return tokens (refresh in cookie)
    Frontend-->>User: Redirect to dashboard

    %% OAuth Login
    User->>Frontend: Click "Login with Google"
    Frontend->>Backend: GET /auth/oauth/google
    Backend->>OAuth: Redirect to Google
    OAuth->>User: Google login page
    User->>OAuth: Enter credentials
    OAuth->>Backend: Callback with code
    Backend->>OAuth: Exchange code for tokens
    OAuth-->>Backend: User info
    Backend->>Database: Find/create user
    Backend->>Backend: Generate JWT tokens
    Backend-->>Frontend: Redirect with tokens
    Frontend-->>User: Redirect to dashboard

    %% Protected Request
    User->>Frontend: Access protected page
    Frontend->>Backend: GET /protected/portfolio
    Note over Backend: Validate access token
    Backend->>Database: Query user's portfolio
    Database-->>Backend: Portfolio data
    Backend-->>Frontend: Return portfolio
    Frontend-->>User: Display portfolio

    %% Token Refresh
    Frontend->>Backend: POST /auth/refresh
    Note over Backend: Validate refresh token
    Backend->>Database: Verify session exists
    Database-->>Backend: Session valid
    Backend->>Backend: Generate new tokens
    Backend-->>Frontend: Return new tokens
    Frontend-->>Frontend: Update tokens

    %% Logout
    User->>Frontend: Click logout
    Frontend->>Backend: POST /auth/logout
    Backend->>Database: Delete session
    Backend-->>Frontend: Success
    Frontend-->>User: Redirect to login
```

---

### 8.2 Password Reset Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database
    participant Email

    User->>Frontend: Click "Forgot password?"
    Frontend->>Frontend: Show email input
    User->>Frontend: Enter email
    Frontend->>Backend: POST /auth/password/reset
    Backend->>Database: Find user by email
    Database-->>Backend: User found (or not)
    Backend->>Backend: Generate reset token (1hr expiry)
    Backend->>Database: Store token hash
    Backend->>Email: Send reset email
    Email-->>Backend: Email sent
    Backend-->>Frontend: Success (generic message)
    Frontend-->>User: "If email exists, reset link sent"

    User->>Email: Open email
    User->>Frontend: Click reset link
    Frontend->>Frontend: Extract token from URL
    Frontend->>Frontend: Show reset password form
    User->>Frontend: Enter new password
    Frontend->>Backend: POST /auth/password/reset/:token
    Backend->>Database: Verify token
    Database-->>Backend: Token valid
    Backend->>Backend: Hash new password
    Backend->>Database: Update password hash
    Backend->>Database: Invalidate all sessions
    Backend-->>Frontend: Success
    Frontend-->>User: Redirect to login
```

---

### 8.3 Data Flow Diagram (localStorage → Database)

```mermaid
flowchart TD
    A[v1.5 User with localStorage] --> B{User logs in}
    B --> C[First login?]
    C -->|Yes| D[Check localStorage]
    C -->|No| E[Load from database]
    D --> F{Data exists?}
    F -->|No| E
    F -->|Yes| G[Show migration modal]
    G --> H{User accepts?}
    H -->|Yes| I[Send data to backend]
    H -->|No| J[Continue with empty cloud portfolio]
    I --> K[Backend saves to database]
    K --> L[Verify migration]
    L --> M[Clear localStorage]
    M --> N[Redirect to dashboard]
    J --> N
    E --> N
```

---

## 9. Environment Variables

### 9.1 Backend Environment Variables

```bash
# .env (backend)

# Database
DATABASE_URL="postgresql://user:password@host:5432/klyrsignals"

# JWT
JWT_SECRET="your-super-secret-key-min-32-chars"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth - Google
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
GOOGLE_REDIRECT_URI="https://api.klyrsignals.com/api/v1/auth/oauth/google/callback"

# OAuth - GitHub
GITHUB_CLIENT_ID="your-github-client-id"
GITHUB_CLIENT_SECRET="your-github-client-secret"
GITHUB_REDIRECT_URI="https://api.klyrsignals.com/api/v1/auth/oauth/github/callback"

# Email (SendGrid)
SENDGRID_API_KEY="your-sendgrid-api-key"
EMAIL_FROM="noreply@klyrsignals.com"

# Rate Limiting
REDIS_URL="redis://localhost:6379"

# CORS
ALLOWED_ORIGINS="https://klyrsignals.com,https://www.klyrsignals.com,http://localhost:3000"

# Security
BCRYPT_ROUNDS=12
```

### 9.2 Frontend Environment Variables

```bash
# .env.local (frontend)

# API
NEXT_PUBLIC_API_URL="https://api.klyrsignals.com"

# OAuth
NEXT_PUBLIC_GOOGLE_CLIENT_ID="your-google-client-id"
NEXT_PUBLIC_GITHUB_CLIENT_ID="your-github-client-id"

# Feature Flags
NEXT_PUBLIC_ENABLE_OAUTH=true
NEXT_PUBLIC_ENABLE_EMAIL_VERIFICATION=false
```

---

## 10. Testing Strategy

### 10.1 Backend Unit Tests

**Test Files:**
- `tests/test_auth.py` - Auth endpoints
- `tests/test_users.py` - User management
- `tests/test_portfolio.py` - Portfolio endpoints
- `tests/test_security.py` - Security tests

**Example Test:**
```python
# tests/test_auth.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "accessToken" in data
    assert "refreshToken" in data
    assert data["user"]["email"] == "test@example.com"

def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"

def test_rate_limiting():
    # Make 6 login attempts in 1 minute
    for i in range(6):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword"
            }
        )
    
    # 6th attempt should be rate limited
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMITED"
```

### 10.2 Frontend Component Tests

**Test Files:**
- `components/Login.test.tsx`
- `components/Register.test.tsx`
- `context/AuthContext.test.tsx`

**Example Test:**
```typescript
// components/Login.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { Login } from './Login';

test('shows validation error for invalid email', async () => {
  render(<Login />);
  
  const emailInput = screen.getByLabelText(/email/i);
  const submitButton = screen.getByRole('button', { name: /login/i });
  
  fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
  fireEvent.click(submitButton);
  
  const error = await screen.findByText(/invalid email/i);
  expect(error).toBeInTheDocument();
});

test('calls login function with correct credentials', async () => {
  const mockLogin = jest.fn();
  render(<Login onLogin={mockLogin} />);
  
  fireEvent.change(screen.getByLabelText(/email/i), {
    target: { value: 'test@example.com' }
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: 'SecurePass123!' }
  });
  fireEvent.click(screen.getByRole('button', { name: /login/i }));
  
  await waitFor(() => {
    expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'SecurePass123!');
  });
});
```

---

## 11. Success Criteria Checklist

### Architecture Design
- [x] Complete database schema designed (User, Account, Session, Portfolio, Holding, AuditLog)
- [x] API endpoints documented (auth, protected, user management)
- [x] Security architecture defined (JWT, bcrypt, rate limiting, CORS)
- [x] Frontend auth flow designed (login, register, OAuth, password reset)
- [x] Migration strategy documented (v1.5 → v1.6)
- [x] Technology stack selected and justified
- [x] All diagrams created (ERD, sequence, flow)
- [x] Tasks broken down for Peter (implementation)
- [x] Estimated timeline provided (6 weeks)

### Implementation Readiness
- [x] Prisma schema ready for migration
- [x] API contract defined (request/response formats)
- [x] Frontend components specified
- [x] Security requirements documented
- [x] Testing strategy outlined
- [x] Deployment checklist created

---

## 12. Next Steps

1. **Review this document** with team (Jarvis, Peter, Heimdall)
2. **Create TASKS_V1.6.md** with detailed implementation tasks
3. **Spawn Peter** for implementation (estimated 40-50 hours)
4. **Update RUN_STATE.md** to track v1.6 development
5. **Begin Phase 1** (Database Setup)

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-01  
**Next Review:** After implementation begins
