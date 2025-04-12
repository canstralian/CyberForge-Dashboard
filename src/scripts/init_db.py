"""
Database initialization script.

This script creates all database tables and sets up initial data.
"""
import os
import sys
import asyncio
import logging
from datetime import datetime

# Add the parent directory to the path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

# Import the models
from src.models.base import Base
from src.models.user import User
from src.models.threat import Threat, ThreatSeverity, ThreatCategory, ThreatStatus
from src.models.indicator import Indicator, IndicatorType
from src.models.dark_web_content import DarkWebContent, DarkWebMention, ContentType, ContentStatus
from src.models.alert import Alert, AlertStatus, AlertCategory
from src.models.report import Report, ReportType, ReportStatus

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

# Create engine and session
engine = create_async_engine(
    ASYNC_DATABASE_URL, 
    echo=True,  # Set to True to see all SQL queries
)

async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        # Drop all tables if they exist (be careful with this in production!)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created.")

async def create_admin_user():
    """Create an admin user if none exists."""
    from sqlalchemy.future import select
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    async with async_session() as session:
        # Check if admin user exists
        result = await session.execute(select(User).filter(User.username == "admin"))
        admin_user = result.scalars().first()
        
        if not admin_user:
            # Create admin user
            hashed_password = pwd_context.hash("admin")  # Don't use simple passwords in production!
            admin_user = User(
                username="admin",
                email="admin@example.com",
                full_name="System Administrator",
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=True
            )
            session.add(admin_user)
            await session.commit()
            logger.info("Admin user created.")
        else:
            logger.info("Admin user already exists.")

async def create_initial_data():
    """Create initial data for testing."""
    # Here you can add code to create initial data for your application
    # For example, create some test threats, content, etc.
    pass

async def main():
    """Main function to initialize the database."""
    try:
        # Create tables
        await create_tables()
        
        # Create admin user
        await create_admin_user()
        
        # Create initial data
        await create_initial_data()
        
        logger.info("Database initialization completed successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())