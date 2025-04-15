"""
Database initialization for Hugging Face Spaces environment.
This creates an in-memory SQLite database for demo purposes.
"""
import logging
import os
import sqlite3
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.models.base import Base
from src.models.user import User
try:
    # Try to import from src.api.security first (for local development)
    from src.api.security import get_password_hash
except ImportError:
    # Fall back to simplified security module for HF (copied during deployment)
    from security_hf import get_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL for SQLite in-memory
DATABASE_URL = "sqlite:///:memory:"

# Create engine with special configuration for in-memory SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

# Add pragma for foreign key support
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Create all tables
Base.metadata.create_all(engine)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_demo_data():
    """Initialize demo data for the in-memory database."""
    session = SessionLocal()
    try:
        # Check if we already have users
        user_count = session.query(User).count()
        if user_count == 0:
            # Create admin user
            admin_user = User(
                username="admin",
                email="admin@example.com",
                full_name="Admin User",
                hashed_password=get_password_hash("adminpassword"),
                is_active=True,
                is_superuser=True
            )
            session.add(admin_user)
            
            # Create regular user
            regular_user = User(
                username="user",
                email="user@example.com",
                full_name="Regular User",
                hashed_password=get_password_hash("userpassword"),
                is_active=True,
                is_superuser=False
            )
            session.add(regular_user)
            
            # Create API user
            api_user = User(
                username="api_user",
                email="api@example.com",
                full_name="API User",
                hashed_password=get_password_hash("apipassword"),
                is_active=True,
                is_superuser=False
            )
            session.add(api_user)
            
            # Commit the session
            session.commit()
            logger.info("Demo users created successfully")
        else:
            logger.info("Demo data already exists")
            
        # Here you would add other demo data like threats, indicators, etc.
            
    except Exception as e:
        session.rollback()
        logger.error(f"Error initializing demo data: {e}")
    finally:
        session.close()

# Initialize demo data
init_demo_data()

logger.info("Hugging Face database initialized with demo data")