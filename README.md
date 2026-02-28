# KlyrSignals - AI-Powered Financial Portfolio Analyst

**AI-powered financial analysis platform that identifies portfolio blind spots and over-exposure risks.**

## 🎯 What It Does

KlyrSignals analyzes your investment portfolio using AI to:
- **Detect Blind Spots** - Hidden risks you're not seeing
- **Identify Over-Exposure** - Sector, asset class, geographic concentration
- **Provide Recommendations** - Data-driven rebalancing suggestions
- **Monitor Risk** - Real-time portfolio health scoring

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
                          │  Alpha Vantage  │
                          └─────────────────┘
```

## 📁 Project Structure

```
klyrsignals/
├── frontend/              # Next.js application
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   ├── lib/             # Utilities, hooks, types
│   └── package.json
├── backend/              # Python FastAPI application
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── analysis/    # Portfolio analysis engine
│   │   ├── ml/          # ML models for blind spots
│   │   └── data/        # Market data fetchers
│   ├── requirements.txt
│   └── pyproject.toml
├── docs/
│   ├── agent-workflow/  # Agent pipeline docs
│   ├── DECISIONS.md
│   └── RUN_STATE.md
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.12+
- API keys (Yahoo Finance, Alpha Vantage - optional)

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
# http://localhost:3000
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
# http://localhost:8000
```

## 📊 Features (v1.0 Roadmap)

### Portfolio Analysis
- [ ] Import portfolio (CSV, manual entry, broker integration)
- [ ] Asset allocation visualization
- [ ] Performance tracking (returns, volatility)
- [ ] Benchmark comparison (S&P 500, etc.)

### AI-Powered Insights
- [ ] Blind spot detection (concentration risks)
- [ ] Over-exposure alerts (sector, geography, asset class)
- [ ] Correlation analysis
- [ ] Risk scoring (0-100 portfolio health)

### Recommendations
- [ ] Rebalancing suggestions
- [ ] Tax-loss harvesting opportunities
- [ ] Diversification improvements
- [ ] Risk-adjusted optimization

### Monitoring
- [ ] Real-time portfolio updates
- [ ] Price alerts
- [ ] News impact analysis
- [ ] Earnings calendar integration

## 🔧 Tech Stack

### Frontend
- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Charts:** Recharts / Chart.js
- **State:** Zustand + SWR
- **Deployment:** Vercel

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.12
- **Data:** pandas, numpy
- **ML:** scikit-learn
- **Market Data:** yfinance, alpha-vantage
- **Database:** PostgreSQL (optional, for user portfolios)
- **Deployment:** Railway / Render

## 📈 API Endpoints

### Portfolio
- `POST /api/v1/portfolio` - Create/import portfolio
- `GET /api/v1/portfolio/:id` - Get portfolio details
- `PUT /api/v1/portfolio/:id` - Update portfolio
- `DELETE /api/v1/portfolio/:id` - Delete portfolio

### Analysis
- `GET /api/v1/portfolio/:id/analysis` - Full portfolio analysis
- `GET /api/v1/portfolio/:id/allocation` - Asset allocation
- `GET /api/v1/portfolio/:id/risk` - Risk metrics
- `GET /api/v1/portfolio/:id/blind-spots` - AI-detected blind spots

### Market Data
- `GET /api/v1/market/price/:symbol` - Current price
- `GET /api/v1/market/history/:symbol` - Historical data
- `GET /api/v1/market/news/:symbol` - Related news

## 🔐 Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Backend (.env)
```
# API Keys (optional for testing)
YAHOO_FINANCE_API_KEY=your-key
ALPHA_VANTAGE_API_KEY=your-key

# Database (optional for v1.0)
DATABASE_URL=postgresql://user:pass@localhost:5432/klyrsignals

# Security
SECRET_KEY=your-secret-key
```

## 🧪 Testing

### Frontend
```bash
cd frontend
npm test
```

### Backend
```bash
cd backend
pytest
```

## 📝 Development Workflow

This project follows the Jarvis agent workflow:

1. **Pepper (Analyst)** - Requirements gathering
2. **Tony (Architect)** - System design & architecture
3. **Peter (Developer)** - Implementation & unit tests
4. **Heimdall (QA)** - Security audit & validation
5. **Pepper (Closeout)** - Documentation & final report

Agent workflow documents are in `docs/agent-workflow/`.

## 🚧 Current Status

**Phase:** 🌱 Bootstrap  
**Pipeline:** Not started  
**Version:** 0.0.0

## 📋 Roadmap

### v1.0 - MVP (4-6 weeks)
- Portfolio import (CSV, manual)
- Basic allocation charts
- Simple over-exposure detection
- Risk scoring
- Web dashboard

### v1.5 - AI Insights (6-8 weeks)
- ML-powered blind spot detection
- Correlation analysis
- Rebalancing recommendations
- Email alerts

### v2.0 - Production (3-4 months)
- User authentication
- Multiple portfolios
- Broker integrations (Plaid, etc.)
- Mobile-responsive design
- Performance optimization

## 🔗 Links

- [GitHub Repository](https://github.com/humac/klyrsignals)
- [Requirements](docs/agent-workflow/REQ.md)
- [Architecture](docs/agent-workflow/ARCH.md)
- [Tasks](docs/agent-workflow/TASKS.md)

## 📄 License

MIT

---

**Built with ❤️ using Next.js + Python FastAPI**
