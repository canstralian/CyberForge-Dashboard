"""
Service for dark web content operations.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, text
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from src.models.dark_web_content import DarkWebContent, DarkWebMention, ContentType, ContentStatus
from src.models.threat import Threat, ThreatCategory, ThreatSeverity, ThreatStatus
from src.api.schemas import PaginationParams

async def create_content(
    db: AsyncSession,
    url: str,
    content: str,
    title: Optional[str] = None,
    content_type: ContentType = ContentType.OTHER,
    content_status: ContentStatus = ContentStatus.NEW,
    source_name: Optional[str] = None,
    source_type: Optional[str] = None,
    language: Optional[str] = None,
    relevance_score: float = 0.0,
    sentiment_score: float = 0.0,
    entity_data: Optional[str] = None,
) -> DarkWebContent:
    """
    Create a new dark web content entry.
    
    Args:
        db: Database session
        url: URL of the content
        content: Text content
        title: Title of the content
        content_type: Type of content
        content_status: Status of content
        source_name: Name of the source
        source_type: Type of source
        language: Language of the content
        relevance_score: Relevance score (0-1)
        sentiment_score: Sentiment score (-1 to 1)
        entity_data: JSON string of extracted entities
        
    Returns:
        DarkWebContent: Created content
    """
    # Extract domain from URL if possible
    domain = None
    if url:
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
        except:
            pass
    
    db_content = DarkWebContent(
        url=url,
        domain=domain,
        title=title,
        content=content,
        content_type=content_type,
        content_status=content_status,
        source_name=source_name,
        source_type=source_type,
        language=language,
        scraped_at=datetime.utcnow(),
        relevance_score=relevance_score,
        sentiment_score=sentiment_score,
        entity_data=entity_data,
    )
    
    db.add(db_content)
    await db.commit()
    await db.refresh(db_content)
    
    return db_content

async def get_content_by_id(db: AsyncSession, content_id: int) -> Optional[DarkWebContent]:
    """
    Get dark web content by ID.
    
    Args:
        db: Database session
        content_id: Content ID
        
    Returns:
        Optional[DarkWebContent]: Content or None if not found
    """
    result = await db.execute(select(DarkWebContent).filter(DarkWebContent.id == content_id))
    return result.scalars().first()

async def get_contents(
    db: AsyncSession,
    pagination: PaginationParams,
    content_type: Optional[List[ContentType]] = None,
    content_status: Optional[List[ContentStatus]] = None,
    source_name: Optional[str] = None,
    search_query: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> List[DarkWebContent]:
    """
    Get dark web contents with filtering and pagination.
    
    Args:
        db: Database session
        pagination: Pagination parameters
        content_type: Filter by content type
        content_status: Filter by content status
        source_name: Filter by source name
        search_query: Search in title and content
        from_date: Filter by scraped_at >= from_date
        to_date: Filter by scraped_at <= to_date
        
    Returns:
        List[DarkWebContent]: List of dark web contents
    """
    query = select(DarkWebContent)
    
    # Apply filters
    if content_type:
        query = query.filter(DarkWebContent.content_type.in_(content_type))
    
    if content_status:
        query = query.filter(DarkWebContent.content_status.in_(content_status))
    
    if source_name:
        query = query.filter(DarkWebContent.source_name == source_name)
    
    if search_query:
        search_filter = or_(
            DarkWebContent.title.ilike(f"%{search_query}%"),
            DarkWebContent.content.ilike(f"%{search_query}%")
        )
        query = query.filter(search_filter)
    
    if from_date:
        query = query.filter(DarkWebContent.scraped_at >= from_date)
    
    if to_date:
        query = query.filter(DarkWebContent.scraped_at <= to_date)
    
    # Apply pagination
    query = query.order_by(DarkWebContent.scraped_at.desc())
    query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)
    
    result = await db.execute(query)
    return result.scalars().all()

async def count_contents(
    db: AsyncSession,
    content_type: Optional[List[ContentType]] = None,
    content_status: Optional[List[ContentStatus]] = None,
    source_name: Optional[str] = None,
    search_query: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> int:
    """
    Count dark web contents with filtering.
    
    Args:
        db: Database session
        content_type: Filter by content type
        content_status: Filter by content status
        source_name: Filter by source name
        search_query: Search in title and content
        from_date: Filter by scraped_at >= from_date
        to_date: Filter by scraped_at <= to_date
        
    Returns:
        int: Count of dark web contents
    """
    query = select(func.count(DarkWebContent.id))
    
    # Apply filters (same as in get_contents)
    if content_type:
        query = query.filter(DarkWebContent.content_type.in_(content_type))
    
    if content_status:
        query = query.filter(DarkWebContent.content_status.in_(content_status))
    
    if source_name:
        query = query.filter(DarkWebContent.source_name == source_name)
    
    if search_query:
        search_filter = or_(
            DarkWebContent.title.ilike(f"%{search_query}%"),
            DarkWebContent.content.ilike(f"%{search_query}%")
        )
        query = query.filter(search_filter)
    
    if from_date:
        query = query.filter(DarkWebContent.scraped_at >= from_date)
    
    if to_date:
        query = query.filter(DarkWebContent.scraped_at <= to_date)
    
    result = await db.execute(query)
    return result.scalar()

async def create_mention(
    db: AsyncSession,
    content_id: int,
    keyword: str,
    keyword_category: Optional[str] = None,
    context: Optional[str] = None,
    snippet: Optional[str] = None,
    mention_type: Optional[str] = None,
    confidence: float = 0.0,
    is_verified: bool = False,
) -> DarkWebMention:
    """
    Create a new dark web mention.
    
    Args:
        db: Database session
        content_id: ID of the content where the mention was found
        keyword: Keyword that was mentioned
        keyword_category: Category of the keyword
        context: Text surrounding the mention
        snippet: Extract of text containing the mention
        mention_type: Type of mention
        confidence: Confidence score (0-1)
        is_verified: Whether the mention is verified
        
    Returns:
        DarkWebMention: Created mention
    """
    db_mention = DarkWebMention(
        content_id=content_id,
        keyword=keyword,
        keyword_category=keyword_category,
        context=context,
        snippet=snippet,
        mention_type=mention_type,
        confidence=confidence,
        is_verified=is_verified,
    )
    
    db.add(db_mention)
    await db.commit()
    await db.refresh(db_mention)
    
    return db_mention

async def get_mention_by_id(db: AsyncSession, mention_id: int) -> Optional[DarkWebMention]:
    """
    Get dark web mention by ID.
    
    Args:
        db: Database session
        mention_id: Mention ID
        
    Returns:
        Optional[DarkWebMention]: Mention or None if not found
    """
    result = await db.execute(select(DarkWebMention).filter(DarkWebMention.id == mention_id))
    return result.scalars().first()

async def get_mentions(
    db: AsyncSession,
    pagination: PaginationParams,
    keyword: Optional[str] = None,
    content_id: Optional[int] = None,
    is_verified: Optional[bool] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> List[DarkWebMention]:
    """
    Get dark web mentions with filtering and pagination.
    
    Args:
        db: Database session
        pagination: Pagination parameters
        keyword: Filter by keyword
        content_id: Filter by content ID
        is_verified: Filter by verification status
        from_date: Filter by created_at >= from_date
        to_date: Filter by created_at <= to_date
        
    Returns:
        List[DarkWebMention]: List of dark web mentions
    """
    query = select(DarkWebMention)
    
    # Apply filters
    if keyword:
        query = query.filter(DarkWebMention.keyword.ilike(f"%{keyword}%"))
    
    if content_id:
        query = query.filter(DarkWebMention.content_id == content_id)
    
    if is_verified is not None:
        query = query.filter(DarkWebMention.is_verified == is_verified)
    
    if from_date:
        query = query.filter(DarkWebMention.created_at >= from_date)
    
    if to_date:
        query = query.filter(DarkWebMention.created_at <= to_date)
    
    # Apply pagination
    query = query.order_by(DarkWebMention.created_at.desc())
    query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)
    
    result = await db.execute(query)
    return result.scalars().all()

async def create_threat_from_content(
    db: AsyncSession,
    content_id: int,
    title: str,
    description: str,
    severity: ThreatSeverity,
    category: ThreatCategory,
    confidence_score: float = 0.0,
) -> Threat:
    """
    Create a threat from dark web content.
    
    Args:
        db: Database session
        content_id: ID of the content
        title: Threat title
        description: Threat description
        severity: Threat severity
        category: Threat category
        confidence_score: Confidence score (0-1)
        
    Returns:
        Threat: Created threat
    """
    # Get the content
    content = await get_content_by_id(db, content_id)
    if not content:
        raise ValueError(f"Content with ID {content_id} not found")
    
    # Create the threat
    from src.api.services.threat_service import create_threat
    
    threat = await create_threat(
        db=db,
        title=title,
        description=description,
        severity=severity,
        category=category,
        status=ThreatStatus.NEW,
        source_url=content.url,
        source_name=content.source_name,
        source_type=content.source_type,
        confidence_score=confidence_score,
    )
    
    return threat