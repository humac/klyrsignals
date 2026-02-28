# KlyrSignals - System Architecture

**Version:** 1.0.0  
**Status:** 🎨 Design Complete  
**Last Updated:** 2026-02-28  
**Author:** Tony (Architect)

---

## Executive Summary

KlyrSignals is a hybrid architecture financial portfolio analyst platform that identifies blind spots and over-exposure risks in investment portfolios. The system uses a **Next.js 16 frontend** (TypeScript, Tailwind CSS) deployed on Vercel and a **Python FastAPI backend** (pandas, numpy) deployed on Railway, communicating via REST API.

**Key Architectural Decisions:**
- **No authentication in v1.0** - Portfolios stored in browser localStorage
- **No database in v1.0** - Stateless backend API
- **Rules-based ML** - Simple concentration/correlation rules for blind spot detection
- **yfinance for market data** - Free tier sufficient for MVP validation

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                            │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Next.js 16 Frontend (Vercel)                 │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │ │
│  │  │  Dashboard  │ │   Import    │ │     Holdings        │  │ │
│  │  │    Page     │ │    Page     │ │       Page          │  │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │ │
│  │  │  Analysis   │ │  Settings   │ │   React Components  │  │ │
│  │  │    Page     │ │    Page     │ │   (Recharts, UI)    │  │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  │ │
│  │                                                           │ │
│  │  State: localStorage (portfolio holdings)                 │ │
│  │  HTTP Client: fetch API / axios                           │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS REST API (JSON)
                              │ CORS-enabled
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Python FastAPI Backend (Railway)                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    API Gateway Layer                      │ │
│  │  - CORS middleware                                        │ │
│  │  - Request validation (Pydantic)                          │ │
│  │  - Error handling                                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   Business Logic Layer                    │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐  │ │
│  │  │  Portfolio   │ │     Risk     │ │  Market Data     │  │ │
│  │  │  Analyzer    │ │   Engine     │ │    Service       │  │ │
│  │  └──────────────┘ └──────────────┘ └──────────────────┘  │ │
│  │  ┌──────────────┐ ┌──────────────┐                        │ │
│  │  │   Blind Spot │ │  Rebalancing │                        │ │
│  │  │  Detection   │ │  Generator   │                        │ │
│  │  └──────────────┘ └──────────────┘                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Data Processing Layer                  │ │
│  │  - pandas (data manipulation)                             │ │
│  │  - numpy (numerical calculations)                         │ │
│  │  - yfinance (market data fetch)                           │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ API Calls
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                            │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │  Yahoo Finance  │  │  (Future:       │                      │
│  │   (yfinance)    │  │  Polygon.io)    │                      │
│  │  - Stock prices │  │  - Real-time    │                      │
│  │  - ETF data     │  │  - Higher limit │                      │
│  │  - Historical   │  │                 │                      │
│  └─────────────────┘  └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Pages (App Router)                   │   │
│  │  / (Dashboard) → /import → /holdings → /analysis → /settings │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Components Library                     │   │
│  │  - PortfolioCard, AllocationChart, HoldingsTable        │   │
│  │  - RiskGauge, WarningBanner, RecommendationList         │   │
│  │  - CSVUploader, HoldingForm, PriceTicker                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   State Management                      │   │
│  │  - React Context (PortfolioContext)                     │   │
│  │  - localStorage persistence                             │   │
│  │  - SWR for API data caching                             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                 │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    API Routes (FastAPI)                 │   │
│  │  POST /api/v1/analyze  GET /api/v1/prices               │   │
│  │  GET /api/v1/risk-score  GET /api/v1/blind-spots        │   │
│  │  GET /api/v1/recommendations  GET /api/health           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 Services (Business Logic)               │   │
│  │  - PortfolioService (analysis, allocation)              │   │
│  │  - RiskService (risk scoring, warnings)                 │   │
│  │  - MarketDataService (yfinance integration)             │   │
│  │  - BlindSpotService (concentration detection)           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Data Models (Pydantic)                │   │
│  │  - Holding, Portfolio, Analysis, Warning, Recommendation│   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Frontend Architecture

### Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Framework** | Next.js 16 (App Router) | Server-side rendering, file-based routing, optimal performance |
| **Language** | TypeScript (strict mode) | Type safety, better DX, catch errors early |
| **Styling** | Tailwind CSS | Utility-first, rapid prototyping, responsive design |
| **Charts** | Recharts | React-native, composable, good documentation |
| **State** | React Context + localStorage | Simple, no external dependencies for v1.0 |
| **HTTP** | fetch API (native) | No extra dependencies, modern browser support |
| **Data Fetching** | SWR (optional) | Caching, revalidation, optimistic updates |

### Directory Structure

