# KlyrSignals Coding Standards

## Language & Runtime
- Python 3.12+ with type hints on all public functions
- FastAPI for HTTP layer, Pydantic v2 for all data models
- async/await for all I/O-bound operations

## Data Models (Pydantic)
- All models inherit from a `BaseSchema` with `model_config = ConfigDict(strict=True)`
- Monetary values stored as `int` (cents) — never float dollars
- Use `Decimal` for intermediate financial calculations, convert to cents for storage
- All timestamps as `datetime` with UTC timezone (timezone-aware)
- Enums for fixed categories (Currency, AssetClass, Region)

## Database
- PostgreSQL 16 with TimescaleDB extension for time-series
- Alembic for migrations, SQLAlchemy 2.0 async engine
- All tables have `created_at` and `updated_at` timestamps
- Hypertables for snapshot/time-series data

## Error Handling
- Custom exception hierarchy rooted at `KlyrError`
- All external API calls wrapped in try/except with structured logging
- Never expose internal errors to clients — map to HTTP status codes

## Testing
- pytest with async support (pytest-asyncio)
- Factory pattern for test data (not fixtures with side effects)
- Integration tests use testcontainers for Postgres

## Security
- AES-256-GCM for token encryption at rest
- PII stripping before any cloud AI call
- No secrets in code — all via environment variables
- CORS restricted to configured origins only
