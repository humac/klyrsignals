# KlyrSignals v1.6 - Deployment Checklist

**Version:** 1.6.0  
**Status:** Ready for Production  
**Last Updated:** 2026-03-01

---

## Pre-Deployment Verification

### ✅ Code Quality

- [ ] All tests passing (`npm test` + `pytest`)
- [ ] No TypeScript errors (`npm run build`)
- [ ] No Python import errors
- [ ] Linting passes (ESLint, Flake8/Black)
- [ ] No console.log() statements in production code
- [ ] No TODO comments blocking deployment

### ✅ Documentation

- [ ] README.md updated with v1.6 features
- [ ] DECISIONS.md includes auth/OAuth decisions
- [ ] ISSUES.md lists known limitations
- [ ] API documentation current (Swagger at `/docs`)
- [ ] Environment variables documented (see below)

### ✅ Git Hygiene

- [ ] All changes committed
- [ ] Clean working tree (`git status`)
- [ ] On main branch
- [ ] Pushed to remote (`git push origin main`)
- [ ] Tag created for release (`git tag v1.6.0`)

---

## Environment Variables Setup

### Frontend (.env.local → Vercel)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://api.klyrsignals.com
NEXT_PUBLIC_APP_URL=https://klyrsignals.com

# OAuth (optional for build, required for runtime)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=<google-client-id>
NEXT_PUBLIC_GITHUB_CLIENT_ID=<github-client-id>
```

**Vercel Setup:**
1. Go to Vercel Dashboard → Project → Settings → Environment Variables
2. Add each variable above
3. Select "Production" environment
4. Save and redeploy

### Backend (.env → Railway)

**Required Variables:**
```bash
# Security (CRITICAL - Generate secure random string)
SECRET_KEY=<generate-with-python-secrets-token-urlsafe-32>

# Database (CRITICAL - PostgreSQL connection string)
DATABASE_URL=postgresql://user:password@host:5432/klyrsignals

# OAuth - Google (Required for Google sign-in)
GOOGLE_CLIENT_ID=<google-client-id-from-console>
GOOGLE_CLIENT_SECRET=<google-client-secret-from-console>
GOOGLE_REDIRECT_URI=https://api.klyrsignals.com/api/v1/oauth/google/callback

# OAuth - GitHub (Required for GitHub sign-in)
GITHUB_CLIENT_ID=<github-client-id-from-settings>
GITHUB_CLIENT_SECRET=<github-client-secret-from-settings>
GITHUB_REDIRECT_URI=https://api.klyrsignals.com/api/v1/oauth/github/callback

# CORS (Required - Comma-separated list of allowed origins)
CORS_ORIGINS=https://klyrsignals.com,https://www.klyrsignals.com

