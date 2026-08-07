from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root directory (AegisAI/)
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str
    app_version: str
    app_description: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()