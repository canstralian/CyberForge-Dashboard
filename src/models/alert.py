"""
Model for storing alerts generated from threats and dark web mentions.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from typing import Optional

from src.models.base import BaseModel
from src.models.threat import ThreatSeverity

class AlertCategory(enum.Enum):
    """Categories of alerts."""
    THREAT_DETECTED = "Threat Detected"
    MENTION_DETECTED = "Mention Detected"
    CREDENTIAL_LEAK = "Credential Leak"
    DATA_BREACH = "Data Breach"
    VULNERABILITY = "Vulnerability"
    MALWARE = "Malware"
    PHISHING = "Phishing"
    SUSPICIOUS_ACTIVITY = "Suspicious Activity"
    SYSTEM = "System Alert"
    OTHER = "Other"


class AlertStatus(enum.Enum):
    """Status of alerts."""
    NEW = "New"
    ASSIGNED = "Assigned"
    INVESTIGATING = "Investigating"
    RESOLVED = "Resolved"
    FALSE_POSITIVE = "False Positive"
    IGNORED = "Ignored"


class Alert(BaseModel):
    """Model for alerts generated from threats and mentions."""
    __tablename__ = "alerts"
    
    # Alert details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(ThreatSeverity), nullable=False)
    status = Column(Enum(AlertStatus), nullable=False, default=AlertStatus.NEW)
    category = Column(Enum(AlertCategory), nullable=False)
    
    # Alert metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    source_url = Column(String(1024))
    is_read = Column(Boolean, default=False)
    
    # Relationships
    threat_id = Column(Integer, ForeignKey("threats.id"))
    threat = relationship("Threat", back_populates="alerts")
    
    mention_id = Column(Integer, ForeignKey("dark_web_mentions.id"))
    mention = relationship("DarkWebMention", back_populates="alerts")
    
    # Assignment and resolution
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    assigned_to = relationship("User")
    
    action_taken = Column(Text)
    resolved_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Alert(id={self.id}, title={self.title}, severity={self.severity}, status={self.status})>"