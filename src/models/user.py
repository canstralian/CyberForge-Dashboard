"""
User model for authentication and authorization.
"""
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from src.models.base import BaseModel

class User(BaseModel):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100))
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Additional fields for user profile
    bio = Column(Text)
    avatar_url = Column(String(255))
    last_login = Column(String(255))
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"