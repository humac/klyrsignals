# KlyrSignals

Net worth and investment blind-spot analysis powered by SnapTrade + AI.

## What It Does

KlyrSignals connects to your Wealthsimple (and other brokerages) via SnapTrade to:

1. **Aggregate** all accounts and holdings into a unified view
2. **Enrich** positions with 36-month historical price data and ETF look-through analysis
3. **Detect blind spots** via concentration auditing and correlation analysis
4. **Generate AI signals** identifying risks you might miss: home bias, hidden twins, sector concentration

### Example Signal

> **Signal:** You are 45% exposed to the Canadian Banking sector across equity and debt.
> High interest rate sensitivity detected.

## Architecture

```
FastAPI (REST API)
  ├── /services/aggregator    → SnapTrade OAuth, holdings sync, ticker normalization
  ├── /services/auditor       → Concentration audit, correlation engine
  ├── /services/ai            → LLM prompt engineering, multi-provider connector
  └── /routes                 → REST endpoints

Streamlit Dashboard (UI)
  ├── Geographic Treemap      → Plotly treemap (size=value, color=region)
  ├── Sector Sunburst         → Multi-level (Total → Asset Class → Sector)
  └── Risk Heatmap            → Correlation matrix visualization

PostgreSQL + TimescaleDB      → Positions, snapshots, price history
Redis                         → Caching layer
```

## Quick Start

```bash
# 1. Copy env and configure
cp .env.example .env
# Edit .env with your SnapTrade credentials and AI provider keys

# 2. Start infrastructure
docker-compose up -d db redis

# 3. Run migrations
alembic upgrade head

# 4. Start the API
uvicorn app.main:app --reload

# 5. Start the dashboard
streamlit run ui/app.py
```

Or run everything with Docker:

```bash
docker-compose up --build
```

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0
- **Data:** Pandas, NumPy, yfinance
- **Database:** PostgreSQL 16 + TimescaleDB
- **AI:** OpenAI GPT-4o / Anthropic Claude / Ollama (local fallback)
- **Dashboard:** Streamlit + Plotly
- **Security:** AES-256-GCM token encryption, PII stripping

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/users/` | Create user |
| POST | `/api/v1/connections/connect` | Start SnapTrade connection flow |
| POST | `/api/v1/connections/{user_id}/sync` | Sync accounts & positions |
| GET | `/api/v1/positions/{user_id}` | Portfolio summary |
| POST | `/api/v1/analysis/{user_id}/run` | Run full analysis pipeline |
| GET | `/api/v1/analysis/{user_id}/latest` | Get latest analysis |
| GET | `/health` | Health check |

## Running Tests

```bash
pytest tests/ -v
```

## Security

- No raw bank credentials stored
- SnapTrade tokens encrypted with AES-256-GCM at rest
- PII stripped before sending data to cloud AI providers
- Fully self-hostable on Proxmox/Docker
