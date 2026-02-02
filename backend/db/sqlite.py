from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings
from backend.core.logging import logger
from backend.core.paths import STORAGE_DIR

# Import models to register them with Base
from backend.db.models import Base

SQLITE_URL = f"sqlite:///{STORAGE_DIR}/research.db"

engine = create_engine(
    SQLITE_URL, 
    connect_args={"check_same_thread": False}  # Needed for SQLite with FastAPI
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("SQLite tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite tables: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_sqlite_connection():
    try:
        # Simple check using execute
        with engine.connect() as connection:
            # SQLAlchemy 1.4+ / 2.0 style
            from sqlalchemy import text
            connection.execute(text("SELECT 1"))
        logger.info("SQLite connection verified")
        return True
    except Exception as e:
        logger.error(f"SQLite connection failed: {e}")
        return False

# Auto-initialize on import (or better, call explicitly in main.py)
init_db()
