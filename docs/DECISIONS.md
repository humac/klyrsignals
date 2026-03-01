# DECISIONS.md - KlyrSignals

**Project:** KlyrSignals v1.6.0  
**Created:** 2026-02-28  
**Last Updated:** 2026-03-01  
**Status:** ✅ v1.5 Complete | 🔄 v1.6 Architecture Complete

---

## [DEC-001] Hybrid Architecture (Next.js + FastAPI)

**Date:** 2026-02-28  
**Decided By:** User + Jarvis (Agent Team)  
**Status:** ✅ Implemented

### Context
KlyrSignals requires both sophisticated financial analysis (Python's strength) and an interactive, modern user interface (JavaScript/React's strength). Initial bootstrap was Python-only, but requirements demanded better UX.

### Decision
**Implement hybrid architecture:**
- **Frontend:** Next.js 16 + TypeScript + Tailwind CSS + Recharts
- **Backend:** Python 3.12 + FastAPI + pandas + numpy + yfinance
- **Communication:** REST API (JSON) with CORS
- **Deployment:** Vercel (frontend) + Railway (backend)

### Rationale
1. **Python Backend Strengths:**
   - Rich financial ecosystem (pandas, numpy, yfinance, scikit-learn)
   - Excellent for data processing and numerical calculations
   - FastAPI provides automatic API documentation and type validation
   - Async support for I/O operations

2. **Next.js Frontend Strengths:**
   - Modern React with App Router and server-side rendering
   - Excellent developer experience with TypeScript
   - Built-in optimizations (image, font, script)
   - Seamless deployment to Vercel with CDN
   - Rich charting ecosystem (Recharts, Chart.js)

3. **Separation of Concerns:**
   - Backend focuses on analysis, data processing, and business logic
   - Frontend focuses on user experience, visualization, and interactivity
   - Independent scaling and deployment

### Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| **Python-only (Streamlit)** | Faster MVP, single codebase | Limited UI customization, poor UX, not production-ready | Doesn't meet UX requirements |
| **Next.js-only** | Single deployment, unified stack | Limited financial libraries in JS, would need to reinvent wheel | Loses Python's financial ecosystem |
| **Django + Templates** | Full-featured Python framework | Heavier, less modern UX, monolithic | Overkill for MVP, worse DX |
| **Flask + React** | Lightweight, flexible | More manual configuration, less opinionated | FastAPI provides better DX with auto-docs |

### Consequences

**Positive:**
- Access to full Python financial ecosystem for analysis
- Modern, responsive UI with excellent user experience
- Independent scaling of frontend and backend
- Industry-standard tools for both domains
- Clear separation of concerns

**Negative:**
- Two codebases to maintain
- Two services to deploy and monitor
- CORS configuration required
- Slightly longer development time
- Need to manage API contracts between frontend/backend

### Implementation Details

**Frontend Structure:**
```
frontend/
├── app/              # Next.js App Router pages
├── components/       # React components
├── context/          # PortfolioContext (state management)
├── hooks/            # Custom hooks
├── lib/              # API client, utilities
└── types/            # TypeScript types
```

**Backend Structure:**
```
backend/
├── app/
│   ├── api/v1/       # API routes
│   ├── models/       # Pydantic models
│   ├── services/     # Business logic
│   └── core/         # Core algorithms
└── requirements.txt
```

**API Contract:**
- RESTful design with JSON responses
- Pydantic models for request/response validation
- Swagger UI auto-generated at `/docs`
- CORS configured for Vercel domain

---

## [DEC-002] Market Data Provider (yfinance)

**Date:** 2026-02-28  
**Decided By:** Pepper + Tony (Agent Team)  
**Status:** ✅ Implemented

### Context
Need reliable market data source for portfolio valuation and analysis. Must balance cost, reliability, and data quality for MVP.

### Decision
**Use Yahoo Finance via yfinance library for MVP:**
- Free, no API key required
- Sufficient for MVP validation
- Easy to swap provider later via abstraction layer

### Rationale
1. **Cost:** Free (critical for MVP validation)
2. **Simplicity:** No API key management, no rate limit tracking for MVP
3. **Data Quality:** Sufficient accuracy for portfolio analysis
4. **Upgrade Path:** Abstract data provider interface allows easy swap to Polygon.io ($29/mo) or Alpha Vantage ($50/mo) when needed

### Alternatives Considered

