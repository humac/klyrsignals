# KlyrSignals - AI-Powered Financial Portfolio Analyst

**KlyrSignals** is an AI-powered financial analysis platform that identifies portfolio blind spots and over-exposure risks, providing data-driven rebalancing recommendations.

![Status](https://img.shields.io/badge/status-complete-success)
![Version](https://img.shields.io/badge/version-1.5.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 What It Does

KlyrSignals analyzes your investment portfolio to:

- **Detect Blind Spots** - Identify hidden concentration risks and correlation patterns you're not seeing
- **Identify Over-Exposure** - Alert on sector, asset class, and single-stock concentration risks
- **Provide Recommendations** - Generate actionable rebalancing suggestions with priority ranking
- **Monitor Risk** - Calculate real-time portfolio health scores (0-100) with detailed breakdowns

## ✨ Key Features

### Portfolio Analysis
- **Import Portfolio**: CSV upload or manual entry for holdings
- **Real-Time Valuation**: Live market data via Yahoo Finance (yfinance)
- **Asset Allocation**: Visual breakdown by asset class, sector, and geography
- **Performance Tracking**: Cost basis, gains/losses, and returns calculation

### AI-Powered Insights
- **Blind Spot Detection**: Rules-based ML identifies hidden risks:
  - Sector concentration (>25% warning, >40% critical)
  - Single stock concentration (>10% warning, >20% critical)
  - Style drift (large-cap growth, small-cap value, etc.)
  - Correlation patterns between holdings
- **Confidence Scoring**: Each insight includes confidence level (0-100%)

### Risk Management
- **Composite Risk Score**: 0-100 score based on:
  - Concentration risk (50% weight)
  - Volatility risk (30% weight)
  - Correlation risk (20% weight)
- **Warning System**: Severity-based alerts (low, medium, high, critical)
- **Benchmark Comparison**: Compare portfolio risk to S&P 500, 60/40 portfolio

### Smart Recommendations
- **Rebalancing Actions**: Specific "sell X, buy Y" recommendations
- **Priority Ranking**: Actions sorted by risk reduction impact
- **Expected Impact**: Estimated risk score improvement for each action

## 🏗️ Architecture (Hybrid)

```
┌─────────────────┐         ┌─────────────────┐
│   Frontend      │  API    │    Backend      │
│   Next.js 16    │ ←────→  │   Python 3.12   │
│   TypeScript    │  REST   │   FastAPI       │
│   Tailwind CSS  │         │   pandas/numpy  │
│   (Vercel)      │         │   (Railway)     │
└─────────────────┘         └─────────────────┘
                                   ↓
                          ┌─────────────────┐
                          │  Market Data    │
                          │  Yahoo Finance  │
                          │  (yfinance)     │
                          └─────────────────┘
```

**Why Hybrid?**
- **Python Backend**: Leverages powerful financial libraries (pandas, numpy, yfinance) for analysis
- **Next.js Frontend**: Modern, responsive UI with real-time updates and interactive charts
- **Independent Scaling**: Frontend and backend can scale separately based on demand

## 📁 Project Structure

```
klyrsignals/
├── frontend/                 # Next.js application
│   ├── app/                  # App Router pages
│   │   ├── page.tsx          # Dashboard
│   │   ├── import/page.tsx   # Portfolio import
│   │   ├── holdings/page.tsx # Holdings management
│   │   ├── analysis/page.tsx # Risk analysis
│   │   └── settings/page.tsx # Settings
│   ├── components/           # React components
│   ├── context/              # PortfolioContext (state)
│   ├── hooks/                # Custom hooks (usePortfolio, useAnalysis)
│   ├── lib/                  # API client, utilities
│   ├── types/                # TypeScript types
│   └── package.json
├── backend/                  # Python FastAPI application
│   ├── app/
│   │   ├── main.py           # FastAPI app entry
│   │   ├── api/v1/           # API routes
│   │   │   ├── health.py     # Health check
│   │   │   ├── market.py     # Market data endpoints
│   │   │   ├── portfolio.py  # Portfolio endpoints
│   │   │   └── analysis.py   # Analysis endpoints
│   │   ├── models/           # Pydantic models
│   │   │   ├── holding.py    # Holding model
│   │   │   └── portfolio.py  # Portfolio/analysis models
│   │   ├── services/         # Business logic
│   │   │   ├── market_data_service.py  # yfinance integration
│   │   │   └── portfolio_service.py    # Portfolio analysis
│   │   └── core/             # Core algorithms
│   │       ├── allocation.py # Allocation calculations
│   │       └── scoring.py    # Risk scoring
│   ├── requirements.txt
│   └── venv/
├── docs/
│   ├── agent-workflow/       # Agent pipeline documentation
│   ├── DECISIONS.md          # Architectural decisions
│   ├── FINAL_REPORT.md       # Project closeout report
│   └── RUN_STATE.md          # Pipeline state
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+
- **Python** 3.12+
- **Git**

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Frontend will be available at [http://localhost:3000](http://localhost:3000)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Backend API will be available at [http://localhost:8000](http://localhost:8000)
Swagger docs at [http://localhost:8000/docs](http://localhost:8000/docs)

## 📊 API Endpoints

### Portfolio Analysis

**POST /api/v1/analyze**
Analyze portfolio and return comprehensive analysis.

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "holdings": [
      {"symbol": "AAPL", "quantity": 50, "purchase_price": 150.00},
      {"symbol": "MSFT", "quantity": 30, "purchase_price": 280.00}
    ]
  }'
```

**Response:**
```json
{
  "total_value": 24991.20,
  "total_cost_basis": 15900.00,
  "total_gain_loss": 9091.20,
  "risk_score": 85,
  "warnings": [...],
  "recommendations": [...],
  "blind_spots": [...]
}
```

### Risk Score

**GET /api/v1/risk-score**
Calculate portfolio risk score (0-100).

```bash
curl "http://localhost:8000/api/v1/risk-score?holdings=[{\"symbol\":\"AAPL\",\"quantity\":50,\"purchase_price\":150}]"
```

### Blind Spots

**POST /api/v1/blind-spots**
Detect hidden concentration risks.

```bash
curl -X POST http://localhost:8000/api/v1/blind-spots \
  -H "Content-Type: application/json" \
  -d '{
    "holdings": [
      {"symbol": "AAPL", "quantity": 50, "purchase_price": 150.00}
    ]
  }'
```

### Market Prices

**GET /api/v1/prices**
Get current market prices.

```bash
curl "http://localhost:8000/api/v1/prices?symbols=AAPL,MSFT,GOOGL"
```

### Health Check

**GET /api/health**
Check backend health status.

```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-28T19:00:00Z",
  "version": "1.0.0"
}
```

Full API documentation available at `/docs` (Swagger UI) when backend is running.

## ✨ Latest Features (v1.5)

### 🌙 Dark Mode
- Toggle between light and dark themes
- System preference detection (auto-switches based on OS)
- Persistent theme preference (saved to browser)
- All pages, charts, and components fully styled

### 📊 WealthSimple Import
- Auto-detect WealthSimple CSV format
- Specialized parser for WealthSimple Trade confirmations
- Handles BUY/SELL orders
- Includes commission in cost basis
- Averages multiple purchases (weighted average cost)
- Generic CSV fallback for other formats

### 🐛 Bug Fixes
- Fixed import state persistence issue (race condition in PortfolioContext)
- Improved error handling in CSV parser
- Enhanced theme toggle reliability

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/humac/klyrsignals.git
cd klyrsignals

# Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start frontend (new terminal)
cd frontend
npm install
npm run dev
```

**Access:** http://localhost:3000

### Try Dark Mode
1. Click sun/moon icon in top-right
2. Theme switches instantly
3. Reload page - preference persists

### Import WealthSimple CSV
1. Go to Import page
2. Upload WealthSimple CSV export
3. Auto-detection shows "WealthSimple" banner
4. Preview holdings
5. Click Import
6. Dashboard shows your portfolio

## 🔧 Tech Stack

### Frontend
- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS
- **Charts:** Recharts
- **State:** React Context + localStorage
- **HTTP:** fetch API
- **Deployment:** Vercel

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.12
- **Data Processing:** pandas, numpy
- **Market Data:** yfinance
- **Validation:** Pydantic v2
- **Server:** uvicorn
- **Deployment:** Railway

## 🔐 Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Backend (.env)
```env
# No API keys required for yfinance (free tier)
# Optional: Add for higher rate limits
# YAHOO_FINANCE_API_KEY=your-key
```

## 🧪 Testing

### Frontend
```bash
cd frontend
npm run build  # Build test
```

### Backend
```bash
cd backend
source venv/bin/activate
pytest  # Run unit tests
```

## 📝 Development Workflow

This project follows the **Jarvis agent workflow**:

1. **Jarvis (Intake)** - Project intake and coordination
2. **Pepper (Requirements)** - Requirements gathering and documentation
3. **Tony (Architecture)** - System design and task generation
4. **Peter (Build)** - Implementation and unit testing
5. **Heimdall (QA)** - Security audit and validation
6. **Pepper (Closeout)** - Final documentation and reporting

Agent workflow documents are in `docs/agent-workflow/`.

## 🚧 Current Status

**Version:** 1.0.0  
**Status:** ✅ **COMPLETE**  
**Pipeline:** All phases complete (Jarvis → Pepper → Tony → Peter → Heimdall → Pepper Closeout)

**Deliverables:**
- ✅ Frontend: Next.js 16 app with 5 pages (Dashboard, Import, Holdings, Analysis, Settings)
- ✅ Backend: FastAPI with 7 API endpoints
- ✅ Portfolio import (CSV + manual entry)
- ✅ Real-time market data integration (yfinance)
- ✅ Risk scoring algorithm (0-100)
- ✅ Blind spot detection (rules-based ML)
- ✅ Rebalancing recommendations
- ✅ Asset and sector allocation charts
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ localStorage persistence
- ✅ Comprehensive documentation

## 📈 Roadmap

### v1.0 - MVP ✅ (Complete)
- Portfolio import (CSV, manual)
- Asset allocation visualization
- Over-exposure detection
- Blind spot detection (rules-based)
- Risk scoring
- Rebalancing recommendations
- Web dashboard

### v1.5 - Enhanced Features ✅ COMPLETE (2026-03-01)

**Status:** ✅ PRODUCTION READY

**Features Delivered:**
- ✅ Dark Mode (theme toggle, system preference, localStorage persistence)
- ✅ WealthSimple Import (auto-detection, specialized parser, BUY/SELL handling)
- ✅ Bug fix (import persistence with isInitialized guard)

**Files Created:**
- `frontend/context/ThemeContext.tsx` - Theme provider
- `frontend/components/ThemeToggle.tsx` - Toggle button
- `frontend/lib/csv-parsers/wealthsimple.ts` - WealthSimple parser
- `frontend/lib/csv-parsers/generic.ts` - Generic parser
- `frontend/lib/csv-parsers/index.ts` - Auto-detection
- `docs/agent-workflow/CLAUDE.md` - AI instructions
- `docs/agent-workflow/GEMINI.md` - AI instructions
- `agents/tony.md` - Architect persona
- `agents/peter.md` - Developer persona
- `agents/heimdall.md` - QA persona
- `agents/pepper.md` - Analyst persona

**QA Status:** ✅ PASS (all tests passing)

### v2.0 - Production (Future)
- [ ] Broker integration (Plaid, etc.)
- [ ] Real-time price streaming (WebSocket)
- [ ] Mobile app (iOS/Android)
- [ ] Tax-loss harvesting recommendations
- [ ] Automated rebalancing execution
- [ ] Multi-user collaboration

## 🐛 Known Limitations

See `docs/agent-workflow/ISSUES.md` for known issues and limitations.

## 📄 Documentation

- [Requirements](docs/agent-workflow/REQ.md)
- [Architecture](docs/agent-workflow/ARCH.md)
- [Tasks](docs/agent-workflow/TASKS.md)
- [QA Report](docs/agent-workflow/QA.md)
- [Decisions](docs/DECISIONS.md)
- [Final Report](docs/FINAL_REPORT.md)

## 🔗 Links

- **GitHub Repository:** https://github.com/humac/klyrsignals
- **Swagger API Docs:** http://localhost:8000/docs (when backend running)

## 📄 License

MIT

## ⚠️ Disclaimer

**KlyrSignals is for informational and educational purposes only.** It is not a registered investment advisor and does not provide investment advice. All analysis and recommendations should be verified with a qualified financial professional before making investment decisions.

Past performance does not guarantee future results. Market data is provided by Yahoo Finance and may be delayed or inaccurate.

---

**Built with ❤️ using Next.js 16 + Python FastAPI**
