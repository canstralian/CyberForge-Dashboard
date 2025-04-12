"""
Model for storing indicators of compromise (IOCs) and other threat indicators.
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from src.models.base import BaseModel

class IndicatorType(enum.Enum):
    """Type of indicator."""
    IP_ADDRESS = "IP Address"
    DOMAIN = "Domain"
    URL = "URL"
    HASH = "Hash"
    EMAIL = "Email"
    FILE = "File"
    REGISTRY = "Registry"
    USER_AGENT = "User Agent"
    CVE = "CVE"
    SOFTWARE = "Software"
    KEYWORD = "Keyword"
    OTHER = "Other"


class Indicator(BaseModel):
    """Model for indicators related to threats."""
    __tablename__ = "indicators"
    
    # Indicator details
    value = Column(String(1024), nullable=False)
    indicator_type = Column(Enum(IndicatorType), nullable=False)
    description = Column(Text)
    is_verified = Column(Boolean, default=False)
    context = Column(Text)
    source = Column(String(255))
    
    # Relationship to threat
    threat_id = Column(Integer, ForeignKey("threats.id"))
    threat = relationship("Threat", back_populates="indicators")
    
    # Confidence and metadata
    confidence_score = Column(Float, default=0.0)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Indicator(id={self.id}, value={self.value}, type={self.indicator_type})>"