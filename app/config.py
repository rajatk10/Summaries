import os
from datetime import UTC, datetime
from logging.config import dictConfig
from typing import Any, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: Literal["dev", "test", "prod"] = "dev"
    LOG_LEVEL: Literal["INFO", "DEBUG", "ERROR", "WARN"] = "INFO"
    database_url: str = (
        "postgresql://postgres:postgres-tdd@localhost:15432/summaries-dev"
    )

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
"""
The pydantic setting load in order 
1. Process environment variables
2. .env file
3. the overrides in config.py
"""

TORTOISE_ORM: dict[str, Any] = {
    "connections": {
        "default": settings.database_url,
    },
    "apps": {
        "models": {
            "models": ["app.models.summary"],
            "default_connection": "default",
            "migrations": "app.migrations",
        }
    },
    "use_tz": True,
    "timezone": "UTC",
}

# Logging
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)


def configure_logging(log_level: str = "INFO") -> None:
    datetime_suffix = datetime.now(tz=UTC).strftime("%Y-%m-%d_%H-%M-%S")
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "standard",
                    "filename": f"{log_dir}/app-{datetime_suffix}.log",
                    "maxBytes": 10485760,
                    "backupCount": 5,
                    "encoding": "utf-8",
                },
            },
            "root": {"level": log_level, "handlers": ["console", "file"]},
        }
    )
