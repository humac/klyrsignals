# Github Copilot Instructions for KlyrSignals

You are an AI assistant helping a Senior Engineer build a High-Integrity Financial Dashboard.

## Critical Rules to Follow

1.  **Cents-Base Math**:
    - ALWAYS suggest integer math for money.
    - `balance_cents: int` NOT `balance: float`.
    - If you see `10.50`, correct it to `1050`.

2.  **Database Compatibility**:
    - Use `sqlalchemy.types.JSON` (not `JSONB`).
    - Use `sqlalchemy.types.Uuid` (not `postgresql.UUID`).
    - When filtering by ID, wrap strings: `.filter(Model.id == uuid.UUID(id_str))`.

3.  **Security First**:
    - If code involves an "Access Token", suggest `SecurityService.encrypt_token()`.
    - Read secrets (`FERNET_KEY`) lazily via `os.getenv()`.

4.  **Pandas usage**:
    - When generating analysis code, use vectorized operations.
    - Avoid `iterrows()` where possible.

5.  **FastAPI / Pydantic**:
    - Use Pydantic 2.0+ `BaseModel` syntax.
    - Keep Routes thin; delegate logic to `AssetManager` or `InvestmentAuditor`.
