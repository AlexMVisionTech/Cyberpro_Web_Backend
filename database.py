"""Database configuration for the Cyberpro API."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DEFAULT_DATABASE_PATH = Path(os.getenv("DATA_DIR", str(Path(__file__).with_name("data"))))
DEFAULT_DATABASE_PATH.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DATABASE_PATH / 'cyberpro.db'}")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Yield a database session and always close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
