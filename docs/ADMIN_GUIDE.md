# KlyrSignals Admin Guide

## Architecture Overview

### System Diagram

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend API    │────▶│  Market Data    │
│   Next.js 15    │     │   FastAPI        │     │  yfinance       │
│   React 19      │◀────│   Python 3.12    │◀────│  Alpha Vantage  │
│   Vercel        │     │   Railway        │     │  CoinGecko      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌──────────────────┐
│  Browser        │     │  Analysis Engine │
│  localStorage   │     │  Risk Scoring    │
│  (v1.0)         │     │  Blind Spots     │
└─────────────────┘     └──────────────────┘
```

### Components

**Frontend (Next.js on Vercel)**
- Framework: Next.js 15 with App Router
- UI Library: React 19 with Tailwind CSS
- State Management: React Context API
- Storage: Browser localStorage (client-side only)
- Deployment: Vercel (serverless, global CDN)

**Backend (FastAPI on Railway)**
- Framework: FastAPI (Python 3.12)
- API Style: RESTful with OpenAPI docs
- Analysis: NumPy, Pandas for portfolio math
- Deployment: Railway (auto-scaling, managed)
- Health Checks: `/api/health`, `/api/market/status`

**Data Flow**
1. User imports portfolio via frontend
2. Data stored in browser localStorage
3. Frontend sends holdings to backend for analysis
4. Backend fetches market data from providers
5. Analysis results returned to frontend
6. Charts and insights rendered client-side

---

## Deployment

### Prerequisites

**Required:**
- Node.js 18+ (frontend)
- Python 3.12+ (backend)
- Git (version control)
- GitHub account (code hosting)

**Deployment Platforms:**
- Vercel account (frontend hosting)
- Railway account (backend hosting)

**Optional (for enhanced features):**
- Alpha Vantage API key (faster market data)
- Custom domain (professional branding)
- Sentry account (error tracking)

### Frontend Deployment (Vercel)

#### Step 1: Prepare the Project

```bash
cd /home/openclaw/.openclaw/workspace/jarvis/projects/klyrsignals/frontend
npm install
```

#### Step 2: Configure Environment Variables

Create `.env.local`:

```bash
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=https://klyrsignals-backend.railway.app
NEXT_PUBLIC_APP_NAME=KlyrSignals
NEXT_PUBLIC_VERSION=1.0.0
```

**Important:** All `NEXT_PUBLIC_` variables are exposed to the browser. Never store secrets here.

#### Step 3: Deploy to Vercel

**Option A: Vercel CLI**

```bash
npm install -g vercel
vercel login
vercel deploy
```

**Option B: Vercel Dashboard**

1. Go to https://vercel.com/new
2. Import GitHub repository
3. Select `frontend` as root directory
4. Add environment variables
5. Click "Deploy"

#### Step 4: Build Settings

Vercel auto-detects Next.js. Verify in dashboard:

- **Build Command**: `npm run build`
- **Output Directory**: `.next` (auto-detected)
- **Install Command**: `npm install`
- **Node Version**: 18.x or higher

#### Step 5: Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your domain (e.g., `klyrsignals.com`)
3. Update DNS records as instructed
4. Wait for SSL certificate (automatic)

### Backend Deployment (Railway)

#### Step 1: Prepare the Project

```bash
cd /home/openclaw/.openclaw/workspace/jarvis/projects/klyrsignals/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Step 2: Configure Environment Variables

Create `.env`:

```bash
# Backend Environment Variables
ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Market Data APIs (optional)
ALPHA_VANTAGE_API_KEY=your_key_here
YFINANCE_ENABLED=true

# CORS Configuration
ALLOWED_ORIGINS=https://klyrsignals.com,https://www.klyrsignals.com
```

#### Step 3: Deploy to Railway

**Option A: Railway CLI**

```bash
npm install -g @railway/cli
railway login
railway init  # Create new project
railway up     # Deploy
```

**Option B: Railway Dashboard**

1. Go to https://railway.app/new
2. Select "Deploy from GitHub repo"
3. Choose repository and `backend` directory
4. Add environment variables
5. Deploy

