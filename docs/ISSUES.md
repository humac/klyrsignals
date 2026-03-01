# ISSUES.md - KlyrSignals

**Project:** KlyrSignals v1.6.0  
**Created:** 2026-02-28  
**Last Updated:** 2026-03-01  
**Status:** ✅ v1.6 Complete

---

## Resolved Issues

### ✅ [ISSUE-001] Missing Import in analysis.py

**Status:** ✅ RESOLVED  
**Severity:** Critical  
**Found:** 2026-02-28 (Heimdall QA Phase)  
**Resolved:** 2026-02-28 (Peter Fix Phase)

**Description:**
Missing import for `PortfolioAnalysisRequest` model in `backend/app/api/v1/analysis.py` caused `/api/v1/blind-spots` endpoint to return 400 error.

**Root Cause:**
Import statement at top of file did not include `PortfolioAnalysisRequest` from `app.models.portfolio`, even though the model was used in the endpoint handler.

**Error:**
```
400 Bad Request - Field required
```

**Fix Applied:**
Added `PortfolioAnalysisRequest` to imports:
```python
from app.models.portfolio import (
    RiskScoreResponse,
    RecommendationResponse,
    BlindSpotResponse,
    PortfolioAnalysisRequest,  # ✅ ADDED
)
```

**Verification:**
- ✅ Endpoint `/api/v1/blind-spots` now returns 200 OK
- ✅ Response schema matches ARCH.md specification
- ✅ No regression in other endpoints
- ✅ Heimdall Re-QA: PASS

**Lessons Learned:**
- Always verify imports match usage before handoff
- Peter's runtime verification caught this before production
- Heimdall's live API testing validated the fix

---

## Known Limitations (v1.6)

### ⚠️ [LIMITATION-001] In-Memory Database (Development Only)

**Status:** Known Limitation  
**Impact:** High  
**Workaround:** Deploy with PostgreSQL for production

**Description:**
Current implementation uses in-memory database service for development. All data is lost on server restart.

**Reason:**
PostgreSQL integration designed but not yet deployed in development environment.

**Resolution:**
Deploy with managed PostgreSQL (Railway or Supabase) for production. See `docs/DEPLOYMENT_CHECKLIST.md` for setup steps.

---

### ⚠️ [LIMITATION-002] OAuth Not Configured in Development

**Status:** Known Limitation  
**Impact:** Medium  
**Workaround:** Use email/password authentication

**Description:**
OAuth endpoints return errors when Google/GitHub credentials are not configured in environment variables.

**Reason:**
OAuth requires external app registration and credentials (client ID, secret).

**Resolution:**
Configure OAuth credentials in production:
- Google Cloud Console: Create OAuth 2.0 credentials
- GitHub Developer Settings: Create OAuth App
- Add credentials to environment variables

See `docs/DEPLOYMENT_CHECKLIST.md` for OAuth setup instructions.

---

### ⚠️ [LIMITATION-003] No Password Reset Flow

**Status:** Known Limitation  
**Impact:** Medium  
**Workaround:** Manual password reset via database

**Description:**
Users cannot reset forgotten passwords via email.

**Reason:**
Password reset requires email service integration (SendGrid, Postmark) and secure token generation.

**Resolution Path:**
v1.7 will add:
- Password reset request endpoint
- Email template with reset link
- Secure token with expiration
- Password reset confirmation endpoint

---

### ⚠️ [LIMITATION-004] No Rate Limiting Configured

**Status:** Known Limitation  
**Impact:** Medium  
**Workaround:** Deploy behind Cloudflare or reverse proxy

**Description:**
Backend API has no rate limiting middleware configured, making it vulnerable to abuse.

**Reason:**
Rate limiting deferred to production deployment; `fastapi-limiter` in requirements but not configured.

**Resolution:**
Add rate limiting in production deployment:
```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.post("/api/v1/auth/login")
@RateLimiter(times=10, seconds=60)
async def login(...):
    ...
```

See `docs/DEPLOYMENT_CHECKLIST.md` for rate limiting configuration.

---

### ⚠️ [LIMITATION-005] No Email Verification

**Status:** Known Limitation  
**Impact:** Low  
**Workaround:** Manual verification if needed

**Description:**
User registration does not require email verification. Users can register with any email address.

**Reason:**
Email verification requires email service integration and additional flow complexity.

**Resolution Path:**
v1.7 will add:
- Verification token on registration
- Email with verification link
- Verify email endpoint
- Restrict protected features until verified

---

### ⚠️ [LIMITATION-006] No Frontend Automated Tests

**Status:** Known Limitation  
**Impact:** Medium  
**Workaround:** Manual browser testing

**Description:**
Frontend lacks automated test suite (Jest, React Testing Library, Playwright).

**Reason:**
MVP focus on core functionality; tests deferred to post-v1.6.

