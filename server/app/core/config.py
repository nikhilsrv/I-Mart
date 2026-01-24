from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str

    # App
    APP_ENV: str
    DEBUG: bool
    SECRET_KEY: str

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str 

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # JWT Settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 12
    REFRESH_TOKEN_EXPIRE_DAYS: int = 2


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
