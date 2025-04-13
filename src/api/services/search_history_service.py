"""
Search History and Trends Service

This service manages search history, saved searches, and trend analysis.
"""
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union

from sqlalchemy import func, desc, and_, or_, text
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.search_history import SearchHistory, SearchResult, SavedSearch, TrendTopic
from src.models.dark_web_content import DarkWebContent
from src.models.user import User

# Configure logging
logger = logging.getLogger(__name__)

async def add_search_history(
    db: AsyncSession,
    query: str,
    user_id: Optional[int] = None,
    result_count: int = 0,
    category: Optional[str] = None,
    is_saved: bool = False,
    notes: Optional[str] = None,
    tags: Optional[str] = None
) -> SearchHistory:
    """
    Add a new search history entry.
    
    Args:
        db: Database session
        query: Search query
        user_id: ID of the user who performed the search (optional)
        result_count: Number of results returned
        category: Category of the search
        is_saved: Whether this is a saved search
        notes: Optional notes
        tags: Optional tags (comma-separated)
        
    Returns:
        The created SearchHistory object
    """
    search_history = SearchHistory(
        query=query,
        user_id=user_id,
        result_count=result_count,
        category=category,
        is_saved=is_saved,
        notes=notes,
        tags=tags
    )
    
    db.add(search_history)
    await db.commit()
    await db.refresh(search_history)
    
    # Update trend data
    await update_trend_data(db, query, category)
    
    return search_history

async def add_search_result(
    db: AsyncSession,
    search_id: int,
    url: str,
    title: Optional[str] = None,
    snippet: Optional[str] = None,
    source: Optional[str] = None,
    relevance_score: float = 0.0,
    content_id: Optional[int] = None
) -> SearchResult:
    """
    Add a new search result.
    
    Args:
        db: Database session
        search_id: ID of the parent search
        url: URL of the result
        title: Title of the result
        snippet: Text snippet from the result
        source: Source of the result
        relevance_score: Score indicating relevance to the search query
        content_id: ID of the content in our database (if applicable)
        
    Returns:
        The created SearchResult object
    """
    search_result = SearchResult(
        search_id=search_id,
        url=url,
        title=title,
        snippet=snippet,
        source=source,
        relevance_score=relevance_score,
        content_id=content_id
    )
    
    db.add(search_result)
    await db.commit()
    await db.refresh(search_result)
    
    return search_result

async def get_search_history(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    query_filter: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    category: Optional[str] = None,
    is_saved: Optional[bool] = None,
    include_results: bool = False
) -> List[SearchHistory]:
    """
    Get search history with filtering options.
    
    Args:
        db: Database session
        skip: Number of items to skip
        limit: Maximum number of items to return
        user_id: Filter by user ID
        query_filter: Filter by search query (partial match)
        date_from: Filter by timestamp (from)
        date_to: Filter by timestamp (to)
        category: Filter by category
        is_saved: Filter by saved status
        include_results: Whether to include search results
        
    Returns:
        List of SearchHistory objects
    """
    statement = select(SearchHistory)
    
    # Apply filters
    if user_id is not None:
        statement = statement.where(SearchHistory.user_id == user_id)
    
    if query_filter:
        statement = statement.where(SearchHistory.query.ilike(f"%{query_filter}%"))
    
    if date_from:
        statement = statement.where(SearchHistory.timestamp >= date_from)
    
    if date_to:
        statement = statement.where(SearchHistory.timestamp <= date_to)
    
    if category:
        statement = statement.where(SearchHistory.category == category)
    
    if is_saved is not None:
        statement = statement.where(SearchHistory.is_saved == is_saved)
    
    # Load related data if requested
    if include_results:
        statement = statement.options(selectinload(SearchHistory.search_results))
    
    # Apply pagination
    statement = statement.order_by(desc(SearchHistory.timestamp)).offset(skip).limit(limit)
    
    result = await db.execute(statement)
    return result.scalars().all()

async def get_search_by_id(
    db: AsyncSession,
    search_id: int,
    include_results: bool = False
) -> Optional[SearchHistory]:
    """
    Get a search history entry by ID.
    
    Args:
        db: Database session
        search_id: Search history ID
        include_results: Whether to include search results
        
    Returns:
        SearchHistory object or None if not found
    """
    statement = select(SearchHistory).where(SearchHistory.id == search_id)
    
    if include_results:
        statement = statement.options(selectinload(SearchHistory.search_results))
    
    result = await db.execute(statement)
    return result.scalars().first()

async def delete_search_history(db: AsyncSession, search_id: int) -> bool:
    """
    Delete a search history entry.
    
    Args:
        db: Database session
        search_id: ID of the search to delete
        
    Returns:
        True if successful, False otherwise
    """
    search = await get_search_by_id(db, search_id)
    if not search:
        return False
    
    await db.delete(search)
    await db.commit()
    return True

