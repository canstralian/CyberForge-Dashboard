"""
Database utilities for Streamlit application.

This module provides functions to interact with the database from Streamlit.
"""
import os
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional, AsyncGenerator, Callable, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Create async engine
if DATABASE_URL.startswith("postgresql://"):
    # Convert to async format
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

if not DATABASE_URL:
    logger.warning("DATABASE_URL not set. Using in-memory SQLite.")
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create engine and session factory
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    session = async_session()
    try:
        yield session
    finally:
        await session.close()


# Helper type for generic function return
T = TypeVar('T')


def run_async(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Run an async function in a synchronous context.
    This is needed for Streamlit which doesn't support async functions directly.
    
    Args:
        func: The async function to run
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
    
    Returns:
        The result of the async function
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(func(*args, **kwargs))
    finally:
        loop.close()