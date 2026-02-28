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

## Functional Requirements

### FR-1: Portfolio Import
**As a** user  
**I want to** import my portfolio holdings  
**So that** I can analyze my current investments

**Acceptance Criteria:**
- [ ] Manual entry form (symbol, quantity, purchase price, date)
- [ ] CSV import (support major broker formats: Fidelity, Schwab, Vanguard)
- [ ] Validate ticker symbols against market data
- [ ] Calculate current value using real-time prices
- [ ] Support multiple asset classes (stocks, ETFs, mutual funds, crypto)

### FR-2: Asset Allocation Visualization
**As a** user  
**I want to** see my portfolio allocation visually  
**So that** I understand my current exposure

**Acceptance Criteria:**
- [ ] Pie chart showing allocation by asset class
- [ ] Bar chart showing sector allocation
- [ ] Geographic allocation map
- [ ] Top 10 holdings table
- [ ] Interactive filtering (click sector to see holdings)

### FR-3: Over-Exposure Detection
**As a** user  
**I want to** be alerted when I'm over-exposed  
**So that** I can rebalance before taking excessive risk

**Acceptance Criteria:**
- [ ] Detect sector concentration >25% (warning), >40% (critical)
- [ ] Detect single stock >10% of portfolio (warning), >20% (critical)
- [ ] Detect geographic concentration >60% in one region
- [ ] Detect asset class imbalance (e.g., 100% equities)
- [ ] Provide specific rebalancing recommendations

### FR-4: Blind Spot Detection (AI)
**As a** user  
**I want** AI to identify risks I'm not seeing  
**So that** I can address hidden vulnerabilities

**Acceptance Criteria:**
- [ ] Analyze correlation between holdings (identify hidden concentration)
- [ ] Detect style drift (e.g., thinking you're diversified but all large-cap growth)
- [ ] Identify factor exposure (value, growth, momentum, quality)
- [ ] Flag ESG concerns if user has sustainability preferences
- [ ] Provide confidence score for each insight (0-100%)

### FR-5: Risk Scoring
**As a** user  
**I want** a simple portfolio health score  
**So that** I can quickly assess overall risk

**Acceptance Criteria:**
- [ ] Calculate composite risk score (0-100, lower is better)
- [ ] Break down score by category (concentration, volatility, liquidity)
- [ ] Compare to benchmark (S&P 500, 60/40 portfolio)
- [ ] Show historical trend (risk score over time)
- [ ] Provide actionable improvement suggestions

### FR-6: Rebalancing Recommendations
**As a** user  
**I want** specific rebalancing actions  
**So that** I know exactly what to do

**Acceptance Criteria:**
- [ ] Generate "sell X shares of A, buy Y shares of B" recommendations
- [ ] Estimate tax impact (short-term vs long-term capital gains)
- [ ] Prioritize recommendations by impact (highest risk reduction first)
- [ ] Support target allocation input (user defines desired allocation)
- [ ] Export recommendations to CSV/PDF

### FR-7: Real-Time Monitoring
**As a** user  
**I want** my portfolio updated in real-time  
**So that** I see current values and risks

**Acceptance Criteria:**
- [ ] Fetch live prices every 15 minutes during market hours
- [ ] Send alerts for significant changes (>5% portfolio move)
- [ ] Update risk metrics automatically
- [ ] Show pre-market and after-hours prices
- [ ] Display news impact on holdings

### FR-8: Performance Tracking
**As a** user  
**I want** to track my portfolio performance  
**So that** I know if my strategy is working

**Acceptance Criteria:**
- [ ] Calculate total return (absolute and percentage)
- [ ] Calculate time-weighted return (TWR) and money-weighted return (IRR)
- [ ] Compare to benchmarks (S&P 500, NASDAQ, custom)
- [ ] Show performance by asset class, sector, individual holding
- [ ] Generate monthly/quarterly performance reports

---

## Non-Functional Requirements

### NFR-1: Performance
- Portfolio analysis completes in <5 seconds
- Real-time price updates <1 second latency
- Dashboard loads in <2 seconds
- Support 1000+ concurrent users

### NFR-2: Security
- All data encrypted in transit (TLS 1.3) and at rest (AES-256)
- API authentication required (JWT tokens)
- No sensitive data (account numbers, passwords) stored
- Regular security audits

### NFR-3: Data Accuracy
- Market data from reliable sources (Yahoo Finance, Alpha Vantage)
- Calculations validated against known benchmarks
- Clear disclaimers about data limitations

### NFR-4: Scalability
- Backend handles 10,000+ portfolios
- Database queries optimized (<100ms response time)
- Horizontal scaling capability

### NFR-5: Compliance
- Investment advice disclaimer (not registered investment advisor)
- Terms of service and privacy policy
- GDPR compliance for EU users

---

## Technical Constraints

1. **Hybrid Architecture:** Next.js frontend + Python backend
2. **Market Data:** Free tier APIs for MVP (upgrade to paid for production)
3. **Deployment:** Frontend on Vercel, backend on Railway/Render
4. **Database:** PostgreSQL (managed service)
5. **Budget:** <$100/month infrastructure for MVP

---

## Success Metrics (v1.0)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Portfolio import success rate | >95% | Analytics tracking |
| Analysis completion time | <5 seconds | Backend logs |
| User engagement (DAU/MAU) | >40% | Analytics |
| Blind spot detection accuracy | >80% | User feedback |
| Customer satisfaction (NPS) | >50 | Surveys |
| System uptime | >99.5% | Monitoring |

---

## Out of Scope (v1.0)

- [ ] Broker integration (Plaid, etc.) - manual import only
- [ ] Tax optimization (beyond basic capital gains estimates)
- [ ] Mobile app (responsive web only)
- [ ] Multi-user collaboration
- [ ] Automated trading (analysis only, no execution)
- [ ] Cryptocurrency deep analysis (basic support only)

---

## Open Questions

1. **Market Data Provider:** Yahoo Finance (free but unreliable) vs Alpha Vantage (paid but stable)?
2. **Authentication:** Implement in v1.0 or wait until v1.5?
3. **Database:** Need PostgreSQL for v1.0 or can start with in-memory/file-based?
4. **ML Complexity:** Start with simple rules-based blind spots or full ML models?

---

## Acceptance Criteria (v1.0 MVP)

**MVP is complete when:**
- [ ] User can import portfolio (CSV or manual)
- [ ] Asset allocation charts display correctly
- [ ] Over-exposure warnings trigger appropriately
- [ ] Basic blind spot detection works (concentration, correlation)
- [ ] Risk score calculated and displayed
- [ ] Rebalancing recommendations generated
- [ ] Real-time price updates working
- [ ] Dashboard is responsive and usable
- [ ] No critical security vulnerabilities
- [ ] Deployed and accessible online

---

**Next Phase:** Tony (Architect) will create system architecture based on these requirements.
