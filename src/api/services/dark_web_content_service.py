"""
Service for working with dark web content data.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func, desc, and_, or_
from typing import List, Optional, Dict, Any, Union
import logging
import hashlib
from datetime import datetime

from src.models.dark_web_content import DarkWebContent, DarkWebMention, ContentType, ContentStatus
from src.models.threat import Threat, ThreatCategory, ThreatSeverity
from src.api.schemas import PaginationParams

# Configure logger
logger = logging.getLogger(__name__)


async def create_content(
    db: AsyncSession, 
    url: str, 
    content: str, 
    title: Optional[str] = None,
    content_type: ContentType = ContentType.OTHER,
    source_name: Optional[str] = None,
    source_type: Optional[str] = None,
    language: str = "en",
    references: Optional[Dict[str, Any]] = None,
    analysis_results: Optional[Dict[str, Any]] = None,
) -> DarkWebContent:
    """
    Create new dark web content entry.
    
    Args:
        db: Database session
        url: URL of the content
        content: Text content
        title: Title of the content
        content_type: Type of content
        source_name: Name of the source
        source_type: Type of source
        language: Language of the content
        references: References and connections in the content
        analysis_results: Results of content analysis
        
    Returns:
        DarkWebContent: Created content
    """
    # Generate content hash to avoid duplicates
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    # Check if content already exists with this hash
    result = await db.execute(
        select(DarkWebContent).where(DarkWebContent.content_hash == content_hash)
    )
    existing_content = result.scalars().first()
    
    if existing_content:
        logger.info(f"Content with hash {content_hash} already exists, updating last seen")
        # Update the existing content's scraped_at timestamp
        existing_content.scraped_at = datetime.utcnow()
        await db.commit()
        return existing_content
    
    # Create new content
    db_content = DarkWebContent(
        url=url,
        title=title,
        content=content,
        content_type=content_type,
        content_hash=content_hash,
        source_name=source_name,
        source_type=source_type,
        language=language,
        references=references or {},
        analysis_results=analysis_results or {},
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
        Optional[DarkWebContent]: Found content or None
    """
    result = await db.execute(
        select(DarkWebContent).where(DarkWebContent.id == content_id)
    )
    return result.scalars().first()


async def get_content_by_url(db: AsyncSession, url: str) -> Optional[DarkWebContent]:
    """
    Get dark web content by URL.
    
    Args:
        db: Database session
        url: URL of the content
        
    Returns:
        Optional[DarkWebContent]: Found content or None
    """
    result = await db.execute(
        select(DarkWebContent).where(DarkWebContent.url == url)
    )
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
    Get dark web contents with filtering.
    
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
        List[DarkWebContent]: List of contents
    """
    query = select(DarkWebContent)
    
    # Apply filters
    if content_type:
        query = query.where(DarkWebContent.content_type.in_(content_type))
    
    if content_status:
        query = query.where(DarkWebContent.content_status.in_(content_status))
    
    if source_name:
        query = query.where(DarkWebContent.source_name == source_name)
    
    if search_query:
        search_filter = or_(
            DarkWebContent.title.ilike(f"%{search_query}%"),
            DarkWebContent.content.ilike(f"%{search_query}%")
        )
        query = query.where(search_filter)
    
    if from_date:
        query = query.where(DarkWebContent.scraped_at >= from_date)
    
    if to_date:
        query = query.where(DarkWebContent.scraped_at <= to_date)
    
    # Apply pagination
    query = query.order_by(desc(DarkWebContent.scraped_at))
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
    
    Args are the same as get_contents, except pagination.
    
    Returns:
        int: Count of matching contents
    """
    query = select(func.count(DarkWebContent.id))
    
    # Apply filters
    if content_type:
        query = query.where(DarkWebContent.content_type.in_(content_type))
    
    if content_status:
        query = query.where(DarkWebContent.content_status.in_(content_status))
    
    if source_name:
        query = query.where(DarkWebContent.source_name == source_name)
    
    if search_query:
        search_filter = or_(
            DarkWebContent.title.ilike(f"%{search_query}%"),
            DarkWebContent.content.ilike(f"%{search_query}%")
        )
        query = query.where(search_filter)
    
    if from_date:
        query = query.where(DarkWebContent.scraped_at >= from_date)
    
    if to_date:
        query = query.where(DarkWebContent.scraped_at <= to_date)
    
    result = await db.execute(query)
    return result.scalar()


