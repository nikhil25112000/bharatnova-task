from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Social Feed & Media Metadata Microservice"
    app_env: Literal["local", "development", "staging", "production", "test"] = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    allowed_origins: list[str] = ["*"]

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/social_feed_db"
    )
    database_echo: bool = False
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl_seconds: int = 300

    upload_url_expiry_seconds: int = 300
    upload_base_url: str = "http://localhost:8000/uploads"

    max_caption_length: int = 2200
    default_page_limit: int = 10
    max_page_limit: int = 50
    upload_max_file_size_bytes: int = 104857600

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