```
frontend/
├── app/                      # Next.js App Router pages
│   ├── layout.tsx            # Root layout (providers, nav)
│   ├── page.tsx              # Dashboard (home page)
│   ├── import/
│   │   └── page.tsx          # Portfolio import page
│   ├── holdings/
│   │   └── page.tsx          # Holdings management page
│   ├── analysis/
│   │   └── page.tsx          # Detailed analysis page
│   ├── settings/
│   │   └── page.tsx          # User settings page
│   └── globals.css           # Global styles (Tailwind)
├── components/               # Reusable React components
│   ├── ui/                   # Base UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Table.tsx
│   │   └── Badge.tsx
│   ├── portfolio/            # Portfolio-specific components
│   │   ├── PortfolioCard.tsx
│   │   ├── AllocationChart.tsx
│   │   ├── HoldingsTable.tsx
│   │   ├── RiskGauge.tsx
│   │   └── ImportWizard.tsx
│   ├── analysis/             # Analysis components
│   │   ├── WarningBanner.tsx
│   │   ├── RecommendationList.tsx
│   │   ├── BlindSpotCard.tsx
│   │   └── CorrelationMatrix.tsx
│   └── layout/               # Layout components
│       ├── Header.tsx
│       ├── Footer.tsx
│       └── Navigation.tsx
├── lib/                      # Utilities and helpers
│   ├── api.ts                # API client (fetch wrapper)
│   ├── utils.ts              # General utilities
│   ├── validators.ts         # Data validation functions
│   └── constants.ts          # App constants
├── context/                  # React Context providers
│   └── PortfolioContext.tsx  # Portfolio state management
├── types/                    # TypeScript type definitions
│   ├── portfolio.ts          # Portfolio-related types
│   ├── analysis.ts           # Analysis-related types
│   └── api.ts                # API types
├── hooks/                    # Custom React hooks
│   ├── usePortfolio.ts       # Portfolio data hook
│   ├── usePrices.ts          # Market prices hook
│   └── useAnalysis.ts        # Analysis data hook
├── public/                   # Static assets
│   ├── favicon.ico
│   └── logo.svg
├── .env.local                # Environment variables (gitignored)
├── .env.example              # Environment template
├── next.config.js            # Next.js configuration
├── tailwind.config.js        # Tailwind configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # Dependencies
```

### Page Components

#### 1. Dashboard (`/`)

**Purpose:** Main portfolio overview and quick actions

**Components:**
- `PortfolioCard` - Total value, daily change, risk score
- `AllocationChart` - Pie chart (asset class), Bar chart (sectors)
- `HoldingsTable` - Top 10 holdings with performance
- `WarningBanner` - Critical over-exposure alerts
- `QuickActions` - Import, Add Holding, Analyze buttons

**Data Flow:**
```
localStorage → PortfolioContext → Components
              ↓
         API (prices) → SWR cache → Real-time updates
```

#### 2. Import Page (`/import`)

**Purpose:** Import portfolio via CSV or manual entry

**Components:**
- `ImportWizard` - Step-by-step import flow
- `CSVUploader` - Drag-and-drop file upload
- `CSVPreview` - Validate and preview parsed data
- `HoldingForm` - Manual entry form
- `ImportSummary` - Confirmation before save

**Validation:**
- Ticker symbol validation (API call)
- Required fields check
- Duplicate detection
- Error messages for invalid data

#### 3. Holdings Page (`/holdings`)

**Purpose:** Manage individual portfolio positions

**Components:**
- `HoldingsTable` - Full list with sorting/filtering
- `HoldingRow` - Individual holding with actions
- `EditHoldingModal` - Edit existing position
- `AddHoldingModal` - Add new position
- `DeleteConfirmation` - Confirm removal

**Features:**
- Sort by symbol, quantity, value, performance
- Filter by sector, asset class
- Real-time price updates
- Bulk actions (delete multiple)

#### 4. Analysis Page (`/analysis`)

**Purpose:** Detailed risk analysis and recommendations

**Components:**
- `RiskGauge` - Visual risk score (0-100)
- `WarningList` - All detected warnings
- `BlindSpotCard` - AI-detected blind spots
- `RecommendationList` - Rebalancing suggestions
- `CorrelationMatrix` - Heatmap of holdings correlation
- `SectorExposureChart` - Detailed sector breakdown

**Data Flow:**
```
Frontend (holdings) → POST /api/v1/analyze → Backend
                      ↓
            Analysis results (JSON)
                      ↓
            Display charts/warnings
```

#### 5. Settings Page (`/settings`)

**Purpose:** User preferences and data management

**Components:**
- `TargetAllocationForm` - Set desired allocation
- `RiskToleranceSelector` - Conservative/Moderate/Aggressive
- `DataExport` - Export portfolio to CSV
- `ClearPortfolio` - Reset localStorage
- `AppInfo` - Version, disclaimer

---

### State Management

#### PortfolioContext

```typescript
interface PortfolioContextType {
  holdings: Holding[];
  totalValue: number;
  lastUpdated: Date | null;
  addHolding: (holding: Holding) => void;
  updateHolding: (symbol: string, updates: Partial<Holding>) => void;
  removeHolding: (symbol: string) => void;
  importHoldings: (holdings: Holding[]) => void;
  clearPortfolio: () => void;
  refreshPrices: () => Promise<void>;
}
```