| Provider | Cost | Rate Limit | Reliability | Decision |
|----------|------|------------|-------------|----------|
| **yfinance** | Free | ~2000/day | Good | ✅ Selected for MVP |
| **Polygon.io** | $29/mo | 5 req/sec | Excellent | Upgrade path |
| **Alpha Vantage** | $50/mo | 5 req/min | Excellent | Too expensive for MVP |
| **Finnhub** | $60/mo | 60 req/min | Excellent | Too expensive for MVP |

### Tradeoffs
- **Pros:** Free, easy to use, no API key management
- **Cons:** Rate-limited (~2000 requests/day), occasional reliability issues, unofficial API
- **Mitigation:** Implement caching (15-minute TTL), abstract provider interface for easy swap

### Implementation
```python
# backend/app/services/market_data_service.py
class MarketDataService:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 900  # 15 minutes
    
    async def get_prices(self, symbols: list[str]) -> dict[str, float]:
        # Check cache first
        # Fetch from yfinance if expired
        # Update cache
        # Return prices
        pass
```

### Upgrade Criteria
Switch to paid provider when:
- Hitting yfinance rate limits consistently
- Need real-time data (yfinance has 15-min delay)
- Require higher reliability for production
- Budget allows ($29-60/mo)

---

## [DEC-003] No Authentication in v1.0

**Date:** 2026-02-28  
**Decided By:** Pepper + Tony (Agent Team)  
**Status:** ✅ Implemented

### Context
User authentication adds significant complexity (JWT, sessions, password management, database). Need to decide if it's necessary for MVP.

### Decision
**Defer authentication to v1.5 (post-MVP):**
- v1.0: Portfolios stored in browser localStorage (client-side only)
- v1.5: Add JWT authentication with PostgreSQL for user accounts

### Rationale
1. **MVP Focus:** Validate core value proposition (portfolio analysis) before adding auth complexity
2. **Single-User Testing:** MVP is for individual testing/validation, not multi-user production
3. **Reduced Complexity:** No database, no sessions, no password management in v1.0
4. **GDPR Compliance:** No personal data stored = simpler compliance
5. **Fast Iteration:** Can iterate on core features without auth bottlenecks

### Alternatives Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **v1.0 Auth** | Multi-user from start, production-ready | Adds 2-3 weeks complexity, distracts from core features | ❌ Rejected |
| **v1.5 Auth** | Focus on core features, validate first | Users can't sync across devices in v1.0 | ✅ Selected |
| **OAuth Only** | No password management | Still requires database, sessions | ❌ Overkill for MVP |

### Tradeoffs
- **Pros:** Faster MVP development, simpler architecture, validates demand before infra investment
- **Cons:** Users can't access portfolios across devices, no persistence if browser data cleared
- **Mitigation:** Clear messaging that data is stored locally, export functionality for backup

### Implementation
```typescript
// frontend/context/PortfolioContext.tsx
const STORAGE_KEY = 'klyrsignals_portfolio';

// Load from localStorage on init
const loadFromStorage = () => {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored ? JSON.parse(stored) : [];
};

// Save to localStorage on every mutation
const saveToStorage = (holdings: Holding[]) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(holdings));
};
```

### v1.5 Requirements
When adding auth:
- JWT tokens with refresh rotation
- PostgreSQL for user accounts and portfolio persistence
- Password hashing (bcrypt)
- Session management
- Cross-device sync
- Opt-in migration path for v1.0 localStorage users

---

## [DEC-004] Rules-Based ML for v1.0

**Date:** 2026-02-28  
**Decided By:** Tony + Peter (Agent Team)  
**Status:** ✅ Implemented

### Context
Blind spot detection could use advanced ML (clustering, anomaly detection) or simple rules-based approach. Need to balance sophistication with MVP speed.

### Decision
**Use rules-based approach for v1.0, ML enhancement in v1.5:**
- v1.0: Simple concentration thresholds, correlation detection, style categorization
- v1.5: Add clustering, anomaly detection, factor analysis

### Rationale
1. **80/20 Rule:** Rules-based provides 80% of value with 20% of complexity
2. **Interpretability:** Rules are transparent and explainable to users
3. **Speed:** Can implement in days vs. weeks for ML models
4. **Validation:** Validate demand for blind spot detection before investing in ML
5. **Data Requirements:** ML needs historical data; v1.0 has no persistence

### Detection Rules (v1.0)

