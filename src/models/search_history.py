"""
Search History Model

This module defines the search history model for tracking dark web searches and trends.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship

from src.models.base import Base

class SearchHistory(Base):
    """
    Model for tracking search history and trends in dark web content.
    
    Attributes:
        id: Unique identifier for the search
        query: The search query or term
        timestamp: When the search was performed
        user_id: ID of the user who performed the search (optional)
        result_count: Number of results returned
        category: Category of the search (e.g., "marketplace", "forum", "paste", etc.)
        is_saved: Whether this is a saved/favorited search
        notes: Optional notes about this search
        tags: Tags associated with this search
    """
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    result_count = Column(Integer, default=0)
    category = Column(String(50), nullable=True)
    is_saved = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    tags = Column(String(255), nullable=True)  # Comma-separated tags
    
    # Relationships
    user = relationship("User", back_populates="searches")
    search_results = relationship("SearchResult", back_populates="search", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SearchHistory(id={self.id}, query='{self.query}', timestamp={self.timestamp})>"


class SearchResult(Base):
    """
    Model for individual search results associated with a search query.
    
    Attributes:
        id: Unique identifier for the search result
        search_id: ID of the parent search
        content_id: ID of the content found (if in our database)
        url: URL of the result
        title: Title of the result
        snippet: Text snippet from the result
        source: Source of the result (e.g., "dark web forum", "marketplace", etc.)
        relevance_score: Score indicating relevance to the search query
        timestamp: When this result was found
    """
    __tablename__ = "search_results"
    
    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, ForeignKey("search_history.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("dark_web_content.id"), nullable=True)
    url = Column(String(1024), nullable=True)
    title = Column(String(255), nullable=True)
    snippet = Column(Text, nullable=True)
    source = Column(String(100), nullable=True)
    relevance_score = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    search = relationship("SearchHistory", back_populates="search_results")
    content = relationship("DarkWebContent", back_populates="search_results")
    
    def __repr__(self):
        return f"<SearchResult(id={self.id}, search_id={self.search_id}, title='{self.title}')>"


class SavedSearch(Base):
    """
    Model for saved searches with custom parameters for periodic monitoring.
    
    Attributes:
        id: Unique identifier for the saved search
        name: Name of the saved search
        query: The search query or term
        user_id: ID of the user who created the saved search
        created_at: When this saved search was created
        last_run_at: When this saved search was last executed
        frequency: How often to run this search (in hours, 0 for manual only)
        notification_enabled: Whether to send notifications for new results
        is_active: Whether this saved search is active
        threshold: Threshold for notifications (e.g., min number of new results)
    """
    __tablename__ = "saved_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    query = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_run_at = Column(DateTime, nullable=True)
    frequency = Column(Integer, default=24)  # In hours, 0 for manual only
    notification_enabled = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    threshold = Column(Integer, default=1)  # Min number of new results for notification
    category = Column(String(50), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="saved_searches")
    
    def __repr__(self):
        return f"<SavedSearch(id={self.id}, name='{self.name}', query='{self.query}')>"


class TrendTopic(Base):
    """
    Model for tracking trending topics on the dark web.
    
    Attributes:
        id: Unique identifier for the trend topic
        topic: The topic or term
        first_seen: When this topic was first detected
        last_seen: When this topic was last detected
        mention_count: Number of mentions of this topic
        growth_rate: Rate of growth in mentions (percentage)
        category: Category of the trend (e.g., "ransomware", "data breach", etc.)
        is_active: Whether this trend is currently active
    """
    __tablename__ = "trend_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(100), nullable=False, index=True)
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    mention_count = Column(Integer, default=1)
    growth_rate = Column(Float, default=0.0)
    category = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<TrendTopic(id={self.id}, topic='{self.topic}', mention_count={self.mention_count})>"