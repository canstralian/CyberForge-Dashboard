"""
Database integration for Streamlit application.

This module provides functions to interact with the database for the Streamlit frontend.
It wraps the async database functions in sync functions for Streamlit compatibility.
"""
import os
import asyncio
import pandas as pd
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Import database models
from src.models.threat import Threat, ThreatSeverity, ThreatStatus, ThreatCategory
from src.models.indicator import Indicator, IndicatorType
from src.models.dark_web_content import DarkWebContent, DarkWebMention, ContentType, ContentStatus
from src.models.alert import Alert, AlertStatus, AlertCategory
from src.models.report import Report, ReportType, ReportStatus

# Import service functions
from src.api.services.dark_web_content_service import (
    create_content, get_content_by_id, get_contents, count_contents,
    create_mention, get_mentions, create_threat_from_content
)
from src.api.services.alert_service import (
    create_alert, get_alert_by_id, get_alerts, count_alerts,
    update_alert_status, mark_alert_as_read, get_alert_counts_by_severity
)
from src.api.services.threat_service import (
    create_threat, get_threat_by_id, get_threats, count_threats,
    update_threat, add_indicator_to_threat, get_threat_statistics
)
from src.api.services.report_service import (
    create_report, get_report_by_id, get_reports, count_reports,
    update_report, add_threat_to_report, publish_report
)

# Import schemas
from src.api.schemas import PaginationParams

# Get database URL from environment
db_url = os.getenv("DATABASE_URL", "")
if db_url.startswith("postgresql://"):
    # Remove sslmode parameter if present which causes issues with asyncpg
    if "?" in db_url:
        base_url, params = db_url.split("?", 1)
        param_list = params.split("&")
        filtered_params = [p for p in param_list if not p.startswith("sslmode=")]
        if filtered_params:
            db_url = f"{base_url}?{'&'.join(filtered_params)}"
        else:
            db_url = base_url
    
    ASYNC_DATABASE_URL = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    future=True,
    pool_size=5,
    max_overflow=10
)

# Create async session factory
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


