from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func, or_, and_
from typing import Optional, List, Dict, Any, Tuple
import logging
from datetime import datetime

from src.models.threat import Threat, ThreatSeverity, ThreatStatus, ThreatCategory
from src.api.schemas import ThreatCreate, ThreatUpdate, ThreatFilter, PaginationParams

# Configure logger
logger = logging.getLogger(__name__)

async def create_threat(db: AsyncSession, threat_data: ThreatCreate) -> Optional[Threat]:
    """
    Create a new threat.
    
    Args:
        db: Database session
        threat_data: Threat data
        
    Returns:
        Optional[Threat]: Created threat
    """
    try:
        # Convert pydantic model to dict
        threat_dict = threat_data.dict()
        
        # Create new threat
        threat = Threat(**threat_dict)
        
        db.add(threat)
        await db.commit()
        await db.refresh(threat)
        
        return threat
    except Exception as e:
        logger.error(f"Error creating threat: {e}")
        await db.rollback()
        return None

async def get_threat_by_id(db: AsyncSession, threat_id: int) -> Optional[Threat]:
    """
    Get threat by ID.
    
    Args:
        db: Database session
        threat_id: Threat ID
        
    Returns:
        Optional[Threat]: Threat if found, None otherwise
    """
    try:
        result = await db.execute(select(Threat).where(Threat.id == threat_id))
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error getting threat by ID: {e}")
        return None

async def update_threat(
    db: AsyncSession, threat_id: int, threat_data: ThreatUpdate
) -> Optional[Threat]:
    """
    Update threat.
    
    Args:
        db: Database session
        threat_id: Threat ID
        threat_data: Threat data
        
    Returns:
        Optional[Threat]: Updated threat
    """
    try:
        # Get existing threat
        threat = await get_threat_by_id(db, threat_id)
        
        if not threat:
            return None
            
        # Update threat with new data
        update_data = threat_data.dict(exclude_unset=True)
        
        stmt = update(Threat).where(Threat.id == threat_id).values(**update_data)
        await db.execute(stmt)
        await db.commit()
        
        # Get updated threat
        return await get_threat_by_id(db, threat_id)
    except Exception as e:
        logger.error(f"Error updating threat: {e}")
        await db.rollback()
        return None

async def delete_threat(db: AsyncSession, threat_id: int) -> bool:
    """
    Delete threat.
    
    Args:
        db: Database session
        threat_id: Threat ID
        
    Returns:
        bool: True if deleted, False otherwise
    """
    try:
        # Delete threat
        stmt = delete(Threat).where(Threat.id == threat_id)
        result = await db.execute(stmt)
        await db.commit()
        
        # Check if any rows were deleted
        return result.rowcount > 0
    except Exception as e:
        logger.error(f"Error deleting threat: {e}")
        await db.rollback()
        return False

async def get_threats(
    db: AsyncSession,
    filter_params: ThreatFilter,
    pagination: PaginationParams
) -> Tuple[List[Threat], int]:
    """
    Get threats with filtering and pagination.
    
    Args:
        db: Database session
        filter_params: Filter parameters
        pagination: Pagination parameters
        
    Returns:
        Tuple[List[Threat], int]: List of threats and total count
    """
    try:
        # Base query
        query = select(Threat)
        count_query = select(func.count()).select_from(Threat)
        
        # Apply filters
        filters = []
        
        if filter_params.severity:
            filters.append(Threat.severity.in_(filter_params.severity))
            
        if filter_params.status:
            filters.append(Threat.status.in_(filter_params.status))
            
        if filter_params.category:
            filters.append(Threat.category.in_(filter_params.category))
            
        if filter_params.search:
            search_filter = or_(
                Threat.title.ilike(f"%{filter_params.search}%"),
                Threat.description.ilike(f"%{filter_params.search}%"),
                Threat.source_name.ilike(f"%{filter_params.search}%"),
                Threat.affected_entity.ilike(f"%{filter_params.search}%")
            )
            filters.append(search_filter)
            
        if filter_params.from_date:
            filters.append(Threat.discovered_at >= filter_params.from_date)
            
        if filter_params.to_date:
            filters.append(Threat.discovered_at <= filter_params.to_date)
            
        # Combine filters with AND
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
            
        # Get total count
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        # Apply pagination
        query = query.order_by(Threat.discovered_at.desc())
        query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)
        
        # Execute query
        result = await db.execute(query)
        threats = result.scalars().all()
        
        return threats, total_count
    except Exception as e:
        logger.error(f"Error getting threats: {e}")
        return [], 0

async def get_threat_statistics(db: AsyncSession) -> Dict[str, Any]:
    """
    Get threat statistics.
    
    Args:
        db: Database session
        
    Returns:
        Dict[str, Any]: Dictionary with threat statistics
    """
    try:
        # Total count
        total_query = select(func.count()).select_from(Threat)
        total_result = await db.execute(total_query)
        total_count = total_result.scalar()
        
        # Count by severity
        severity_stats = {}
        for severity in ThreatSeverity:
            query = select(func.count()).select_from(Threat).where(Threat.severity == severity)
            result = await db.execute(query)
            severity_stats[severity.value] = result.scalar()
            
        # Count by status
        status_stats = {}
        for status in ThreatStatus:
            query = select(func.count()).select_from(Threat).where(Threat.status == status)
            result = await db.execute(query)
            status_stats[status.value] = result.scalar()
            
        # Count by category
        category_stats = {}
        for category in ThreatCategory:
            query = select(func.count()).select_from(Threat).where(Threat.category == category)
            result = await db.execute(query)
            category_stats[category.value] = result.scalar()
            
        # Latest threats
        latest_query = select(Threat).order_by(Threat.discovered_at.desc()).limit(5)
        latest_result = await db.execute(latest_query)
        latest_threats = [threat.to_dict() for threat in latest_result.scalars().all()]
        
        # Return statistics
        return {
            "total_count": total_count,
            "by_severity": severity_stats,
            "by_status": status_stats,
            "by_category": category_stats,
            "latest_threats": latest_threats
        }
    except Exception as e:
        logger.error(f"Error getting threat statistics: {e}")
        return {
            "total_count": 0,
            "by_severity": {},
            "by_status": {},
            "by_category": {},
            "latest_threats": []
        }