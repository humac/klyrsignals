# KlyrSignals - Implementation Tasks

**Version:** 1.0.0  
**Status:** 📋 Ready for Development  
**Last Updated:** 2026-02-28  
**Author:** Tony (Architect)  
**Handoff to:** Peter (Developer)

---

## Implementation Roadmap

**Total Phases:** 8  
**Estimated Duration:** 4-6 weeks  
**Priority:** P0 (MVP critical) → P1 (Important) → P2 (Nice to have)

---

## Phase 1: Project Setup

**Goal:** Scaffold frontend and backend projects with all dependencies  
**Duration:** 1-2 days  
**Priority:** P0

### Task 1.1: Frontend Scaffolding

**Files:** `frontend/package.json`, `frontend/tsconfig.json`, `frontend/next.config.js`, `frontend/tailwind.config.js`

**Acceptance Criteria:**
- [ ] Next.js 16 project created with App Router
- [ ] TypeScript configured in strict mode
- [ ] Tailwind CSS installed and configured
- [ ] Recharts library installed
- [ ] ESLint + Prettier configured
- [ ] `.env.example` created with `NEXT_PUBLIC_API_URL`
- [ ] `npm run dev` starts dev server on port 3000
- [ ] `npm run build` completes without errors

**Implementation Steps:**
```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --eslint
npm install recharts
npm install -D prettier eslint-config-prettier
```

**Verification:**
```bash
cd frontend
npm run dev
# Open http://localhost:3000 - should show Next.js starter page
npm run build
# Should complete with no errors
```

---

### Task 1.2: Backend Scaffolding

**Files:** `backend/requirements.txt`, `backend/pyproject.toml`, `backend/app/main.py`, `backend/.env.example`

**Acceptance Criteria:**
- [ ] Python 3.12 virtual environment created
- [ ] FastAPI installed with uvicorn
- [ ] pandas, numpy, yfinance installed
- [ ] Pydantic v2 installed
- [ ] Basic FastAPI app with `/api/health` endpoint
- [ ] CORS middleware configured
- [ ] `.env.example` created (empty for v1.0)
- [ ] `uvicorn app.main:app --reload` starts server on port 8000
- [ ] `/api/health` returns `{"status": "healthy"}`

**Implementation Steps:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn[standard] pandas numpy yfinance pydantic
pip install pytest pytest-asyncio httpx
```

**Verification:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
# Open http://localhost:8000/api/health - should return JSON
# Open http://localhost:8000/docs - should show Swagger UI
```

---

### Task 1.3: Git Repository Setup

**Files:** `.gitignore`, `README.md` (update)

**Acceptance Criteria:**
- [ ] `.gitignore` includes Node.js and Python patterns
- [ ] Initial commit made with scaffolding
- [ ] README.md updated with setup instructions
- [ ] Remote repository linked (if applicable)

**Verification:**
```bash
git status
git add .
git commit -m "Initial project scaffolding (frontend + backend)"
```

---

## Phase 2: Backend Core

**Goal:** Implement core backend services and data models  
**Duration:** 3-4 days  
**Priority:** P0

### Task 2.1: Pydantic Models

**Files:** `backend/app/models/holding.py`, `backend/app/models/portfolio.py`, `backend/app/models/analysis.py`, `backend/app/models/common.py`

**Acceptance Criteria:**
- [ ] `Holding` model with validation (symbol, quantity, purchase_price, purchase_date, asset_class)
- [ ] `PortfolioAnalysisRequest` model (list of holdings)
- [ ] `Warning` model with severity levels (low, medium, high, critical)
- [ ] `Recommendation` model with action types (buy, sell, hold)
- [ ] `BlindSpot` model with confidence score
- [ ] `PortfolioAnalysis` response model (complete analysis)
- [ ] All models have example data in `json_schema_extra`
- [ ] Unit tests for model validation (invalid data rejected)

**Implementation:**
```python
# backend/app/models/holding.py
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, Literal

class Holding(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    quantity: float = Field(..., gt=0)
    purchase_price: float = Field(..., gt=0)
    purchase_date: Optional[date] = None
    asset_class: Literal["stock", "etf", "crypto", "mutual_fund"] = "stock"
```

**Verification:**
```bash
cd backend
pytest tests/test_models/ -v
# All model validation tests should pass
```

---

### Task 2.2: Market Data Service

**Files:** `backend/app/services/market_data_service.py`, `backend/app/utils/exceptions.py`