def run_async(coro):
    """Run an async function in a sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


async def get_session():
    """Get an async database session."""
    async with async_session() as session:
        yield session


def get_db_session():
    """Get a database session for use in Streamlit."""
    try:
        session_gen = get_session().__aiter__()
        return run_async(session_gen.__anext__())
    except StopAsyncIteration:
        return None


# Dark Web Content functions
def get_dark_web_contents(
    page: int = 1,
    size: int = 10,
    content_type: Optional[List[ContentType]] = None,
    content_status: Optional[List[ContentStatus]] = None,
    source_name: Optional[str] = None,
    search_query: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> pd.DataFrame:
    """
    Get dark web contents as a DataFrame.
    
    Args:
        page: Page number
        size: Page size
        content_type: Filter by content type
        content_status: Filter by content status
        source_name: Filter by source name
        search_query: Search in title and content
        from_date: Filter by scraped_at >= from_date
        to_date: Filter by scraped_at <= to_date
        
    Returns:
        pd.DataFrame: DataFrame with dark web contents
    """
    session = get_db_session()
    
    if not session:
        return pd.DataFrame()
    
    contents = run_async(get_contents(
        db=session,
        pagination=PaginationParams(page=page, size=size),
        content_type=content_type,
        content_status=content_status,
        source_name=source_name,
        search_query=search_query,
        from_date=from_date,
        to_date=to_date,
    ))
    
    if not contents:
        return pd.DataFrame()
    
    # Convert to DataFrame
    data = []
    for content in contents:
        data.append({
            "id": content.id,
            "url": content.url,
            "title": content.title,
            "content_type": content.content_type.value if content.content_type else None,
            "content_status": content.content_status.value if content.content_status else None,
            "source_name": content.source_name,
            "source_type": content.source_type,
            "language": content.language,
            "scraped_at": content.scraped_at,
            "relevance_score": content.relevance_score,
            "sentiment_score": content.sentiment_score,
        })
    
    return pd.DataFrame(data)


def add_dark_web_content(
    url: str,
    content: str,
    title: Optional[str] = None,
    content_type: ContentType = ContentType.OTHER,
    source_name: Optional[str] = None,
    source_type: Optional[str] = None,
) -> Optional[DarkWebContent]:
    """
    Add a new dark web content.
    
    Args:
        url: URL of the content
        content: Text content
        title: Title of the content
        content_type: Type of content
        source_name: Name of the source
        source_type: Type of source
        
    Returns:
        Optional[DarkWebContent]: Created content or None
    """
    session = get_db_session()
    
    if not session:
        return None
    
    return run_async(create_content(
        db=session,
        url=url,
        content=content,
        title=title,
        content_type=content_type,
        source_name=source_name,
        source_type=source_type,
    ))


def get_dark_web_mentions(
    page: int = 1,
    size: int = 10,
    keyword: Optional[str] = None,
    content_id: Optional[int] = None,
    is_verified: Optional[bool] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> pd.DataFrame:
    """
    Get dark web mentions as a DataFrame.
    
    Args:
        page: Page number
        size: Page size
        keyword: Filter by keyword
        content_id: Filter by content ID
        is_verified: Filter by verification status
        from_date: Filter by created_at >= from_date
        to_date: Filter by created_at <= to_date
        
    Returns:
        pd.DataFrame: DataFrame with dark web mentions
    """
    session = get_db_session()
    
    if not session:
        return pd.DataFrame()
    
    mentions = run_async(get_mentions(
        db=session,
        pagination=PaginationParams(page=page, size=size),
        keyword=keyword,
        content_id=content_id,
        is_verified=is_verified,
        from_date=from_date,
        to_date=to_date,
    ))
    
    if not mentions:
        return pd.DataFrame()
    
    # Convert to DataFrame
    data = []
    for mention in mentions:
        data.append({
            "id": mention.id,
            "content_id": mention.content_id,
            "keyword": mention.keyword,
            "snippet": mention.snippet,
            "mention_type": mention.mention_type,
            "confidence": mention.confidence,
            "is_verified": mention.is_verified,
            "created_at": mention.created_at,
        })
    
    return pd.DataFrame(data)


def add_dark_web_mention(
    content_id: int,
    keyword: str,
    context: Optional[str] = None,
    snippet: Optional[str] = None,
) -> Optional[DarkWebMention]:
    """
    Add a new dark web mention.
    
    Args:
        content_id: ID of the content where the mention was found
        keyword: Keyword that was mentioned
        context: Text surrounding the mention
        snippet: Extract of text containing the mention
        
    Returns:
        Optional[DarkWebMention]: Created mention or None
    """
    session = get_db_session()
    
    if not session:
        return None
    
    return run_async(create_mention(
        db=session,
        content_id=content_id,
        keyword=keyword,
        context=context,
        snippet=snippet,
    ))


# Alerts functions
def get_alerts_df(
    page: int = 1,
    size: int = 10,
    severity: Optional[List[ThreatSeverity]] = None,
    status: Optional[List[AlertStatus]] = None,
    category: Optional[List[AlertCategory]] = None,
    is_read: Optional[bool] = None,
    search_query: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> pd.DataFrame:
    """
    Get alerts as a DataFrame.
    
    Args:
        page: Page number
        size: Page size
        severity: Filter by severity
        status: Filter by status
        category: Filter by category
        is_read: Filter by read status
        search_query: Search in title and description
        from_date: Filter by generated_at >= from_date
        to_date: Filter by generated_at <= to_date
        
    Returns:
        pd.DataFrame: DataFrame with alerts
    """
    session = get_db_session()
    
    if not session:
        return pd.DataFrame()
    
    alerts = run_async(get_alerts(
        db=session,
        pagination=PaginationParams(page=page, size=size),
        severity=severity,
        status=status,
        category=category,
        is_read=is_read,
        search_query=search_query,
        from_date=from_date,
        to_date=to_date,
    ))
    
    if not alerts:
        return pd.DataFrame()
    
    # Convert to DataFrame
    data = []
    for alert in alerts:
        data.append({
            "id": alert.id,
            "title": alert.title,
            "description": alert.description,
            "severity": alert.severity.value if alert.severity else None,
            "status": alert.status.value if alert.status else None,
            "category": alert.category.value if alert.category else None,
            "generated_at": alert.generated_at,
            "source_url": alert.source_url,
            "is_read": alert.is_read,
            "threat_id": alert.threat_id,
            "mention_id": alert.mention_id,
            "assigned_to_id": alert.assigned_to_id,
            "action_taken": alert.action_taken,
            "resolved_at": alert.resolved_at,
        })
    
    return pd.DataFrame(data)


def add_alert(
    title: str,
    description: str,
    severity: ThreatSeverity,
    category: AlertCategory,
    source_url: Optional[str] = None,
    threat_id: Optional[int] = None,
    mention_id: Optional[int] = None,
) -> Optional[Alert]:
    """
    Add a new alert.
    
    Args:
        title: Alert title
        description: Alert description
        severity: Alert severity
        category: Alert category
        source_url: Source URL for the alert
        threat_id: ID of related threat
        mention_id: ID of related dark web mention
        
    Returns:
        Optional[Alert]: Created alert or None
    """
    session = get_db_session()
    
    if not session:
        return None
    
    return run_async(create_alert(
        db=session,
        title=title,
        description=description,
        severity=severity,
        category=category,
        source_url=source_url,
        threat_id=threat_id,
        mention_id=mention_id,
    ))


def update_alert(
    alert_id: int,
    status: AlertStatus,
    action_taken: Optional[str] = None,
) -> Optional[Alert]:
    """
    Update alert status.
    
    Args:
        alert_id: Alert ID
        status: New status
        action_taken: Description of action taken
        
    Returns:
        Optional[Alert]: Updated alert or None
    """
    session = get_db_session()
    
    if not session:
        return None
    
    return run_async(update_alert_status(
        db=session,
        alert_id=alert_id,
        status=status,
        action_taken=action_taken,
    ))


def get_alert_severity_counts(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> Dict[str, int]:
    """
    Get count of alerts by severity.
    
    Args:
        from_date: Filter by generated_at >= from_date
        to_date: Filter by generated_at <= to_date
        
    Returns:
        Dict[str, int]: Mapping of severity to count
    """
    session = get_db_session()
    
    if not session:
        return {}
    
    return run_async(get_alert_counts_by_severity(
        db=session,
        from_date=from_date,
        to_date=to_date,
    ))


# Threats functions
def get_threats_df(
    page: int = 1,
    size: int = 10,
    severity: Optional[List[ThreatSeverity]] = None,
    status: Optional[List[ThreatStatus]] = None,
    category: Optional[List[ThreatCategory]] = None,
    search_query: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> pd.DataFrame:
    """
    Get threats as a DataFrame.
    
    Args:
        page: Page number
        size: Page size
        severity: Filter by severity
        status: Filter by status
        category: Filter by category
        search_query: Search in title and description
        from_date: Filter by discovered_at >= from_date
        to_date: Filter by discovered_at <= to_date
        
    Returns:
        pd.DataFrame: DataFrame with threats
    """
    session = get_db_session()
    
    if not session:
        return pd.DataFrame()
    
    threats = run_async(get_threats(
        db=session,
        pagination=PaginationParams(page=page, size=size),
        severity=severity,
        status=status,
        category=category,
        search_query=search_query,
        from_date=from_date,
        to_date=to_date,
    ))
    
    if not threats:
        return pd.DataFrame()
    
    # Convert to DataFrame
    data = []
    for threat in threats:
        data.append({
            "id": threat.id,
            "title": threat.title,
            "description": threat.description,
            "severity": threat.severity.value if threat.severity else None,
            "status": threat.status.value if threat.status else None,
            "category": threat.category.value if threat.category else None,
            "source_url": threat.source_url,
            "source_name": threat.source_name,
            "source_type": threat.source_type,
            "discovered_at": threat.discovered_at,
            "affected_entity": threat.affected_entity,
            "affected_entity_type": threat.affected_entity_type,
            "confidence_score": threat.confidence_score,
            "risk_score": threat.risk_score,
        })
    
    return pd.DataFrame(data)


def add_threat(
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
) -> Optional[Threat]:
    """
    Add a new threat.
    
    Args:
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
        Optional[Threat]: Created threat or None
    """
    session = get_db_session()
    
    if not session:
        return None
    
    return run_async(create_threat(
        db=session,
        title=title,
        description=description,
        severity=severity,
        category=category,
        status=status,
        source_url=source_url,
        source_name=source_name,
        source_type=source_type,
        affected_entity=affected_entity,
        affected_entity_type=affected_entity_type,
        confidence_score=confidence_score,
        risk_score=risk_score,
    ))


def add_indicator(
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
    session = get_db_session()
    
    if not session:
        return None
    
    return run_async(add_indicator_to_threat(
        db=session,
        threat_id=threat_id,
        value=value,
        indicator_type=indicator_type,
        description=description,
        is_verified=is_verified,
        context=context,
        source=source,
    ))


def get_threat_stats(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Get threat statistics.
    
    Args:
        from_date: Filter by discovered_at >= from_date
        to_date: Filter by discovered_at <= to_date
        
    Returns:
        Dict[str, Any]: Threat statistics
    """
    session = get_db_session()
    
    if not session:
        return {}
    
    return run_async(get_threat_statistics(
        db=session,
        from_date=from_date,
        to_date=to_date,
    ))


