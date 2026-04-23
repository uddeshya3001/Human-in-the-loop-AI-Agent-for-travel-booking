"""
Database connection and initialization.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# Create database directory if it doesn't exist
DB_DIR = Path(__file__).parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)

# Database URL
DATABASE_URL = f"sqlite:///{DB_DIR}/travel_agent.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False  # Set to True for SQL query logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def init_db():
    """
    Initialize database - create all tables.
    """
    from database.models import User, TravelPlanDB, ExecutionResult
    Base.metadata.create_all(bind=engine)


def get_session():
    """
    Get a database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db():
    """
    Get a database session (simple version).
    
    Returns:
        Database session
    """
    return SessionLocal()