**Acceptance Criteria:**
- [ ] `MarketDataService` class implemented
- [ ] `get_prices(symbols: list[str])` method fetches from yfinance
- [ ] Price caching with 15-minute TTL
- [ ] Error handling for invalid symbols
- [ ] Rate limit handling (retry logic)
- [ ] Unit tests with mocked yfinance
- [ ] Integration test with real yfinance calls (limited)

**Implementation:**
```python
# backend/app/services/market_data_service.py
import yfinance as yf
from datetime import datetime, timedelta

class MarketDataService:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 900  # 15 minutes
    
    async def get_prices(self, symbols: list[str]) -> dict[str, float]:
        # Check cache first
        # Fetch from yfinance if expired
        # Handle errors gracefully
        pass
```

**Verification:**
```bash
cd backend
pytest tests/test_services/test_market_data.py -v
# Test price fetching, caching, error handling
```

---

### Task 2.3: Portfolio Service

**Files:** `backend/app/services/portfolio_service.py`, `backend/app/core/allocation.py`

**Acceptance Criteria:**
- [ ] `PortfolioService` class implemented
- [ ] `analyze(holdings)` method returns complete analysis
- [ ] Total value calculation (quantity × current price)
- [ ] Cost basis calculation (quantity × purchase_price)
- [ ] Gain/loss calculation (absolute and percentage)
- [ ] Asset allocation calculation (by asset class)
- [ ] Sector allocation calculation (by sector)
- [ ] Unit tests for all calculations
- [ ] Integration test with sample portfolio

**Implementation:**
```python
# backend/app/services/portfolio_service.py
class PortfolioService:
    def __init__(self, market_data_service: MarketDataService):
        self.market_data = market_data_service
    
    async def analyze(self, holdings: list[Holding]) -> PortfolioAnalysis:
        # Fetch prices
        # Calculate total value
        # Compute allocations
        # Generate warnings
        # Detect blind spots
        # Generate recommendations
        pass
```

**Verification:**
```bash
cd backend
pytest tests/test_services/test_portfolio.py -v
# Test with sample portfolio data
```

---

### Task 2.4: Risk Service

**Files:** `backend/app/services/risk_service.py`, `backend/app/core/scoring.py`

**Acceptance Criteria:**
- [ ] `RiskService` class implemented
- [ ] `calculate_risk_score(holdings)` returns score 0-100
- [ ] Concentration risk calculation (0-50 points)
- [ ] Volatility risk calculation (0-30 points)
- [ ] Correlation risk calculation (0-20 points)
- [ ] Warning generation based on thresholds:
  - Sector >25% (warning), >40% (critical)
  - Single stock >10% (warning), >20% (critical)
- [ ] Risk breakdown by category
- [ ] Unit tests for scoring algorithm
- [ ] Edge case tests (empty portfolio, single holding)

**Implementation:**
```python
# backend/app/services/risk_service.py
class RiskService:
    def calculate_risk_score(self, holdings: list[Holding], prices: dict) -> tuple[int, dict]:
        # Calculate concentration risk
        # Calculate volatility risk
        # Calculate correlation risk
        # Return composite score + breakdown
        pass
    
    def generate_warnings(self, holdings: list[Holding], allocation: dict) -> list[Warning]:
        # Check sector concentration
        # Check single stock concentration
        # Check asset class imbalance
        pass
```

**Verification:**
```bash
cd backend
pytest tests/test_services/test_risk.py -v
# Test scoring accuracy, warning thresholds
```

---

## Phase 3: ML Pipeline

**Goal:** Implement blind spot detection and recommendation generation  
**Duration:** 2-3 days  
**Priority:** P0

### Task 3.1: Blind Spot Service

**Files:** `backend/app/services/blind_spot_service.py`, `backend/app/core/correlation.py`

**Acceptance Criteria:**
- [ ] `BlindSpotService` class implemented
- [ ] Hidden sector concentration detection (3+ holdings, correlation >0.7)
- [ ] Style concentration detection (>80% in single style)
- [ ] Geographic concentration detection (>70% in single region)
- [ ] Market cap concentration detection (>75% in single category)
- [ ] Confidence score calculation (0-100%)
- [ ] Correlation matrix calculation (Pearson coefficient)
- [ ] Unit tests for detection rules
- [ ] Integration test with sample portfolio

