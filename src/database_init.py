"""
Database initialization for the application.

This script checks if the database is initialized and creates tables if needed.
It's meant to be imported and run at application startup.
"""
import os
import logging
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Database URL from environment
db_url = os.getenv("DATABASE_URL", "")
if db_url.startswith("postgresql://"):
    # Remove sslmode parameter if present which causes issues with asyncpg
    if "?" in db_url:
        base_url, params = db_url.split("?", 1)
        param_list = params.split("&")
        filtered_params = [p for p in param_list if not p.startswith("sslmode=")]
        if filtered_params:
            db_url = f"{base_url}?{'&'.join(filtered_params)}"
        else:
            db_url = base_url
    
    ASYNC_DATABASE_URL = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"


async def check_db_initialized():
    """Check if the database is initialized with required tables."""
    try:
        engine = create_async_engine(
            ASYNC_DATABASE_URL,
            echo=False,
        )
        
        # Create session factory
        async_session = sessionmaker(
            engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        
        async with async_session() as session:
            # Try to query tables
            # Replace with actual table names once you've defined them
            try:
                # Check if the 'users' table exists
                query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
                result = await session.execute(query)
                exists = result.scalar()
                
                if exists:
                    logger.info("Database is initialized.")
                    return True
                else:
                    logger.warning("Database tables are not initialized.")
                    return False
            except Exception as e:
                logger.error(f"Error checking tables: {e}")
                return False
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return False


def initialize_database():
    """Initialize the database with required tables."""
    try:
        # Call the init_db.py script
        logger.info("Initializing database...")
        
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, "scripts", "init_db.py")
        
        # Run the script using the current Python interpreter
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Database initialized successfully.")
            logger.debug(result.stdout)
            return True
        else:
            logger.error(f"Failed to initialize database: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False


def ensure_database_initialized():
    """Ensure the database is initialized with required tables."""
    is_initialized = asyncio.run(check_db_initialized())
    
    if not is_initialized:
        return initialize_database()
    
    return True