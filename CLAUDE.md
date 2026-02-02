# KlyrSignals Coding Standards & Rules

## 1. Mathematical Precision (The "Cents" Rule)
- **NO FLOATING POINT CURRENCY**: All currency values must be stored, transported, and calculated as **Integers (Cents)**.
  - Correct: `10050` (represents $100.50)
  - Incorrect: `100.50`
- **Conversion**: Convert to float *only* at the final presentation layer (Streamlit/API Response).

## 2. Database & Schema
- **Generic Types**: Use SQLAlchemy's `JSON` and `Uuid` types instead of dialect-specific `JSONB` or `UUID` to ensure compatibility with SQLite (testing) and PostgreSQL (prod).
- **UUID Handling**: When querying by ID in SQLAlchemy, explicitly convert string strings to objects: `uuid.UUID(id_str)`.
- **Snapshots**: Never overwrite history. Always `INSERT` a new snapshot.

## 3. Security & Validation
- **Fernet Encryption**: 
  - Store tokens as `Text` columns, encrypted using `SecurityService`.
  - Load keys **lazily** (`os.getenv` inside the method/property) to allow for test environment overrides.
- **Pydantic**: Use Pydantic models for all API inputs/outputs.

## 4. Code Style & Architecture
- **Type Hinting**: Python 3.12+ type hints are mandatory.
- **Service Layer**: Business logic lives in `backend/app/services/`. API routes should only handle request/response mapping.
- **Imports**: Avoid circular imports by careful placement of Pydantic models vs ORM models.

## 5. Testing
- **SQLite Compatibility**: Ensure all models run on SQLite for fast, self-contained verification scripts.
- **Mocking**: Mock external APIs (`yfinance`) in tests using dependency injection or monkeypatching (as seen in `test_verification.py`).
