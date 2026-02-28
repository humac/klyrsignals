# DECISIONS.md - KlyrSignals

**Project:** KlyrSignals  
**Started:** 2026-02-28  
**Status:** 🔄 In Progress

---

## [DEC-001] Project Reset & Hybrid Architecture

**Date:** 2026-02-28  
**Decided By:** User + Jarvis  
**Status:** Accepted

### Context
KlyrSignals was initially bootstrapped as a Python-only project. After review, determined that hybrid architecture (Next.js + Python) better serves the requirements.

### Decision
**Delete and re-bootstrap with hybrid architecture:**
- **Frontend:** Next.js 16 + TypeScript + Tailwind CSS
- **Backend:** Python 3.12 + FastAPI + pandas/numpy
- **Deployment:** Vercel (frontend) + Railway (backend)

### Rationale
1. **Python strengths:** Financial analysis, ML, data processing (pandas, numpy, scikit-learn)
2. **Next.js strengths:** Interactive UI, real-time dashboards, charts, user experience
3. **Best of both:** Powerful analysis backend + beautiful, responsive frontend
4. **Scalability:** Can scale frontend and backend independently

### Alternatives Considered
- **Python-only (Streamlit):** Faster to build, but limited UI capabilities
- **Next.js-only:** Better UI, but limited financial libraries in JavaScript
- **Decision:** Hybrid provides best long-term value despite added complexity

### Consequences
- **Pros:**
  - Access to full Python financial ecosystem
  - Excellent user experience with Next.js
  - Scalable architecture
  - Industry-standard tools for both analysis and UI
- **Cons:**
  - More complex (2 codebases to maintain)
  - Need to deploy and monitor 2 services
  - Slightly longer development time

### Implementation
- Deleted old Python-only codebase
- Created fresh project structure with frontend/ and backend/ directories
- Pre-drafted REQ.md with hybrid architecture in mind
- Ready to start full agent pipeline

---

## [DEC-002] Market Data Strategy (Pending)

**Date:** TBD  
**Decided By:** TBD  
**Status:** ⏳ Open Question

### Context
Need to decide on market data provider for MVP.

### Options
1. **Yahoo Finance (yfinance)** - Free, but unreliable rate limits
2. **Alpha Vantage** - Paid ($50/month), but stable and reliable
3. **Polygon.io** - Paid ($29/month), excellent API, comprehensive data

### Decision
**Deferred until Pepper requirements phase** - will evaluate based on:
- Required data freshness (real-time vs delayed)
- Budget constraints
- Required data points (OHLCV, fundamentals, news)

---

## [DEC-003] Authentication Timing (Pending)

**Date:** TBD  
**Decided By:** TBD  
**Status:** ⏳ Open Question

### Context
Should user authentication be implemented in v1.0 or deferred to v1.5?

### Options
1. **v1.0 (MVP):** Implement auth from start (JWT, secure sessions)
2. **v1.5 (Post-MVP):** Start without auth, add later

### Recommendation
**v1.5 (defer)** - Focus on core analysis features first, add auth when ready for multi-user support.

**Rationale:**
- MVP is for single-user testing/validation
- Auth adds complexity without validating core value prop
- Can add auth in v1.5 before opening to public

---

**Next Decision:** Market data provider (after Pepper requirements phase)