**Concentration Detection:**
- Sector >25% → Warning, >40% → Critical
- Single stock >10% → Warning, >20% → Critical
- Asset class >80% → Warning

**Style Detection:**
- Categorize holdings as large-cap growth, small-cap value, etc.
- Flag if >80% in single style category

**Correlation Detection:**
- Group holdings by sector
- Calculate pairwise correlation for holdings in same sector
- Flag if correlation >0.7 for 3+ holdings

### Alternatives Considered

| Approach | Complexity | Accuracy | Explainability | Decision |
|----------|------------|----------|----------------|----------|
| **Rules-Based** | Low | Good (80%) | High | ✅ Selected for v1.0 |
| **Clustering (K-Means)** | Medium | Better | Medium | v1.5 enhancement |
| **Anomaly Detection (Isolation Forest)** | High | Best | Low | v1.5 enhancement |
| **Neural Networks** | Very High | Best | Very Low | Overkill for MVP |

### Tradeoffs
- **Pros:** Fast implementation, transparent logic, no training data needed, easy to debug
- **Cons:** Less sophisticated, may miss subtle patterns, requires manual threshold tuning
- **Mitigation:** Design rules to be conservative (err on side of caution), add confidence scores

### Implementation
```python
# backend/app/services/blind_spot_service.py
def detect(self, holdings: list[Holding]) -> list[BlindSpot]:
    blind_spots = []
    
    # Rule 1: Sector concentration
    sector_holdings = self.group_by_sector(holdings)
    for sector, holdings_list in sector_holdings.items():
        if len(holdings_list) >= 3:
            corr = self.calculate_correlation(holdings_list)
            if corr > 0.7:
                blind_spots.append(BlindSpot(
                    type="hidden_correlation",
                    confidence=85,
                    message=f"High correlation in {sector} sector",
                    affected_symbols=[h.symbol for h in holdings_list]
                ))
    
    return blind_spots
```

### v1.5 ML Enhancements
- Clustering for hidden concentration patterns
- Anomaly detection for outlier positions
- Factor analysis (momentum, quality, volatility)
- Require historical data and user portfolio persistence

---

## [DEC-005] No Database in v1.0

**Date:** 2026-02-28  
**Decided By:** Pepper + Tony (Agent Team)  
**Status:** ✅ Implemented

### Context
Database adds infrastructure complexity (PostgreSQL setup, migrations, backups, scaling). Need to decide if necessary for MVP.

### Decision
**No database in v1.0 - use localStorage only:**
- v1.0: Stateless backend, client-side localStorage for portfolio persistence
- v1.5: Add PostgreSQL for user accounts and portfolio persistence

### Rationale
1. **Zero Infrastructure:** No database setup, maintenance, or cost
2. **Stateless Backend:** Simpler deployment, easier scaling
3. **GDPR Compliance:** No personal data stored on servers
4. **MVP Validation:** Validate demand before investing in database infrastructure
5. **Cost:** $0/month for v1.0 (Vercel free tier + Railway basic)

### Alternatives Considered

| Storage | Cost | Complexity | Persistence | Decision |
|---------|------|------------|-------------|----------|
| **localStorage** | $0 | None | Browser-only | ✅ Selected for v1.0 |
| **PostgreSQL** | $10-30/mo | High | Full | v1.5 requirement |
| **MongoDB** | $10-25/mo | Medium | Full | Overkill for v1.0 |
| **SQLite** | $0 | Low | File-based | Doesn't solve multi-user |

### Tradeoffs
- **Pros:** Zero infrastructure cost, no database maintenance, simpler deployment, GDPR-friendly
- **Cons:** No cross-device sync, data lost if browser cleared, no multi-user support
- **Mitigation:** Export to CSV functionality, clear user messaging about local storage

### Implementation
```typescript
// Frontend: localStorage persistence
const STORAGE_KEY = 'klyrsignals_portfolio';

// Load on app init
const holdings = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');

// Save on every mutation
localStorage.setItem(STORAGE_KEY, JSON.stringify(newHoldings));
```

```python
# Backend: Stateless API (no DB connections)
@app.post("/api/v1/analyze")
async def analyze_portfolio(request: PortfolioAnalysisRequest):
    # Process request, return response
    # No database operations
    return analysis_result
```

### v1.5 Database Requirements
When adding database:
- PostgreSQL for relational data (users, portfolios, holdings)
- SQLAlchemy or Prisma for ORM
- Database migrations (Alembic)
- Connection pooling
- Backup strategy
- User opt-in migration from localStorage

