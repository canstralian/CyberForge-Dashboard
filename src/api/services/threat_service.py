"""
Service for threat operations.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union

from src.models.threat import Threat, ThreatSeverity, ThreatStatus, ThreatCategory
from src.models.indicator import Indicator, IndicatorType
from src.api.schemas import PaginationParams

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
        
    Returns:
        Threat: Created threat
    """
    db_threat = Threat(
        title=title,
        description=description,
        severity=severity,
        category=category,
        status=status,
        source_url=source_url,
        source_name=source_name,
        source_type=source_type,
        discovered_at=datetime.utcnow(),
        affected_entity=affected_entity,
        affected_entity_type=affected_entity_type,
        confidence_score=confidence_score,
        risk_score=risk_score,
    )
    
    db.add(db_threat)
    await db.commit()
    await db.refresh(db_threat)
    
    return db_threat

async def get_threat_by_id(db: AsyncSession, threat_id: int) -> Optional[Threat]:
    """
    Get threat by ID.
    
    Args:
        db: Database session
        threat_id: Threat ID
        
    Returns:
        Optional[Threat]: Threat or None if not found
    """
    result = await db.execute(select(Threat).filter(Threat.id == threat_id))
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
    Get threats with filtering and pagination.
    
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
        query = query.filter(Threat.severity.in_(severity))
    
    if status:
        query = query.filter(Threat.status.in_(status))
    
    if category:
        query = query.filter(Threat.category.in_(category))
    
    if search_query:
        search_filter = or_(
            Threat.title.ilike(f"%{search_query}%"),
            Threat.description.ilike(f"%{search_query}%")
        )
        query = query.filter(search_filter)
    
    if from_date:
        query = query.filter(Threat.discovered_at >= from_date)
    
    if to_date:
        query = query.filter(Threat.discovered_at <= to_date)
    
    # Apply pagination
    query = query.order_by(Threat.discovered_at.desc())
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
    
    Args:
        db: Database session
        severity: Filter by severity
        status: Filter by status
        category: Filter by category
        search_query: Search in title and description
        from_date: Filter by discovered_at >= from_date
        to_date: Filter by discovered_at <= to_date
        
    Returns:
        int: Count of threats
    """
    query = select(func.count(Threat.id))
    
    # Apply filters (same as in get_threats)
    if severity:
        query = query.filter(Threat.severity.in_(severity))
    
    if status:
        query = query.filter(Threat.status.in_(status))
    
    if category:
        query = query.filter(Threat.category.in_(category))
    
    if search_query:
        search_filter = or_(
            Threat.title.ilike(f"%{search_query}%"),
            Threat.description.ilike(f"%{search_query}%")
        )
        query = query.filter(search_filter)
    
    if from_date:
        query = query.filter(Threat.discovered_at >= from_date)
    
    if to_date:
        query = query.filter(Threat.discovered_at <= to_date)
    
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
) -> Optional[Threat]:
    """
    Update threat.
    
    Args:
        db: Database session
        threat_id: Threat ID
        title: New title
        description: New description
        severity: New severity
        status: New status
        category: New category
        affected_entity: New affected entity
        affected_entity_type: New affected entity type
        confidence_score: New confidence score
        risk_score: New risk score
        
    Returns:
        Optional[Threat]: Updated threat or None if not found
    """
    threat = await get_threat_by_id(db, threat_id)
    if not threat:
        return None
    
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
    
    threat.updated_at = datetime.utcnow()
    
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
    confidence_score: float = 0.0,
) -> Indicator:
    """
    Add an indicator to a threat.
    
    Args:
        db: Database session
        threat_id: Threat ID
        value: Indicator value
        indicator_type: Indicator type
        description: Description of the indicator
        is_verified: Whether the indicator is verified
        context: Context of the indicator
        source: Source of the indicator
        confidence_score: Confidence score (0-1)
        
    Returns:
        Indicator: Created indicator
    """
    # Check if threat exists
    threat = await get_threat_by_id(db, threat_id)
    if not threat:
        raise ValueError(f"Threat with ID {threat_id} not found")
    
    # Create indicator
    db_indicator = Indicator(
        threat_id=threat_id,
        value=value,
        indicator_type=indicator_type,
        description=description,
        is_verified=is_verified,
        context=context,
        source=source,
        confidence_score=confidence_score,
        first_seen=datetime.utcnow(),
        last_seen=datetime.utcnow(),
    )
    
    db.add(db_indicator)
    await db.commit()
    await db.refresh(db_indicator)
    
    return db_indicator

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
    # Set default time range if not provided
    if not to_date:
        to_date = datetime.utcnow()
    
    if not from_date:
        from_date = to_date - timedelta(days=30)
    
    # Get count by severity
    severity_counts = {}
    for severity in ThreatSeverity:
        query = select(func.count(Threat.id)).filter(and_(
            Threat.severity == severity,
            Threat.discovered_at >= from_date,
            Threat.discovered_at <= to_date,
        ))
        result = await db.execute(query)
        severity_counts[severity.value] = result.scalar() or 0
    
    # Get count by status
    status_counts = {}
    for status in ThreatStatus:
        query = select(func.count(Threat.id)).filter(and_(
            Threat.status == status,
            Threat.discovered_at >= from_date,
            Threat.discovered_at <= to_date,
        ))
        result = await db.execute(query)
        status_counts[status.value] = result.scalar() or 0
    
    # Get count by category
    category_counts = {}
    for category in ThreatCategory:
        query = select(func.count(Threat.id)).filter(and_(
            Threat.category == category,
            Threat.discovered_at >= from_date,
            Threat.discovered_at <= to_date,
        ))
        result = await db.execute(query)
        category_counts[category.value] = result.scalar() or 0
    
    # Get total count
    query = select(func.count(Threat.id)).filter(and_(
        Threat.discovered_at >= from_date,
        Threat.discovered_at <= to_date,
    ))
    result = await db.execute(query)
    total_count = result.scalar() or 0
    
    # Get count by day
    time_series = []
    current_date = from_date.date()
    end_date = to_date.date()
    
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        query = select(func.count(Threat.id)).filter(and_(
            Threat.discovered_at >= datetime.combine(current_date, datetime.min.time()),
            Threat.discovered_at < datetime.combine(next_date, datetime.min.time()),
        ))
        result = await db.execute(query)
        count = result.scalar() or 0
        time_series.append({
            "date": current_date.isoformat(),
            "count": count
        })
        current_date = next_date
    
    # Return statistics
    return {
        "total_count": total_count,
        "severity_counts": severity_counts,
        "status_counts": status_counts,
        "category_counts": category_counts,
        "time_series": time_series,
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
    }