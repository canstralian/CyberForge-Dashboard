"""
Model for storing dark web content scraped from sources.
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from src.models.base import BaseModel

class ContentType(enum.Enum):
    """Types of dark web content."""
    FORUM_POST = "Forum Post"
    MARKETPLACE_LISTING = "Marketplace Listing"
    PASTE = "Paste"
    BLOG = "Blog"
    CHAT = "Chat"
    LEAK = "Leak"
    OTHER = "Other"


class ContentStatus(enum.Enum):
    """Status of content analysis."""
    UNPROCESSED = "Unprocessed"
    PROCESSING = "Processing"
    PROCESSED = "Processed"
    FAILED = "Failed"


class DarkWebContent(BaseModel):
    """Model for storing dark web content."""
    __tablename__ = "dark_web_contents"
    
    # Content details
    url = Column(String(2048), nullable=False, index=True)
    title = Column(String(512))
    content = Column(Text, nullable=False)
    content_type = Column(Enum(ContentType), nullable=False)
    content_hash = Column(String(64), nullable=False, index=True, unique=True)
    
    # Source metadata
    source_name = Column(String(255))
    source_type = Column(String(100))
    language = Column(String(10), default="en")
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Analysis metadata
    content_status = Column(Enum(ContentStatus), default=ContentStatus.UNPROCESSED)
    relevance_score = Column(Float, default=0.0)
    sentiment_score = Column(Float)
    
    # References and connections
    references = Column(JSON)  # Links, mentions, or references in the content
    
    # Relationships (one-to-many relationship with threats)
    threats = relationship("Threat", secondary="content_threat_association", back_populates="contents")
    
    # Analysis results
    analysis_results = Column(JSON)  # Store NLP, entity extraction results
    
    def __repr__(self):
        return f"<DarkWebContent(id={self.id}, url={self.url}, content_type={self.content_type})>"


# Association table for many-to-many relationship between content and threats
from sqlalchemy import Table, Column, ForeignKey
from src.models.base import Base

# This will be created as a table directly, not as a model
content_threat_association = Table(
    'content_threat_association',
    Base.metadata,
    Column('content_id', Integer, ForeignKey('dark_web_contents.id'), primary_key=True),
    Column('threat_id', Integer, ForeignKey('threats.id'), primary_key=True)
)


class DarkWebMention(BaseModel):
    """Model for storing mentions of monitored keywords/entities in dark web content."""
    __tablename__ = "dark_web_mentions"
    
    # Content reference
    content_id = Column(Integer, ForeignKey("dark_web_contents.id"), nullable=False)
    content = relationship("DarkWebContent")
    
    # Mention details
    keyword = Column(String(255), nullable=False, index=True)
    context = Column(Text)  # Text surrounding the mention
    snippet = Column(Text)  # Extract of text containing the mention
    
    # Mention metadata
    mention_type = Column(String(100))  # Type of mention (e.g., direct, indirect, etc.)
    confidence = Column(Float, default=1.0)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    alerts = relationship("Alert", back_populates="mention", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DarkWebMention(id={self.id}, keyword={self.keyword}, content_id={self.content_id})>"