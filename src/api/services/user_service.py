from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from passlib.context import CryptContext
from typing import Optional, List, Dict, Any
import logging

from src.models.user import User
from src.api.schemas import UserCreate, UserUpdate, UserInDB

# Configure logger
logger = logging.getLogger(__name__)

# Password context for hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        plain_password: Plain password
        hashed_password: Hashed password
        
    Returns:
        bool: True if password is correct
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash password.
    
    Args:
        password: Plain password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[UserInDB]:
    """
    Get user by username.
    
    Args:
        db: Database session
        username: Username
        
    Returns:
        Optional[UserInDB]: User if found, None otherwise
    """
    try:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        
        if not user:
            return None
            
        # Convert SQLAlchemy model to Pydantic model
        user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
        return UserInDB(**user_dict)
    except Exception as e:
        logger.error(f"Error getting user by username: {e}")
        return None

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate user.
    
    Args:
        db: Database session
        username: Username
        password: Plain password
        
    Returns:
        Optional[UserInDB]: User if authenticated, None otherwise
    """
    user = await get_user_by_username(db, username)
    
    if not user:
        return None
        
    if not verify_password(password, user.hashed_password):
        return None
        
    return user

async def create_user(db: AsyncSession, user_data: UserCreate) -> Optional[UserInDB]:
    """
    Create a new user.
    
    Args:
        db: Database session
        user_data: User data
        
    Returns:
        Optional[UserInDB]: Created user
    """
    try:
        # Check if user already exists
        existing_user = await get_user_by_username(db, user_data.username)
        if existing_user:
            return None
            
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=user_data.is_active
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Convert SQLAlchemy model to Pydantic model
        user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
        return UserInDB(**user_dict)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        await db.rollback()
        return None

async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[UserInDB]:
    """
    Update user.
    
    Args:
        db: Database session
        user_id: User ID
        user_data: User data
        
    Returns:
        Optional[UserInDB]: Updated user
    """
    try:
        # Create update dictionary
        update_data = user_data.dict(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
        # Update user
        stmt = update(User).where(User.id == user_id).values(**update_data)
        await db.execute(stmt)
        await db.commit()
        
        # Get updated user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        
        if not user:
            return None
            
        # Convert SQLAlchemy model to Pydantic model
        user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
        return UserInDB(**user_dict)
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        await db.rollback()
        return None