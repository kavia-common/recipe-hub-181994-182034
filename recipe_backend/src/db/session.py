from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import get_settings, is_sqlite_url

# Create engine with SQLite specific connect args if needed
settings = get_settings()
engine_kwargs = {}
if is_sqlite_url(settings.DATABASE_URL):
    # Needed for SQLite when used in single-threaded async servers
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, **engine_kwargs)

# SQLAlchemy session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# PUBLIC_INTERFACE
def get_db() -> Generator:
    """Yield a SQLAlchemy database session and ensure it's closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
