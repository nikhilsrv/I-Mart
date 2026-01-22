from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ecommerce"

    # App
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "changeme"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
