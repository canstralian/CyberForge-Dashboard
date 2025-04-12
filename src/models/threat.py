from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from src.models.base import BaseModel

class ThreatSeverity(enum.Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ThreatStatus(enum.Enum):
    NEW = "New"
    INVESTIGATING = "Investigating"
    CONFIRMED = "Confirmed"
    MITIGATED = "Mitigated"
    RESOLVED = "Resolved"
    FALSE_POSITIVE = "False Positive"


class ThreatCategory(enum.Enum):
    DATA_BREACH = "Data Breach"
    RANSOMWARE = "Ransomware"
    PHISHING = "Phishing"
    MALWARE = "Malware"
    CREDENTIAL_LEAK = "Credential Leak"
    ZERO_DAY = "Zero-day Exploit"
    DARK_WEB_MENTION = "Dark Web Mention"
    BRAND_ABUSE = "Brand Abuse"
    INFRASTRUCTURE_EXPOSURE = "Infrastructure Exposure"
    SOURCE_CODE_LEAK = "Source Code Leak"
    PII_EXPOSURE = "PII Exposure"
    OTHER = "Other"


class Threat(BaseModel):
    """Model for dark web threats."""
    __tablename__ = "threats"
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(ThreatSeverity), nullable=False)
    status = Column(Enum(ThreatStatus), nullable=False, default=ThreatStatus.NEW)
    category = Column(Enum(ThreatCategory), nullable=False)
    
    # Source information
    source_url = Column(String(1024))
    source_name = Column(String(255))
    source_type = Column(String(100))
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    # Affected entity information
    affected_entity = Column(String(255))
    affected_entity_type = Column(String(100))
    
    # Threat details
    confidence_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    raw_content = Column(Text)
    metadata = Column(JSON)
    
    # Relationships
    indicators = relationship("Indicator", back_populates="threat", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Threat(id={self.id}, title={self.title}, severity={self.severity})>"