---

## [DEC-006] Risk Scoring Algorithm

**Date:** 2026-02-28  
**Decided By:** Tony + Peter (Agent Team)  
**Status:** ✅ Implemented

### Context
Need a simple, interpretable portfolio health score (0-100) that users can understand and act upon.

### Decision
**Composite risk score with weighted categories:**
- **Concentration Risk (50% weight):** Single stock, sector, asset class concentration
- **Volatility Risk (30% weight):** Portfolio beta, high-volatility holdings
- **Correlation Risk (20% weight):** Pairwise correlation between holdings

### Rationale
1. **Concentration is Primary Risk:** Most common portfolio mistake is over-concentration
2. **Weighted Approach:** Reflects relative importance of different risk types
3. **0-100 Scale:** Intuitive for users (like credit score)
4. **Breakdown Transparency:** Show users exactly what's driving their score

### Scoring Algorithm

**Concentration Risk (0-50 points):**
- Single stock >20%: +20 points
- Single stock >10%: +10 points
- Sector >40%: +20 points
- Sector >25%: +10 points
- Asset class >80%: +10 points

**Volatility Risk (0-30 points):**
- Portfolio beta >1.5: +15 points
- Portfolio beta >1.2: +8 points
- High-volatility holdings >50%: +15 points

**Correlation Risk (0-20 points):**
- Average pairwise correlation >0.8: +20 points
- Average pairwise correlation >0.6: +10 points

**Total Score:** `min(100, concentration + volatility + correlation)`

### Alternatives Considered

| Approach | Complexity | Interpretability | Accuracy | Decision |
|----------|------------|------------------|----------|----------|
| **Weighted Categories** | Low | High | Good | ✅ Selected |
| **VaR (Value at Risk)** | High | Low | Better | Too complex for MVP |
| **Sharpe Ratio** | Medium | Medium | Good | Requires historical data |
| **ML-Based Score** | Very High | Very Low | Best | Overkill, unexplainable |

### Tradeoffs
- **Pros:** Simple, transparent, actionable, no historical data required
- **Cons:** Doesn't capture all risk factors (liquidity, tail risk), thresholds are arbitrary
- **Mitigation:** Clear documentation of methodology, conservative thresholds

### Implementation
```python
# backend/app/core/scoring.py
def calculate_risk_score(holdings, prices, allocation):
    concentration_risk = measure_concentration(allocation)  # 0-50 points
    volatility_risk = measure_volatility(holdings, prices)  # 0-30 points
    correlation_risk = measure_correlation(holdings)        # 0-20 points
    
    total_risk = concentration_risk + volatility_risk + correlation_risk
    return min(100, int(total_risk))
```

### Future Enhancements (v1.5+)
- Add liquidity risk factor
- Incorporate tail risk metrics (CVaR)
- Use historical volatility instead of implied
- Benchmark-relative scoring (vs. S&P 500)

---

## Summary of Architectural Decisions

| Decision | Status | Impact |
|----------|--------|--------|
| Hybrid Architecture (Next.js + FastAPI) | ✅ Implemented | Enables best-in-class UX + financial analysis |
| Market Data: yfinance | ✅ Implemented | $0 cost for MVP, easy upgrade path |
| No Auth in v1.0 | ✅ Implemented (v1.5) | Faster MVP, simpler architecture |
| Rules-Based ML | ✅ Implemented | 80% value, 20% complexity |
| No Database in v1.0 | ✅ Implemented (v1.5) | Zero infra cost, stateless backend |
| Risk Scoring Algorithm | ✅ Implemented | Transparent, actionable risk metric |
| **PostgreSQL + Prisma for v1.6** | 🔄 Designed | Production-ready data persistence |
| **JWT Auth with OAuth for v1.6** | 🔄 Designed | Secure multi-user support |
| **bcrypt Password Hashing** | 🔄 Designed | Industry-standard security |
| **GDPR Compliance** | 🔄 Designed | Right to deletion, data export |

---

## [DEC-007] PostgreSQL Database for v1.6

**Date:** 2026-03-01  
**Decided By:** Tony (Lead Architect)  
**Status:** 🔄 Architecture Complete

### Context
v1.5 uses browser localStorage for all data storage, which means:
- No data persistence across devices
- No user accounts
- No multi-user support
- Data loss if browser cache cleared

v1.6 requires a production-ready database for user accounts, portfolios, and audit logging.

