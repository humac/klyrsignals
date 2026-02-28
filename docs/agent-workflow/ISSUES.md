# ISSUES.md - KlyrSignals

**Project:** KlyrSignals v1.0.0  
**Created:** 2026-02-28  
**Status:** ✅ Active

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

## Known Limitations (v1.0)

### ⚠️ [LIMITATION-001] No Cross-Device Sync

**Status:** Known Limitation  
**Impact:** Medium  
**Workaround:** Export portfolio to CSV for backup

**Description:**
Portfolios are stored in browser localStorage only. Users cannot access their portfolio from multiple devices or browsers.

**Reason:**
No authentication or database in v1.0 (see DEC-003, DEC-005).

**Resolution Path:**
v1.5 will add user authentication and PostgreSQL for cross-device sync.

---

### ⚠️ [LIMITATION-002] No Frontend Automated Tests

**Status:** Known Limitation  
**Impact:** Medium  
**Workaround:** Manual browser testing

**Description:**
Frontend lacks automated test suite (Jest, React Testing Library, Playwright).

**Reason:**
MVP focus on core functionality; tests deferred to v1.5.

**Resolution Path:**
Add Jest + React Testing Library in v1.5 before production deployment.

---

### ⚠️ [LIMITATION-003] No Rate Limiting

**Status:** Known Limitation  
**Impact:** Medium  
**Workaround:** Deploy behind Cloudflare or similar

**Description:**
Backend API has no rate limiting, making it vulnerable to abuse or accidental DDoS.

**Reason:**
v1.0 is for single-user testing; rate limiting deferred to production deployment.

**Resolution Path:**
Add `slowapi` middleware in v1.5:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/prices")
@limiter.limit("100/minute")
async def get_prices(...):
    ...
```

---

### ⚠️ [LIMITATION-004] Market Data Rate Limits

**Status:** Known Limitation  
**Impact:** Low  
**Workaround:** 15-minute caching implemented

**Description:**
yfinance has unofficial rate limits (~2000 requests/day). Heavy usage may trigger temporary blocks.

**Reason:**
Using free tier for MVP validation (see DEC-002).

**Mitigation:**
- 15-minute TTL cache on all price requests
- Batch requests when possible

**Resolution Path:**
Upgrade to Polygon.io ($29/mo) or Alpha Vantage ($50/mo) when hitting limits.

---

### ⚠️ [LIMITATION-005] No Historical Performance Tracking

**Status:** Known Limitation  
**Impact:** Low  
**Workaround:** Manual export to CSV

**Description:**
Cannot track portfolio performance over time (no historical data storage).

**Reason:**
Requires database persistence (deferred to v1.5).

**Resolution Path:**
Add PostgreSQL in v1.5 with daily snapshot jobs.

---

### ⚠️ [LIMITATION-006] Rules-Based ML Only

**Status:** Known Limitation  
**Impact:** Low  
**Workaround:** N/A (rules provide 80% of value)

**Description:**
Blind spot detection uses simple rules-based approach, not advanced ML (clustering, anomaly detection).

**Reason:**
Rules-based provides sufficient value for MVP with much lower complexity (see DEC-004).

**Resolution Path:**
Add ML models in v1.5 when historical data available.

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
No end-to-end tests for critical user flows (import → analyze → results).

**Action:**
Add Playwright in v1.5:
```bash
npm install -D @playwright/test
npx playwright install
```

Test flows:
- Portfolio import via CSV
- Manual holding entry
- Analysis generation
- Export to CSV

---

### 🔧 [DEBT-003] Add API Versioning

**Priority:** Low  
**Effort:** Low

**Description:**
API uses `/api/v1/` prefix but no actual versioning strategy.

**Action:**
Implement proper API versioning in v1.5:
- URL versioning: `/api/v1/`, `/api/v2/`
- Or header versioning: `Accept: application/vnd.klyrsignals.v1+json`

---

## Future Enhancements (v1.5+ Roadmap)

### 🚀 [ENHANCE-001] User Authentication

**Priority:** High  
**Effort:** High

**Description:**
Add JWT authentication for user accounts.

**Requirements:**
- JWT tokens with refresh rotation
- Password hashing (bcrypt)
- Session management
- Password reset flow

**Estimated Effort:** 2-3 weeks

---

### 🚀 [ENHANCE-002] PostgreSQL Database

**Priority:** High  
**Effort:** High

**Description:**
Add PostgreSQL for portfolio persistence and user accounts.

**Requirements:**
- User accounts table
- Portfolios table
- Holdings table (with history)
- Daily snapshots table
- Database migrations (Alembic)

**Estimated Effort:** 2-3 weeks

---

### 🚀 [ENHANCE-003] Advanced ML Models

**Priority:** Medium  
**Effort:** Medium

**Description:**
Enhance blind spot detection with ML.

**Features:**
- Clustering for hidden concentration
- Anomaly detection for outlier positions
- Factor analysis (momentum, quality, volatility)

**Requirements:**
- Historical price data
- User portfolio persistence
- scikit-learn integration

**Estimated Effort:** 1-2 weeks

---

### 🚀 [ENHANCE-004] Broker Integration

**Priority:** Medium  
**Effort:** High

**Description:**
Integrate with Plaid or similar for automatic portfolio sync.

**Requirements:**
- Plaid API integration
- OAuth flow
- Secure credential storage
- Automatic portfolio updates

**Estimated Effort:** 3-4 weeks

---

### 🚀 [ENHANCE-005] Mobile App

**Priority:** Low  
**Effort:** High

**Description:**
Native iOS/Android app.

**Options:**
- React Native (code sharing with web)
- Flutter (cross-platform)
- Native Swift/Kotlin (best UX)

**Estimated Effort:** 8-12 weeks

---

## Issue Tracking Process

1. **Discovery:** Issues found during QA (Heimdall) or user testing
2. **Documentation:** Log in this file with severity and impact
3. **Prioritization:** Jarvis + User decide priority for next sprint
4. **Resolution:** Peter implements fix, Heimdall verifies
5. **Closure:** Move to "Resolved" section with verification notes

---

**Last Updated:** 2026-02-28  
**Total Issues:** 1 resolved, 6 known limitations, 3 technical debt items, 5 future enhancements
