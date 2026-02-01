# KlyrSignals Agent Roles

## @Architect
- **Responsibility**: System design, API contracts, data flow orchestration
- **Scope**: FastAPI route design, SnapTrade integration patterns, database schema evolution
- **Standards**: All services must be stateless. Use dependency injection via FastAPI's `Depends()`. Every external call must have retry logic with exponential backoff.
- **Review Focus**: Service boundaries, error propagation, async patterns

## @Security-Officer
- **Responsibility**: Credential management, PII handling, encryption standards
- **Scope**: SnapTrade token encryption (AES-256-GCM), PII stripping before cloud AI calls, CORS/CSP headers
- **Standards**: NO raw credentials in logs or responses. All tokens encrypted at rest. Environment variables for all secrets. Rate limiting on all public endpoints.
- **Review Focus**: Token lifecycle, data sanitization, audit logging

## @Data-Scientist
- **Responsibility**: Financial calculations, statistical analysis, AI prompt engineering
- **Scope**: Correlation matrices, sector/geographic concentration, look-through analysis, LLM context generation
- **Standards**: All monetary values in cents (int64). Use Decimal for intermediate calculations. Correlation thresholds must be configurable. All DataFrames must have explicit dtypes.
- **Review Focus**: Numerical accuracy, statistical validity, prompt quality