async def save_search(
    db: AsyncSession,
    search_id: int,
    is_saved: bool = True,
    notes: Optional[str] = None,
    tags: Optional[str] = None
) -> Optional[SearchHistory]:
    """
    Save or unsave a search history entry.
    
    Args:
        db: Database session
        search_id: ID of the search
        is_saved: Whether to save or unsave
        notes: Optional notes to add
        tags: Optional tags to add (comma-separated)
        
    Returns:
        Updated SearchHistory object or None if not found
    """
    search = await get_search_by_id(db, search_id)
    if not search:
        return None
    
    search.is_saved = is_saved
    
    if notes:
        search.notes = notes
    
    if tags:
        search.tags = tags
    
    await db.commit()
    await db.refresh(search)
    return search

async def create_saved_search(
    db: AsyncSession,
    name: str,
    query: str,
    user_id: int,
    frequency: int = 24,
    notification_enabled: bool = True,
    threshold: int = 1,
    category: Optional[str] = None
) -> SavedSearch:
    """
    Create a new saved search with periodic monitoring.
    
    Args:
        db: Database session
        name: Name of the saved search
        query: Search query
        user_id: ID of the user
        frequency: How often to run this search (in hours, 0 for manual only)
        notification_enabled: Whether to send notifications for new results
        threshold: Minimum number of new results for notification
        category: Category of the search
        
    Returns:
        The created SavedSearch object
    """
    saved_search = SavedSearch(
        name=name,
        query=query,
        user_id=user_id,
        frequency=frequency,
        notification_enabled=notification_enabled,
        threshold=threshold,
        category=category
    )
    
    db.add(saved_search)
    await db.commit()
    await db.refresh(saved_search)
    
    return saved_search

