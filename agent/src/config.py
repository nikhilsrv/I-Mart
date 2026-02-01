from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Google Gemini
    GOOGLE_API_KEY: str

    # Deepgram
    DEEPGRAM_API_KEY: str

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8765

    # I-Mart API (your FastAPI backend)
    IMART_API_URL: str = "http://localhost:8000"

    # STUN/TURN servers for WebRTC
    STUN_SERVERS: list[str] = ["stun:stun.l.google.com:19302"]
    TURN_SERVER: str | None = None
    TURN_USERNAME: str | None = None
    TURN_PASSWORD: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
