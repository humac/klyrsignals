# Architecture Brief for Tony

**Project:** KlyrSignals  
**Phase:** tony_design (Architecture)  
**Prepared by:** Pepper (Analyst)  
**Date:** 2026-02-28  
**Handoff from:** pepper_reqs (DONE)

---

## Executive Summary

Build a **hybrid architecture** financial portfolio analyst app:
- **Frontend:** Next.js 16 (TypeScript, App Router, Tailwind, Recharts)
- **Backend:** Python 3.12 FastAPI (stateless API, no DB in v1.0)
- **Key Decision:** MVP has NO authentication, NO database (localStorage only)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER BROWSER                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Next.js 16 Frontend (Vercel)              │   │
│  │  - TypeScript, App Router                           │   │
│  │  - Tailwind CSS, Recharts                           │   │
│  │  - localStorage (portfolio persistence)             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API (JSON)
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Python FastAPI Backend (Railway)               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  - Stateless API (no database v1.0)                 │   │
│  │  - pandas, numpy for calculations                   │   │
│  │  - yfinance for market data                         │   │
│  │  - Rules-based blind spot detection                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ API Calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              External Services                              │
│  - Yahoo Finance (yfinance) - Market data                  │
│  - (Future: Polygon.io for production)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Frontend Requirements

### Tech Stack
- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS
- **Charts:** Recharts (pie, bar, line charts)
- **State Management:** React Context + localStorage
- **HTTP Client:** fetch API or axios

### Key Pages to Design
1. **Dashboard (`/`)** - Main portfolio overview
   - Asset allocation pie chart
   - Sector allocation bar chart
   - Top 10 holdings table
   - Risk score display
   - Quick actions (import, add holding)

2. **Portfolio Import (`/import`)** - CSV upload & manual entry
   - CSV file upload with validation
   - Manual entry form (symbol, quantity, price, date)
   - Preview before import
   - Error handling for invalid tickers

3. **Holdings (`/holdings`)** - Manage individual positions
   - Table of all holdings
   - Add/Edit/Delete actions
   - Real-time price updates
   - Performance per holding

4. **Analysis (`/analysis`)** - Detailed risk analysis
   - Over-exposure warnings
   - Blind spot detection results
   - Correlation matrix (visual)
   - Rebalancing recommendations

5. **Settings (`/settings`)** - User preferences
   - Target allocation input
   - Risk tolerance settings
   - Data export (CSV)
   - Clear portfolio (localStorage)

### UI/UX Requirements
- **Responsive:** Mobile-first design (320px → 1920px+)
- **Loading States:** Skeleton loaders for charts
- **Error Handling:** User-friendly error messages
- **Accessibility:** WCAG 2.1 AA compliance
- **Performance:** Lighthouse score >90

---

## Backend Requirements

### Tech Stack
- **Framework:** FastAPI (Python 3.12)
- **Data Processing:** pandas, numpy
- **Market Data:** yfinance library
- **ML (v1.0):** Rules-based (no scikit-learn needed yet)
- **Validation:** Pydantic models

### API Endpoints (REST)

#### Portfolio Analysis
```
POST   /api/v1/analyze          # Analyze portfolio holdings
GET    /api/v1/risk-score       # Calculate risk score (0-100)
GET    /api/v1/recommendations  # Get rebalancing recommendations
```

#### Market Data
```
GET    /api/v1/prices           # Get current prices for symbols
GET    /api/v1/prices/{symbol}  # Get price for single symbol
```

#### Blind Spot Detection
```
POST   /api/v1/blind-spots      # Detect concentration risks
GET    /api/v1/sector-exposure  # Get sector breakdown
```

#### Health Check
```
GET    /api/health              # API health status
```

### Request/Response Examples

**POST /api/v1/analyze**
```json
// Request
{
  "holdings": [
    {"symbol": "AAPL", "quantity": 50, "purchase_price": 150.00},
    {"symbol": "MSFT", "quantity": 30, "purchase_price": 280.00}
  ]
}

// Response
{
  "total_value": 22400.00,
  "allocation": {
    "Technology": 100.0
  },
  "risk_score": 72,
  "warnings": [
    {"type": "sector_concentration", "severity": "critical", "message": "100% in Technology sector"}
  ]
}
```

### Data Models (Pydantic)

```python
class Holding(BaseModel):
    symbol: str
    quantity: float
    purchase_price: float
    purchase_date: Optional[date] = None

class PortfolioAnalysis(BaseModel):
    total_value: float
    allocation: Dict[str, float]
    risk_score: int
    warnings: List[Warning]
    recommendations: List[Recommendation]
```

