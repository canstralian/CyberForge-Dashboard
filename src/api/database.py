from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from typing import AsyncGenerator
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Get database URL from environment (convert synchronous to async URL)
db_url = os.getenv("DATABASE_URL", "")
if db_url.startswith("postgresql://"):
    ASYNC_DATABASE_URL = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # Set to True for debugging
    future=True,
    pool_size=5,
    max_overflow=10
)

# Create async session factory
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session generator.
    
    Yields:
        AsyncSession: Database session
    """
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        await session.close()

# Dependency for getting DB session
async def get_db_session() -> AsyncSession:
    """
    Get database session.
    
    Returns:
        AsyncSession: Database session
    """
    async with async_session() as session:
        return session