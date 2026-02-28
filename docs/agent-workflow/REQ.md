# KlyrSignals - Requirements Document

**Version:** 0.1.0  
**Status:** 🌱 Draft  
**Last Updated:** 2026-02-28

---

## Problem Statement

Individual investors and small portfolio managers lack access to institutional-grade portfolio analysis tools. They struggle to:
- Identify hidden concentration risks in their portfolios
- Detect over-exposure to specific sectors, asset classes, or geographies
- Get objective, data-driven rebalancing recommendations
- Understand correlation risks between holdings

## Solution

**KlyrSignals** - AI-powered financial analyst that:
1. Analyzes portfolio holdings and allocation
2. Detects blind spots using ML pattern recognition
3. Identifies over-exposure across multiple dimensions
4. Provides actionable rebalancing recommendations
5. Monitors portfolio health in real-time

---

## User Personas

### 1. Retail Investor (Primary)
- **Profile:** Individual investor managing personal portfolio ($50k-$500k)
- **Goals:** Maximize returns while managing risk, avoid costly mistakes
- **Pain Points:** 
  - Doesn't know what they don't know (blind spots)
  - Emotional decision-making
  - Limited access to professional analysis tools
- **Willingness to Pay:** $15-30/month

### 2. Financial Advisor (Secondary)
- **Profile:** Independent advisor managing 20-100 client portfolios
- **Goals:** Provide better client service, scale analysis capabilities
- **Pain Points:**
  - Manual portfolio analysis is time-consuming
  - Hard to monitor all clients continuously
  - Need to justify recommendations with data
- **Willingness to Pay:** $99-299/month (team plan)

### 3. Family Office Analyst (Future)
- **Profile:** Managing UHNW family portfolios ($10M+)
- **Goals:** Institutional-grade risk management, comprehensive reporting
- **Pain Points:**
  - Complex multi-asset portfolios
  - Need custom risk metrics
  - Regulatory compliance requirements
- **Willingness to Pay:** $500+/month (enterprise)

---

## Functional Requirements (Prioritized)

**Priority Legend:**
- **P0:** MVP critical (must have for v1.0)
- **P1:** Important but can defer to v1.1
- **P2:** Nice to have (v1.5+)

### FR-1: Portfolio Import **[P0]**
**As a** user  
**I want to** import my portfolio holdings  
**So that** I can analyze my current investments

**Acceptance Criteria:**
- [ ] Manual entry form (symbol, quantity, purchase price, date)
- [ ] CSV import (support major broker formats: Fidelity, Schwab, Vanguard)
- [ ] Validate ticker symbols against market data
- [ ] Calculate current value using real-time prices
- [ ] Support multiple asset classes (stocks, ETFs, mutual funds, crypto)

### FR-2: Asset Allocation Visualization **[P0]**
**As a** user  
**I want to** see my portfolio allocation visually  
**So that** I understand my current exposure

**Acceptance Criteria:**
- [ ] Pie chart showing allocation by asset class
- [ ] Bar chart showing sector allocation
- [ ] Top 10 holdings table
- [ ] Interactive filtering (click sector to see holdings)
- [ ] Geographic allocation (v1.1 - defer map visualization)

### FR-3: Over-Exposure Detection **[P0]**
**As a** user  
**I want to** be alerted when I'm over-exposed  
**So that** I can rebalance before taking excessive risk

**Acceptance Criteria:**
- [ ] Detect sector concentration >25% (warning), >40% (critical)
- [ ] Detect single stock >10% of portfolio (warning), >20% (critical)
- [ ] Detect asset class imbalance (e.g., 100% equities)
- [ ] Provide specific rebalancing recommendations
- [ ] Geographic concentration (v1.1 - defer until multi-region data available)

### FR-4: Blind Spot Detection **[P0]**
**As a** user  
**I want** AI to identify risks I'm not seeing  
**So that** I can address hidden vulnerabilities

**Acceptance Criteria (v1.0 - Rules-Based):**
- [ ] Detect holdings in same sector (simple correlation proxy)
- [ ] Detect style drift (categorize as large-cap growth, small-cap value, etc.)
- [ ] Flag concentration risks not obvious from surface allocation
- [ ] Provide confidence score for each insight (0-100%)
- [ ] Factor exposure (v1.5 - defer advanced ML analysis)
- [ ] ESG concerns (v1.5 - defer until user preferences feature)

### FR-5: Risk Scoring **[P0]**
**As a** user  
**I want** a simple portfolio health score  
**So that** I can quickly assess overall risk

**Acceptance Criteria:**
- [ ] Calculate composite risk score (0-100, lower is better)
- [ ] Break down score by category (concentration, volatility)
- [ ] Compare to benchmark (S&P 500, 60/40 portfolio)
- [ ] Provide actionable improvement suggestions
- [ ] Historical trend (v1.1 - requires portfolio persistence)

