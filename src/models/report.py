"""
Model for storing reports generated from threats and analysis.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from typing import List

from src.models.base import BaseModel
from src.models.threat import ThreatSeverity

# Many-to-many relationship table for reports and threats
report_threats = Table(
    "report_threats",
    BaseModel.metadata,
    Column("report_id", Integer, ForeignKey("reports.id"), primary_key=True),
    Column("threat_id", Integer, ForeignKey("threats.id"), primary_key=True),
)


class ReportType(enum.Enum):
    """Type of report."""
    THREAT_DIGEST = "Threat Digest"
    DARK_WEB_ANALYSIS = "Dark Web Analysis"
    VULNERABILITY_ASSESSMENT = "Vulnerability Assessment"
    INCIDENT_RESPONSE = "Incident Response"
    THREAT_INTELLIGENCE = "Threat Intelligence"
    EXECUTIVE_SUMMARY = "Executive Summary"
    TECHNICAL_ANALYSIS = "Technical Analysis"
    WEEKLY_SUMMARY = "Weekly Summary"
    MONTHLY_SUMMARY = "Monthly Summary"
    CUSTOM = "Custom"


class ReportStatus(enum.Enum):
    """Status of report."""
    DRAFT = "Draft"
    REVIEW = "In Review"
    APPROVED = "Approved"
    PUBLISHED = "Published"
    ARCHIVED = "Archived"


class Report(BaseModel):
    """Model for reports on threats and analysis."""
    __tablename__ = "reports"
    
    # Report metadata
    report_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    report_type = Column(Enum(ReportType), nullable=False)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.DRAFT)
    severity = Column(Enum(ThreatSeverity))
    
    # Report scheduling and timing
    publish_date = Column(DateTime)
    time_period_start = Column(DateTime)
    time_period_end = Column(DateTime)
    
    # Keywords for searchability
    keywords = Column(String(500))
    
    # Related entities
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User")
    
    # Many-to-many relationship with threats
    threats = relationship(
        "Threat",
        secondary=report_threats,
        backref="reports"
    )
    
    def __repr__(self):
        return f"<Report(id={self.id}, report_id={self.report_id}, title={self.title})>"