"""
Model for users of the application.
"""
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from typing import List

from src.models.base import BaseModel

class User(BaseModel):
    """
    User model for authentication and authorization.
    """
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100))
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"