#### Step 4: Configure Build & Start

In Railway dashboard:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Python Version**: 3.12

#### Step 5: Health Check Endpoint

Railway automatically checks `/api/health`. Verify it returns:

```json
{
  "status": "healthy",
  "timestamp": "2026-02-28T20:00:00Z",
  "version": "1.0.0"
}
```

### Environment Variables Reference

#### Frontend (.env.local)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API base URL |
| `NEXT_PUBLIC_APP_NAME` | No | App name (default: "KlyrSignals") |
| `NEXT_PUBLIC_VERSION` | No | Version string for display |

#### Backend (.env)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENV` | No | `development` | Environment (development/production) |
| `DEBUG` | No | `True` | Enable debug logging |
| `HOST` | No | `0.0.0.0` | Server bind address |
| `PORT` | No | `8000` | Server port |
| `ALPHA_VANTAGE_API_KEY` | No | None | Premium market data API key |
| `YFINANCE_ENABLED` | No | `true` | Enable Yahoo Finance data |
| `ALLOWED_ORIGINS` | No | `*` | CORS allowed origins (comma-separated) |

---

## Configuration

### Market Data Providers

#### yfinance (Default, Free)

**Pros:**
- Free, no API key required
- Covers US stocks, ETFs, mutual funds
- Reasonable rate limits for personal use

**Cons:**
- 15-minute delay on quotes
- Limited international coverage
- No official support (unofficial library)

**Configuration:**
```bash
YFINANCE_ENABLED=true
```

#### Alpha Vantage (Paid Upgrade)

**Pros:**
- Real-time data available
- Global market coverage
- Official API with SLA

**Cons:**
- Free tier: 5 requests/minute, 500/day
- Paid plans start at $49/month

**Configuration:**
```bash
ALPHA_VANTAGE_API_KEY=your_api_key
```

Get API key: https://www.alphavantage.co/support/#api-key

#### Polygon.io (Premium)

**Pros:**
- Professional-grade data
- Real-time WebSocket feeds
- Comprehensive historical data

**Cons:**
- Expensive ($29/month minimum)
- Overkill for v1.0

**Future Integration:** Planned for v1.5+

### Risk Scoring Configuration

Adjust risk calculation parameters in backend:

**File:** `backend/app/services/risk_calculator.py`

```python
# Default thresholds
SECTOR_CONCENTRATION_THRESHOLD = 0.25  # 25% max in one sector
GEOGRAPHIC_CONCENTRATION_THRESHOLD = 0.40  # 40% max in one region
SINGLE_STOCK_THRESHOLD = 0.10  # 10% max in single stock
ASSET_CLASS_THRESHOLD = 0.50  # 50% max in one asset class

# Risk score weights
CONCENTRATION_WEIGHT = 0.40
VOLATILITY_WEIGHT = 0.30
CORRELATION_WEIGHT = 0.30
```

**To Customize:**
1. Fork repository
2. Modify thresholds
3. Redeploy backend
4. Test with sample portfolio

### Alert Sensitivity

Configure warning thresholds:

**File:** `backend/app/services/alert_service.py`

```python
WARNING_THRESHOLDS = {
    'critical': 0.90,  # 90% of threshold = critical
    'high': 0.75,      # 75% of threshold = high
    'medium': 0.60,    # 60% of threshold = medium
    'low': 0.50,       # 50% of threshold = low
}
```

---

## Monitoring

### Health Checks

**Backend Endpoints:**

```bash
# Basic health check
curl https://your-backend.railway.app/api/health

# Market data status
curl https://your-backend.railway.app/api/market/status

# Detailed system info
curl https://your-backend.railway.app/api/system/info
```

**Expected Responses:**

```json
// /api/health
{
  "status": "healthy",
  "timestamp": "2026-02-28T20:00:00Z",
  "version": "1.0.0"
}

// /api/market/status
{
  "market_open": true,
  "next_close": "2026-02-28T21:00:00Z",
  "data_provider": "yfinance",
  "last_update": "2026-02-28T20:00:00Z"
}
```

