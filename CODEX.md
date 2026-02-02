# CODEX: KlyrSignals "Unified Ledger" Schema

## Philosophy
The database is designed as a **Unified Ledger** capable of holding diverse asset types (Liquid Stocks, Real Estate, Crypto, Art, Liabilities) without frequent schema migrations. It uses SQLAlchemy generic types to support both PostgreSQL (Prod) and SQLite (Test).

## Core Entities

### 1. `Asset` (The Master Table)
Represents any tracking entity, whether a bank account, a house, or a loan.
- `id` (**Uuid**): Unique identifier.
- `name` (String): Display name (e.g., "Main Wealthsimple Account" or "6-Plex").
- `type` (Enum): `LIQUID`, `FIXED`, `BUSINESS`, `CRYPTO`, `LIABILITY`.
- `provider_type` (Enum): `MANUAL`, `SNAPTRADE`, `PLAID`.
- `currency` (String): e.g., 'CAD', 'USD'.
- `attributes` (**JSON**): Flexible storage for specific metadata.
  - *Real Estate Example*: `{"valuation_cents": 120000000, "proxy_ticker": "XRE.TO"}`
  - *Account Example*: `{"institution_id": "wealthsimple", "mask": "1234"}`
- `access_token_enc` (Text): **Encrypted** Access Token (Fernet). Never store raw.

### 2. `AssetHolding` (The Line Items)
Represents the specific positions held within an Asset (mostly for Liquid accounts).
- `id` (**Uuid**): Unique identifier.
- `asset_id` (**Uuid**): FK to parent Asset.
- `ticker` (String): e.g., "VFV.TO".
- `qty` (Decimal): Quantity held.
- `metadata_json` (**JSON**): e.g., `{"avg_cost_cents": 10500}`.

### 3. `NetWorthSnapshot` (Time-Series)
Analysis-ready snapshots of the portfolio at a specific point in time.
- `id` (**Uuid**): Unique identifier.
- `timestamp` (DateTime UTC): When the snapshot was taken.
- `total_assets_cents` (BigInt): Sum of all positive asset values.
- `total_liabilities_cents` (BigInt): Sum of all liability balances.
- `total_equity_cents` (BigInt): Assets - Liabilities.
- `breakdown` (**JSON**): A frozen copy of the sector/geo exposure at that time.

### 4. `TickerPriceHistory` (Market Cache)
A rolling cache of daily close prices to support the implementation of the Correlation Matrix without API throttling.
- `id` (**Uuid**): Unique identifier.
- `ticker` (String): Standardized ticker symbol.
- `date` (DateTime): Market date.
- `close_cents` (BigInt): Adjusted close price.
- **Retention**: Logic to check `date` prevents fetching if data < 24h old.

## Relationships
- **One** `Asset` **Has Many** `AssetHoldings`.
- **System** **Has Many** `NetWorthSnapshots`.
- `Asset` optionally maps to `TickerPriceHistory` via `attributes['proxy_ticker']`.
