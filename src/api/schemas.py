"""
Pydantic schemas for the API.
"""
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

# Base models
class BaseSchema(BaseModel):
    """Base model for all schemas."""
    class Config:
        from_attributes = True
        populate_by_name = True

# Authentication schemas
class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for token data."""
    username: Optional[str] = None

class UserBase(BaseSchema):
    """Base schema for user data."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    """Schema for user creation."""
    password: str

class UserUpdate(BaseSchema):
    """Schema for user update."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    """Schema for user response."""
    id: int
    created_at: datetime
    updated_at: datetime

class UserInDB(User):
    """Schema for user in database."""
    hashed_password: str

# Pagination and filtering
class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)