# JWT Configuration
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Optional Variables:**
```bash
# Rate Limiting (Recommended for production)
REDIS_URL=redis://localhost:6379
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_AUTH=10/minute

# Email (Required for password reset in v1.7)
SENDGRID_API_KEY=<sendgrid-api-key>
EMAIL_FROM=noreply@klyrsignals.com

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

**Railway Setup:**
1. Go to Railway Dashboard → Project → Variables
2. Add each variable above
3. Save (automatic redeploy)

---

## PostgreSQL Database Setup

### Option 1: Railway PostgreSQL (Recommended)

**Steps:**
1. **Create Database:**
   - Railway Dashboard → New → Database → PostgreSQL
   - Wait for provisioning (~2 minutes)
   - Copy `DATABASE_URL` from Variables tab

2. **Configure Connection:**
   - Add `DATABASE_URL` to Railway project variables
   - Railway auto-provides SSL/TLS
   - Connection pooling enabled by default

3. **Run Migrations:**
   ```bash
   # Install Prisma CLI globally or use npx
   npx prisma migrate deploy --schema backend/prisma/schema.prisma
   
   # Generate Prisma client
   npx prisma generate --schema backend/prisma/schema.prisma
   ```

4. **Verify Connection:**
   ```bash
   # Connect to database
   psql $DATABASE_URL
   
   # Check tables exist
   \dt
   
   # Should see: users, accounts, sessions, portfolios, holdings, audit_logs
   ```

**Cost:** Free tier (500MB storage, sufficient for MVP)

### Option 2: Supabase PostgreSQL

**Steps:**
1. **Create Project:**
   - Go to supabase.com
   - New Project → Organization → Name: KlyrSignals
   - Set database password (save securely)
   - Wait for provisioning (~2 minutes)

2. **Get Connection String:**
   - Project Settings → Database
   - Copy "Connection string" (URI mode)
   - Format: `postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres`

3. **Configure SSL:**
   - Download SSL certificate (if required)
   - Add `?sslmode=require` to connection string

4. **Run Migrations:**
   ```bash
   DATABASE_URL=<supabase-connection-string> npx prisma migrate deploy
   ```

**Cost:** Free tier (500MB database, sufficient for MVP)

### Option 3: Self-Hosted PostgreSQL

**Not recommended for MVP** - Use managed service unless you have DevOps expertise.

---

## OAuth Credential Setup

### Google OAuth 2.0

**Steps:**

1. **Create Google Cloud Project:**
   - Go to https://console.cloud.google.com/
   - Create new project: "KlyrSignals"
   - Note Project ID

2. **Enable Google+ API:**
   - API & Services → Library
   - Search "Google+ API"
   - Enable (required for profile info)

3. **Create OAuth Credentials:**
   - API & Services → Credentials
   - Create Credentials → OAuth 2.0 Client ID
   - Application type: Web application
   - Name: "KlyrSignals Production"

4. **Configure Redirect URI:**
   - Authorized redirect URIs:
     - `https://api.klyrsignals.com/api/v1/oauth/google/callback`
     - `http://localhost:8000/api/v1/oauth/google/callback` (development)

5. **Configure OAuth Consent Screen:**
   - API & Services → OAuth consent screen
   - User Type: External
   - App name: KlyrSignals
   - User support email: your-email@domain.com
   - Developer contact: your-email@domain.com
   - Scopes: email, profile, openid

6. **Copy Credentials:**
   - Client ID: `<copy-this>`
   - Client Secret: `<copy-this>`
   - Add to Railway environment variables

**Documentation:** https://developers.google.com/identity/protocols/oauth2

### GitHub OAuth App

**Steps:**

1. **Register OAuth App:**
   - Go to https://github.com/settings/developers
   - New OAuth App
   - Application name: KlyrSignals
   - Homepage URL: `https://klyrsignals.com`
   - Authorization callback URL:
     - `https://api.klyrsignals.com/api/v1/oauth/github/callback`
     - `http://localhost:8000/api/v1/oauth/github/callback` (development)

2. **Generate Client Secret:**
   - After creation, click "Generate a new client secret"
   - **Copy immediately** (shown only once)
   - If lost, regenerate

3. **Copy Credentials:**
   - Client ID: `<copy-this>`
   - Client Secret: `<copy-this>`
   - Add to Railway environment variables

**Documentation:** https://docs.github.com/en/developers/apps/building-oauth-apps

---

## Security Hardening

### HTTPS/TLS

- [ ] Frontend deployed with HTTPS (Vercel provides automatically)
- [ ] Backend deployed with HTTPS (Railway provides automatically)
- [ ] All redirect URIs use HTTPS
- [ ] CORS_ORIGINS only includes HTTPS URLs
- [ ] HSTS headers enabled (Vercel/Railway default)

### Cookie Security

- [ ] Refresh tokens use httpOnly flag (prevents XSS)
- [ ] Refresh tokens use Secure flag (HTTPS only)
- [ ] Refresh tokens use SameSite=strict (CSRF protection)
- [ ] Cookie domain set to production domain

### Rate Limiting

**Configure fastapi-limiter:**

```python
# backend/app/main.py
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis

@app.on_event("startup")
async def startup():
    redis = await aioredis.create_redis_pool("redis://localhost")
    await FastAPILimiter.init(redis, prefix="klyrsignals")

@app.post("/api/v1/auth/login")
@RateLimiter(times=10, seconds=60)  # 10 requests per minute
async def login(...):
    ...

@app.post("/api/v1/auth/register")
@RateLimiter(times=5, seconds=60)  # 5 requests per minute
async def register(...):
    ...
```