### Decision
**Use PostgreSQL with Prisma ORM:**
- **Database:** PostgreSQL 15 (managed: Railway or Supabase)
- **ORM:** Prisma ORM (type-safe, auto-generated client)
- **Hosting:** Managed service (Railway or Supabase)
- **Migrations:** Prisma Migrate

### Rationale
1. **PostgreSQL Strengths:**
   - Robust, production-ready RDBMS
   - Excellent JSON support (for metadata)
   - Strong consistency and ACID compliance
   - Managed services available (Railway, Supabase)
   - Free tier sufficient for MVP

2. **Prisma ORM Strengths:**
   - Type-safe database client (auto-generated from schema)
   - Excellent TypeScript/Python support
   - Built-in migration system
   - Great developer experience
   - Prevents SQL injection by design

3. **Managed Service Benefits:**
   - Automatic backups
   - High availability
   - No infrastructure management
   - Easy scaling

### Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| **MongoDB** | Flexible schema, JSON-native | Less type safety, overkill for structured data | PostgreSQL better fit for relational data |
| **SQLite** | Simple, file-based | No concurrent writes, not production-ready | Doesn't scale for multi-user |
| **Supabase (PostgreSQL)** | PostgreSQL + auth + realtime | Vendor lock-in, more complex | Railway simpler for MVP |
| **Firebase** | Real-time sync, auth included | NoSQL, vendor lock-in, expensive at scale | PostgreSQL more flexible |
| **Self-hosted PostgreSQL** | Full control | Infrastructure overhead | Managed service better for MVP |

### Consequences
- **Positive:**
  - Production-ready data persistence
  - Multi-user support
  - Data sync across devices
  - Audit logging capability
  - GDPR compliance (right to deletion)
- **Negative:**
  - Infrastructure cost (~$5-10/month for managed PostgreSQL)
  - Increased complexity (migrations, connection pooling)
  - Database management required

---

## [DEC-008] JWT-Based Authentication for v1.6

**Date:** 2026-03-01  
**Decided By:** Tony (Lead Architect)  
**Status:** 🔄 Architecture Complete

### Context
v1.5 has no authentication - all endpoints are public. v1.6 requires secure user authentication with support for:
- Email/password login
- OAuth login (Google, GitHub)
- Session management
- Token refresh

### Decision
**Use JWT (JSON Web Tokens) with dual-token system:**
- **Access Token:** JWT, 15-minute expiry, for API authentication
- **Refresh Token:** JWT + database, 7-day expiry, for obtaining new access tokens
- **Storage:** httpOnly cookies for refresh tokens, memory for access tokens
- **Algorithm:** HS256 (HMAC with SHA-256)
- **OAuth:** Authlib for Google and GitHub OAuth

### Rationale
1. **JWT Benefits:**
   - Stateless authentication (no session storage needed for access tokens)
   - Self-contained (contains user info)
   - Widely supported (libraries in all languages)
   - Standard format (RFC 7519)

2. **Dual-Token System:**
   - Short-lived access tokens reduce risk if compromised
   - Long-lived refresh tokens provide good UX (stay logged in)
   - Refresh tokens stored in database (revocable)

3. **httpOnly Cookies:**
   - Not accessible via JavaScript (XSS protection)
   - Automatically sent with requests
   - Can be marked secure (HTTPS only)
   - Can be marked sameSite (CSRF protection)

4. **HS256 Algorithm:**
   - Simpler than RS256 (single secret key)
   - Sufficient for MVP
   - Can upgrade to RS256 later if needed

### Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| **Session-based auth** | Simple, server-controlled | Requires session storage, less scalable | JWT better for distributed systems |
| **OAuth only** | No password management | Users without Google/GitHub accounts | Need email/password fallback |
| **RS256 (asymmetric)** | Better for microservices | More complex (key management) | HS256 sufficient for MVP |
| **NextAuth.js** | Built-in for Next.js | Less control, vendor lock-in | Custom implementation more flexible |

### Consequences
- **Positive:**
  - Secure authentication
  - Good UX (stay logged in for 7 days)
  - OAuth support (Google, GitHub)
  - Revocable sessions
  - XSS protection (httpOnly cookies)
- **Negative:**
  - Increased complexity (token management)
  - Token expiry handling required
  - OAuth app registration required

---

## [DEC-009] bcrypt Password Hashing

**Date:** 2026-03-01  
**Decided By:** Tony (Lead Architect)  
**Status:** 🔄 Architecture Complete

