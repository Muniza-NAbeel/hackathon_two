"""
Configuration settings for Phase 3 AI Chatbot

Loads settings from environment variables using pydantic-settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables are loaded from .env file in development.
    In production, set these in your deployment environment.
    """

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://phase3_user:phase3_password@localhost:5432/phase3_db",
        description="PostgreSQL connection string"
    )

    # JWT Authentication (shared with Phase 2)
    JWT_SECRET: str = Field(
        ...,
        description="Secret key for JWT token verification"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm (HS256 for symmetric key)"
    )
    ACCESS_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Number of days before access token expires"
    )

    # Gemini AI
    GEMINI_API_KEY: str = Field(
        ...,
        description="Google Gemini API key for AI agent"
    )

    # MCP Server (DEPRECATED - now using internal service)
    # Kept for backward compatibility but not used
    MCP_SERVER_URL: str = Field(
        default="",
        description="[DEPRECATED] MCP server URL - now using internal service"
    )

    # Application
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode (logs SQL queries)"
    )
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )

    # Phase 5: Event-Driven Architecture
    EVENTS_ENABLED: bool = Field(
        default=False,
        description="Enable event publishing to Kafka via Dapr"
    )
    DAPR_HTTP_PORT: int = Field(
        default=3500,
        description="Dapr sidecar HTTP port"
    )
    DAPR_PUBSUB_NAME: str = Field(
        default="kafka-pubsub",
        description="Dapr pub/sub component name"
    )
    TASK_EVENTS_TOPIC: str = Field(
        default="task-events",
        description="Kafka topic for task events"
    )
    REMINDERS_TOPIC: str = Field(
        default="reminders",
        description="Kafka topic for reminder events"
    )

    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