**Persistence Strategy:**
- All holdings stored in `localStorage` under key `klyrsignals_portfolio`
- Auto-save on every mutation
- Load from localStorage on app initialization
- No server-side persistence in v1.0

#### Custom Hooks

**usePortfolio:**
```typescript
const { holdings, totalValue, addHolding, removeHolding } = usePortfolio();
```

**usePrices:**
```typescript
const { prices, loading, error } = usePrices(['AAPL', 'MSFT', 'GOOGL']);
```

**useAnalysis:**
```typescript
const { analysis, loading, error, refresh } = useAnalysis(holdings);
```

---

### UI/UX Design System

#### Color Palette

```css
/* Primary */
--primary: #2563eb;        /* Blue-600 */
--primary-hover: #1d4ed8;  /* Blue-700 */

/* Risk Colors */
--risk-low: #10b981;       /* Green-500 */
--risk-medium: #f59e0b;    /* Amber-500 */
--risk-high: #ef4444;      /* Red-500 */

/* Neutral */
--background: #ffffff;
--foreground: #0f172a;     /* Slate-900 */
--muted: #64748b;          /* Slate-500 */
--border: #e2e8f0;         /* Slate-200 */
```

#### Typography

- **Headings:** Inter (sans-serif), font-weight: 600-700
- **Body:** Inter (sans-serif), font-weight: 400-500
- **Monospace:** JetBrains Mono (for symbols, numbers)

#### Spacing Scale

- Base unit: 4px
- Scale: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128

#### Component Examples

**Button Variants:**
- Primary (blue background, white text)
- Secondary (white background, border)
- Danger (red background, white text)
- Ghost (transparent, hover background)

**Card Component:**
- White background
- Subtle shadow (sm)
- Rounded corners (md)
- Padding: 16-24px

---

## Backend Architecture

### Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Framework** | FastAPI | Auto docs, type validation, async support |
| **Language** | Python 3.12 | Latest features, performance improvements |
| **Data Processing** | pandas 2.x | DataFrame operations, time series |
| **Numerical** | numpy 1.x | Fast array operations |
| **Market Data** | yfinance | Free, easy API, sufficient for MVP |
| **Validation** | Pydantic v2 | Type validation, auto docs |
| **Server** | uvicorn | ASGI server, production-ready |

### Directory Structure

```
backend/
├── app/
│   ├── main.py               # FastAPI app entry point
│   ├── config.py             # Configuration settings
│   ├── api/                  # API routes
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── portfolio.py  # Portfolio endpoints
│   │   │   ├── analysis.py   # Analysis endpoints
│   │   │   ├── market.py     # Market data endpoints
│   │   │   └── health.py     # Health check endpoint
│   │   └── deps.py           # Dependencies (validation, etc.)
│   ├── models/               # Pydantic models
│   │   ├── __init__.py
│   │   ├── holding.py        # Holding model
│   │   ├── portfolio.py      # Portfolio model
│   │   ├── analysis.py       # Analysis models
│   │   └── common.py         # Common models (Warning, Recommendation)
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   ├── portfolio_service.py    # Portfolio analysis
│   │   ├── risk_service.py         # Risk scoring, warnings
│   │   ├── market_data_service.py  # yfinance integration
│   │   ├── blind_spot_service.py   # Blind spot detection
│   │   └── recommendation_service.py # Rebalancing logic
│   ├── utils/                # Utilities
│   │   ├── __init__.py
│   │   ├── validators.py     # Data validation
│   │   ├── formatters.py     # Response formatting
│   │   └── exceptions.py     # Custom exceptions
│   └── core/                 # Core logic
│       ├── __init__.py
│       ├── allocation.py     # Allocation calculations
│       ├── correlation.py    # Correlation matrix
│       └── scoring.py        # Risk scoring algorithms
├── tests/                    # Unit tests
│   ├── __init__.py
│   ├── test_api/
│   ├── test_services/
│   └── test_core/
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Project metadata
├── .env                      # Environment variables (gitignored)
├── .env.example              # Environment template
└── README.md                 # Backend documentation
```

### API Routes

#### Health Check

```python
# GET /api/health
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

#### Portfolio Analysis

```python
# POST /api/v1/analyze
@app.post("/api/v1/analyze", response_model=PortfolioAnalysis)
async def analyze_portfolio(request: PortfolioAnalysisRequest):
    """
    Analyze portfolio holdings and return comprehensive analysis.
    
    - **holdings**: List of portfolio holdings
    - **Returns**: Complete analysis including allocation, risk score, warnings
    """
    return await portfolio_service.analyze(request.holdings)
```

#### Risk Score

```python
# GET /api/v1/risk-score
@app.get("/api/v1/risk-score", response_model=RiskScoreResponse)
async def get_risk_score(holdings: str):
    """
    Calculate portfolio risk score (0-100).
    
    - **holdings**: JSON-encoded list of holdings
    - **Returns**: Risk score with breakdown
    """
    holdings_list = parse_holdings(holdings)
    return await risk_service.calculate_risk_score(holdings_list)