async def get_saved_searches(
    db: AsyncSession,
    user_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[SavedSearch]:
    """
    Get saved searches with filtering options.
    
    Args:
        db: Database session
        user_id: Filter by user ID
        is_active: Filter by active status
        skip: Number of items to skip
        limit: Maximum number of items to return
        
    Returns:
        List of SavedSearch objects
    """
    statement = select(SavedSearch)
    
    # Apply filters
    if user_id is not None:
        statement = statement.where(SavedSearch.user_id == user_id)
    
    if is_active is not None:
        statement = statement.where(SavedSearch.is_active == is_active)
    
    # Apply pagination
    statement = statement.order_by(SavedSearch.name).offset(skip).limit(limit)
    
    result = await db.execute(statement)
    return result.scalars().all()

async def update_trend_data(
    db: AsyncSession,
    query: str,
    category: Optional[str] = None
) -> None:
    """
    Update trend data based on search queries.
    
    Args:
        db: Database session
        query: Search query
        category: Category of the search
    """
    # Split query into individual terms/topics
    topics = [t.strip() for t in query.split() if len(t.strip()) > 3]
    
    # Process each topic
    for topic in topics:
        # Check if topic already exists
        statement = select(TrendTopic).where(TrendTopic.topic == topic)
        result = await db.execute(statement)
        trend_topic = result.scalars().first()
        
        if trend_topic:
            # Update existing topic
            trend_topic.last_seen = datetime.utcnow()
            trend_topic.mention_count += 1
            
            # Calculate growth rate (percentage change over the last 24 hours)
            time_diff = (trend_topic.last_seen - trend_topic.first_seen).total_seconds() / 3600  # hours
            if time_diff > 0:
                hourly_rate = trend_topic.mention_count / time_diff
                trend_topic.growth_rate = hourly_rate * 24  # daily growth rate
            
            # Update category if provided and not already set
            if category and not trend_topic.category:
                trend_topic.category = category
        else:
            # Create a new trend topic
            trend_topic = TrendTopic(
                topic=topic,
                category=category,
                mention_count=1,
                growth_rate=1.0  # Initial growth rate
            )
            db.add(trend_topic)
    
    await db.commit()

async def get_trending_topics(
    db: AsyncSession,
    days: int = 7,
    limit: int = 20,
    category: Optional[str] = None,
    min_mentions: int = 3
) -> List[TrendTopic]:
    """
    Get trending topics over a specific time period.
    
    Args:
        db: Database session
        days: Number of days to consider
        limit: Maximum number of topics to return
        category: Filter by category
        min_mentions: Minimum number of mentions
        
    Returns:
        List of TrendTopic objects sorted by growth rate
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    statement = select(TrendTopic).where(
        and_(
            TrendTopic.last_seen >= cutoff_date,
            TrendTopic.mention_count >= min_mentions,
            TrendTopic.is_active == True
        )
    )
    
    if category:
        statement = statement.where(TrendTopic.category == category)
    
    statement = statement.order_by(desc(TrendTopic.growth_rate)).limit(limit)
    
    result = await db.execute(statement)
    return result.scalars().all()

async def get_search_frequency(
    db: AsyncSession,
    days: int = 30,
    interval: str = 'day'
) -> List[Dict[str, Any]]:
    """
    Get search frequency over time for visualization.
    
    Args:
        db: Database session
        days: Number of days to analyze
        interval: Time interval ('hour', 'day', 'week', 'month')
        
    Returns:
        List of dictionaries with time intervals and search counts
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # SQL query depends on the interval
    if interval == 'hour':
        date_format = "YYYY-MM-DD HH24:00"
        trunc_expr = func.date_trunc('hour', SearchHistory.timestamp)
    elif interval == 'day':
        date_format = "YYYY-MM-DD"
        trunc_expr = func.date_trunc('day', SearchHistory.timestamp)
    elif interval == 'week':
        date_format = "YYYY-WW"
        trunc_expr = func.date_trunc('week', SearchHistory.timestamp)
    else:  # month
        date_format = "YYYY-MM"
        trunc_expr = func.date_trunc('month', SearchHistory.timestamp)
    
    # Query for search count by interval
    statement = select(
        trunc_expr.label('interval'),
        func.count(SearchHistory.id).label('count')
    ).where(
        SearchHistory.timestamp >= cutoff_date
    ).group_by(
        'interval'
    ).order_by(
        'interval'
    )
    
    result = await db.execute(statement)
    rows = result.all()
    
    # Convert to list of dictionaries
    return [{"interval": row.interval, "count": row.count} for row in rows]

async def get_popular_searches(
    db: AsyncSession,
    days: int = 30,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get the most popular search terms.
    
    Args:
        db: Database session
        days: Number of days to analyze
        limit: Maximum number of terms to return
        
    Returns:
        List of dictionaries with search queries and counts
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    statement = select(
        SearchHistory.query,
        func.count(SearchHistory.id).label('count')
    ).where(
        SearchHistory.timestamp >= cutoff_date
    ).group_by(
        SearchHistory.query
    ).order_by(
        desc('count')
    ).limit(limit)
    
    result = await db.execute(statement)
    rows = result.all()
    
    return [{"query": row.query, "count": row.count} for row in rows]

async def get_search_categories(
    db: AsyncSession,
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Get distribution of search categories.
    
    Args:
        db: Database session
        days: Number of days to analyze
        
    Returns:
        List of dictionaries with categories and counts
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    statement = select(
        SearchHistory.category,
        func.count(SearchHistory.id).label('count')
    ).where(
        and_(
            SearchHistory.timestamp >= cutoff_date,
            SearchHistory.category.is_not(None)
        )
    ).group_by(
        SearchHistory.category
    ).order_by(
        desc('count')
    )
    
    result = await db.execute(statement)
    rows = result.all()
    
    return [{"category": row.category or "Uncategorized", "count": row.count} for row in rows]

async def get_search_trend_analysis(
    db: AsyncSession,
    days: int = 90,
    trend_days: int = 7,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get comprehensive analysis of search trends.
    
    Args:
        db: Database session
        days: Total days to analyze
        trend_days: Days to calculate short-term trends
        limit: Maximum number of items in each category
        
    Returns:
        Dictionary with various trend analyses
    """
    # Get overall search frequency
    frequency = await get_search_frequency(db, days, 'day')
    
    # Get popular searches
    popular = await get_popular_searches(db, days, limit)
    
    # Get recent trending topics
    trending = await get_trending_topics(db, trend_days, limit)
    
    # Get category distribution
    categories = await get_search_categories(db, days)
    
    # Get recent (last 24 hours) vs. overall popular terms
    recent_popular = await get_popular_searches(db, 1, limit)
    
    # Calculate velocity (rate of change)
    # This compares the last 7 days to the previous 7 days
    cutoff_recent = datetime.utcnow() - timedelta(days=trend_days)
    cutoff_previous = cutoff_recent - timedelta(days=trend_days)
    
    # Query for velocity calculation
    statement_recent = select(func.count(SearchHistory.id)).where(
        SearchHistory.timestamp >= cutoff_recent
    )
    statement_previous = select(func.count(SearchHistory.id)).where(
        and_(
            SearchHistory.timestamp >= cutoff_previous,
            SearchHistory.timestamp < cutoff_recent
        )
    )
    
    result_recent = await db.execute(statement_recent)
    result_previous = await db.execute(statement_previous)
    
    count_recent = result_recent.scalar() or 0
    count_previous = result_previous.scalar() or 0
    
    if count_previous > 0:
        velocity = (count_recent - count_previous) / count_previous * 100  # percentage change
    else:
        velocity = 100.0 if count_recent > 0 else 0.0
    
    # Compile the results
    return {
        "frequency": frequency,
        "popular_searches": popular,
        "trending_topics": [
            {"topic": t.topic, "mentions": t.mention_count, "growth_rate": t.growth_rate} 
            for t in trending
        ],
        "categories": categories,
        "recent_popular": recent_popular,
        "velocity": velocity,
        "total_searches": {
            "total": count_recent + count_previous,
            "recent": count_recent,
            "previous": count_previous
        }
    }