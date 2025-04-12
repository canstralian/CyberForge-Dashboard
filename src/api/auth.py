from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
import logging

from src.api.database import get_db
from src.api.schemas import TokenData, UserInDB
from src.api.services.user_service import get_user_by_username

# Configure logger
logger = logging.getLogger(__name__)

# Constants for JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-jwt-please-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2PasswordBearer for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary of data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> UserInDB:
    """
    Get the current authenticated user based on the JWT token.
    
    Args:
        token: JWT token
        db: Database session
        
    Returns:
        UserInDB: User data
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
        token_data = TokenData(username=username)
    except JWTError as e:
        logger.error(f"JWT error: {e}")
        raise credentials_exception
        
    # Get user from database
    user = await get_user_by_username(db, username=token_data.username)
    
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    Get the current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserInDB: User data
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return current_user