import os
import secrets
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables with safe defaults."""
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./recipes.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "") or secrets.token_urlsafe(32)

    class Config:
        extra = "ignore"


@lru_cache
# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# PUBLIC_INTERFACE
def is_sqlite_url(db_url: Optional[str] = None) -> bool:
    """Check if the provided (or configured) database URL is a SQLite URL."""
    url = db_url or get_settings().DATABASE_URL
    return url.startswith("sqlite:///") or url.startswith("sqlite:///")


__all__ = ["Settings", "get_settings", "is_sqlite_url"]