### FR-6: Rebalancing Recommendations **[P1]**
**As a** user  
**I want** specific rebalancing actions  
**So that** I know exactly what to do

**Acceptance Criteria:**
- [ ] Generate "sell X shares of A, buy Y shares of B" recommendations
- [ ] Prioritize recommendations by impact (highest risk reduction first)
- [ ] Support target allocation input (user defines desired allocation)
- [ ] Tax impact estimates (v1.5 - defer until auth + cost basis tracking)
- [ ] Export to CSV/PDF (v1.1 - defer)

### FR-7: Real-Time Monitoring **[P1]**
**As a** user  
**I want** my portfolio updated in real-time  
**So that** I see current values and risks

**Acceptance Criteria:**
- [ ] Fetch live prices every 15 minutes during market hours
- [ ] Update risk metrics automatically
- [ ] Show pre-market and after-hours prices (v1.1 - defer)
- [ ] Alerts for significant changes (v1.5 - requires auth/notification system)
- [ ] News impact (v1.5 - defer)

### FR-8: Performance Tracking **[P1]**
**As a** user  
**I want** to track my portfolio performance  
**So that** I know if my strategy is working

**Acceptance Criteria:**
- [ ] Calculate total return (absolute and percentage)
- [ ] Compare to benchmarks (S&P 500, NASDAQ, custom)
- [ ] Show performance by asset class, sector, individual holding
- [ ] Time-weighted return (TWR) (v1.1 - requires transaction history)
- [ ] Money-weighted return (IRR) (v1.1 - requires transaction history)
- [ ] Monthly/quarterly reports (v1.5 - requires auth + persistence)

---

## Non-Functional Requirements

### NFR-1: Performance **[P0]**
- Portfolio analysis completes in <5 seconds
- Real-time price updates <1 second latency
- Dashboard loads in <2 seconds
- Support 100+ concurrent users (MVP), scale to 1000+ (v1.5)

### NFR-2: Security **[P0]**
- All data encrypted in transit (TLS 1.3)
- No sensitive data (account numbers, passwords) stored in v1.0
- API rate limiting to prevent abuse
- Security headers (CORS, CSP, etc.)
- **Note:** Auth/JWT tokens deferred to v1.5

### NFR-3: Data Accuracy **[P0]**
- Market data from Yahoo Finance (yfinance library)
- Calculations validated against known benchmarks
- Clear disclaimers about data limitations and delays
- Fallback handling for API rate limits

### NFR-4: Scalability **[P1]**
- Backend handles 100+ portfolios (MVP), 10,000+ (v1.5)
- Stateless API design (no DB in v1.0)
- Horizontal scaling capability (v1.5 with DB)

### NFR-5: Compliance **[P0]**
- Investment advice disclaimer (not registered investment advisor)
- Terms of service and privacy policy
- GDPR compliance for EU users (data deletion, consent)
- **Note:** No personal data stored in v1.0 (localStorage only)

---

## Technical Constraints

### Architecture
1. **Hybrid Architecture:** Next.js 16 frontend + Python 3.12 FastAPI backend
2. **API Design:** RESTful API (JSON), stateless backend for v1.0
3. **Frontend:** App Router, TypeScript, Tailwind CSS, Recharts
4. **Backend:** FastAPI, pandas, numpy, scikit-learn (v1.5)

### Infrastructure
5. **Market Data:** yfinance (free) for MVP, upgrade to Polygon.io ($29/mo) when needed
6. **Deployment:** Vercel (frontend) + Railway (backend)
7. **Database:** None for v1.0 (localStorage), PostgreSQL for v1.5
8. **Budget:** <$50/month for MVP (Vercel free tier + Railway basic)

### Development
9. **No auth in v1.0:** Focus on core features first
10. **Rules-based ML:** Simple concentration/correlation rules for v1.0
11. **Responsive design:** Mobile-friendly web app (no native mobile app)
12. **Browser support:** Chrome, Firefox, Safari, Edge (latest 2 versions)

---

## Success Metrics

### v1.0 MVP Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Portfolio import success rate | >95% | Analytics tracking |
| Analysis completion time | <5 seconds | Backend logs |
| Dashboard load time | <2 seconds | Frontend performance |
| Blind spot detection usefulness | >80% positive feedback | User surveys |
| System uptime | >99% | Uptime monitoring |
| API response time (p95) | <500ms | Backend logs |

### v1.5+ Metrics (Post-Auth)
| Metric | Target | Measurement |
|--------|--------|-------------|
| User engagement (DAU/MAU) | >40% | Analytics |
| Customer satisfaction (NPS) | >50 | Surveys |
| Conversion rate (free → paid) | >5% | Analytics |
| Portfolio retention (30-day) | >70% | Analytics |