**Implementation:**
```python
# backend/app/services/blind_spot_service.py
class BlindSpotService:
    def detect(self, holdings: list[Holding], prices_history: dict) -> list[BlindSpot]:
        blind_spots = []
        
        # Rule 1: Hidden sector concentration
        sector_holdings = self.group_by_sector(holdings)
        for sector, holdings_list in sector_holdings.items():
            if len(holdings_list) >= 3:
                corr = self.calculate_correlation(holdings_list, prices_history)
                if corr > 0.7:
                    blind_spots.append(BlindSpot(...))
        
        # Rule 2: Style concentration
        # Rule 3: Geographic concentration
        # Rule 4: Market cap concentration
        
        return blind_spots
```

**Verification:**
```bash
cd backend
pytest tests/test_services/test_blind_spot.py -v
# Test detection rules with various portfolio scenarios
```

---

### Task 3.2: Recommendation Service

**Files:** `backend/app/services/recommendation_service.py`

**Acceptance Criteria:**
- [ ] `RecommendationService` class implemented
- [ ] `generate(holdings, target_allocation)` returns prioritized recommendations
- [ ] Over-exposure detection (find positions > target)
- [ ] Sell recommendation generation (symbol, quantity, reason)
- [ ] Buy recommendation generation (for under-weight sectors)
- [ ] Priority calculation (1-10, 1=highest)
- [ ] Expected impact estimation (risk score reduction)
- [ ] ETF suggestions for sector exposure
- [ ] Unit tests for recommendation logic
- [ ] Integration test with sample portfolio

**Implementation:**
```python
# backend/app/services/recommendation_service.py
class RecommendationService:
    def generate(self, holdings: list[Holding], target_allocation: dict = None) -> list[Recommendation]:
        recommendations = []
        
        # Find over-exposed positions
        over_exposed = self.find_over_exposure(holdings)
        
        # Generate sell recommendations
        for position in over_exposed:
            sell_qty = self.calculate_sell_quantity(position)
            recommendations.append(Recommendation(
                action="sell",
                symbol=position.symbol,
                quantity=sell_qty,
                reason=f"Reduce {position.sector} exposure",
                priority=self.calculate_priority(position),
                expected_impact=f"Reduce risk score by {self.estimate_impact(position)} points"
            ))
        
        # Generate buy recommendations for under-weight sectors
        # Sort by priority
        return sorted(recommendations, key=lambda r: r.priority)
```

**Verification:**
```bash
cd backend
pytest tests/test_services/test_recommendation.py -v
# Test recommendation generation, prioritization
```

---

## Phase 4: Backend API

**Goal:** Implement REST API endpoints  
**Duration:** 2-3 days  
**Priority:** P0

### Task 4.1: API Routes

**Files:** `backend/app/api/v1/portfolio.py`, `backend/app/api/v1/analysis.py`, `backend/app/api/v1/market.py`, `backend/app/api/v1/health.py`, `backend/app/main.py`

**Acceptance Criteria:**
- [ ] `POST /api/v1/analyze` endpoint implemented
- [ ] `GET /api/v1/risk-score` endpoint implemented
- [ ] `GET /api/v1/recommendations` endpoint implemented
- [ ] `POST /api/v1/blind-spots` endpoint implemented
- [ ] `GET /api/v1/prices` endpoint implemented
- [ ] `GET /api/v1/prices/{symbol}` endpoint implemented
- [ ] `GET /api/health` endpoint implemented
- [ ] All endpoints return proper JSON responses
- [ ] Error handling returns proper HTTP status codes
- [ ] Request validation (400 for invalid input)
- [ ] Swagger UI documentation auto-generated
- [ ] Integration tests for all endpoints