```

#### Market Prices

```python
# GET /api/v1/prices
@app.get("/api/v1/prices", response_model=PriceResponse)
async def get_prices(symbols: str):
    """
    Get current market prices for multiple symbols.
    
    - **symbols**: Comma-separated list of ticker symbols
    - **Returns**: Current prices for all symbols
    """
    symbol_list = symbols.split(",")
    return await market_data_service.get_prices(symbol_list)
```

#### Blind Spots

```python
# POST /api/v1/blind-spots
@app.post("/api/v1/blind-spots", response_model=BlindSpotResponse)
async def detect_blind_spots(request: PortfolioAnalysisRequest):
    """
    Detect hidden concentration risks and blind spots.
    
    - **holdings**: List of portfolio holdings
    - **Returns**: List of detected blind spots with confidence scores
    """
    return await blind_spot_service.detect(request.holdings)
```

#### Recommendations

```python
# GET /api/v1/recommendations
@app.get("/api/v1/recommendations", response_model=RecommendationResponse)
async def get_recommendations(holdings: str, target_allocation: str = None):
    """
    Generate rebalancing recommendations.
    
    - **holdings**: JSON-encoded list of holdings
    - **target_allocation**: Optional target allocation JSON
    - **Returns**: Prioritized list of rebalancing actions
    """
    holdings_list = parse_holdings(holdings)
    target = parse_allocation(target_allocation) if target_allocation else None
    return await recommendation_service.generate(holdings_list, target)
```

---

### Data Models (Pydantic)

#### Holding

```python
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class Holding(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10, description="Ticker symbol")
    quantity: float = Field(..., gt=0, description="Number of shares")
    purchase_price: float = Field(..., gt=0, description="Price per share at purchase")
    purchase_date: Optional[date] = Field(None, description="Purchase date")
    asset_class: Optional[str] = Field("stock", description="Asset class (stock, etf, crypto)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "quantity": 50,
                "purchase_price": 150.00,
                "purchase_date": "2024-01-15",
                "asset_class": "stock"
            }
        }
```

#### Portfolio Analysis Request

```python
class PortfolioAnalysisRequest(BaseModel):
    holdings: list[Holding] = Field(..., min_length=1, description="List of portfolio holdings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "holdings": [
                    {"symbol": "AAPL", "quantity": 50, "purchase_price": 150.00},
                    {"symbol": "MSFT", "quantity": 30, "purchase_price": 280.00}
                ]
            }
        }
```

#### Warning

```python
from enum import Enum

class WarningSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class WarningType(str, Enum):
    SECTOR_CONCENTRATION = "sector_concentration"
    SINGLE_STOCK = "single_stock"
    ASSET_CLASS_IMBALANCE = "asset_class_imbalance"
    GEOGRAPHIC_CONCENTRATION = "geographic_concentration"

class Warning(BaseModel):
    type: WarningType
    severity: WarningSeverity
    message: str
    details: dict = {}
    affected_symbols: list[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "sector_concentration",
                "severity": "critical",
                "message": "Portfolio is 100% exposed to Technology sector",
                "details": {"sector": "Technology", "percentage": 100.0},
                "affected_symbols": ["AAPL", "MSFT", "GOOGL"]
            }
        }
```

#### Recommendation

```python
class RecommendationAction(str, Enum):
    SELL = "sell"
    BUY = "buy"
    HOLD = "hold"

class Recommendation(BaseModel):
    action: RecommendationAction
    symbol: str
    quantity: Optional[float] = None
    reason: str
    priority: int = Field(..., ge=1, le=10, description="Priority (1=highest)")
    expected_impact: str = Field(..., description="Expected risk reduction impact")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "sell",
                "symbol": "AAPL",
                "quantity": 20,
                "reason": "Reduce single-stock concentration from 25% to 15%",
                "priority": 1,
                "expected_impact": "Reduce risk score by 12 points"
            }
        }
```

#### Portfolio Analysis Response

```python
class PortfolioAnalysis(BaseModel):
    total_value: float
    total_cost_basis: float
    total_gain_loss: float
    total_gain_loss_pct: float
    allocation: dict[str, float] = Field(..., description="Allocation by category")
    sector_allocation: dict[str, float]
    risk_score: int = Field(..., ge=0, le=100)
    risk_breakdown: dict[str, int]
    warnings: list[Warning]
    recommendations: list[Recommendation]
    blind_spots: list[BlindSpot]
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_value": 22400.00,
                "total_cost_basis": 15900.00,
                "total_gain_loss": 6500.00,
                "total_gain_loss_pct": 40.88,
                "allocation": {"stock": 100.0},
                "sector_allocation": {"Technology": 100.0},
                "risk_score": 72,
                "risk_breakdown": {"concentration": 40, "volatility": 20, "correlation": 12},
                "warnings": [...],
                "recommendations": [...],
                "blind_spots": [...],
                "timestamp": "2026-02-28T19:00:00Z"
            }
        }
