from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from src.models.base import BaseModel

class IndicatorType(enum.Enum):
    IP = "IP Address"
    DOMAIN = "Domain"
    URL = "URL"
    EMAIL = "Email"
    HASH = "File Hash"
    CVE = "CVE"
    FILENAME = "Filename"
    REGISTRY = "Registry Key"
    USER_AGENT = "User Agent"
    BITCOIN_ADDRESS = "Bitcoin Address"
    CREDIT_CARD = "Credit Card"
    SSN = "Social Security Number"
    OTHER = "Other"


class Indicator(BaseModel):
    """Model for indicators of compromise (IoCs)."""
    __tablename__ = "indicators"
    
    value = Column(String(1024), nullable=False)
    type = Column(Enum(IndicatorType), nullable=False)
    description = Column(Text)
    
    # Relationships
    threat_id = Column(Integer, ForeignKey("threats.id"))
    threat = relationship("Threat", back_populates="indicators")
    
    # Tracking data
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    # Validation and verification
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    
    # Context
    context = Column(Text)
    source = Column(String(255))
    
    def __repr__(self):
        return f"<Indicator(id={self.id}, value={self.value}, type={self.type})>"