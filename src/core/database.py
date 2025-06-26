"""
Database connection and session management for Ayala Foundation Backend

Handles PostgreSQL connection, session management, and database initialization.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator
import logging

from .config import get_settings

# Get settings
settings = get_settings()

# Create database engine
engine = create_engine(
    settings.database_url,
    poolclass=NullPool,
    echo=settings.debug,  # Log SQL queries in debug mode
    pool_pre_ping=True,   # Verify connections before use
)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

# Metadata for database operations
metadata = MetaData()

def get_database() -> Generator[Session, None, None]:
    """
    Database dependency that provides a database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logging.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_database():
    """
    Initialize database tables.
    Creates all tables defined in models.
    """
    try:
        # Import all models to register them with Base
        from ..companies.models import Company, Location
        from ..auth.models import User
        from ..funds.models import FundProfile
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables initialized successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise

def test_database_connection() -> bool:
    """
    Test database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        db = SessionLocal()
        # Simple query to test connection
        db.execute("SELECT 1")
        db.close()
        logging.info("Database connection test successful")
        return True
    except Exception as e:
        logging.error(f"Database connection test failed: {e}")
        return False 