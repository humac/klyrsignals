# KlyrSignals 🇨🇦

**The Holistic Net Worth Tracker & Investment Auditor**

KlyrSignals is a self-hosted financial dashboard designed for Canadian investors with complex asset profiles (Real Estate, Holding Corps, ETFs). It goes beyond simple balance tracking to provide **Look-Through Analysis** and **Blind Spot Detection**.

## 🚀 Features

### 1. Unified Ledger
- **Flexible Asset Tracking**: Manage Liquid Assets (Wealthsimple, Questrade), Fixed Assets (Real Estate, Art), and Business holdings in a single system.
- **Cent-Based Math**: All currency calculations are performed in integers (cents) to eliminate floating-point errors.
- **Privacy First**: Zero-Knowledge architecture. Raw banking credentials are never stored. Access tokens are encrypted using **AES-256 (Fernet)**.

### 2. Investment Auditor (The "Blind Spot" Engine)
- **ETF Look-Through**: Automatically decomposes ETFs (e.g., `VFV.TO`, `XIU.TO`) into their underlying Sector and Geographic exposures using `yfinance` hooks.
- **Concentration Alerts**:
  - 🚨 **Home Bias**: Warns if Canadian exposure > 60%.
  - 🚨 **Sector Risk**: Warns if any single sector > 25%.
- **Correlation Matrix**: Uses 36-month trailing price history (and proxies like `XRE.TO` for Real Estate) to identify hidden correlations between your assets.

### 3. Time-Traveling Snapshots
- **Historical Net Worth**: The `SnapshotEngine` captures point-in-time valuations of your entire portfolio.
- **No Overwrites**: History is preserved immutable.

## 🛠 Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy (Sync).
- **Database**: PostgreSQL 16 (TimescaleDB + pgvector ready).
- **Frontend**: Streamlit (Data Visualization).
- **Services**:
  - `yfinance`: Market data & ETF composition.
  - `pandas`: Vectorized financial analysis.
  - `cryptography`: Token security.
- **Infrastructure**: Docker Compose.

## 📦 Installation & Setup

### Prerequisites
- Docker & Docker Compose
- (Optional) Python 3.12+ for local dev

### Quick Start (Docker)
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/klyrsignals.git
   cd klyrsignals
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env and set a secure FERNET_KEY
   # Generate key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

3. **Launch**:
   ```bash
   docker-compose up --build
   ```

4. **Access**:
   - Dashboard: `http://localhost:8501`
   - API Docs: `http://localhost:8000/docs`

### Local Development (No Docker)
1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
2. **Frontend**:
   ```bash
   cd frontend
   pip install -r requirements.txt
   streamlit run app.py
   ```
   *Note: Ensure `DATABASE_URL` is set in your env.*

## 📂 Project Structure

```
klyrsignals/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI Routes (Assets, Auditor)
│   │   ├── models.py     # SQLAlchemy Models (Unified Ledger)
│   │   └── services/     # Core Logic (Auditor, Snapshot, Security)
│   └── Dockerfile
├── frontend/
│   ├── pages/            # Streamlit Pages
│   ├── app.py            # Main Dashboard
│   └── utils.py          # API Client
├── docker-compose.yml
└── AGENTS.md             # AI Persona Definitions
```

## 🔐 Security

- **Encryption**: Sensitive fields (`access_token_enc`) are encrypted at rest.
- **Validation**: All inputs are validated via Pydantic schemas.
- **Isolation**: Market data is cached locally (`TickerPriceHistory`) to prevent data leakage and API throttling.

## 🧩 Documentation
- **[CODEX.md](CODEX.md)**: Database Schema & Data Dictionary.
- **[CLAUDE.md](CLAUDE.md)**: Coding Standards & Best Practices.
- **[AGENTS.md](AGENTS.md)**: AI Contributor Roles.
