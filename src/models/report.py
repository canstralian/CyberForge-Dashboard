"""
Model for storing intelligence reports generated from dark web data.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum, JSON, Table
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from src.models.base import Base, BaseModel
from src.models.threat import ThreatSeverity


class ReportType(enum.Enum):
    """Type of intelligence report."""
    THREAT_INTELLIGENCE = "Threat Intelligence"
    DATA_BREACH = "Data Breach"
    EXECUTIVE = "Executive"
    TECHNICAL = "Technical"
    CUSTOM = "Custom"


class ReportStatus(enum.Enum):
    """Status of a report."""
    DRAFT = "Draft"
    REVIEW = "In Review"
    PUBLISHED = "Published"
    ARCHIVED = "Archived"


# Association table for many-to-many relationship between reports and threats
report_threat_association = Table(
    'report_threat_association',
    Base.metadata,
    Column('report_id', Integer, ForeignKey('reports.id'), primary_key=True),
    Column('threat_id', Integer, ForeignKey('threats.id'), primary_key=True)
)


class Report(BaseModel):
    """Model for intelligence reports."""
    __tablename__ = "reports"
    
    # Report metadata
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    report_type = Column(Enum(ReportType), nullable=False)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.DRAFT)
    severity = Column(Enum(ThreatSeverity))
    
    # Report details
    report_id = Column(String(20), nullable=False, unique=True)  # Custom ID format (e.g., RPT-2023-0001)
    publish_date = Column(DateTime)
    time_period_start = Column(DateTime)
    time_period_end = Column(DateTime)
    
    # Keywords and tags
    keywords = Column(JSON)  # List of keywords related to the report
    
    # Additional metadata
    source_data = Column(JSON)  # Sources and references
    
    # Relationships
    threats = relationship("Threat", secondary=report_threat_association)
    
    # Author
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User")
    
    def __repr__(self):
        return f"<Report(id={self.id}, report_id={self.report_id}, title={self.title})>"