**Redis Setup (Railway):**
1. Railway → New → Redis
2. Copy `REDIS_URL` from Variables
3. Add to backend environment variables
4. Install dependencies: `pip install fastapi-limiter aioredis`

### Input Validation

- [ ] All endpoints use Pydantic models for validation
- [ ] Email validation enabled (email-validator package)
- [ ] Password strength validation (min 8 chars, mixed case, numbers)
- [ ] Symbol validation (uppercase, max length)
- [ ] Quantity/price validation (positive numbers)

### CORS Configuration

**Production CORS Settings:**
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://klyrsignals.com",
        "https://www.klyrsignals.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Never allow `*` in production with credentials!**

---

## Deployment Steps

### Frontend (Vercel)

1. **Connect Repository:**
   - Vercel Dashboard → Add New → Project
   - Import from GitHub: `humac/klyrsignals`
   - Root Directory: `frontend`

2. **Configure Build:**
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

3. **Add Environment Variables:**
   - See "Frontend Environment Variables" section above
   - Add all required variables

4. **Deploy:**
   - Click "Deploy"
   - Wait for build (~2-3 minutes)
   - Verify deployment at `https://klyrsignals.vercel.app`

5. **Add Custom Domain (Optional):**
   - Project Settings → Domains
   - Add: `klyrsignals.com`
   - Configure DNS (Vercel provides instructions)
   - SSL certificate auto-provisioned

### Backend (Railway)

1. **Connect Repository:**
   - Railway Dashboard → New Project → Deploy from GitHub
   - Select: `humac/klyrsignals`
   - Root Directory: `backend`

2. **Configure Build:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables:**
   - See "Backend Environment Variables" section above
   - Add all required variables (SECRET_KEY, DATABASE_URL, OAuth creds)

4. **Deploy:**
   - Railway auto-deploys on push
   - Wait for build (~1-2 minutes)
   - Verify deployment at `https://<project>.railway.app`

5. **Add Custom Domain (Optional):**
   - Project Settings → Domains
   - Add: `api.klyrsignals.com`
   - Configure DNS (CNAME to Railway domain)
   - SSL certificate auto-provisioned

### Database (Railway PostgreSQL)

1. **Create Database:**
   - Railway → New → Database → PostgreSQL
   - Wait for provisioning

2. **Get Connection String:**
   - Copy `DATABASE_URL` from Variables tab
   - Add to backend environment variables

3. **Run Migrations:**
   ```bash
   # In Railway shell or locally with connection string
   npx prisma migrate deploy --schema backend/prisma/schema.prisma
   ```

4. **Verify Tables:**
   ```bash
   psql $DATABASE_URL -c "\dt"
   # Should see: users, accounts, sessions, portfolios, holdings, audit_logs
   ```

---

## Post-Deployment Verification

### Health Checks

**Frontend:**
```bash
curl https://klyrsignals.com
# Should return 200 OK with HTML
```

**Backend:**
```bash
curl https://api.klyrsignals.com/api/health
# Should return: {"status": "healthy", "timestamp": "...", "version": "1.6.0"}
```

**Database:**
```bash
curl https://api.klyrsignals.com/api/v1/auth/me \
  -H "Authorization: Bearer <test-token>"
# Should return user profile (or 401 if token invalid)
```

### Authentication Flow Test

1. **Register New User:**
   - Go to https://klyrsignals.com/register
   - Enter email, password, confirm password
   - Click "Create Account"
   - Verify redirect to dashboard

2. **Login:**
   - Go to https://klyrsignals.com/login
   - Enter credentials
   - Click "Sign In"
   - Verify redirect to dashboard
   - Check localStorage for tokens

3. **Protected Route:**
   - Navigate to /analysis
   - Verify page loads (not redirected to login)
   - Check network tab for API calls with Authorization header

