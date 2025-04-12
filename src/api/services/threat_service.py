"""
Service for working with threat data.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func, desc, and_, or_
from typing import List, Optional, Dict, Any, Union
import logging
from datetime import datetime

from src.models.threat import Threat, ThreatSeverity, ThreatStatus, ThreatCategory
from src.models.indicator import Indicator, IndicatorType
from src.api.schemas import PaginationParams

# Configure logger
logger = logging.getLogger(__name__)


async def create_threat(
    db: AsyncSession,
    title: str,
    description: str,
    severity: ThreatSeverity,
    category: ThreatCategory,
    status: ThreatStatus = ThreatStatus.NEW,
    source_url: Optional[str] = None,
    source_name: Optional[str] = None,
    source_type: Optional[str] = None,
    affected_entity: Optional[str] = None,
    affected_entity_type: Optional[str] = None,
    confidence_score: float = 0.0,
    risk_score: float = 0.0,
    raw_content: Optional[str] = None,
    meta_data: Optional[Dict[str, Any]] = None,
) -> Threat:
    """
    Create a new threat.
    
    Args:
        db: Database session
        title: Threat title
        description: Threat description
        severity: Threat severity
        category: Threat category
        status: Threat status
        source_url: URL of the source
        source_name: Name of the source
        source_type: Type of source
        affected_entity: Name of affected entity
        affected_entity_type: Type of affected entity
        confidence_score: Confidence score (0-1)
        risk_score: Risk score (0-1)
        raw_content: Raw content of the threat
        meta_data: Additional metadata
        
    Returns:
        Threat: Created threat
    """
    threat = Threat(
        title=title,
        description=description,
        severity=severity,
        status=status,
        category=category,
        source_url=source_url,
        source_name=source_name,
        source_type=source_type,
        affected_entity=affected_entity,
        affected_entity_type=affected_entity_type,
        confidence_score=confidence_score,
        risk_score=risk_score,
        raw_content=raw_content,
        meta_data=meta_data or {},
    )
    
    db.add(threat)
    await db.commit()
    await db.refresh(threat)
    
    return threat


async def get_threat_by_id(db: AsyncSession, threat_id: int) -> Optional[Threat]:
    """
    Get threat by ID.
    
    Args:
        db: Database session
        threat_id: Threat ID
        
    Returns:
        Optional[Threat]: Found threat or None
    """
    result = await db.execute(
        select(Threat).where(Threat.id == threat_id)
    )
    return result.scalars().first()


async def get_threats(
    db: AsyncSession,
    pagination: PaginationParams,
    severity: Optional[List[ThreatSeverity]] = None,
    status: Optional[List[ThreatStatus]] = None,
    category: Optional[List[ThreatCategory]] = None,
    search_query: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> List[Threat]:
    """
    Get threats with filtering.
    
    Args:
        db: Database session
        pagination: Pagination parameters
        severity: Filter by severity
        status: Filter by status
        category: Filter by category
        search_query: Search in title and description
        from_date: Filter by discovered_at >= from_date
        to_date: Filter by discovered_at <= to_date
        
    Returns:
        List[Threat]: List of threats
    """
    query = select(Threat)
    
    # Apply filters
    if severity:
        query = query.where(Threat.severity.in_(severity))
    
    if status:
        query = query.where(Threat.status.in_(status))
    
    if category:
        query = query.where(Threat.category.in_(category))
    
    if search_query:
        search_filter = or_(
            Threat.title.ilike(f"%{search_query}%"),
            Threat.description.ilike(f"%{search_query}%"),
            Threat.affected_entity.ilike(f"%{search_query}%"),
        )
        query = query.where(search_filter)
    
    if from_date:
        query = query.where(Threat.discovered_at >= from_date)
    
    if to_date:
        query = query.where(Threat.discovered_at <= to_date)
    
    # Apply pagination
    query = query.order_by(desc(Threat.discovered_at))
    query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)
    
    result = await db.execute(query)
    return result.scalars().all()


async def count_threats(
    db: AsyncSession,
    severity: Optional[List[ThreatSeverity]] = None,
    status: Optional[List[ThreatStatus]] = None,
    category: Optional[List[ThreatCategory]] = None,
    search_query: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> int:
    """
    Count threats with filtering.
    
    Args are the same as get_threats, except pagination.
    
    Returns:
        int: Count of matching threats
    """
    query = select(func.count(Threat.id))
    
    # Apply filters
    if severity:
        query = query.where(Threat.severity.in_(severity))
    
    if status:
        query = query.where(Threat.status.in_(status))
    
    if category:
        query = query.where(Threat.category.in_(category))
    
    if search_query:
        search_filter = or_(
            Threat.title.ilike(f"%{search_query}%"),
            Threat.description.ilike(f"%{search_query}%"),
            Threat.affected_entity.ilike(f"%{search_query}%"),
        )
        query = query.where(search_filter)
    
    if from_date:
        query = query.where(Threat.discovered_at >= from_date)
    
    if to_date:
        query = query.where(Threat.discovered_at <= to_date)
    
    result = await db.execute(query)
    return result.scalar()


async def update_threat(
    db: AsyncSession,
    threat_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    severity: Optional[ThreatSeverity] = None,
    status: Optional[ThreatStatus] = None,
    category: Optional[ThreatCategory] = None,
    affected_entity: Optional[str] = None,
    affected_entity_type: Optional[str] = None,
    confidence_score: Optional[float] = None,
    risk_score: Optional[float] = None,
    meta_data: Optional[Dict[str, Any]] = None,
) -> Optional[Threat]:
    """
    Update a threat.
    
    Args:
        db: Database session
        threat_id: Threat ID
        Other args: Fields to update
        
    Returns:
        Optional[Threat]: Updated threat or None
    """
    threat = await get_threat_by_id(db, threat_id)
    
    if not threat:
        return None
    
    # Update fields if provided
    if title is not None:
        threat.title = title
    
    if description is not None:
        threat.description = description
    
    if severity is not None:
        threat.severity = severity
    
    if status is not None:
        threat.status = status
    
    if category is not None:
        threat.category = category
    
    if affected_entity is not None:
        threat.affected_entity = affected_entity
    
    if affected_entity_type is not None:
        threat.affected_entity_type = affected_entity_type
    
    if confidence_score is not None:
        threat.confidence_score = confidence_score
    
    if risk_score is not None:
        threat.risk_score = risk_score
    
    if meta_data is not None:
        threat.meta_data = meta_data
    
    await db.commit()
    await db.refresh(threat)
    
    return threat


async def add_indicator_to_threat(
    db: AsyncSession,
    threat_id: int,
    value: str,
    indicator_type: IndicatorType,
    description: Optional[str] = None,
    is_verified: bool = False,
    context: Optional[str] = None,
    source: Optional[str] = None,
) -> Optional[Indicator]:
    """
    Add an indicator to a threat.
    
    Args:
        db: Database session
        threat_id: Threat ID
        value: Indicator value
        indicator_type: Indicator type
        description: Indicator description
        is_verified: Whether the indicator is verified
        context: Context of the indicator
        source: Source of the indicator
        
    Returns:
        Optional[Indicator]: Created indicator or None
    """
    # Ensure threat exists
    threat = await get_threat_by_id(db, threat_id)
    
    if not threat:
        return None
    
    # Create indicator
    indicator = Indicator(
        value=value,
        type=indicator_type,
        description=description,
        threat_id=threat_id,
        is_verified=is_verified,
        context=context,
        source=source,
    )
    
    db.add(indicator)
    await db.commit()
    await db.refresh(indicator)
    
    return indicator


async def get_threat_statistics(
    db: AsyncSession,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Get threat statistics.
    
    Args:
        db: Database session
        from_date: Filter by discovered_at >= from_date
        to_date: Filter by discovered_at <= to_date
        
    Returns:
        Dict[str, Any]: Threat statistics
    """
    # Base query filters
    where_clauses = []
    if from_date:
        where_clauses.append(Threat.discovered_at >= from_date)
    if to_date:
        where_clauses.append(Threat.discovered_at <= to_date)
    
    # Get total count
    total_query = select(func.count(Threat.id))
    if where_clauses:
        total_query = total_query.where(and_(*where_clauses))
    total_result = await db.execute(total_query)
    total_threats = total_result.scalar()
    
    # Get count by severity
    severity_query = select(Threat.severity, func.count(Threat.id).label('count'))
    if where_clauses:
        severity_query = severity_query.where(and_(*where_clauses))
    severity_query = severity_query.group_by(Threat.severity)
    severity_result = await db.execute(severity_query)
    severity_counts = {severity.value: count for severity, count in severity_result.all()}
    
    # Ensure all severities are represented
    for severity in ThreatSeverity:
        if severity.value not in severity_counts:
            severity_counts[severity.value] = 0
    
    # Get count by category
    category_query = select(Threat.category, func.count(Threat.id).label('count'))
    if where_clauses:
        category_query = category_query.where(and_(*where_clauses))
    category_query = category_query.group_by(Threat.category)
    category_result = await db.execute(category_query)
    category_counts = {category.value: count for category, count in category_result.all()}
    
    # Ensure all categories are represented
    for category in ThreatCategory:
        if category.value not in category_counts:
            category_counts[category.value] = 0
    
    # Get count by status
    status_query = select(Threat.status, func.count(Threat.id).label('count'))
    if where_clauses:
        status_query = status_query.where(and_(*where_clauses))
    status_query = status_query.group_by(Threat.status)
    status_result = await db.execute(status_query)
    status_counts = {status.value: count for status, count in status_result.all()}
    
    # Ensure all statuses are represented
    for status in ThreatStatus:
        if status.value not in status_counts:
            status_counts[status.value] = 0
    
    # Compile statistics
    return {
        "total_threats": total_threats,
        "by_severity": severity_counts,
        "by_category": category_counts,
        "by_status": status_counts,
    }