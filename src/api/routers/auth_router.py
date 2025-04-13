"""
Authentication router.

This module provides authentication endpoints for the API.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.database import get_db
from src.api.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    UserInDB,
    authenticate_user,
    create_access_token,
    get_current_active_user,
)

router = APIRouter(tags=["authentication"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires
    )
    
    expires_at = datetime.utcnow() + access_token_expires
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at
    }

@router.get("/users/me", response_model=UserInDB)
async def read_users_me(
    current_user: UserInDB = Depends(get_current_active_user)
) -> UserInDB:
    """
    Get current user.
    """
    return current_user

@router.get("/users/me/scopes")
async def read_own_scopes(
    current_user: UserInDB = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get current user's scopes.
    """
    return {
        "username": current_user.username,
        "scopes": current_user.scopes
    }