```

---

### Service Layer

#### Portfolio Service

**Responsibilities:**
- Calculate total portfolio value
- Compute allocation percentages (asset class, sector, geographic)
- Aggregate holdings by category
- Calculate cost basis and gains/losses

**Key Methods:**
```python
class PortfolioService:
    async def analyze(self, holdings: list[Holding]) -> PortfolioAnalysis:
        # 1. Fetch current prices
        # 2. Calculate total value
        # 3. Compute allocations
        # 4. Generate warnings (risk_service)
        # 5. Detect blind spots (blind_spot_service)
        # 6. Generate recommendations (recommendation_service)
        # 7. Return comprehensive analysis
        pass
    
    def calculate_allocation(self, holdings: list[Holding], prices: dict) -> dict:
        # Group by asset class, sector, etc.
        pass
```

#### Risk Service

**Responsibilities:**
- Calculate composite risk score (0-100)
- Detect over-exposure warnings
- Compare to benchmarks
- Break down risk by category

**Risk Score Algorithm:**
```python
def calculate_risk_score(holdings, prices, allocation):
    concentration_risk = measure_concentration(allocation)  # 0-50 points
    volatility_risk = measure_volatility(holdings, prices)  # 0-30 points
    correlation_risk = measure_correlation(holdings)        # 0-20 points
    
    total_risk = concentration_risk + volatility_risk + correlation_risk
    return min(100, int(total_risk))
```

**Warning Thresholds:**
- Sector concentration: >25% (warning), >40% (critical)
- Single stock: >10% (warning), >20% (critical)
- Asset class: >80% in one class (warning)

#### Market Data Service

**Responsibilities:**
- Fetch current prices from yfinance
- Cache prices to reduce API calls
- Handle rate limiting
- Fallback handling for failed requests

**Implementation:**
```python
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
    
    def _fetch_from_yfinance(self, symbols: list[str]) -> dict[str, float]:
        import yfinance as yf
        prices = {}
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            prices[symbol] = ticker.fast_info['last_price']
        return prices
```

#### Blind Spot Service

**Responsibilities:**
- Detect hidden concentration risks
- Identify correlation patterns
- Flag style drift
- Provide confidence scores

**Detection Rules (v1.0 - Rules-Based):**
```python
class BlindSpotService:
    def detect(self, holdings: list[Holding]) -> list[BlindSpot]:
        blind_spots = []
        
        # Rule 1: Same-sector concentration
        sector_holdings = self.group_by_sector(holdings)
        for sector, holdings_list in sector_holdings.items():
            if len(holdings_list) >= 3 and self.calculate_correlation(holdings_list) > 0.7:
                blind_spots.append(BlindSpot(
                    type="hidden_correlation",
                    confidence=85,
                    message=f"High correlation detected in {sector} sector holdings",
                    affected_symbols=[h.symbol for h in holdings_list]
                ))
        
        # Rule 2: Style drift detection
        style_mix = self.analyze_style(holdings)
        if style_mix['dominant_style'] == 'large_cap_growth' and style_mix['percentage'] > 80:
            blind_spots.append(BlindSpot(
                type="style_concentration",
                confidence=75,
                message="Portfolio heavily tilted toward large-cap growth stocks",
                details=style_mix
            ))
        
        return blind_spots
```

#### Recommendation Service

**Responsibilities:**
- Generate rebalancing recommendations
- Prioritize by impact
- Calculate specific trade quantities
- Estimate risk reduction

**Algorithm:**
```python
class RecommendationService:
    def generate(self, holdings: list[Holding], target_allocation: dict = None) -> list[Recommendation]:
        recommendations = []
        
        # 1. Identify over-exposed positions
        over_exposed = self.find_over_exposure(holdings)
        
        # 2. For each over-exposed position, generate sell recommendation
        for position in over_exposed:
            sell_quantity = self.calculate_sell_quantity(position, target_allocation)
            recommendations.append(Recommendation(
                action="sell",
                symbol=position.symbol,
                quantity=sell_quantity,
                reason=f"Reduce {position.sector} exposure from {position.pct}% to {target_allocation.get(position.sector, 15)}%",
                priority=self.calculate_priority(position),
                expected_impact=f"Reduce risk score by {self.estimate_impact(position)} points"
            ))
        
        # 3. Generate buy recommendations for under-weight sectors
        under_weight = self.find_under_weight(holdings, target_allocation)
        for sector in under_weight:
            recommendations.append(Recommendation(
                action="buy",
                symbol=self.suggest_etf(sector),
                quantity=self.calculate_buy_quantity(sector),
                reason=f"Increase {sector} exposure",
                priority=5,
                expected_impact="Improve diversification"
            ))
        
        # 4. Sort by priority
        return sorted(recommendations, key=lambda r: r.priority)
