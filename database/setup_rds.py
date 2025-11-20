"""
Setup script to initialize RDS PostgreSQL database with BellaTrix schema.

This script will:
1. Connect to the RDS database
2. Create all tables, indexes, views, and triggers
3. Insert initial seed data
"""

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def get_db_connection(create_db=False):
    """
    Get database connection.
    
    Args:
        create_db: If True, connect to postgres database to create the target database
    """
    # Get connection parameters from environment
    host = os.getenv("DB_HOST", "bellatrix-db.c3ea24kmsrmf.ap-south-1.rds.amazonaws.com")
    port = os.getenv("DB_PORT", "5432")
    db_name = "postgres" if create_db else os.getenv("DB_NAME", "bellatrix_db")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    
    if not password:
        logger.error("DB_PASSWORD environment variable is required!")
        sys.exit(1)
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=db_name,
            user=user,
            password=password,
            connect_timeout=10
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logger.info(f"Connected to database: {host}:{port}/{db_name}")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)


def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    db_name = os.getenv("DB_NAME", "bellatrix_db")
    
    logger.info(f"Checking if database '{db_name}' exists...")
    conn = get_db_connection(create_db=True)
    cursor = conn.cursor()
    
    try:
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone()
        
        if not exists:
            logger.info(f"Creating database '{db_name}'...")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            logger.info(f"Database '{db_name}' created successfully")
        else:
            logger.info(f"Database '{db_name}' already exists")
        
        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        logger.error(f"Error creating database: {e}")
        cursor.close()
        conn.close()
        sys.exit(1)


def execute_schema_file(conn, schema_file_path):
    """
    Execute SQL schema file.
    
    Args:
        conn: Database connection
        schema_file_path: Path to SQL schema file
    """
    schema_path = Path(schema_file_path)
    
    if not schema_path.exists():
        logger.error(f"Schema file not found: {schema_path}")
        sys.exit(1)
    
    logger.info(f"Reading schema file: {schema_path}")
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Split by semicolons but handle functions/triggers that contain semicolons
    # We'll execute the entire file as one transaction
    cursor = conn.cursor()
    
    try:
        logger.info("Executing schema SQL...")
        cursor.execute(schema_sql)
        conn.commit()
        logger.info("Schema executed successfully")
        cursor.close()
    except psycopg2.Error as e:
        logger.error(f"Error executing schema: {e}")
        conn.rollback()
        cursor.close()
        raise


def verify_tables(conn):
    """Verify that tables were created successfully."""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        if tables:
            logger.info(f"\nCreated {len(tables)} tables:")
            for table in tables:
                logger.info(f"  - {table[0]}")
        else:
            logger.warning("No tables found in database")
        
        cursor.close()
    except psycopg2.Error as e:
        logger.error(f"Error verifying tables: {e}")
        cursor.close()


def main():
    """Main setup function."""
    logger.info("=" * 60)
    logger.info("BellaTrix RDS Database Setup")
    logger.info("=" * 60)
    
    # Step 1: Create database if it doesn't exist
    create_database_if_not_exists()
    
    # Step 2: Connect to the target database
    logger.info("\nConnecting to target database...")
    conn = get_db_connection(create_db=False)
    
    # Step 3: Execute schema file
    schema_file = Path(__file__).parent / "schema.sql"
    logger.info(f"\nExecuting schema from: {schema_file}")
    try:
        execute_schema_file(conn, schema_file)
    except Exception as e:
        logger.error(f"Failed to execute schema: {e}")
        conn.close()
        sys.exit(1)
    
    # Step 4: Verify tables
    logger.info("\nVerifying database setup...")
    verify_tables(conn)
    
    # Step 5: Close connection
    conn.close()
    
    logger.info("\n" + "=" * 60)
    logger.info("Database setup completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

