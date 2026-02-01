"""Custom exception hierarchy for KlyrSignals."""


class KlyrError(Exception):
    """Base exception for all KlyrSignals errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class SnapTradeError(KlyrError):
    """Errors from SnapTrade API interactions."""

    def __init__(self, message: str):
        super().__init__(message, code="SNAPTRADE_ERROR")


class EncryptionError(KlyrError):
    """Errors during encryption/decryption operations."""

    def __init__(self, message: str):
        super().__init__(message, code="ENCRYPTION_ERROR")


class UserNotFoundError(KlyrError):
    """User not found in database."""

    def __init__(self, user_id: str):
        super().__init__(f"User {user_id} not found", code="USER_NOT_FOUND")


class ConnectionNotFoundError(KlyrError):
    """Brokerage connection not found."""

    def __init__(self, connection_id: str):
        super().__init__(f"Connection {connection_id} not found", code="CONNECTION_NOT_FOUND")


class InsufficientDataError(KlyrError):
    """Not enough data to perform analysis."""

    def __init__(self, message: str = "Insufficient data for analysis"):
        super().__init__(message, code="INSUFFICIENT_DATA")


class AIProviderError(KlyrError):
    """Error from AI provider (OpenAI, Anthropic, Ollama)."""

    def __init__(self, provider: str, message: str):
        super().__init__(f"{provider}: {message}", code="AI_PROVIDER_ERROR")