```

---

## ML Pipeline (Rules-Based v1.0)

### Blind Spot Detection

**Approach:** Rules-based concentration and correlation detection

**Detection Rules:**

1. **Hidden Sector Concentration**
   - Trigger: 3+ holdings in same sector with pairwise correlation >0.7
   - Confidence: 85%
   - Output: Warning with affected symbols

2. **Style Concentration**
   - Trigger: >80% in single style category (large-cap growth, small-cap value, etc.)
   - Confidence: 75%
   - Output: Style drift warning

3. **Geographic Concentration**
   - Trigger: >70% in single geographic region
   - Confidence: 80%
   - Output: Geographic diversification warning

4. **Market Cap Concentration**
   - Trigger: >75% in single market cap category
   - Confidence: 70%
   - Output: Market cap diversification suggestion

### Risk Scoring Algorithm

**Composite Score (0-100):**

```
Risk Score = Concentration Risk (50%) + Volatility Risk (30%) + Correlation Risk (20%)
```

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

### Correlation Calculation

**Method:** Pearson correlation coefficient using historical returns

```python
def calculate_correlation_matrix(holdings, prices_history):
    """
    Calculate pairwise correlation matrix for holdings.
    
    Returns: dict[tuple[str, str], float]
    """
    correlations = {}
    for i, h1 in enumerate(holdings):
        for j, h2 in enumerate(holdings):
            if i < j:
                returns1 = calculate_returns(prices_history[h1.symbol])
                returns2 = calculate_returns(prices_history[h2.symbol])
                corr = np.corrcoef(returns1, returns2)[0, 1]
                correlations[(h1.symbol, h2.symbol)] = corr
    return correlations
```

---

## API Design

### REST Endpoints Summary

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/health` | Health check | No |
| POST | `/api/v1/analyze` | Full portfolio analysis | No |
| GET | `/api/v1/risk-score` | Calculate risk score | No |
| GET | `/api/v1/recommendations` | Get rebalancing recommendations | No |
| POST | `/api/v1/blind-spots` | Detect blind spots | No |
| GET | `/api/v1/sector-exposure` | Get sector breakdown | No |
| GET | `/api/v1/prices` | Get prices for multiple symbols | No |
| GET | `/api/v1/prices/{symbol}` | Get price for single symbol | No |

### Request/Response Examples

#### POST /api/v1/analyze

**Request:**
```json
{
  "holdings": [
    {
      "symbol": "AAPL",
      "quantity": 50,
      "purchase_price": 150.00,
      "purchase_date": "2024-01-15",
      "asset_class": "stock"
    },
    {
      "symbol": "MSFT",
      "quantity": 30,
      "purchase_price": 280.00,
      "purchase_date": "2024-02-20",
      "asset_class": "stock"
    },
    {
      "symbol": "VTI",
      "quantity": 100,
      "purchase_price": 220.00,
      "purchase_date": "2024-03-10",
      "asset_class": "etf"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "total_value": 29800.00,
  "total_cost_basis": 22900.00,
  "total_gain_loss": 6900.00,
  "total_gain_loss_pct": 30.13,
  "allocation": {
    "stock": 67.8,
    "etf": 32.2
  },
  "sector_allocation": {
    "Technology": 55.4,
    "Broad Market": 32.2,
    "Cash": 12.4
  },
  "risk_score": 58,
  "risk_breakdown": {
    "concentration": 30,
    "volatility": 18,
    "correlation": 10
  },
  "warnings": [
    {
      "type": "sector_concentration",
      "severity": "medium",
      "message": "Technology sector represents 55.4% of portfolio",
      "details": {
        "sector": "Technology",
        "percentage": 55.4
      },
      "affected_symbols": ["AAPL", "MSFT"]
    }
  ],
  "recommendations": [
    {
      "action": "sell",
      "symbol": "AAPL",
      "quantity": 15,
      "reason": "Reduce Technology exposure from 55% to 40%",
      "priority": 2,
      "expected_impact": "Reduce risk score by 8 points"
    },
    {
      "action": "buy",
      "symbol": "VXUS",
      "quantity": 25,
      "reason": "Increase international exposure",
      "priority": 4,
      "expected_impact": "Improve geographic diversification"
    }
  ],
  "blind_spots": [
    {
      "type": "style_concentration",
      "confidence": 78,
      "message": "Portfolio heavily tilted toward large-cap growth stocks",
      "details": {
        "dominant_style": "large_cap_growth",
        "percentage": 82
      },
      "affected_symbols": ["AAPL", "MSFT"]
    }
  ],
  "timestamp": "2026-02-28T19:00:00Z"
}
```

#### GET /api/v1/prices?symbols=AAPL,MSFT,GOOGL

**Response (200 OK):**
```json
{
  "prices": {
    "AAPL": 178.52,
    "MSFT": 415.26,
    "GOOGL": 141.80
  },
  "timestamp": "2026-02-28T19:00:00Z",
  "source": "yfinance"
}
```

### Error Handling

**Error Response Format:**
```json
{
  "detail": {
    "code": "INVALID_SYMBOL",
    "message": "Invalid ticker symbol: AAPLX",
    "symbol": "AAPLX",
    "timestamp": "2026-02-28T19:00:00Z"
  }
}
```

**HTTP Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid input (validation error)
- `404 Not Found` - Symbol not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - External API down

---

## Security Considerations

### v1.0 Security Measures

1. **Transport Security**
   - HTTPS enforced (Vercel + Railway provide TLS)
   - TLS 1.3 minimum
   - HSTS headers enabled

