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
    # Format: postgresql://user:password@localhost:5432/continuum (for PostgreSQL)
    # or: sqlite:///./continuum.db (for SQLite)
    DATABASE_URL: str = "sqlite:///./continuum.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    USE_PERSISTENT_GRAPH: bool = False  # Use database instead of in-memory graph

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

    # Performance & Caching
    ENABLE_CACHING: bool = True
    CACHE_TYPE: str = "local"  # "local", "redis", or "none"
    CACHE_TTL_SECONDS: int = 3600
    CACHE_MAX_SIZE: int = 1000  # For local cache
    ASYNC_BATCH_SIZE: int = 10
    REDIS_URL: Optional[str] = None  # redis://localhost:6379/0

    # Feature Flags
    FEATURE_REAL_WEB_SEARCH: bool = False  # Use real web search instead of mocks
    FEATURE_REAL_IMAGE_GENERATION: bool = False  # Use real image generation
    FEATURE_PERSISTENT_LEARNING: bool = True  # Enable persistent learning system
    FEATURE_DISTRIBUTED_TRACING: bool = False  # Enable OpenTelemetry tracing

    # Distributed Tracing Configuration
    TRACING_ENABLED: bool = False  # Enable/disable tracing
    TRACING_EXPORTER: str = "console"  # console, jaeger, otlp, in_memory, none
    TRACING_JAEGER_HOST: str = "localhost"
    TRACING_JAEGER_PORT: int = 6831
    TRACING_OTLP_ENDPOINT: str = "http://localhost:4317"

    # Web Search Integration
    BRAVE_SEARCH_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None

    # Image Generation
    OPENAI_IMAGE_API_KEY: Optional[str] = None  # Uses OPENAI_API_KEY by default
    STABLE_DIFFUSION_ENDPOINT: Optional[str] = None  # e.g., http://localhost:7860

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

        # Allow extra fields from environment
        extra = "ignore"


# Global settings instance
settings = Settings()
