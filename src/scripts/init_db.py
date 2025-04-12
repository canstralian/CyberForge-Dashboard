"""
Script to initialize the database and create all tables.

Run this script to create all database tables on a fresh setup.
For subsequent schema changes, use Alembic migrations.
"""
import asyncio
import os
import sys
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.base import Base
from src.models.user import User
from src.models.threat import Threat, ThreatSeverity, ThreatStatus, ThreatCategory
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
    ASYNC_DATABASE_URL = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

logger.info(f"Using database URL: {ASYNC_DATABASE_URL}")


async def init_db():
    """Initialize the database and create all tables."""
    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=True,  # Set to True for debugging
    )
    
    logger.info("Creating all tables...")
    
    # Create all tables
    async with engine.begin() as conn:
        # Drop all tables if they exist
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("All tables created successfully!")
    
    # Create admin user if needed
    async_session = sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with async_session() as session:
        # Check if admin user exists
        from sqlalchemy.future import select
        from passlib.context import CryptContext
        
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        admin_user = result.scalars().first()
        
        if not admin_user:
            logger.info("Creating admin user...")
            
            # Hash password
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash("admin")
            
            # Create admin user
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
    
    logger.info("Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(init_db())