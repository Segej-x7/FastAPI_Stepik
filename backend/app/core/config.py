from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str# = "postgresql+asyncpg://....:.....@db:5432/fastapi_db"  # Значение по умолчанию
    SECRET_KEY: str# = ".............."  # Значение по умолчанию
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        # Правильный путь к .env (на 2 уровня выше от app/core/config.py)
        env_file = Path(__file__).resolve().parents[2] / ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = "ignore"  # Игнорировать отсутствующие переменные

settings = Settings()