"""
API Security Module

This module provides security features for the API, including:
1. Authentication using JWT tokens
2. Rate limiting to prevent abuse
3. Role-based access control
4. Request validation
5. Audit logging
"""
import os
import time
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable

from fastapi import Depends, HTTPException, Security, status, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr

from src.models.user import User
from src.api.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
API_KEY_NAME = "X-API-Key"

# Set up password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Set up security schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# User models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class UserInDB(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    scopes: List[str] = []
    
    class Config:
        from_attributes = True

# Rate limiting
class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, rate_limit: int = 100, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            rate_limit: Maximum number of requests per time window
            time_window: Time window in seconds
        """
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.requests = {}
    
    def is_rate_limited(self, key: str) -> bool:
        """
        Check if a key is rate limited.
        
        Args:
            key: Identifier for the client (IP address, API key, etc.)
            
        Returns:
            True if rate limited, False otherwise
        """
        current_time = time.time()
        
        # Initialize or clean up old requests
        if key not in self.requests:
            self.requests[key] = []
        else:
            # Remove requests outside the time window
            self.requests[key] = [t for t in self.requests[key] if t > current_time - self.time_window]
        
        # Check if rate limit is exceeded
        if len(self.requests[key]) >= self.rate_limit:
            return True
        
        # Add the current request
        self.requests[key].append(current_time)
        return False

# Create global rate limiter instance
rate_limiter = RateLimiter()

# Role-based access control
# Define roles and permissions
ROLES = {
    "admin": ["read:all", "write:all", "delete:all"],
    "analyst": ["read:all", "write:threats", "write:indicators", "write:reports"],
    "user": ["read:threats", "read:reports", "read:dashboard"],
    "api": ["read:all", "write:threats", "write:indicators"]
}

# Security utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password for storage"""
    return pwd_context.hash(password)

async def get_user(db: AsyncSession, username: str) -> Optional[UserInDB]:
    """Get a user from the database by username"""
    result = await db.execute(select(User).filter(User.username == username))
    user_db = result.scalars().first()
    
    if not user_db:
        return None
        
    # Get user roles and scopes
    scopes = []
    if user_db.is_superuser:
        scopes = ROLES["admin"]
    else:
        # In a real application, you would look up user roles in a database
        # For simplicity, we'll assume non-superusers have the "user" role
        scopes = ROLES["user"]
    
    return UserInDB(
        id=user_db.id,
        username=user_db.username,
        email=user_db.email,
        full_name=user_db.full_name,
        is_active=user_db.is_active,
        is_superuser=user_db.is_superuser,
        scopes=scopes
    )

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user with username and password"""
    user = await get_user(db, username)
    if not user:
        return None
    
    # Get the user from the database again to get the hashed password
    result = await db.execute(select(User).filter(User.username == username))
    user_db = result.scalars().first()
    
    if not verify_password(password, user_db.hashed_password):
        return None
        
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_api_key_user(
    api_key: str, 
    db: AsyncSession
) -> Optional[UserInDB]:
    """Get user associated with an API key"""
    # In a real application, you would look up API keys in a database
    # For simplicity, we'll use a simple hardcoded mapping
    # TODO: Replace with database-backed API key storage
    API_KEYS = {
        "test-api-key": "api_user",
        # Add more API keys here
    }
    
    if api_key not in API_KEYS:
        return None
        
    username = API_KEYS[api_key]
    user = await get_user(db, username)
    
    if not user:
        return None
        
    # Override scopes with API role scopes
    user.scopes = ROLES["api"]
    
    return user

# Dependencies for FastAPI
async def rate_limit(request: Request):
    """Rate limiting dependency"""
    # Use API key or IP address as the rate limit key
    client_key = request.headers.get(API_KEY_NAME) or request.client.host
    
    if rate_limiter.is_rate_limited(client_key):
        logger.warning(f"Rate limit exceeded for {client_key}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    return True

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    api_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> UserInDB:
    """
    Get the current user from either JWT token or API key.
    
    This dependency can be used to require authentication for endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check API key first
    if api_key:
        user = await get_api_key_user(api_key, db)
        if user:
            return user
    
    # Then check JWT token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        token_data = TokenData(
            username=username,
            scopes=payload.get("scopes", [])
        )
    except JWTError:
        raise credentials_exception
        
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """
    Get the current active user.
    
    This dependency can be used to require an active user for endpoints.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return current_user

def has_scope(required_scopes: List[str]):
    """
    Create a dependency that checks if the user has the required scopes.
    
    Args:
        required_scopes: List of required scopes
        
    Returns:
        A dependency function that checks if the user has the required scopes
    """
    async def _has_scope(
        current_user: UserInDB = Depends(get_current_active_user)
    ) -> UserInDB:
        for scope in required_scopes:
            if scope not in current_user.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required scope: {scope}"
                )
                
        return current_user
        
    return _has_scope

def admin_only(
    current_user: UserInDB = Depends(get_current_active_user)
) -> UserInDB:
    """
    Dependency that requires an admin user.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Admin access required."
        )
        
    return current_user

# Audit logging middleware
async def audit_log_middleware(request: Request, call_next):
    """
    Middleware for audit logging.
    
    Records details about API requests.
    """
    # Get request details
    method = request.method
    path = request.url.path
    client_host = request.client.host
    user_agent = request.headers.get("User-Agent", "Unknown")
    
    # Get user details if available
    user = getattr(request.state, "user", None)
    username = user.username if user else "Anonymous"
    
    # Log request
    logger.info(
        f"API Request: {method} {path} | User: {username} | "
        f"Client: {client_host} | User-Agent: {user_agent}"
    )
    
    # Process the request
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        f"API Response: {method} {path} | Status: {response.status_code} | "
        f"Time: {process_time:.4f}s | User: {username}"
    )
    
    return response

# API key validation middleware
def validate_api_key(request: Request):
    """
    Middleware function to validate API keys.
    
    This can be used as a dependency for FastAPI routes.
    """
    api_key = request.headers.get(API_KEY_NAME)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": f"{API_KEY_NAME}"},
        )
    
    # In a real application, you would validate the API key against a database
    # For simplicity, we'll use a hardcoded list
    valid_keys = ["test-api-key"]  # Replace with database lookup
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": f"{API_KEY_NAME}"},
        )
    
    return True