4. **Logout:**
   - Click "Sign Out" in navigation
   - Verify redirect to login page
   - Try accessing /analysis (should redirect to login)

### OAuth Flow Test

1. **Google Sign-In:**
   - Click "Sign in with Google" on login page
   - Complete Google OAuth flow
   - Verify redirect to dashboard
   - Check Account model created in database

2. **GitHub Sign-In:**
   - Click "Sign in with GitHub" on login page
   - Complete GitHub OAuth flow
   - Verify redirect to dashboard
   - Check Account model created in database

### Database Verification

```bash
# Connect to production database
psql $DATABASE_URL

# Check users table
SELECT id, email, "fullName", "createdAt" FROM users LIMIT 5;

# Check accounts table (OAuth links)
SELECT "userId", provider, "providerAccountId" FROM accounts;

# Check audit logs
SELECT "userId", action, details, "timestamp" FROM "auditLogs" ORDER BY "timestamp" DESC LIMIT 10;
```

### Security Verification

1. **Check HTTPS:**
   - All URLs should use https://
   - Browser shows padlock icon
   - No mixed content warnings

2. **Check Cookies:**
   - Open DevTools → Application → Cookies
   - Refresh token should have:
     - httpOnly: ✓
     - secure: ✓
     - sameSite: Strict

3. **Check CORS:**
   ```bash
   curl -X POST https://api.klyrsignals.com/api/v1/auth/login \
     -H "Origin: https://evil.com" \
     -H "Content-Type: application/json" \
     -d '{"email":"test@test.com","password":"test"}'
   # Should NOT include Access-Control-Allow-Origin: https://evil.com
   ```

4. **Check Rate Limiting:**
   ```bash
   # Make 15 rapid login attempts
   for i in {1..15}; do
     curl -X POST https://api.klyrsignals.com/api/v1/auth/login \
       -H "Content-Type: application/json" \
       -d '{"email":"test@test.com","password":"wrong"}'
   done
   # Should return 429 Too Many Requests after 10 attempts
   ```

---

## Monitoring Setup

### Logging

**Backend Logging:**
```python
# backend/app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log authentication events
logger.info(f"User {user_id} logged in successfully")
logger.warning(f"Failed login attempt for {email}")
```

**Frontend Logging:**
- Use Sentry for error tracking
- Log authentication errors
- Log API failures

### Error Tracking

**Sentry Setup:**

1. **Create Sentry Project:**
   - Go to sentry.io
   - New Project → Python (backend) + JavaScript (frontend)

2. **Backend Integration:**
   ```bash
   pip install sentry-sdk[fastapi]
   ```
   
   ```python
   # backend/app/main.py
   import sentry_sdk
   from sentry_sdk.integrations.fastapi import FastApiIntegration
   
   sentry_sdk.init(
       dsn=os.getenv("SENTRY_DSN"),
       integrations=[FastApiIntegration()],
       traces_sample_rate=1.0,
   )
   ```

3. **Frontend Integration:**
   ```bash
   npm install @sentry/react @sentry/tracing
   ```
   
   ```typescript
   // frontend/app/layout.tsx
   import * as Sentry from "@sentry/react";
   
   Sentry.init({
     dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
     tracesSampleRate: 1.0,
   });
   ```

### Uptime Monitoring

**UptimeRobot Setup:**

1. **Create Account:**
   - Go to uptimerobot.com
   - Free tier: 50 monitors, 5-minute checks

2. **Add Monitors:**
   - Frontend: `https://klyrsignals.com`
   - Backend: `https://api.klyrsignals.com/api/health`
   - Frequency: Every 5 minutes
   - Alert contacts: Email, SMS

3. **Configure Alerts:**
   - Email alerts for downtime
   - SMS alerts for critical services
   - Slack webhook (optional)

---

## Backup Strategy

### Database Backups

**Railway Automatic Backups:**
- Daily backups automatically enabled
- Retention: 7 days (free tier)
- Restore via Railway dashboard

**Manual Backup:**
```bash
# Export database
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql

# Import backup
psql $DATABASE_URL < backup-20260301.sql
```

### Code Backups