2. **API Security**
   - CORS configured for specific origins (Vercel domain)
   - Rate limiting: 100 requests/minute per IP
   - Input validation (Pydantic models)
   - SQL injection prevention (no SQL in v1.0)

3. **Data Privacy**
   - No sensitive data stored (no account numbers, passwords)
   - No authentication in v1.0 (localStorage only)
   - Client-side data only (not transmitted to backend except for analysis)
   - GDPR compliance: No personal data collected

4. **Frontend Security**
   - Content Security Policy (CSP) headers
   - XSS prevention (React auto-escapes)
   - CSRF protection (stateless API, no cookies)

### Future Security (v1.5+)

- JWT authentication
- PostgreSQL database encryption
- API key management
- OAuth2 for broker integration
- Audit logging

---

## Performance Targets

### Frontend Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| First Contentful Paint | <1.5s | Lighthouse |
| Time to Interactive | <3.0s | Lighthouse |
| Largest Contentful Paint | <2.5s | Lighthouse |
| Cumulative Layout Shift | <0.1 | Lighthouse |
| Total Bundle Size | <500KB | Webpack bundle analyzer |
| Dashboard Load Time | <2s | Frontend logs |

### Backend Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (p50) | <200ms | Backend logs |
| API Response Time (p95) | <500ms | Backend logs |
| Portfolio Analysis Time | <5s | Backend logs |
| Price Fetch Time | <1s | Backend logs |
| Concurrent Users Supported | 100+ | Load testing |

### Optimization Strategies

**Frontend:**
- Code splitting (Next.js automatic)
- Image optimization (Next.js Image component)
- Lazy loading for charts
- SWR caching for API data
- Memoization for expensive calculations

**Backend:**
- Price caching (15-minute TTL)
- Async/await for I/O operations
- Pandas vectorization (avoid loops)
- Connection pooling (future: database)
- Horizontal scaling (Railway auto-scaling)

---

## Testing Strategy

### Frontend Testing

**Unit Tests (Jest + React Testing Library):**
- Component rendering tests
- User interaction tests
- Hook tests
- Utility function tests

**Integration Tests:**
- API integration tests
- State management tests
- End-to-end flows (import → analyze → display)

**Test Coverage Target:** >80%

**Example Test:**
```typescript
describe('PortfolioCard', () => {
  it('displays total portfolio value correctly', () => {
    render(<PortfolioCard />, {
      wrapper: ({ children }) => (
        <PortfolioContext.Provider value={{ totalValue: 25000 }}>
          {children}
        </PortfolioContext.Provider>
      )
    });
    
    expect(screen.getByText(/\$25,000/)).toBeInTheDocument();
  });
});
```

### Backend Testing

**Unit Tests (pytest):**
- Service layer tests
- Model validation tests
- Calculation accuracy tests

**Integration Tests:**
- API endpoint tests (TestClient)
- yfinance integration tests (mocked)
- End-to-end analysis tests

**Test Coverage Target:** >90%

**Example Test:**
```python
def test_calculate_risk_score_concentration():
    holdings = [
        Holding(symbol="AAPL", quantity=100, purchase_price=150.00)
    ]
    risk_score = risk_service.calculate_risk_score(holdings)
    assert risk_score > 50  # High concentration risk
    assert risk_score <= 100
```

### Manual Testing Checklist

- [ ] Portfolio import via CSV
- [ ] Manual holding entry
- [ ] Asset allocation charts render correctly
- [ ] Over-exposure warnings trigger appropriately
- [ ] Risk score calculation accuracy
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Browser compatibility (Chrome, Firefox, Safari, Edge)
- [ ] Error handling (invalid symbols, network errors)

---

## Deployment Architecture

### Frontend Deployment (Vercel)

**Configuration:**
```javascript
// next.config.js
module.exports = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  // Auto-detects Node.js version
  // Automatic HTTPS
  // Automatic CDN caching
}
```

**Environment Variables:**
```
NEXT_PUBLIC_API_URL=https://klyrsignals-backend.railway.app
NEXT_PUBLIC_APP_URL=https://klyrsignals.vercel.app
```

**Deployment Command:**
```bash
git push origin main
# Vercel auto-deploys on push to main branch
```

**Build Process:**
```bash
npm install
npm run build
# Output: .next/ folder
# Deployed to Vercel edge network
```

### Backend Deployment (Railway)

**Configuration:**
```yaml
# railway.toml (optional)
[build]
builder = "nixpacks"
pythonVersion = "3.12"

[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

**Environment Variables:**
```
PORT=8000  # Railway auto-injects
# No API keys needed for yfinance (free tier)
```

**Deployment Command:**
```bash
railway up
# Or connect GitHub repo for auto-deploy
```

**Health Check:**
```bash
curl https://klyrsignals-backend.railway.app/api/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

### CORS Configuration

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://klyrsignals.vercel.app",
        "http://localhost:3000",  # Development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Monitoring & Observability

### Frontend Monitoring

