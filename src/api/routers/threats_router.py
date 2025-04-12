from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from src.api.database import get_db
from src.api.auth import get_current_user
from src.api.schemas import (
    Threat, ThreatCreate, ThreatUpdate, ThreatFilter, 
    PaginationParams, User
)
from src.api.services.threat_service import (
    create_threat, get_threat_by_id, update_threat, 
    delete_threat, get_threats, get_threat_statistics
)

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["threats"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=Threat, status_code=status.HTTP_201_CREATED)
async def create_threat_endpoint(
    threat_data: ThreatCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new threat.
    
    Args:
        threat_data: Threat data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Threat: Created threat
    """
    try:
        threat = await create_threat(db, threat_data)
        
        if not threat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create threat"
            )
            
        return threat
    except Exception as e:
        logger.error(f"Error creating threat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/{threat_id}", response_model=Threat)
async def get_threat_endpoint(
    threat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get threat by ID.
    
    Args:
        threat_id: Threat ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Threat: Threat data
    """
    threat = await get_threat_by_id(db, threat_id)
    
    if not threat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threat with ID {threat_id} not found"
        )
        
    return threat

@router.put("/{threat_id}", response_model=Threat)
async def update_threat_endpoint(
    threat_id: int,
    threat_data: ThreatUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update threat.
    
    Args:
        threat_id: Threat ID
        threat_data: Threat data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Threat: Updated threat
    """
    # Check if threat exists
    threat = await get_threat_by_id(db, threat_id)
    
    if not threat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threat with ID {threat_id} not found"
        )
    
    # Update threat
    updated_threat = await update_threat(db, threat_id, threat_data)
    
    if not updated_threat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update threat"
        )
        
    return updated_threat

@router.delete("/{threat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_threat_endpoint(
    threat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete threat.
    
    Args:
        threat_id: Threat ID
        db: Database session
        current_user: Current authenticated user
    """
    # Check if threat exists
    threat = await get_threat_by_id(db, threat_id)
    
    if not threat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threat with ID {threat_id} not found"
        )
    
    # Delete threat
    deleted = await delete_threat(db, threat_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete threat"
        )

@router.get("/", response_model=List[Threat])
async def get_threats_endpoint(
    pagination: PaginationParams = Depends(),
    severity: Optional[List[str]] = Query(None),
    status: Optional[List[str]] = Query(None),
    category: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get threats with filtering and pagination.
    
    Args:
        pagination: Pagination parameters
        severity: Filter by severity
        status: Filter by status
        category: Filter by category
        search: Search in title and description
        from_date: Filter from date
        to_date: Filter to date
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[Threat]: List of threats
    """
    # Create filter params
    filter_params = ThreatFilter(
        severity=severity,
        status=status,
        category=category,
        search=search,
        from_date=from_date,
        to_date=to_date
    )
    
    # Get threats
    threats, total = await get_threats(db, filter_params, pagination)
    
    return threats

@router.get("/statistics", response_model=dict)
async def get_threat_statistics_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get threat statistics.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Threat statistics
    """
    statistics = await get_threat_statistics(db)
    return statistics