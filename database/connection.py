"""
Database connection and session management for BellaTrix.

This module provides database connection utilities and session management
for SQLAlchemy ORM integration.
"""

import os
from typing import Optional
from sqlalchemy import create_engine, MetaData, event, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Base class for declarative models
Base = declarative_base()

# Metadata for schema reflection
metadata = MetaData()


def get_database_url() -> str:
    """
    Get database connection URL from environment variables.
    
    Environment variables:
        DATABASE_URL: Full PostgreSQL connection string
        Or individual components:
        - DB_HOST: Database host (default: localhost)
        - DB_PORT: Database port (default: 5432)
        - DB_NAME: Database name (default: bellatrix_db)
        - DB_USER: Database user
        - DB_PASSWORD: Database password
    
    Returns:
        PostgreSQL connection URL
    """
    # Try full DATABASE_URL first
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # Build from components
    host = os.getenv("DB_HOST", "bellatrix-db.c3ea24kmsrmf.ap-south-1.rds.amazonaws.com")
    port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "bellatrix_db")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    
    if password:
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    else:
        return f"postgresql://{user}@{host}:{port}/{db_name}"


def create_db_engine(
    database_url: Optional[str] = None,
    pool_size: int = 10,
    max_overflow: int = 20,
    pool_pre_ping: bool = True,
    echo: bool = False
):
    """
    Create SQLAlchemy database engine with connection pooling.
    
    Args:
        database_url: Database connection URL (defaults to get_database_url())
        pool_size: Number of connections to maintain in pool
        max_overflow: Maximum overflow connections
        pool_pre_ping: Enable connection health checks
        echo: Enable SQL query logging
    
    Returns:
        SQLAlchemy Engine instance
    """
    if database_url is None:
        database_url = get_database_url()
    
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=pool_pre_ping,  # Verify connections before using
        echo=echo,
        # Connection arguments
        connect_args={
            "connect_timeout": 10,
            "application_name": "bellatrix_app"
        }
    )
    
    # Log connection pool events
    @event.listens_for(engine, "connect")
    def set_postgres_settings(dbapi_conn, connection_record):
        """Set connection-level settings."""
        # Set timezone to UTC
        with dbapi_conn.cursor() as cursor:
            cursor.execute("SET timezone TO 'UTC'")
    
    return engine


# Global engine instance (lazy initialization)
_engine: Optional[object] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine():
    """Get or create the global database engine."""
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


def get_session_factory():
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
    return _SessionLocal


@contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    
    Usage:
        with get_db_session() as session:
            # Use session
            session.query(Model).all()
            session.commit()
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Initialize database schema (create all tables)."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized")


def drop_db():
    """Drop all database tables (use with caution!)."""
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")


def test_connection() -> bool:
    """
    Test database connection.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


# Health check function
def health_check() -> dict:
    """
    Perform database health check.
    
    Returns:
        Dictionary with health status and metrics
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Check connection
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            
            # Check pool status
            pool = engine.pool
            pool_status = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid()
            }
            
            return {
                "status": "healthy",
                "version": version,
                "pool": pool_status
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


