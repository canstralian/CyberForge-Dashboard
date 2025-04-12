"""
Service for working with intelligence reports.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func, desc, and_, or_
from typing import List, Optional, Dict, Any, Union
import logging
from datetime import datetime

from src.models.report import Report, ReportType, ReportStatus
from src.models.threat import ThreatSeverity
from src.api.schemas import PaginationParams

# Configure logger
logger = logging.getLogger(__name__)


async def create_report(
    db: AsyncSession,
    title: str,
    summary: str,
    content: str,
    report_type: ReportType,
    report_id: str,
    status: ReportStatus = ReportStatus.DRAFT,
    severity: Optional[ThreatSeverity] = None,
    publish_date: Optional[datetime] = None,
    time_period_start: Optional[datetime] = None,
    time_period_end: Optional[datetime] = None,
    keywords: Optional[List[str]] = None,
    source_data: Optional[Dict[str, Any]] = None,
    author_id: Optional[int] = None,
) -> Report:
    """
    Create a new intelligence report.
    
    Args:
        db: Database session
        title: Report title
        summary: Report summary
        content: Report content
        report_type: Type of report
        report_id: Custom ID for the report
        status: Report status
        severity: Report severity
        publish_date: Publication date
        time_period_start: Start of time period covered
        time_period_end: End of time period covered
        keywords: List of keywords related to the report
        source_data: Sources and references
        author_id: ID of the report author
        
    Returns:
        Report: Created report
    """
    report = Report(
        title=title,
        summary=summary,
        content=content,
        report_type=report_type,
        report_id=report_id,
        status=status,
        severity=severity,
        publish_date=publish_date,
        time_period_start=time_period_start,
        time_period_end=time_period_end,
        keywords=keywords or [],
        source_data=source_data or {},
        author_id=author_id,
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    return report


async def get_report_by_id(db: AsyncSession, report_id: int) -> Optional[Report]:
    """
    Get report by ID.
    
    Args:
        db: Database session
        report_id: Report ID
        
    Returns:
        Optional[Report]: Found report or None
    """
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    return result.scalars().first()


async def get_report_by_custom_id(db: AsyncSession, custom_id: str) -> Optional[Report]:
    """
    Get report by custom ID.
    
    Args:
        db: Database session
        custom_id: Custom report ID (e.g., RPT-2023-0001)
        
    Returns:
        Optional[Report]: Found report or None
    """
    result = await db.execute(
        select(Report).where(Report.report_id == custom_id)
    )
    return result.scalars().first()


async def get_reports(
    db: AsyncSession,
    pagination: PaginationParams,
    report_type: Optional[List[ReportType]] = None,
    status: Optional[List[ReportStatus]] = None,
    severity: Optional[List[ThreatSeverity]] = None,
    search_query: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    author_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> List[Report]:
    """
    Get reports with filtering.
    
    Args:
        db: Database session
        pagination: Pagination parameters
        report_type: Filter by report type
        status: Filter by status
        severity: Filter by severity
        search_query: Search in title and summary
        keywords: Filter by keywords
        author_id: Filter by author ID
        from_date: Filter by created_at >= from_date
        to_date: Filter by created_at <= to_date
        
    Returns:
        List[Report]: List of reports
    """
    query = select(Report)
    
    # Apply filters
    if report_type:
        query = query.where(Report.report_type.in_(report_type))
    
    if status:
        query = query.where(Report.status.in_(status))
    
    if severity:
        query = query.where(Report.severity.in_(severity))
    
    if search_query:
        search_filter = or_(
            Report.title.ilike(f"%{search_query}%"),
            Report.summary.ilike(f"%{search_query}%"),
            Report.content.ilike(f"%{search_query}%"),
        )
        query = query.where(search_filter)
    
    if keywords:
        # For JSON arrays, need to use a more complex query
        for keyword in keywords:
            query = query.where(Report.keywords.contains([keyword]))
    
    if author_id:
        query = query.where(Report.author_id == author_id)
    
    if from_date:
        query = query.where(Report.created_at >= from_date)
    
    if to_date:
        query = query.where(Report.created_at <= to_date)
    
    # Apply pagination
    query = query.order_by(desc(Report.created_at))
    query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)
    
    result = await db.execute(query)
    return result.scalars().all()


async def count_reports(
    db: AsyncSession,
    report_type: Optional[List[ReportType]] = None,
    status: Optional[List[ReportStatus]] = None,
    severity: Optional[List[ThreatSeverity]] = None,
    search_query: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    author_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> int:
    """
    Count reports with filtering.
    
    Args are the same as get_reports, except pagination.
    
    Returns:
        int: Count of matching reports
    """
    query = select(func.count(Report.id))
    
    # Apply filters
    if report_type:
        query = query.where(Report.report_type.in_(report_type))
    
    if status:
        query = query.where(Report.status.in_(status))
    
    if severity:
        query = query.where(Report.severity.in_(severity))
    
    if search_query:
        search_filter = or_(
            Report.title.ilike(f"%{search_query}%"),
            Report.summary.ilike(f"%{search_query}%"),
            Report.content.ilike(f"%{search_query}%"),
        )
        query = query.where(search_filter)
    
    if keywords:
        # For JSON arrays, need to use a more complex query
        for keyword in keywords:
            query = query.where(Report.keywords.contains([keyword]))
    
    if author_id:
        query = query.where(Report.author_id == author_id)
    
    if from_date:
        query = query.where(Report.created_at >= from_date)
    
    if to_date:
        query = query.where(Report.created_at <= to_date)
    
    result = await db.execute(query)
    return result.scalar()


async def update_report(
    db: AsyncSession,
    report_id: int,
    title: Optional[str] = None,
    summary: Optional[str] = None,
    content: Optional[str] = None,
    report_type: Optional[ReportType] = None,
    status: Optional[ReportStatus] = None,
    severity: Optional[ThreatSeverity] = None,
    publish_date: Optional[datetime] = None,
    time_period_start: Optional[datetime] = None,
    time_period_end: Optional[datetime] = None,
    keywords: Optional[List[str]] = None,
    source_data: Optional[Dict[str, Any]] = None,
) -> Optional[Report]:
    """
    Update a report.
    
    Args:
        db: Database session
        report_id: Report ID
        Other args: Fields to update
        
    Returns:
        Optional[Report]: Updated report or None
    """
    report = await get_report_by_id(db, report_id)
    
    if not report:
        return None
    
    # Update fields if provided
    if title is not None:
        report.title = title
    
    if summary is not None:
        report.summary = summary
    
    if content is not None:
        report.content = content
    
    if report_type is not None:
        report.report_type = report_type
    
    if status is not None:
        report.status = status
    
    if severity is not None:
        report.severity = severity
    
    if publish_date is not None:
        report.publish_date = publish_date
    
    if time_period_start is not None:
        report.time_period_start = time_period_start
    
    if time_period_end is not None:
        report.time_period_end = time_period_end
    
    if keywords is not None:
        report.keywords = keywords
    
    if source_data is not None:
        report.source_data = source_data
    
    await db.commit()
    await db.refresh(report)
    
    return report


async def add_threat_to_report(
    db: AsyncSession,
    report_id: int,
    threat_id: int,
) -> Optional[Report]:
    """
    Add a threat to a report.
    
    Args:
        db: Database session
        report_id: Report ID
        threat_id: Threat ID
        
    Returns:
        Optional[Report]: Updated report or None
    """
    from src.api.services.threat_service import get_threat_by_id
    
    # Get report and threat
    report = await get_report_by_id(db, report_id)
    threat = await get_threat_by_id(db, threat_id)
    
    if not report or not threat:
        return None
    
    # Add threat to report
    report.threats.append(threat)
    await db.commit()
    await db.refresh(report)
    
    return report


async def remove_threat_from_report(
    db: AsyncSession,
    report_id: int,
    threat_id: int,
) -> Optional[Report]:
    """
    Remove a threat from a report.
    
    Args:
        db: Database session
        report_id: Report ID
        threat_id: Threat ID
        
    Returns:
        Optional[Report]: Updated report or None
    """
    from src.api.services.threat_service import get_threat_by_id
    
    # Get report and threat
    report = await get_report_by_id(db, report_id)
    threat = await get_threat_by_id(db, threat_id)
    
    if not report or not threat:
        return None
    
    # Remove threat from report
    if threat in report.threats:
        report.threats.remove(threat)
        await db.commit()
        await db.refresh(report)
    
    return report


async def publish_report(
    db: AsyncSession,
    report_id: int,
) -> Optional[Report]:
    """
    Publish a report.
    
    Args:
        db: Database session
        report_id: Report ID
        
    Returns:
        Optional[Report]: Updated report or None
    """
    report = await get_report_by_id(db, report_id)
    
    if not report:
        return None
    
    # Update status and publish date
    report.status = ReportStatus.PUBLISHED
    
    if not report.publish_date:
        report.publish_date = datetime.utcnow()
    
    await db.commit()
    await db.refresh(report)
    
    return report


async def archive_report(
    db: AsyncSession,
    report_id: int,
) -> Optional[Report]:
    """
    Archive a report.
    
    Args:
        db: Database session
        report_id: Report ID
        
    Returns:
        Optional[Report]: Updated report or None
    """
    report = await get_report_by_id(db, report_id)
    
    if not report:
        return None
    
    # Update status
    report.status = ReportStatus.ARCHIVED
    await db.commit()
    await db.refresh(report)
    
    return report