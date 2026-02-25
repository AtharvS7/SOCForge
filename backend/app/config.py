"""Application configuration via environment variables."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://socforge_admin:StrongPassword123!@localhost:5432/socforge"

    # Redis
    REDIS_URL: str = "redis://:StrongRedisPassword123!@localhost:6379/0"

    # JWT
    JWT_SECRET: str = "SOCForge_JWT_Super_Secret_Key_2024!"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 480

    # App
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # ── SIEM Integration (optional) ──
    SPLUNK_HEC_URL: str = ""
    SPLUNK_HEC_TOKEN: str = ""
    ELASTICSEARCH_URL: str = ""
    ELASTICSEARCH_API_KEY: str = ""

    # ── Notifications (optional) ──
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SLACK_WEBHOOK_URL: str = ""

    # ── IOC Enrichment (optional) ──
    VIRUSTOTAL_API_KEY: str = ""
    ABUSEIPDB_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