---

## Out of Scope

### v1.0 MVP (Explicitly Excluded)
- [ ] **User authentication** - localStorage only, no accounts
- [ ] **Database persistence** - client-side storage only
- [ ] **Broker integration** (Plaid, etc.) - manual/CSV import only
- [ ] **Mobile app** - responsive web only
- [ ] **Automated trading** - analysis only, no execution
- [ ] **Tax optimization** - beyond basic capital gains estimates
- [ ] **Multi-user collaboration** - single user per browser
- [ ] **Cryptocurrency deep analysis** - basic price tracking only
- [ ] **ESG screening** - deferred to v1.5
- [ ] **Advanced ML models** - rules-based only for v1.0
- [ ] **Push notifications** - deferred to v1.5 with auth
- [ ] **Historical performance trends** - requires persistence

### v1.5+ (Future Roadmap)
- User authentication & accounts
- PostgreSQL database for persistence
- Multi-portfolio support
- Cross-device sync
- Advanced ML (clustering, anomaly detection)
- Tax-loss harvesting recommendations
- Broker integration (read-only)
- Mobile app (iOS/Android)
- Automated rebalancing execution
- Factor analysis & smart beta

---

## Technical Decisions (Made 2026-02-28)

### 1. Market Data Provider
**Decision:** Yahoo Finance (`yfinance`) for MVP
- **Rationale:** Free, sufficient for MVP validation
- **Trade-off:** Rate-limited (~2000 requests/day), occasional reliability issues
- **Upgrade Path:** Switch to Polygon.io ($29/month) when hitting limits or needing higher reliability
- **Implementation:** Abstract data provider behind interface for easy swapping

### 2. Authentication Timing
**Decision:** v1.5 (Post-MVP)
- **Rationale:** Focus on core value prop (analysis) before auth complexity
- **MVP Approach:** No user accounts, portfolios stored in browser localStorage
- **v1.5 Requirement:** Add auth before any public launch or multi-user features
- **Risk:** Users can't access portfolios across devices in v1.0 (acceptable for MVP)

### 3. Database Strategy
**Decision:** No database for v1.0 (localStorage only)
- **v1.0:** Portfolios stored in browser localStorage (client-side only)
- **v1.5:** Add PostgreSQL for user accounts, portfolio persistence, sharing
- **Rationale:** Reduces MVP complexity, validates demand before infra investment
- **Backend State:** Stateless API (no DB connections in v1.0)

### 4. ML Complexity
**Decision:** Rules-based blind spots for v1.0, ML in v1.5
- **v1.0 (Rules-Based):**
  - Concentration >25% = warning, >40% = critical
  - Single stock >10% = warning, >20% = critical
  - Simple correlation detection (holdings in same sector)
  - Style detection via basic categorization (large-cap growth, small-cap value, etc.)
- **v1.5 (ML Enhancement):**
  - Clustering for hidden concentration
  - Anomaly detection for outlier positions
  - Factor analysis (momentum, quality, volatility)
- **Rationale:** Rules-based provides 80% of value with 20% of complexity

---

## Open Questions (RESOLVED)

All open questions resolved. See "Technical Decisions" section above.

---

## Acceptance Criteria (v1.0 MVP)

**MVP is complete when ALL of the following are verified:**

### Core Functionality
- [ ] User can import portfolio via CSV upload
- [ ] User can manually add/edit/remove holdings
- [ ] Asset allocation pie chart displays correctly
- [ ] Sector allocation bar chart displays correctly
- [ ] Top 10 holdings table shows correct data
- [ ] Over-exposure warnings trigger at >25% sector concentration
- [ ] Over-exposure warnings trigger at >10% single stock
- [ ] Risk score (0-100) calculated and displayed
- [ ] Blind spot detection identifies concentration risks
- [ ] Rebalancing recommendations generated (sell X, buy Y)

### Technical Requirements
- [ ] Real-time price updates working (15-min intervals)
- [ ] Portfolio analysis completes in <5 seconds
- [ ] Dashboard loads in <2 seconds
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] No console errors in browser dev tools
- [ ] API endpoints return valid JSON responses
- [ ] HTTPS enabled in production
- [ ] Investment advice disclaimer visible

### Deployment
- [ ] Frontend deployed to Vercel (production URL)
- [ ] Backend deployed to Railway (production URL)
- [ ] CORS configured correctly
- [ ] No critical security vulnerabilities (basic scan)
- [ ] Accessible online (tested on multiple browsers)

### Documentation
- [ ] README.md updated with setup instructions
- [ ] API documentation available
- [ ] User guide for CSV import format

---

**Next Phase:** Tony (Architect) will create system architecture based on these requirements.