**Implementation:**
```python
# backend/app/api/v1/portfolio.py
from fastapi import APIRouter, HTTPException
from app.models.portfolio import PortfolioAnalysisRequest, PortfolioAnalysis
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/api/v1", tags=["portfolio"])

@router.post("/analyze", response_model=PortfolioAnalysis)
async def analyze_portfolio(request: PortfolioAnalysisRequest):
    """Analyze portfolio holdings and return comprehensive analysis."""
    try:
        portfolio_service = PortfolioService(...)
        return await portfolio_service.analyze(request.holdings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Verification:**
```bash
cd backend
pytest tests/test_api/ -v
# Test all endpoints with various inputs
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"holdings": [{"symbol": "AAPL", "quantity": 50, "purchase_price": 150.00}]}'
# Should return complete analysis JSON
```

---

### Task 4.2: Error Handling & Validation

**Files:** `backend/app/api/deps.py`, `backend/app/utils/exceptions.py`

**Acceptance Criteria:**
- [ ] Custom exception classes (InvalidSymbolError, RateLimitError, etc.)
- [ ] Global exception handler (FastAPI exception handlers)
- [ ] Consistent error response format
- [ ] Input validation middleware
- [ ] Symbol validation (check against yfinance)
- [ ] Request size limits
- [ ] Rate limiting (100 requests/minute)
- [ ] Unit tests for error scenarios

**Verification:**
```bash
cd backend
pytest tests/test_api/test_error_handling.py -v
# Test invalid inputs, error responses
```

---

## Phase 5: Frontend Core

**Goal:** Implement core frontend pages and components  
**Duration:** 4-5 days  
**Priority:** P0

### Task 5.1: Portfolio Context & State

**Files:** `frontend/context/PortfolioContext.tsx`, `frontend/hooks/usePortfolio.ts`, `frontend/types/portfolio.ts`

**Acceptance Criteria:**
- [ ] `PortfolioContext` provider implemented
- [ ] Holdings state managed in context
- [ ] localStorage persistence (save/load)
- [ ] `addHolding(symbol, quantity, purchasePrice)` function
- [ ] `updateHolding(symbol, updates)` function
- [ ] `removeHolding(symbol)` function
- [ ] `importHoldings(holdings[])` function
- [ ] `clearPortfolio()` function
- [ ] `refreshPrices()` function (API call)
- [ ] `usePortfolio()` hook for consuming context
- [ ] Auto-save on every mutation
- [ ] Load from localStorage on app initialization

**Implementation:**
```typescript
// frontend/context/PortfolioContext.tsx
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

