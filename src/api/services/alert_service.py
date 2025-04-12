"""
Service for working with alerts.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func, desc, and_, or_
from typing import List, Optional, Dict, Any, Union
import logging
from datetime import datetime

from src.models.alert import Alert, AlertStatus, AlertCategory
from src.models.threat import ThreatSeverity
from src.api.schemas import PaginationParams

# Configure logger
logger = logging.getLogger(__name__)


async def create_alert(
    db: AsyncSession,
    title: str,
    description: str,
    severity: ThreatSeverity,
    category: AlertCategory,
    source_url: Optional[str] = None,
    threat_id: Optional[int] = None,
    mention_id: Optional[int] = None,
    assigned_to_id: Optional[int] = None,
) -> Alert:
    """
    Create a new alert.
    
    Args:
        db: Database session
        title: Alert title
        description: Alert description
        severity: Alert severity
        category: Alert category
        source_url: Source URL for the alert
        threat_id: ID of related threat
        mention_id: ID of related dark web mention
        assigned_to_id: ID of user assigned to the alert
        
    Returns:
        Alert: Created alert
    """
    alert = Alert(
        title=title,
        description=description,
        severity=severity,
        category=category,
        source_url=source_url,
        threat_id=threat_id,
        mention_id=mention_id,
        assigned_to_id=assigned_to_id,
    )
    
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    return alert


async def get_alert_by_id(db: AsyncSession, alert_id: int) -> Optional[Alert]:
    """
    Get alert by ID.
    
    Args:
        db: Database session
        alert_id: Alert ID
        
    Returns:
        Optional[Alert]: Found alert or None
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    return result.scalars().first()


async def get_alerts(
    db: AsyncSession,
    pagination: PaginationParams,
    severity: Optional[List[ThreatSeverity]] = None,
    status: Optional[List[AlertStatus]] = None,
    category: Optional[List[AlertCategory]] = None,
    is_read: Optional[bool] = None,
    threat_id: Optional[int] = None,
    assigned_to_id: Optional[int] = None,
    search_query: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> List[Alert]:
    """
    Get alerts with filtering.
    
    Args:
        db: Database session
        pagination: Pagination parameters
        severity: Filter by severity
        status: Filter by status
        category: Filter by category
        is_read: Filter by read status
        threat_id: Filter by threat ID
        assigned_to_id: Filter by assigned user ID
        search_query: Search in title and description
        from_date: Filter by generated_at >= from_date
        to_date: Filter by generated_at <= to_date
        
    Returns:
        List[Alert]: List of alerts
    """
    query = select(Alert)
    
    # Apply filters
    if severity:
        query = query.where(Alert.severity.in_(severity))
    
    if status:
        query = query.where(Alert.status.in_(status))
    
    if category:
        query = query.where(Alert.category.in_(category))
    
    if is_read is not None:
        query = query.where(Alert.is_read == is_read)
    
    if threat_id:
        query = query.where(Alert.threat_id == threat_id)
    
    if assigned_to_id:
        query = query.where(Alert.assigned_to_id == assigned_to_id)
    
    if search_query:
        search_filter = or_(
            Alert.title.ilike(f"%{search_query}%"),
            Alert.description.ilike(f"%{search_query}%"),
        )
        query = query.where(search_filter)
    
    if from_date:
        query = query.where(Alert.generated_at >= from_date)
    
    if to_date:
        query = query.where(Alert.generated_at <= to_date)
    
    # Apply pagination
    query = query.order_by(desc(Alert.generated_at))
    query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)
    
    result = await db.execute(query)
    return result.scalars().all()


async def count_alerts(
    db: AsyncSession,
    severity: Optional[List[ThreatSeverity]] = None,
    status: Optional[List[AlertStatus]] = None,
    category: Optional[List[AlertCategory]] = None,
    is_read: Optional[bool] = None,
    threat_id: Optional[int] = None,
    assigned_to_id: Optional[int] = None,
    search_query: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> int:
    """
    Count alerts with filtering.
    
    Args are the same as get_alerts, except pagination.
    
    Returns:
        int: Count of matching alerts
    """
    query = select(func.count(Alert.id))
    
    # Apply filters
    if severity:
        query = query.where(Alert.severity.in_(severity))
    
    if status:
        query = query.where(Alert.status.in_(status))
    
    if category:
        query = query.where(Alert.category.in_(category))
    
    if is_read is not None:
        query = query.where(Alert.is_read == is_read)
    
    if threat_id:
        query = query.where(Alert.threat_id == threat_id)
    
    if assigned_to_id:
        query = query.where(Alert.assigned_to_id == assigned_to_id)
    
    if search_query:
        search_filter = or_(
            Alert.title.ilike(f"%{search_query}%"),
            Alert.description.ilike(f"%{search_query}%"),
        )
        query = query.where(search_filter)
    
    if from_date:
        query = query.where(Alert.generated_at >= from_date)
    
    if to_date:
        query = query.where(Alert.generated_at <= to_date)
    
    result = await db.execute(query)
    return result.scalar()


async def update_alert_status(
    db: AsyncSession,
    alert_id: int,
    status: AlertStatus,
    action_taken: Optional[str] = None,
) -> Optional[Alert]:
    """
    Update alert status.
    
    Args:
        db: Database session
        alert_id: Alert ID
        status: New status
        action_taken: Description of action taken
        
    Returns:
        Optional[Alert]: Updated alert or None
    """
    alert = await get_alert_by_id(db, alert_id)
    
    if not alert:
        return None
    
    # Update fields
    alert.status = status
    
    if action_taken:
        alert.action_taken = action_taken
    
    if status == AlertStatus.RESOLVED:
        alert.resolved_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(alert)
    
    return alert


async def mark_alert_as_read(db: AsyncSession, alert_id: int) -> Optional[Alert]:
    """
    Mark alert as read.
    
    Args:
        db: Database session
        alert_id: Alert ID
        
    Returns:
        Optional[Alert]: Updated alert or None
    """
    alert = await get_alert_by_id(db, alert_id)
    
    if not alert:
        return None
    
    alert.is_read = True
    await db.commit()
    await db.refresh(alert)
    
    return alert


async def assign_alert(
    db: AsyncSession,
    alert_id: int,
    user_id: int
) -> Optional[Alert]:
    """
    Assign alert to a user.
    
    Args:
        db: Database session
        alert_id: Alert ID
        user_id: ID of user to assign
        
    Returns:
        Optional[Alert]: Updated alert or None
    """
    alert = await get_alert_by_id(db, alert_id)
    
    if not alert:
        return None
    
    alert.assigned_to_id = user_id
    await db.commit()
    await db.refresh(alert)
    
    return alert


async def get_alert_counts_by_severity(
    db: AsyncSession,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> Dict[str, int]:
    """
    Get count of alerts by severity.
    
    Args:
        db: Database session
        from_date: Filter by generated_at >= from_date
        to_date: Filter by generated_at <= to_date
        
    Returns:
        Dict[str, int]: Mapping of severity to count
    """
    query = select(Alert.severity, func.count(Alert.id).label('count'))
    
    if from_date:
        query = query.where(Alert.generated_at >= from_date)
    
    if to_date:
        query = query.where(Alert.generated_at <= to_date)
    
    query = query.group_by(Alert.severity)
    
    result = await db.execute(query)
    counts = {severity.value: count for severity, count in result.all()}
    
    # Ensure all severities are represented
    for severity in ThreatSeverity:
        if severity.value not in counts:
            counts[severity.value] = 0
    
    return counts