**Monitoring Setup:**

Use UptimeRobot or Pingdom to check `/api/health` every 5 minutes.

### Logging

#### Frontend Logs (Vercel)

Access via Vercel Dashboard:
1. Go to Project → Logs
2. Filter by environment (Production/Preview)
3. Search by request ID or error message

**Enable Debug Logging:**
```bash
NEXT_PUBLIC_DEBUG=true
```

#### Backend Logs (Railway)

Access via Railway Dashboard:
1. Go to Project → Deployments
2. Click on active deployment
3. View "Logs" tab

**Enable Debug Logging:**
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

#### Error Tracking

**Sentry Integration (Recommended):**

1. Create account at https://sentry.io
2. Install SDK:
   ```bash
   # Frontend
   npm install @sentry/nextjs
   
   # Backend
   pip install sentry-sdk
   ```

3. Configure DSN in environment variables
4. Errors automatically reported with stack traces

### Performance Metrics

Track these KPIs:

**API Response Times:**
- Target: <200ms for analysis endpoints
- Monitor: `/api/analysis/portfolio`
- Alert if: >500ms average over 5 minutes

**Page Load Times:**
- Target: <2s for initial load
- Monitor: Vercel Analytics
- Alert if: >3s average

**Concurrent Users:**
- v1.0 Capacity: ~100 concurrent users (Railway basic plan)
- Monitor: Railway dashboard
- Scale up if: Consistently >80% capacity

**Error Rates:**
- Target: <1% of requests
- Monitor: Sentry or Railway logs
- Alert if: >5% error rate

---

## Security

### Data Protection

#### Encryption in Transit

- All API calls use HTTPS/TLS 1.3
- Vercel and Railway provide automatic SSL
- HSTS headers enabled by default

#### Data Storage (v1.0)

**Client-Side Only:**
- Portfolio data stored in browser localStorage
- No server-side database (v1.0)
- Data never leaves user's device (except for analysis API calls)

**Security Implications:**
- ✅ No server breach risk (no data to steal)
- ✅ GDPR compliant (no PII stored)
- ⚠️ User must backup their own data
- ⚠️ Clear cache on shared computers

**Future Versions (v1.5+):**
- Encrypted database (PostgreSQL with pgcrypto)
- User authentication (OAuth 2.0)
- End-to-end encryption option

### API Security

#### Rate Limiting

**Default Limits:**
- 100 requests/minute per IP
- 1000 requests/hour per IP
- 10,000 requests/day per IP

**Configuration:**
```python
# backend/app/main.py
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=100,
    requests_per_hour=1000,
)
```

#### CORS Configuration

**Production Settings:**
```bash
ALLOWED_ORIGINS=https://klyrsignals.com,https://www.klyrsignals.com
```

**Development Settings:**
```bash
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

**Never use `*` in production.**

#### Input Validation

All API endpoints validate inputs:

```python
# Example: Portfolio analysis request
class PortfolioRequest(BaseModel):
    holdings: List[Holding]
    
    @validator('holdings')
    def validate_holdings(cls, v):
        if len(v) == 0:
            raise ValueError("At least one holding required")
        if len(v) > 1000:
            raise ValueError("Maximum 1000 holdings")
        return v
```

### Authentication (Future)

**Planned for v1.5:**
- OAuth 2.0 (Google, GitHub)
- JWT tokens with refresh rotation
- Session management
- API keys for programmatic access

---

## Backup & Recovery

### Portfolio Data Export

**User-Initiated Export:**
1. Navigate to Settings page
2. Click "Export Portfolio"
3. Download CSV or JSON file
4. Store securely (encrypted drive, cloud storage)

**Automated Backups (Future):**
- Daily email with portfolio snapshot
- Google Drive integration
- GitHub Gist sync

### Configuration Backup

**Backup These Files:**
```bash
# Frontend
frontend/.env.local
frontend/next.config.ts
frontend/package.json