# Reports functions
def get_reports_df(
    page: int = 1,
    size: int = 10,
    report_type: Optional[List[ReportType]] = None,
    status: Optional[List[ReportStatus]] = None,
    severity: Optional[List[ThreatSeverity]] = None,
    search_query: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> pd.DataFrame:
    """
    Get reports as a DataFrame.
    
    Args:
        page: Page number
        size: Page size
        report_type: Filter by report type
        status: Filter by status
        severity: Filter by severity
        search_query: Search in title and summary
        from_date: Filter by created_at >= from_date
        to_date: Filter by created_at <= to_date
        
    Returns:
        pd.DataFrame: DataFrame with reports
    """
    session = get_db_session()
    
    if not session:
        return pd.DataFrame()
    
    reports = run_async(get_reports(
        db=session,
        pagination=PaginationParams(page=page, size=size),
        report_type=report_type,
        status=status,
        severity=severity,
        search_query=search_query,
        from_date=from_date,
        to_date=to_date,
    ))
    
    if not reports:
        return pd.DataFrame()
    
    # Convert to DataFrame
    data = []
    for report in reports:
        data.append({
            "id": report.id,
            "report_id": report.report_id,
            "title": report.title,
            "summary": report.summary,
            "report_type": report.report_type.value if report.report_type else None,
            "status": report.status.value if report.status else None,
            "severity": report.severity.value if report.severity else None,
            "publish_date": report.publish_date,
            "created_at": report.created_at,
            "time_period_start": report.time_period_start,
            "time_period_end": report.time_period_end,
            "author_id": report.author_id,
        })
    
    return pd.DataFrame(data)


def add_report(
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
    author_id: Optional[int] = None,
) -> Optional[Report]:
    """
    Add a new report.
    
    Args:
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
        author_id: ID of the report author
        
    Returns:
        Optional[Report]: Created report or None
    """
    session = get_db_session()
    
    if not session:
        return None
    
    return run_async(create_report(
        db=session,
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
        keywords=keywords,
        author_id=author_id,
    ))


# Helper functions
def get_time_range_dates(time_range: str) -> Tuple[datetime, datetime]:
    """
    Get start and end dates for a time range.
    
    Args:
        time_range: Time range string (e.g., "Last 7 Days")
        
    Returns:
        Tuple[datetime, datetime]: (start_date, end_date)
    """
    end_date = datetime.utcnow()
    
    if time_range == "Last 24 Hours":
        start_date = end_date - timedelta(days=1)
    elif time_range == "Last 7 Days":
        start_date = end_date - timedelta(days=7)
    elif time_range == "Last 30 Days":
        start_date = end_date - timedelta(days=30)
    elif time_range == "Last Quarter":
        start_date = end_date - timedelta(days=90)
    else:  # Default to last 30 days
        start_date = end_date - timedelta(days=30)
    
    return start_date, end_date


# Initialize database connection
def init_db_connection():
    """Initialize database connection and check if tables exist."""
    session = get_db_session()
    
    if not session:
        return False
    
    # Check if tables exist
    from sqlalchemy.future import select
    
    try:
        # Try to query if tables exist
        query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
        result = run_async(session.execute(query))
        exists = result.scalar()
        
        return exists
    except Exception as e:
        # Tables might not exist yet
        print(f"Error checking database: {e}")
        return False