from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
RUNTIME_DIR = BASE_DIR / "runtime"

load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    bot_token: str
    openai_api_key: str | None = None
    max_file_mb: int = 20

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")


settings = Settings()
