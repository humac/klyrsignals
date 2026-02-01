"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central configuration for KlyrSignals."""

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://klyrsignals:klyrsignals_dev@localhost:5432/klyrsignals"
    )
    database_sync_url: str = Field(
        default="postgresql://klyrsignals:klyrsignals_dev@localhost:5432/klyrsignals"
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # SnapTrade
    snaptrade_client_id: str = Field(default="")
    snaptrade_consumer_key: str = Field(default="")

    # Encryption
    encryption_key: str = Field(default="")

    # AI
    ai_provider: str = Field(default="ollama")  # openai | anthropic | ollama
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")
    ollama_base_url: str = Field(default="http://localhost:11434")

    # App
    app_secret_key: str = Field(default="change-this-to-a-random-secret")
    cors_origins: list[str] = Field(default=["http://localhost:8501"])
    log_level: str = Field(default="INFO")

    # Streamlit
    streamlit_api_url: str = Field(default="http://localhost:8000")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