export const PortfolioProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // State management
  // localStorage persistence
  // Context provider
};
```

**Verification:**
```bash
cd frontend
npm test -- tests/context/PortfolioContext.test.tsx
# Test state mutations, localStorage persistence
```

---

### Task 5.2: Dashboard Page

**Files:** `frontend/app/page.tsx`, `frontend/components/portfolio/PortfolioCard.tsx`, `frontend/components/portfolio/AllocationChart.tsx`, `frontend/components/portfolio/HoldingsTable.tsx`

**Acceptance Criteria:**
- [ ] Dashboard page displays total portfolio value
- [ ] PortfolioCard shows value, daily change, risk score
- [ ] AllocationChart displays pie chart (asset class)
- [ ] AllocationChart displays bar chart (sectors)
- [ ] HoldingsTable shows top 10 holdings
- [ ] Real-time price updates (15-min intervals)
- [ ] Loading states (skeleton loaders)
- [ ] Empty state (no holdings → prompt to import)
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Unit tests for components

**Implementation:**
```typescript
// frontend/app/page.tsx
export default function DashboardPage() {
  const { holdings, totalValue, refreshPrices } = usePortfolio();
  const { data: analysis, loading } = useAnalysis(holdings);
  
  if (holdings.length === 0) {
    return <EmptyState onImport={() => router.push('/import')} />;
  }
  
  return (
    <div>
      <PortfolioCard totalValue={totalValue} riskScore={analysis?.risk_score} />
      <AllocationChart allocation={analysis?.allocation} />
      <HoldingsTable holdings={holdings.slice(0, 10)} />
    </div>
  );
}
```

**Verification:**
```bash
cd frontend
npm run dev
# Open http://localhost:3000
# Verify dashboard renders with sample data
# Check responsive design (resize browser)
```

---

### Task 5.3: Import Page

**Files:** `frontend/app/import/page.tsx`, `frontend/components/portfolio/ImportWizard.tsx`, `frontend/components/portfolio/CSVUploader.tsx`, `frontend/components/portfolio/HoldingForm.tsx`

**Acceptance Criteria:**
- [ ] Import page with wizard flow
- [ ] CSVUploader component (drag-and-drop)
- [ ] CSV parsing and validation
- [ ] CSVPreview component (show parsed data before import)
- [ ] HoldingForm for manual entry
- [ ] Symbol validation (API call to backend)
- [ ] Error messages for invalid data
- [ ] ImportSummary confirmation before save
- [ ] Success confirmation after import
- [ ] Unit tests for CSV parsing, validation

**Implementation:**
```typescript
// frontend/app/import/page.tsx
export default function ImportPage() {
  const [step, setStep] = useState<'upload' | 'preview' | 'confirm'>('upload');
  const [parsedHoldings, setParsedHoldings] = useState<Holding[]>([]);
  const { importHoldings } = usePortfolio();
  
  const handleCSVUpload = (file: File) => {
    // Parse CSV
    // Validate symbols
    // Set parsedHoldings
    setStep('preview');
  };
  
  const handleImport = () => {
    importHoldings(parsedHoldings);
    setStep('confirm');
  };
  
  return <ImportWizard step={step} onUpload={handleCSVUpload} onImport={handleImport} />;
}
```

**Verification:**
```bash
cd frontend
npm run dev
# Open http://localhost:3000/import
# Test CSV upload with sample file
# Test manual entry form
# Verify import saves to localStorage
```

---

### Task 5.4: Holdings Page

**Files:** `frontend/app/holdings/page.tsx`, `frontend/components/portfolio/HoldingsTable.tsx`, `frontend/components/portfolio/EditHoldingModal.tsx`, `frontend/components/portfolio/DeleteConfirmation.tsx`

**Acceptance Criteria:**
- [ ] HoldingsTable displays all holdings
- [ ] Sorting by symbol, quantity, value, performance
- [ ] Filtering by sector, asset class
- [ ] EditHoldingModal for editing positions
- [ ] DeleteConfirmation for removing positions
- [ ] Real-time price updates
- [ ] Performance calculation per holding
- [ ] Bulk actions (select multiple, delete)
- [ ] Responsive table design
- [ ] Unit tests for table, modals

**Verification:**
```bash
cd frontend
npm run dev
# Open http://localhost:3000/holdings
# Test sorting, filtering
# Test edit/delete actions
```

---

## Phase 6: Frontend Features

**Goal:** Implement analysis and settings pages  
**Duration:** 3-4 days  
**Priority:** P0

### Task 6.1: Analysis Page

**Files:** `frontend/app/analysis/page.tsx`, `frontend/components/analysis/RiskGauge.tsx`, `frontend/components/analysis/WarningBanner.tsx`, `frontend/components/analysis/BlindSpotCard.tsx`, `frontend/components/analysis/RecommendationList.tsx`

**Acceptance Criteria:**
- [ ] RiskGauge displays score 0-100 (color-coded)
- [ ] WarningList displays all warnings (severity-coded)
- [ ] BlindSpotCard shows AI-detected blind spots
- [ ] RecommendationList shows prioritized recommendations
- [ ] CorrelationMatrix heatmap (optional, P1)
- [ ] SectorExposureChart detailed breakdown
- [ ] Loading states during analysis
- [ ] Error handling (API failures)
- [ ] Refresh button (re-run analysis)
- [ ] Unit tests for components

**Implementation:**
```typescript
// frontend/app/analysis/page.tsx
export default function AnalysisPage() {
  const { holdings } = usePortfolio();
  const { data: analysis, loading, error, refresh } = useAnalysis(holdings);
  
  if (loading) return <AnalysisSkeleton />;
  if (error) return <ErrorState onRetry={refresh} />;
  
  return (
    <div>
      <RiskGauge score={analysis.risk_score} breakdown={analysis.risk_breakdown} />
      <WarningList warnings={analysis.warnings} />
      <BlindSpotList blindSpots={analysis.blind_spots} />
      <RecommendationList recommendations={analysis.recommendations} />
    </div>
  );
}
```

**Verification:**
```bash
cd frontend
npm run dev
# Open http://localhost:3000/analysis
# Verify analysis displays correctly
# Test with various portfolio scenarios (concentrated, diversified)
```

---

### Task 6.2: Settings Page

**Files:** `frontend/app/settings/page.tsx`, `frontend/components/settings/TargetAllocationForm.tsx`, `frontend/components/settings/DataExport.tsx`, `frontend/components/settings/ClearPortfolio.tsx`

**Acceptance Criteria:**
- [ ] TargetAllocationForm for setting desired allocation
- [ ] RiskToleranceSelector (conservative/moderate/aggressive)
- [ ] DataExport downloads portfolio as CSV
- [ ] ClearPortfolio with confirmation dialog
- [ ] AppInfo shows version, disclaimer
- [ ] Settings persist to localStorage
- [ ] Investment advice disclaimer visible
- [ ] Unit tests for forms, export

**Verification:**
```bash
cd frontend
npm run dev
# Open http://localhost:3000/settings
# Test target allocation form
# Test CSV export
# Test clear portfolio
```

---

### Task 6.3: Layout & Navigation

**Files:** `frontend/app/layout.tsx`, `frontend/components/layout/Header.tsx`, `frontend/components/layout/Navigation.tsx`, `frontend/components/layout/Footer.tsx`

**Acceptance Criteria:**
- [ ] Header with logo, app title
- [ ] Navigation with links to all pages
- [ ] Active page highlighting
- [ ] Mobile-responsive navigation (hamburger menu)
- [ ] Footer with disclaimer, links
- [ ] Consistent styling across pages
- [ ] Dark mode support (optional, P1)
- [ ] Unit tests for navigation

**Verification:**
```bash
cd frontend
npm run dev
# Navigate between all pages
# Test mobile navigation (resize browser)
```

---

## Phase 7: Integration

**Goal:** Connect frontend to backend, error handling, loading states  
**Duration:** 2-3 days  
**Priority:** P0

### Task 7.1: API Client

**Files:** `frontend/lib/api.ts`, `frontend/hooks/useAnalysis.ts`, `frontend/hooks/usePrices.ts`

**Acceptance Criteria:**
- [ ] `api.ts` utility with fetch wrapper
- [ ] Base URL from `NEXT_PUBLIC_API_URL`
- [ ] Error handling (network errors, API errors)
- [ ] Request/response typing
- [ ] `useAnalysis(holdings)` hook (POST /api/v1/analyze)
- [ ] `usePrices(symbols)` hook (GET /api/v1/prices)
- [ ] Loading states
- [ ] Error states
- [ ] SWR caching (optional)
- [ ] Unit tests for API client

**Implementation:**
```typescript
// frontend/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function analyzePortfolio(holdings: Holding[]): Promise<PortfolioAnalysis> {
  const response = await fetch(`${API_BASE}/api/v1/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ holdings }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail?.message || 'Analysis failed');
  }
  
  return response.json();
}

export async function getPrices(symbols: string[]): Promise<Record<string, number>> {
  const response = await fetch(`${API_BASE}/api/v1/prices?symbols=${symbols.join(',')}`);
  if (!response.ok) throw new Error('Price fetch failed');
  const data = await response.json();
  return data.prices;
}
```

**Verification:**
```bash
cd frontend
npm test -- tests/lib/api.test.ts
# Test API calls with mocked fetch
```

---

### Task 7.2: CORS & Environment Configuration

**Files:** `backend/app/main.py` (CORS config), `frontend/.env.local`, `backend/.env`

**Acceptance Criteria:**
- [ ] Backend CORS configured for frontend URL
- [ ] Frontend `.env.local` with `NEXT_PUBLIC_API_URL`
- [ ] Development environment (localhost:3000 → localhost:8000)
- [ ] Production environment (Vercel → Railway)
- [ ] Environment variables documented in README
- [ ] CORS test successful (no console errors)

**Verification:**
```bash
# Start backend
cd backend && uvicorn app.main:app --reload

# Start frontend in separate terminal
cd frontend && npm run dev

# Open http://localhost:3000
# Open browser dev tools → Network tab
# Verify API calls succeed (no CORS errors)
```

---

### Task 7.3: Error Handling & Loading States

**Files:** `frontend/components/ui/ErrorBanner.tsx`, `frontend/components/ui/LoadingSpinner.tsx`, `frontend/components/ui/Skeleton.tsx`

**Acceptance Criteria:**
- [ ] ErrorBanner component for API errors
- [ ] LoadingSpinner for async operations
- [ ] Skeleton loaders for charts, tables
- [ ] User-friendly error messages
- [ ] Retry buttons for failed operations
- [ ] Timeout handling (30-second timeout)
- [ ] Network error detection
- [ ] Unit tests for error components

**Verification:**
```bash
cd frontend
npm run dev
# Stop backend server
# Open http://localhost:3000/analysis
# Verify error banner displays
# Restart backend, verify retry works
```

---

## Phase 8: Testing & Verification

**Goal:** Comprehensive testing, runtime verification, deployment  
**Duration:** 3-4 days  
**Priority:** P0

### Task 8.1: Frontend Unit Tests

**Files:** `frontend/tests/**/*.test.tsx`, `frontend/tests/**/*.test.ts`

**Acceptance Criteria:**
- [ ] Component tests for all pages
- [ ] Hook tests for custom hooks
- [ ] Utility function tests
- [ ] Context tests (PortfolioContext)
- [ ] API client tests
- [ ] Test coverage >80%
- [ ] `npm test` passes
- [ ] CI configuration (GitHub Actions, optional)

**Verification:**
```bash
cd frontend
npm test -- --coverage
# Check coverage report (>80%)
# All tests should pass
```

---

### Task 8.2: Backend Unit Tests

**Files:** `backend/tests/test_services/*.py`, `backend/tests/test_api/*.py`, `backend/tests/test_core/*.py`

**Acceptance Criteria:**
- [ ] Service layer tests (portfolio, risk, blind spot, recommendation)
- [ ] API endpoint tests (all endpoints)
- [ ] Model validation tests
- [ ] Core calculation tests (allocation, correlation, scoring)
- [ ] Test coverage >90%
- [ ] `pytest` passes
- [ ] CI configuration (GitHub Actions, optional)

**Verification:**
```bash
cd backend
pytest --cov=app --cov-report=html
# Check coverage report (>90%)
# All tests should pass
```

---

### Task 8.3: Integration Tests

**Files:** `backend/tests/test_integration/`, `frontend/tests/integration/`

**Acceptance Criteria:**
- [ ] End-to-end portfolio import flow
- [ ] End-to-end analysis flow
- [ ] API integration tests (frontend → backend)
- [ ] Market data integration tests (backend → yfinance)
- [ ] Error scenario tests (invalid symbols, network failures)
- [ ] Performance tests (analysis <5 seconds)
- [ ] All integration tests pass

**Verification:**
```bash
# Backend integration tests
cd backend
pytest tests/test_integration/ -v

# Frontend integration tests
cd frontend
npm test -- tests/integration/
```

---

### Task 8.4: Runtime Verification

**Files:** N/A (manual testing)

**Acceptance Criteria:**
- [ ] Dev server runs without errors (`npm run dev`, `uvicorn`)
- [ ] Dashboard loads in <2 seconds
- [ ] Portfolio analysis completes in <5 seconds
- [ ] All pages accessible (no 404s)
- [ ] Charts render correctly (no blank spaces)
- [ ] Responsive design works (mobile, tablet, desktop)
- [ ] No console errors in browser dev tools
- [ ] API endpoints return valid JSON
- [ ] CORS configured correctly (no errors)
- [ ] Browser compatibility (Chrome, Firefox, Safari, Edge)

**Verification Protocol:**
```bash
# 1. Start backend
cd backend && uvicorn app.main:app --reload

# 2. Start frontend (separate terminal)
cd frontend && npm run dev

# 3. Open browser to http://localhost:3000
# 4. Navigate to all pages:
#    - / (Dashboard)
#    - /import
#    - /holdings
#    - /analysis
#    - /settings
# 5. Open dev tools → Console (verify no errors)
# 6. Open dev tools → Network (verify API calls succeed)
# 7. Resize browser (verify responsive design)
# 8. Test with sample portfolio data
```

**Screenshots Required:**
- [ ] Dashboard with sample portfolio
- [ ] Import page with CSV upload
- [ ] Holdings table
- [ ] Analysis page with warnings
- [ ] Settings page
- [ ] Mobile view (responsive)

---

### Task 8.5: Deployment

**Files:** `frontend/vercel.json` (optional), `backend/railway.toml` (optional)

**Acceptance Criteria:**
- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Railway
- [ ] Production URLs configured
- [ ] CORS updated for production domains
- [ ] Environment variables set in Vercel/Railway
- [ ] Health check passes (`/api/health`)
- [ ] Production testing (all pages accessible)
- [ ] HTTPS enabled (automatic on Vercel/Railway)

**Deployment Steps:**

**Frontend (Vercel):**
```bash
cd frontend
# Connect GitHub repo to Vercel
# Set environment variable: NEXT_PUBLIC_API_URL=https://your-backend.railway.app
# Deploy
vercel --prod
```

**Backend (Railway):**
```bash
cd backend
# Connect GitHub repo to Railway
# Deploy
railway up
# Or auto-deploy on push to main
```

**Verification:**
```bash
# Test production deployment
curl https://your-app.vercel.app
curl https://your-backend.railway.app/api/health

# Open production URL in browser
# Verify all pages work
# Check console for errors
```

---

## Task Dependencies

```
Phase 1 (Setup)
├── 1.1 Frontend Scaffolding
├── 1.2 Backend Scaffolding
└── 1.3 Git Repository Setup

Phase 2 (Backend Core) - depends on Phase 1
├── 2.1 Pydantic Models
├── 2.2 Market Data Service
├── 2.3 Portfolio Service
└── 2.4 Risk Service

Phase 3 (ML Pipeline) - depends on Phase 2
├── 3.1 Blind Spot Service
└── 3.2 Recommendation Service

Phase 4 (Backend API) - depends on Phases 2, 3
├── 4.1 API Routes
└── 4.2 Error Handling & Validation

Phase 5 (Frontend Core) - depends on Phase 1
├── 5.1 Portfolio Context & State
├── 5.2 Dashboard Page
├── 5.3 Import Page
└── 5.4 Holdings Page

Phase 6 (Frontend Features) - depends on Phase 5
├── 6.1 Analysis Page
├── 6.2 Settings Page
└── 6.3 Layout & Navigation

Phase 7 (Integration) - depends on Phases 4, 6
├── 7.1 API Client
├── 7.2 CORS & Environment Configuration
└── 7.3 Error Handling & Loading States

Phase 8 (Testing & Verification) - depends on all phases
├── 8.1 Frontend Unit Tests
├── 8.2 Backend Unit Tests
├── 8.3 Integration Tests
├── 8.4 Runtime Verification
└── 8.5 Deployment
```

---

## Acceptance Criteria Summary (MVP)

**MVP is complete when ALL tasks are verified:**

### Core Functionality
- [ ] User can import portfolio via CSV upload (Task 5.3)
- [ ] User can manually add/edit/remove holdings (Task 5.4)
- [ ] Asset allocation pie chart displays correctly (Task 5.2)
- [ ] Sector allocation bar chart displays correctly (Task 5.2)
- [ ] Top 10 holdings table shows correct data (Task 5.2)
- [ ] Over-exposure warnings trigger at >25% sector concentration (Task 2.4)
- [ ] Over-exposure warnings trigger at >10% single stock (Task 2.4)
- [ ] Risk score (0-100) calculated and displayed (Task 6.1)
- [ ] Blind spot detection identifies concentration risks (Task 3.1)
- [ ] Rebalancing recommendations generated (Task 3.2)

### Technical Requirements
- [ ] Real-time price updates working (15-min intervals) (Task 5.2)
- [ ] Portfolio analysis completes in <5 seconds (Task 8.4)
- [ ] Dashboard loads in <2 seconds (Task 8.4)
- [ ] Responsive design (mobile, tablet, desktop) (Task 5.2, 6.3)
- [ ] No console errors in browser dev tools (Task 8.4)
- [ ] API endpoints return valid JSON responses (Task 4.1)
- [ ] HTTPS enabled in production (Task 8.5)
- [ ] Investment advice disclaimer visible (Task 6.2)

### Deployment
- [ ] Frontend deployed to Vercel (production URL) (Task 8.5)
- [ ] Backend deployed to Railway (production URL) (Task 8.5)
- [ ] CORS configured correctly (Task 7.2)
- [ ] No critical security vulnerabilities (basic scan) (Task 8.4)
- [ ] Accessible online (tested on multiple browsers) (Task 8.4)

### Documentation
- [ ] README.md updated with setup instructions (Task 1.3)
- [ ] API documentation available (Swagger UI) (Task 4.1)
- [ ] User guide for CSV import format (Task 5.3)

### Testing
- [ ] Frontend unit tests passing (>80% coverage) (Task 8.1)
- [ ] Backend unit tests passing (>90% coverage) (Task 8.2)
- [ ] Integration tests passing (Task 8.3)
- [ ] Runtime verification complete (Task 8.4)

---

## Handoff Checklist (Tony → Peter)

- [x] ARCH.md complete with all sections
- [x] TASKS.md complete with bounded tasks (max 2-3 files per task)
- [x] All acceptance criteria explicit and testable
- [x] Architecture aligns with REQ.md functional requirements
- [x] Hybrid architecture properly documented (Next.js + FastAPI)
- [ ] Peter acknowledges receipt and starts Phase 1

---

**Next Action:** Peter (Developer) begins Phase 1: Project Setup  
**Estimated Start:** Immediate  
**Model:** ollama/qwen3-coder-next:cloud (specialized coding model)