# Backend
backend/.env
backend/requirements.txt
backend/app/config.py
```

**Store in:**
- Encrypted password manager (1Password, Bitwarden)
- Private GitHub repository
- Secure cloud storage (encrypted)

### Disaster Recovery Steps

**If Frontend Goes Down:**
1. Check Vercel dashboard for errors
2. Review deployment logs
3. Rollback to previous version if needed
4. Redeploy with fixes

**If Backend Goes Down:**
1. Check Railway dashboard for errors
2. Review application logs
3. Restart deployment (Railway auto-restarts)
4. Scale up resources if overloaded

**If Data Lost:**
1. User re-imports from backup CSV
2. Future: Restore from database backup
3. Document incident for post-mortem

---

## Troubleshooting

### Common Issues

#### Backend Not Starting

**Symptoms:** Railway shows "Crashed" or "Failed to start"

**Diagnosis:**
```bash
# Check logs
railway logs

# Test locally
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Common Causes:**
- Missing dependencies: `pip install -r requirements.txt`
- Port conflict: Ensure PORT env var is set
- Python version mismatch: Verify Python 3.12+
- Environment variable missing: Check .env file

**Fix:**
```bash
# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Verify Python version
python --version  # Should be 3.12+

# Check environment
echo $PORT
echo $ENV
```

#### Frontend Build Failures

**Symptoms:** Vercel shows "Build Failed"

**Diagnosis:**
```bash
# Test build locally
cd frontend
npm install
npm run build
```

**Common Causes:**
- TypeScript errors: `npm run build` shows details
- Missing dependencies: Check package.json
- Node version mismatch: Verify Node 18+
- Environment variable missing: Check .env.local

**Fix:**
```bash
# Clear cache and rebuild
rm -rf node_modules .next
npm install
npm run build

# Check Node version
node --version  # Should be 18+
```

#### API Connection Errors

**Symptoms:** Frontend shows "Failed to fetch" or network errors

**Diagnosis:**
```bash
# Test backend health
curl https://your-backend.railway.app/api/health

# Check CORS
curl -H "Origin: https://your-frontend.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://your-backend.railway.app/api/health
```

**Common Causes:**
- Backend down: Check Railway dashboard
- CORS misconfiguration: Verify ALLOWED_ORIGINS
- Wrong API URL: Check NEXT_PUBLIC_API_URL
- Network firewall: Whitelist Railway IPs

**Fix:**
```bash
# Update frontend .env.local
NEXT_PUBLIC_API_URL=https://correct-backend-url.railway.app

# Update backend .env
ALLOWED_ORIGINS=https://correct-frontend.vercel.app
```

#### Market Data Failures

**Symptoms:** Analysis shows "N/A" or stale data

**Diagnosis:**
```bash
# Test market data endpoint
curl https://your-backend.railway.app/api/market/status

# Check backend logs for yfinance errors
railway logs | grep yfinance
```

**Common Causes:**
- yfinance rate limited: Wait 1 minute, retry
- Invalid symbols: Verify ticker symbols
- API key expired: Check Alpha Vantage key
- Market closed: Some data unavailable after hours

**Fix:**
```bash
# Enable debug logging
DEBUG=True

# Check yfinance version
pip show yfinance  # Should be 0.2.0+

# Test symbol manually
python -c "import yfinance as yf; print(yf.Ticker('AAPL').info)"
```

### Debug Mode

#### Enable Debug Logging

**Frontend:**
```bash
NEXT_PUBLIC_DEBUG=true
NEXT_PUBLIC_LOG_LEVEL=debug
```

**Backend:**
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

#### Browser Dev Tools

1. Open browser (Chrome/Firefox)
2. Press F12 to open Dev Tools
3. Go to Console tab
4. Look for errors/warnings
5. Use Network tab to inspect API calls

#### Network Inspection

**Check These:**
- API request URLs (should match NEXT_PUBLIC_API_URL)
- Response status codes (200 = OK, 500 = server error)
- Response bodies (JSON with data or error messages)
- Request timing (slow = backend issue)

---

## Updates & Maintenance

### Updating Frontend

```bash
cd frontend
git pull origin main
npm install  # Install new dependencies
npm run build  # Verify build
vercel deploy --prod  # Deploy to production
```

