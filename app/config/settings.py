from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root directory (AegisAI/)
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str
    app_version: str
    app_description: str
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()