**Resolution Path:**
Add Jest + React Testing Library + Playwright for E2E tests.

---

## Technical Debt

### 🔧 [DEBT-001] Add Test Coverage Metrics

**Priority:** Medium  
**Effort:** Low

**Description:**
Backend tests exist but no coverage metrics (pytest-cov not installed).

**Action:**
Add to `requirements-dev.txt`:
```
pytest-cov>=4.0.0
```

Run with:
```bash
pytest --cov=app --cov-report=html
```

---

### 🔧 [DEBT-002] Add Frontend E2E Tests

**Priority:** Medium  
**Effort:** Medium

**Description:**
No end-to-end tests for critical user flows (register → login → migrate → analyze).

**Action:**
Add Playwright:
```bash
npm install -D @playwright/test
npx playwright install
```

Test flows:
- User registration
- Login with email/password
- OAuth login (Google, GitHub)
- Portfolio migration
- Analysis generation

---

### 🔧 [DEBT-003] Add API Versioning Strategy

**Priority:** Low  
**Effort:** Low

**Description:**
API uses `/api/v1/` prefix but no formal versioning strategy documented.

**Action:**
Document API versioning approach:
- URL versioning: `/api/v1/`, `/api/v2/`
- Deprecation policy
- Backward compatibility guarantees

---

## Security Considerations

### 🔒 [SECURITY-001] HTTPS Required in Production

**Priority:** Critical  
**Status:** Deployment requirement

**Description:**
All authentication endpoints must use HTTPS in production to protect credentials and tokens.

**Action:**
- Deploy backend with HTTPS (Railway provides by default)
- Deploy frontend with HTTPS (Vercel provides by default)
- Set `SECURE_COOKIE=true` in production
- Set `CORS_ORIGINS` to HTTPS URLs only

---

### 🔒 [SECURITY-002] Secret Key Management

**Priority:** Critical  
**Status:** Deployment requirement

**Description:**
`SECRET_KEY` must be a strong random value in production, never hardcoded.

**Action:**
Generate secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add to production environment variables (never commit to git).

---

### 🔒 [SECURITY-003] Database Connection String

**Priority:** Critical  
**Status:** Deployment requirement

**Description:**
PostgreSQL connection string contains credentials and must be kept secret.

**Action:**
- Store in environment variable `DATABASE_URL`
- Never commit to git
- Use managed service (Railway/Supabase) for secure hosting
- Enable SSL/TLS for database connections

---

## Future Enhancements (v1.7+ Roadmap)

### 🚀 [ENHANCE-001] Password Reset Flow

**Priority:** High  
**Effort:** Medium

**Description:**
Add password reset via email for users who forget credentials.

**Requirements:**
- SendGrid or Postmark integration
- Password reset request endpoint
- Secure token generation (1-hour expiry)
- Email template with reset link
- Password reset confirmation endpoint

**Estimated Effort:** 1 week

---

### 🚀 [ENHANCE-002] Email Verification

**Priority:** Medium  
**Effort:** Medium

**Description:**
Require email verification on registration to prevent fake accounts.

**Requirements:**
- Verification token on registration
- Email with verification link
- Verify email endpoint
- Restrict features until verified

**Estimated Effort:** 1 week

---

### 🚀 [ENHANCE-003] Rate Limiting

**Priority:** High  
**Effort:** Low

**Description:**
Add rate limiting to prevent API abuse.

**Requirements:**
- fastapi-limiter middleware
- Redis backend for distributed rate limiting
- Configure limits per endpoint:
  - Auth endpoints: 10 requests/minute
  - Analysis endpoints: 30 requests/minute
  - General endpoints: 100 requests/minute

**Estimated Effort:** 2-3 days

---

### 🚀 [ENHANCE-004] Advanced Session Management

**Priority:** Medium  
**Effort:** Medium

**Description:**
Enhance session management with device tracking and revocation.

**Features:**
- List active sessions
- Revoke specific sessions
- Device fingerprinting
- Session activity logging

**Estimated Effort:** 1-2 weeks

---

### 🚀 [ENHANCE-005] Two-Factor Authentication (2FA)

**Priority:** Medium  
**Effort:** Medium

**Description:**
Add optional 2FA for enhanced security.

**Features:**
- TOTP (Google Authenticator, Authy)
- Backup codes
- SMS option (Twilio)

**Estimated Effort:** 2 weeks

---

## Issue Tracking Process

1. **Discovery:** Issues found during QA (Heimdall) or user testing
2. **Documentation:** Log in this file with severity and impact
3. **Prioritization:** Jarvis + User decide priority for next sprint
4. **Resolution:** Peter implements fix, Heimdall verifies
5. **Closure:** Move to "Resolved" section with verification notes

---

**Last Updated:** 2026-03-01  
**Total Issues:** 1 resolved, 6 known limitations, 3 technical debt items, 3 security considerations, 5 future enhancements