**Post-Deploy:**
- Verify site loads correctly
- Test critical user flows (import, analysis)
- Check Vercel analytics for errors

### Updating Backend

```bash
cd backend
git pull origin main
source venv/bin/activate
pip install -r requirements.txt  # Install new dependencies
railway up  # Deploy to production
```

**Post-Deploy:**
- Check health endpoint
- Test analysis API
- Monitor logs for errors

### Database Migrations (v1.5+)

When database is introduced:

```bash
cd backend
alembic upgrade head  # Run migrations
```

**Always:**
- Backup database before migrations
- Test migrations on staging first
- Have rollback plan ready

### Changelog

**v1.0.0 (2026-02-28)**
- Initial release
- Portfolio import (CSV + manual)
- Risk scoring and analysis
- Blind spot detection
- Over-exposure alerts
- Client-side storage only

**Planned:**
- v1.1: Performance tracking
- v1.5: User authentication + database
- v2.0: Mobile app (React Native)

---

## Support

### GitHub Issues

Report bugs and feature requests:
https://github.com/humac/klyrsignals/issues

**Include:**
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Browser/OS version
- Console errors (if frontend)
- Backend logs (if API issue)

### Email Support (Future)

- General inquiries: support@klyrsignals.com
- Technical issues: tech@klyrsignals.com
- Business: business@klyrsignals.com

### Status Page (Future)

Monitor service status:
https://status.klyrsignals.com

**Shows:**
- API uptime
- Frontend availability
- Market data provider status
- Incident history

---

## Appendix

### API Reference

**Base URL:** `https://your-backend.railway.app/api`

#### Health Check
```
GET /api/health
Response: {"status": "healthy", "timestamp": "...", "version": "1.0.0"}
```

#### Portfolio Analysis
```
POST /api/analysis/portfolio
Body: {"holdings": [{"symbol": "AAPL", "quantity": 50, ...}]}
Response: {"risk_score": 45, "warnings": [...], "allocation": {...}}
```

#### Market Status
```
GET /api/market/status
Response: {"market_open": true, "next_close": "...", "data_provider": "yfinance"}
```

### File Structure

```
klyrsignals/
├── frontend/
│   ├── app/
│   │   ├── page.tsx          # Dashboard
│   │   ├── import/
│   │   ├── holdings/
│   │   ├── analysis/
│   │   └── settings/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   ├── types/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   └── utils/
│   ├── requirements.txt
│   └── .env
└── docs/
    ├── USER_GUIDE.md
    ├── ADMIN_GUIDE.md
    └── screenshots/
```

### Useful Commands

```bash
# Frontend development
cd frontend
npm run dev          # Start dev server
npm run build        # Production build
npm run lint         # ESLint check
npm test             # Run tests

# Backend development
cd backend
source venv/bin/activate
uvicorn app.main:app --reload  # Start dev server
pytest               # Run tests

# Deployment
vercel deploy --prod   # Frontend to production
railway up             # Backend to production

# Monitoring
railway logs           # View backend logs
vercel logs            # View frontend logs
```

---

## v1.5 Deployment Notes

### Dark Mode
- **No backend changes required** - Pure frontend feature
- **No environment variables** - Theme stored in browser localStorage
- **No database migrations** - Client-side only
- **CDN caching** - Theme toggle JS is part of main bundle

### WealthSimple Import
- **No backend changes required** - Client-side CSV parsing
- **No API endpoints** - All parsing happens in browser
- **No rate limits** - No external API calls for import
- **File uploads** - Client-side only (no server storage)

### Version Update
Update version in:
- `frontend/package.json`: `"version": "1.5.0"`
- `README.md`: Version badge to `1.5.0`
- `docs/ADMIN_GUIDE.md`: This section

### Rollback Plan
If issues found:
1. Revert to previous Vercel deployment
2. Clear browser cache if theme issues
3. localStorage can be cleared: `localStorage.clear()`

---

**Version:** 1.5.0  
**Last Updated:** 2026-03-01  
**Maintained By:** KlyrSignals Team
