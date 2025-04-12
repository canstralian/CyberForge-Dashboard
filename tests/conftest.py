"""
Pytest fixtures for testing.
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
from datetime import datetime, timedelta

# Set environment to testing
os.environ["FLASK_ENV"] = "testing"

# Import after setting env
from src.api.main import app
from src.api.database import get_db
from src.models.base import Base
from src.api.auth import create_access_token
from src.models.user import User
from src.models.threat import Threat, ThreatSeverity, ThreatStatus, ThreatCategory
from src.models.indicator import Indicator, IndicatorType

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create engine and session
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency override for database session
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get test database session."""
    async with async_session() as session:
        yield session

# Override database dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def setup_database() -> AsyncGenerator[None, None]:
    """Set up test database."""
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Get test client."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
async def test_user(setup_database) -> User:
    """Create test user."""
    async with async_session() as session:
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="$2b$12$IYVrqQ7lnUUX.CqK5xNdvO.K6jZ7HkB7qJ3aHXCCd9xlfO8hQcNh2",  # password: testpassword
            is_active=True
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return user

@pytest.fixture
def access_token(test_user) -> str:
    """Create access token for test user."""
    return create_access_token(
        data={"sub": test_user.username},
        expires_delta=timedelta(minutes=30)
    )

@pytest.fixture
def authorized_client(client, access_token) -> Generator[TestClient, None, None]:
    """Get authorized test client."""
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client

@pytest.fixture
async def test_threats(setup_database) -> list[Threat]:
    """Create test threats."""
    async with async_session() as session:
        threats = []
        
        # Create threats
        for i in range(5):
            threat = Threat(
                title=f"Test Threat {i}",
                description=f"Test description {i}",
                severity=ThreatSeverity.MEDIUM,
                status=ThreatStatus.NEW,
                category=ThreatCategory.DARK_WEB_MENTION,
                source_url=f"https://example.com/threat/{i}",
                source_name="Test Source",
                discovered_at=datetime.utcnow(),
                confidence_score=0.7,
                risk_score=0.5,
                raw_content=f"Raw content {i}",
                meta_data={"test": "data"}
            )
            
            session.add(threat)
            threats.append(threat)
        
        await session.commit()
        
        # Refresh threats
        for threat in threats:
            await session.refresh(threat)
        
        return threats

@pytest.fixture
async def test_indicators(setup_database, test_threats) -> list[Indicator]:
    """Create test indicators."""
    async with async_session() as session:
        indicators = []
        
        # Create indicators
        for i, threat in enumerate(test_threats):
            indicator = Indicator(
                value=f"192.168.1.{i}",
                type=IndicatorType.IP,
                description=f"Test indicator {i}",
                threat_id=threat.id,
                is_verified=False,
                context=f"Test context {i}",
                source="Test Source"
            )
            
            session.add(indicator)
            indicators.append(indicator)
        
        await session.commit()
        
        # Refresh indicators
        for indicator in indicators:
            await session.refresh(indicator)
        
        return indicators