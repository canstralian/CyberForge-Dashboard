"""
Model for storing threat information discovered in dark web monitoring.
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from src.models.base import BaseModel

class ThreatSeverity(enum.Enum):
    """Severity levels for threats."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"


class ThreatCategory(enum.Enum):
    """Categories of threats."""
    DATA_BREACH = "Data Breach"
    CREDENTIAL_LEAK = "Credential Leak"
    VULNERABILITY = "Vulnerability"
    MALWARE = "Malware"
    PHISHING = "Phishing"
    IDENTITY_THEFT = "Identity Theft"
    RANSOMWARE = "Ransomware"
    DARK_WEB_MENTION = "Dark Web Mention"
    SOCIAL_ENGINEERING = "Social Engineering"
    INSIDER_THREAT = "Insider Threat"
    APT = "Advanced Persistent Threat"
    OTHER = "Other"


class ThreatStatus(enum.Enum):
    """Status of a threat."""
    NEW = "New"
    INVESTIGATING = "Investigating"
    CONFIRMED = "Confirmed"
    MITIGATED = "Mitigated"
    RESOLVED = "Resolved"
    FALSE_POSITIVE = "False Positive"


class Threat(BaseModel):
    """Model for threats discovered in dark web monitoring."""
    __tablename__ = "threats"
    
    # Threat metadata
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(ThreatSeverity), nullable=False)
    category = Column(Enum(ThreatCategory), nullable=False)
    status = Column(Enum(ThreatStatus), nullable=False, default=ThreatStatus.NEW)
    
    # Source information
    source_url = Column(String(1024))
    source_name = Column(String(255))
    source_type = Column(String(100))
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    # Affected entity
    affected_entity = Column(String(255))
    affected_entity_type = Column(String(100))
    
    # Risk assessment
    confidence_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    
    # Relationships
    indicators = relationship("Indicator", back_populates="threat", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="threat", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Threat(id={self.id}, title={self.title}, severity={self.severity})>"