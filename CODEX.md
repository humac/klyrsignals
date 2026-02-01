# KlyrSignals Unified Ledger Schema

## Core Entities

### Users
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| email | VARCHAR(255) | Encrypted, unique |
| snaptrade_user_id | VARCHAR(255) | SnapTrade registered user ID |
| snaptrade_user_secret | TEXT | AES-256-GCM encrypted |
| created_at | TIMESTAMPTZ | UTC |
| updated_at | TIMESTAMPTZ | UTC |

### Connections (Brokerage Links)
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK -> Users |
| brokerage_name | VARCHAR(100) | e.g., "Wealthsimple" |
| snaptrade_authorization_id | VARCHAR(255) | SnapTrade connection ID |
| status | ENUM | active, disconnected, error |
| last_synced_at | TIMESTAMPTZ | Last successful sync |
| created_at | TIMESTAMPTZ | UTC |
| updated_at | TIMESTAMPTZ | UTC |

### Accounts
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| connection_id | UUID | FK -> Connections |
| user_id | UUID | FK -> Users |
| snaptrade_account_id | VARCHAR(255) | SnapTrade account ID |
| account_name | VARCHAR(255) | e.g., "TFSA", "RRSP" |
| account_type | VARCHAR(50) | Account registration type |
| currency | ENUM | CAD, USD |
| created_at | TIMESTAMPTZ | UTC |
| updated_at | TIMESTAMPTZ | UTC |

### Positions (Current Holdings)
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| account_id | UUID | FK -> Accounts |
| user_id | UUID | FK -> Users |
| symbol | VARCHAR(20) | Normalized ticker (e.g., VGRO.TO) |
| description | VARCHAR(255) | Security name |
| asset_class | ENUM | equity, fixed_income, cash, crypto, other |
| units | DECIMAL(18,8) | Number of shares/units |
| cost_basis_cents | BIGINT | Total cost basis in cents |
| market_value_cents | BIGINT | Current market value in cents |
| currency | ENUM | CAD, USD |
| exchange | VARCHAR(20) | Exchange (TSX, NYSE, NASDAQ) |
| last_price_cents | BIGINT | Last known price in cents |
| updated_at | TIMESTAMPTZ | UTC |

### Net Worth Snapshots (TimescaleDB Hypertable)
| Column | Type | Description |
|--------|------|-------------|
| time | TIMESTAMPTZ | Snapshot timestamp (hypertable key) |
| user_id | UUID | FK -> Users |
| total_assets_cents | BIGINT | Sum of all positions |
| total_liabilities_cents | BIGINT | Sum of all debts |
| net_worth_cents | BIGINT | Assets - Liabilities |
| breakdown_json | JSONB | Per-account breakdown |

### Sector Weights (Enrichment Cache)
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| symbol | VARCHAR(20) | Ticker |
| sector | VARCHAR(100) | GICS Sector |
| country | VARCHAR(3) | ISO country code |
| weight_pct | DECIMAL(5,2) | Weight percentage |
| source | VARCHAR(20) | yfinance, manual |
| fetched_at | TIMESTAMPTZ | When data was fetched |

### Price History (TimescaleDB Hypertable)
| Column | Type | Description |
|--------|------|-------------|
| time | TIMESTAMPTZ | Trading date (hypertable key) |
| symbol | VARCHAR(20) | Ticker |
| close_cents | BIGINT | Closing price in cents |
| volume | BIGINT | Trading volume |

### Analysis Results
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK -> Users |
| analysis_type | VARCHAR(50) | concentration, correlation, signal |
| result_json | JSONB | Structured analysis output |
| ai_summary | TEXT | LLM-generated summary |
| created_at | TIMESTAMPTZ | UTC |

## Indexes
- `positions`: Composite on (user_id, symbol)
- `net_worth_snapshots`: TimescaleDB auto-indexes on time
- `price_history`: TimescaleDB auto-indexes on time + symbol index
- `analysis_results`: (user_id, analysis_type, created_at DESC)