### Context
User passwords must be stored securely to protect against data breaches. Industry standard is to hash passwords with a slow, salted hash function.

### Decision
**Use bcrypt for password hashing:**
- **Algorithm:** bcrypt
- **Rounds:** 12 (minimum, can increase over time)
- **Library:** passlib[bcrypt] or bcrypt
- **Salt:** Automatically generated per password

### Rationale
1. **bcrypt Benefits:**
   - Adaptive (can increase rounds as hardware improves)
   - Salted (prevents rainbow table attacks)
   - Slow by design (prevents brute force)
   - Industry standard (widely audited)
   - Built-in salt storage

2. **12 Rounds:**
   - Good balance of security and performance
   - Takes ~200ms per hash (acceptable for login)
   - Can increase to 13-14 over time

### Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| **Argon2** | More secure, memory-hard | Less widely supported, newer | bcrypt more established |
| **scrypt** | Memory-hard, secure | Less widely supported | bcrypt sufficient for MVP |
| **PBKDF2** | Widely supported, NIST approved | Less resistant to GPU attacks | bcrypt better for password storage |
| **SHA-256** | Fast, widely supported | Too fast (vulnerable to brute force) | Not suitable for password hashing |

### Consequences
- **Positive:**
  - Industry-standard security
  - Resistant to brute force attacks
  - Resistant to rainbow table attacks
  - Future-proof (can increase rounds)
- **Negative:**
  - Slower than simple hashes (acceptable for login)
  - Password hashing adds ~200ms to registration/login

---

## [DEC-010] GDPR Compliance for v1.6

**Date:** 2026-03-01  
**Decided By:** Tony (Lead Architect)  
**Status:** 🔄 Architecture Complete

### Context
KlyrSignals will have EU users, so GDPR compliance is required. Key requirements include:
- Right to access (data export)
- Right to deletion (account deletion)
- Right to rectification (profile updates)
- Data minimization
- Consent management

### Decision
**Implement GDPR compliance features:**
- **Right to Deletion:** DELETE /users/me endpoint with cascade delete
- **Right to Access:** Export user data (JSON format)
- **Right to Rectification:** Profile update endpoints
- **Data Minimization:** Only collect necessary data (email, name, portfolio)
- **Consent:** Terms of service checkbox on registration
- **Privacy Policy:** Clear privacy policy page
- **Data Retention:** 90-day audit log retention, immediate deletion on request

### Rationale
1. **Legal Requirement:**
   - GDPR applies to any service with EU users
   - Fines up to 4% of global revenue or €20M
   - Compliance builds user trust

2. **Technical Implementation:**
   - Cascade delete ensures complete data removal
   - Audit logs track deletion for compliance
   - Data export in machine-readable format

### Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| **Geo-blocking EU users** | No GDPR compliance needed | Loses EU market, complex to enforce | Better to comply |
| **Minimal compliance** | Less development effort | Still at risk of fines | Full compliance safer |

### Consequences
- **Positive:**
  - Legal compliance (avoid fines)
  - User trust (transparent data practices)
  - Clear data ownership
- **Negative:**
  - Development effort (delete, export features)
  - Audit log storage (90 days)
  - Privacy policy maintenance

---

## Summary of All Architectural Decisions

| Decision | Status | Impact |
|----------|--------|--------|
| Hybrid Architecture (Next.js + FastAPI) | ✅ Implemented | Enables best-in-class UX + financial analysis |
| Market Data: yfinance | ✅ Implemented | $0 cost for MVP, easy upgrade path |
| No Auth in v1.0 | ✅ Implemented (v1.5) | Faster MVP, simpler architecture |
| Rules-Based ML | ✅ Implemented | 80% value, 20% complexity |
| No Database in v1.0 | ✅ Implemented (v1.5) | Zero infra cost, stateless backend |
| Risk Scoring Algorithm | ✅ Implemented | Transparent, actionable risk metric |
| **PostgreSQL + Prisma for v1.6** | 🔄 Designed | Production-ready data persistence |
| **JWT Auth with OAuth for v1.6** | 🔄 Designed | Secure multi-user support |
| **bcrypt Password Hashing** | 🔄 Designed | Industry-standard security |
| **GDPR Compliance** | 🔄 Designed | Legal compliance, user trust |

---

**v1.5:** All architectural decisions documented and implemented.  
**v1.6:** Architecture design complete, ready for implementation.