**Git Strategy:**
- All code in GitHub repository
- Tag releases: `git tag v1.6.0 && git push origin v1.6.0`
- Protected main branch (require PR review)

### Environment Variable Backups

**Secure Storage:**
- Use 1Password or LastPass for team sharing
- Never commit .env files to git
- Document required variables in README (without values)

---

## Rollback Plan

### If Deployment Fails

1. **Identify Issue:**
   - Check Railway/Vercel deployment logs
   - Check Sentry for errors
   - Check database connection

2. **Rollback Frontend:**
   ```bash
   # Vercel: Revert to previous deployment
   # Dashboard → Deployments → Click previous → Promote to Production
   ```

3. **Rollback Backend:**
   ```bash
   # Railway: Revert environment variables or redeploy previous commit
   git revert HEAD
   git push origin main
   ```

4. **Database Rollback:**
   ```bash
   # Restore from backup
   psql $DATABASE_URL < backup-previous.sql
   ```

### Rollback Triggers

- Critical authentication bugs
- Database migration failures
- OAuth flow broken
- Security vulnerabilities
- >5 minute downtime

---

## Go/No-Go Decision

### Go Criteria (ALL Required)

- [ ] All tests passing (frontend + backend)
- [ ] OAuth credentials configured and tested
- [ ] PostgreSQL database deployed and migrated
- [ ] HTTPS enabled on all endpoints
- [ ] Environment variables set in production
- [ ] Health checks passing
- [ ] Authentication flow tested end-to-end
- [ ] OAuth sign-in tested (Google + GitHub)
- [ ] Monitoring configured (Sentry, UptimeRobot)
- [ ] Backup strategy in place
- [ ] Rollback plan documented

### No-Go Triggers (ANY)

- ❌ OAuth not configured
- ❌ Database connection failing
- ❌ Authentication broken
- ❌ Security vulnerabilities found
- ❌ Critical bugs in QA
- ❌ Missing environment variables
- ❌ HTTPS not enabled

---

## Deployment Timeline

**Estimated Duration:** 2-3 hours

| Task | Duration | Owner |
|------|----------|-------|
| Environment setup | 30 min | DevOps |
| OAuth configuration | 30 min | DevOps |
| Database setup | 20 min | DevOps |
| Frontend deployment | 15 min | DevOps |
| Backend deployment | 15 min | DevOps |
| Testing & verification | 45 min | QA |
| Monitoring setup | 15 min | DevOps |
| **Total** | **2h 50m** | |

---

## Post-Deployment Tasks

### Week 1

- [ ] Monitor error rates (Sentry)
- [ ] Monitor uptime (UptimeRobot)
- [ ] Check database performance
- [ ] Review user feedback
- [ ] Address any critical bugs

### Week 2

- [ ] Analyze user adoption metrics
- [ ] Review authentication success rates
- [ ] Check OAuth usage (Google vs GitHub)
- [ ] Plan v1.7 features (password reset, email verification)

### Month 1

- [ ] Security audit review
- [ ] Performance optimization
- [ ] User retention analysis
- [ ] v1.7 planning and prioritization

---

## Contacts & Support

### Team

- **Project Lead:** Jarvis (Coordinator)
- **Architect:** Tony (Lead Designer)
- **Developer:** Peter (Technical Execution)
- **QA:** Heimdall (Security & Testing)
- **Analyst:** Pepper (Documentation)

### Emergency Contacts

- **Production Issues:** Check Sentry dashboard first
- **Database Issues:** Railway dashboard → Support
- **OAuth Issues:** Google/GitHub developer consoles
- **Deployment Issues:** Vercel/Railway support

### Documentation Links

- README: https://github.com/humac/klyrsignals/blob/main/README.md
- API Docs: https://api.klyrsignals.com/docs
- Architecture: https://github.com/humac/klyrsignals/blob/main/docs/DECISIONS.md
- Issues: https://github.com/humac/klyrsignals/blob/main/docs/ISSUES.md

---

**Deployment Checklist Version:** 1.0  
**Last Updated:** 2026-03-01  
**Next Review:** After v1.7 deployment
