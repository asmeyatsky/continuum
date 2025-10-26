"""
Configuration settings for the Continuum application.

Loads from environment variables with sensible defaults.
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Continuum"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[Path] = None

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4

    # Database
    DATABASE_URL: str = "sqlite:///./continuum.db"
    DATABASE_POOL_SIZE: int = 5

    # Knowledge Graph
    KNOWLEDGE_GRAPH_MAX_NODES: int = 10000
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    # LLM Configuration
    LLM_PROVIDER: str = "openai"  # "openai" or "anthropic"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000

    # Data Pipeline
    RATE_LIMIT_REQUESTS_PER_SECOND: int = 10
    REQUEST_TIMEOUT: int = 30
    RETRY_ATTEMPTS: int = 3
    RETRY_BACKOFF: float = 1.5

    # Content Generation
    MIN_CONTENT_LENGTH: int = 100
    MAX_CONTENT_LENGTH: int = 10000
    QUALITY_THRESHOLD: float = 0.75

    # Performance
    ENABLE_CACHING: bool = True
    CACHE_TTL_SECONDS: int = 3600
    ASYNC_BATCH_SIZE: int = 10

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

        # Allow extra fields from environment
        extra = "ignore"


# Global settings instance
settings = Settings()
