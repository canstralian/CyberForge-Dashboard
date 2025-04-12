from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import logging

from src.api.database import get_db
from src.api.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from src.api.services.user_service import authenticate_user, create_user
from src.api.schemas import Token, UserCreate, User

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"description": "Unauthorized"}},
)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Get access token.
    
    Args:
        form_data: Form with username and password
        db: Database session
        
    Returns:
        Token: Access token
        
    Raises:
        HTTPException: If authentication fails
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
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        user_data: User data
        db: Database session
        
    Returns:
        User: Created user
        
    Raises:
        HTTPException: If user already exists
    """
    user = await create_user(db, user_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
        
    # Don't include hashed_password in response
    user_dict = user.dict()
    user_dict.pop("hashed_password")
    
    return User(**user_dict)