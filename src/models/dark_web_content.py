"""
Models for storing dark web content and mentions.
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from src.models.base import BaseModel

class ContentType(enum.Enum):
    """Type of dark web content."""
    FORUM_POST = "Forum Post"
    MARKETPLACE_LISTING = "Marketplace Listing"
    BLOG_ARTICLE = "Blog Article"
    CHAT_LOG = "Chat Log"
    PASTE = "Paste"
    DOCUMENT = "Document"
    IMAGE = "Image"
    VIDEO = "Video"
    SOURCE_CODE = "Source Code"
    OTHER = "Other"


class ContentStatus(enum.Enum):
    """Status of dark web content."""
    NEW = "New"
    ANALYZING = "Analyzing"
    ANALYZED = "Analyzed"
    RELEVANT = "Relevant"
    IRRELEVANT = "Irrelevant"
    ARCHIVED = "Archived"


class DarkWebContent(BaseModel):
    """Model for storing dark web content."""
    __tablename__ = "dark_web_contents"
    
    # Content source
    url = Column(String(1024), nullable=False)
    domain = Column(String(255))
    
    # Content metadata
    title = Column(String(500))
    content = Column(Text, nullable=False)
    content_type = Column(Enum(ContentType), default=ContentType.OTHER)
    content_status = Column(Enum(ContentStatus), default=ContentStatus.NEW)
    
    # Source information
    source_name = Column(String(255))
    source_type = Column(String(100))
    language = Column(String(10))
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Analysis results
    relevance_score = Column(Float, default=0.0)
    sentiment_score = Column(Float, default=0.0)
    entity_data = Column(Text) # JSON storage for extracted entities
    
    # Relationships
    mentions = relationship("DarkWebMention", back_populates="content", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DarkWebContent(id={self.id}, url={self.url}, content_type={self.content_type})>"


class DarkWebMention(BaseModel):
    """Model for storing mentions of monitored entities in dark web content."""
    __tablename__ = "dark_web_mentions"
    
    # Relationship to content
    content_id = Column(Integer, ForeignKey("dark_web_contents.id"), nullable=False)
    content = relationship("DarkWebContent", back_populates="mentions")
    
    # Mention details
    keyword = Column(String(100), nullable=False)
    keyword_category = Column(String(50))
    
    # Extracted context
    context = Column(Text)
    snippet = Column(Text)
    
    # Mention metadata
    mention_type = Column(String(50)) # Type of mention (e.g., "brand", "employee", "product")
    confidence = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    alerts = relationship("Alert", back_populates="mention", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DarkWebMention(id={self.id}, keyword={self.keyword}, content_id={self.content_id})>"