"""
Model for storing alerts generated from threats and dark web mentions.
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from src.models.base import BaseModel
from src.models.threat import ThreatSeverity

class AlertStatus(enum.Enum):
    """Status of an alert."""
    NEW = "New"
    ACKNOWLEDGED = "Acknowledged"
    INVESTIGATING = "Investigating"
    RESOLVED = "Resolved"
    FALSE_POSITIVE = "False Positive"


class AlertCategory(enum.Enum):
    """Category of an alert."""
    THREAT_DETECTION = "Threat Detection"
    DATA_BREACH = "Data Breach"
    CREDENTIAL_LEAK = "Credential Leak"
    BRAND_MENTION = "Brand Mention"
    INFRASTRUCTURE_MENTION = "Infrastructure Mention"
    EMPLOYEE_MENTION = "Employee Mention"
    CUSTOM = "Custom"


class Alert(BaseModel):
    """Model for alerts from dark web monitoring."""
    __tablename__ = "alerts"
    
    # Alert metadata
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(ThreatSeverity), nullable=False)
    status = Column(Enum(AlertStatus), nullable=False, default=AlertStatus.NEW)
    category = Column(Enum(AlertCategory), nullable=False)
    
    # Alert details
    generated_at = Column(DateTime, default=datetime.utcnow)
    source_url = Column(String(1024))
    is_read = Column(Boolean, default=False)
    
    # Related records
    threat_id = Column(Integer, ForeignKey("threats.id"))
    threat = relationship("Threat", back_populates="alerts")
    
    mention_id = Column(Integer, ForeignKey("dark_web_mentions.id"))
    mention = relationship("DarkWebMention", back_populates="alerts")
    
    # Assigned analyst (if any)
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    assigned_to = relationship("User")
    
    # Action taken
    action_taken = Column(Text)
    resolved_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Alert(id={self.id}, title={self.title}, severity={self.severity}, status={self.status})>"