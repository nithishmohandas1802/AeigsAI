from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root directory (AegisAI/)
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str
    app_version: str
    app_description: str
    database_url: str
    jwt_secret_key: str = Field(
        min_length=32,
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(
        default=30,
        gt=0,
    )
    database_echo: bool = False
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()