async def update_content_status(
    db: AsyncSession, 
    content_id: int, 
    status: ContentStatus,
    analysis_results: Optional[Dict[str, Any]] = None,
    relevance_score: Optional[float] = None,
) -> Optional[DarkWebContent]:
    """
    Update content status and analysis results.
    
    Args:
        db: Database session
        content_id: Content ID
        status: New content status
        analysis_results: Updated analysis results
        relevance_score: Updated relevance score
        
    Returns:
        Optional[DarkWebContent]: Updated content or None
    """
    content = await get_content_by_id(db, content_id)
    
    if not content:
        return None
    
    # Update fields
    content.content_status = status
    
    if analysis_results is not None:
        content.analysis_results = analysis_results
    
    if relevance_score is not None:
        content.relevance_score = relevance_score
    
    await db.commit()
    await db.refresh(content)
    
    return content


async def create_mention(
    db: AsyncSession,
    content_id: int,
    keyword: str,
    context: Optional[str] = None,
    snippet: Optional[str] = None,
    mention_type: Optional[str] = None,
    confidence: float = 1.0,
    is_verified: bool = False,
) -> DarkWebMention:
    """
    Create a new dark web mention.
    
    Args:
        db: Database session
        content_id: ID of the content where the mention was found
        keyword: Keyword that was mentioned
        context: Text surrounding the mention
        snippet: Extract of text containing the mention
        mention_type: Type of mention
        confidence: Confidence score of the mention
        is_verified: Whether the mention has been verified
        
    Returns:
        DarkWebMention: Created mention
    """
    # Ensure content exists
    content = await get_content_by_id(db, content_id)
    
    if not content:
        raise ValueError(f"Content with ID {content_id} not found")
    
    # Create mention
    mention = DarkWebMention(
        content_id=content_id,
        keyword=keyword,
        context=context,
        snippet=snippet,
        mention_type=mention_type,
        confidence=confidence,
        is_verified=is_verified
    )
    
    db.add(mention)
    await db.commit()
    await db.refresh(mention)
    
    return mention


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
    Get mentions with filtering.
    
    Args:
        db: Database session
        pagination: Pagination parameters
        keyword: Filter by keyword
        content_id: Filter by content ID
        is_verified: Filter by verification status
        from_date: Filter by created_at >= from_date
        to_date: Filter by created_at <= to_date
        
    Returns:
        List[DarkWebMention]: List of mentions
    """
    query = select(DarkWebMention)
    
    # Apply filters
    if keyword:
        query = query.where(DarkWebMention.keyword.ilike(f"%{keyword}%"))
    
    if content_id:
        query = query.where(DarkWebMention.content_id == content_id)
    
    if is_verified is not None:
        query = query.where(DarkWebMention.is_verified == is_verified)
    
    if from_date:
        query = query.where(DarkWebMention.created_at >= from_date)
    
    if to_date:
        query = query.where(DarkWebMention.created_at <= to_date)
    
    # Apply pagination
    query = query.order_by(desc(DarkWebMention.created_at))
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
    Create a threat from a dark web content.
    
    Args:
        db: Database session
        content_id: ID of the content that is the source of the threat
        title: Threat title
        description: Threat description
        severity: Threat severity
        category: Threat category
        confidence_score: Confidence score of the threat
        
    Returns:
        Threat: Created threat
    """
    from src.api.services.threat_service import create_threat
    
    # Get the content
    content = await get_content_by_id(db, content_id)
    
    if not content:
        raise ValueError(f"Content with ID {content_id} not found")
    
    # Create threat
    threat = await create_threat(
        db=db,
        title=title,
        description=description,
        severity=severity,
        category=category,
        source_url=content.url,
        source_name=content.source_name,
        source_type=content.source_type,
        raw_content=content.content,
        confidence_score=confidence_score
    )
    
    # Associate content with threat
    content.threats.append(threat)
    await db.commit()
    
    return threat