---

## Data Flow

### 1. Portfolio Import Flow
```
User uploads CSV → Frontend parses → Validate symbols (API) → 
Store in localStorage → Display confirmation
```

### 2. Analysis Flow
```
User clicks "Analyze" → Frontend sends holdings to API → 
Backend fetches prices (yfinance) → Calculate allocation → 
Detect over-exposure (rules) → Generate recommendations → 
Return JSON → Frontend displays charts/warnings
```

### 3. Real-Time Updates Flow
```
Frontend polls /api/v1/prices every 15 min → 
Backend fetches from yfinance → Return updated prices → 
Frontend recalculates values → Update UI
```

---

## Deployment Architecture

### Frontend (Vercel)
- **Hosting:** Vercel (free tier)
- **Build:** `npm run build`
- **Environment Variables:**
  - `NEXT_PUBLIC_API_URL` → Backend Railway URL
- **Custom Domain:** Optional (vercel.app subdomain for MVP)

### Backend (Railway)
- **Hosting:** Railway (free tier ~$5/month)
- **Runtime:** Python 3.12
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**
  - No secrets needed for v1.0 (yfinance is free)
- **Health Check:** `/api/health`

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## What Tony Should Design

### 1. System Architecture Diagram
- Component diagram (frontend, backend, external services)
- Data flow diagrams for key user journeys
- Deployment topology (Vercel + Railway)

### 2. UI/UX Designs
- **Wireframes** for all 5 pages (Dashboard, Import, Holdings, Analysis, Settings)
- **Component hierarchy** (React component tree)
- **Design system** (colors, typography, spacing)
- **Interactive prototypes** (Figma or similar)

### 3. API Specification
- **OpenAPI/Swagger** spec for all endpoints
- **Request/response schemas** (Pydantic models)
- **Error handling** strategy (HTTP codes, error format)
- **Rate limiting** approach (v1.0: basic, v1.5: robust)

### 4. File Structure
```
klyrsignals/
├── frontend/                 # Next.js app
│   ├── app/                  # App Router pages
│   │   ├── page.tsx          # Dashboard
│   │   ├── import/
│   │   ├── holdings/
│   │   ├── analysis/
│   │   └── settings/
│   ├── components/           # Reusable components
│   ├── lib/                  # Utilities, API client
│   └── types/                # TypeScript types
├── backend/                  # FastAPI app
│   ├── main.py               # FastAPI entry point
│   ├── api/                  # API routes
│   ├── models/               # Pydantic models
│   ├── services/             # Business logic
│   └── utils/                # Helpers
└── docs/                     # Documentation
```

### 5. Technical Decisions Document
- State management approach (Context vs Zustand vs Redux)
- Chart library justification (Recharts vs Chart.js vs D3)
- API authentication strategy (for v1.5 planning)
- Database schema (for v1.5 PostgreSQL migration)

---

## Key Constraints & Guidelines

### Must Have (v1.0)
- ✅ No authentication (localStorage only)
- ✅ No database (stateless backend)
- ✅ yfinance for market data
- ✅ Rules-based blind spots (no ML models)
- ✅ Responsive web design

### Nice to Have (v1.1+)
- 🔄 Historical performance charts
- 🔄 CSV export of recommendations
- 🔄 Geographic allocation visualization

### Future (v1.5+)
- ⏳ User authentication (JWT)
- ⏳ PostgreSQL database
- ⏳ Advanced ML models
- ⏳ Push notifications
- ⏳ Broker integration

---

## Success Criteria for Tony Phase

**Architecture is complete when:**
- [ ] System architecture diagram created
- [ ] UI wireframes for all 5 pages
- [ ] API specification (OpenAPI/Swagger)
- [ ] Component hierarchy documented
- [ ] File structure defined
- [ ] Deployment strategy documented
- [ ] Technical decisions logged in DECISIONS.md
- [ ] Handoff to Peter with clear TASKS.md

---

## Handoff Notes

**From Pepper to Tony:**
- Requirements are finalized and prioritized (P0/P1/P2)
- All open questions resolved (see REQ.md "Technical Decisions")
- MVP scope is intentionally narrow (no auth, no DB)
- Focus on core value: portfolio analysis + blind spot detection
- Don't over-engineer v1.0 (keep it simple, validate demand)

**Next Action:** Generate ARCH.md (detailed architecture) and TASKS.md (implementation tasks for Peter)

---

**Questions?** Clarify with Jarvis before proceeding. Don't assume—ask.