**Tools:**
- Vercel Analytics (built-in)
- Sentry (error tracking)
- Google Analytics (optional)

**Metrics to Track:**
- Page views
- User flows (import → analysis)
- Error rates
- Performance metrics (Core Web Vitals)

### Backend Monitoring

**Tools:**
- Railway built-in logs
- Sentry (error tracking)
- Custom logging (Python logging)

**Metrics to Track:**
- API request count
- Response times (p50, p95)
- Error rates
- yfinance API failures
- Rate limit hits

### Logging Strategy

**Backend Logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Log API requests
logger.info(f"Analyze request received: {len(holdings)} holdings")

# Log errors
logger.error(f"yfinance API failed for {symbol}: {error}")
```

---

## Future Architecture (v1.5+)

### Planned Enhancements

1. **Authentication Layer**
   - JWT tokens
   - User accounts
   - Session management

2. **Database Integration**
   - PostgreSQL for portfolio persistence
   - User preferences storage
   - Historical analysis data

3. **Advanced ML Models**
   - Clustering for hidden concentration
   - Anomaly detection
   - Factor analysis

4. **Real-Time Updates**
   - WebSocket connections
   - Push notifications
   - Live price streaming

5. **Broker Integration**
   - Plaid API for account linking
   - Automatic portfolio sync
   - Trade execution (future)

### Migration Path

**v1.0 → v1.5:**
1. Add authentication layer (non-breaking)
2. Introduce PostgreSQL (additive)
3. Migrate localStorage users to accounts (opt-in)
4. Deploy advanced ML models (additive)
5. Add broker integration (additive)

**Backward Compatibility:**
- v1.0 API remains functional
- localStorage users can continue using app
- New features require authentication

---

## Appendix A: File Structure Summary

```
klyrsignals/
├── frontend/                     # Next.js application
│   ├── app/                      # App Router pages
│   │   ├── layout.tsx
│   │   ├── page.tsx              # Dashboard
│   │   ├── import/page.tsx
│   │   ├── holdings/page.tsx
│   │   ├── analysis/page.tsx
│   │   ├── settings/page.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/                   # Base components
│   │   ├── portfolio/            # Portfolio components
│   │   ├── analysis/             # Analysis components
│   │   └── layout/               # Layout components
│   ├── lib/
│   │   ├── api.ts
│   │   ├── utils.ts
│   │   └── validators.ts
│   ├── context/
│   │   └── PortfolioContext.tsx
│   ├── types/
│   │   ├── portfolio.ts
│   │   ├── analysis.ts
│   │   └── api.ts
│   ├── hooks/
│   │   ├── usePortfolio.ts
│   │   ├── usePrices.ts
│   │   └── useAnalysis.ts
│   ├── public/
│   ├── .env.local
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
├── backend/                      # FastAPI application
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── portfolio.py
│   │   │       ├── analysis.py
│   │   │       ├── market.py
│   │   │       └── health.py
│   │   ├── models/
│   │   │   ├── holding.py
│   │   │   ├── portfolio.py
│   │   │   ├── analysis.py
│   │   │   └── common.py
│   │   ├── services/
│   │   │   ├── portfolio_service.py
│   │   │   ├── risk_service.py
│   │   │   ├── market_data_service.py
│   │   │   ├── blind_spot_service.py
│   │   │   └── recommendation_service.py
│   │   ├── utils/
│   │   │   ├── validators.py
│   │   │   └── exceptions.py
│   │   └── core/
│   │       ├── allocation.py
│   │       ├── correlation.py
│   │       └── scoring.py
│   ├── tests/
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── .env
├── docs/
│   ├── agent-workflow/
│   │   ├── REQ.md
│   │   ├── ARCH.md (this file)
│   │   ├── TASKS.md
│   │   └── QA.md
│   ├── DECISIONS.md
│   └── RUN_STATE.md
└── README.md
```

---

## Appendix B: Technology Justification

### Why Next.js 16?
- **Server-side rendering** for optimal SEO and performance
- **App Router** for modern React patterns
- **Built-in optimizations** (image, font, script)
- **Vercel integration** for seamless deployment
- **TypeScript support** out of the box

### Why FastAPI?
- **Automatic API docs** (Swagger UI, ReDoc)
- **Type validation** with Pydantic
- **Async support** for I/O operations
- **Fast development** with hot reload
- **Python ecosystem** (pandas, numpy, scikit-learn)

### Why Recharts?
- **React-native** (no D3 learning curve)
- **Composable** components
- **Responsive** charts
- **Good documentation**
- **Active maintenance**

### Why yfinance?
- **Free** (no API key required)
- **Easy to use** (simple API)
- **Sufficient for MVP** validation
- **Upgrade path** to Polygon.io when needed

### Why localStorage (no DB)?
- **Zero infrastructure** cost
- **No authentication** complexity
- **Fast MVP** development
- **Validates demand** before database investment
- **GDPR compliant** (no personal data stored)

---

**Architecture Sign-off:** ✅ Complete  
**Next Phase:** Peter (Developer) implementation  
**Handoff:** TASKS.md generated with bounded tasks
