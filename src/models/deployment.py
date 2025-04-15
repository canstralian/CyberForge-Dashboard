"""
Models for the deployment recommendation engine.

This module defines database models for tracking deployment recommendations
and deployment history.
"""
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from src.models.base import Base


class SecurityConfigLevel(str, Enum):
    """Security configuration levels for deployments."""
    STANDARD = "STANDARD"
    ENHANCED = "ENHANCED"
    STRICT = "STRICT"
    CUSTOM = "CUSTOM"


class DeploymentTimingRecommendation(str, Enum):
    """Recommendations for deployment timing."""
    SAFE_TO_DEPLOY = "SAFE_TO_DEPLOY"
    CAUTION = "CAUTION"
    DELAY_RECOMMENDED = "DELAY_RECOMMENDED"
    HIGH_RISK = "HIGH_RISK"


class DeploymentPlatform(str, Enum):
    """Supported deployment platforms."""
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"
    HEROKU = "HEROKU"
    DIGITAL_OCEAN = "DIGITAL_OCEAN"
    ON_PREMISE = "ON_PREMISE"
    HUGGING_FACE = "HUGGING_FACE"
    OTHER = "OTHER"


class DeploymentRegion(str, Enum):
    """Recommended deployment regions."""
    US_EAST = "US_EAST"
    US_WEST = "US_WEST"
    EU_CENTRAL = "EU_CENTRAL"
    EU_WEST = "EU_WEST"
    ASIA_PACIFIC = "ASIA_PACIFIC"
    SOUTH_AMERICA = "SOUTH_AMERICA"
    AFRICA = "AFRICA"
    MIDDLE_EAST = "MIDDLE_EAST"
    CUSTOM = "CUSTOM"


class DeploymentRecommendation(Base):
    """Model for storing deployment recommendations."""
    __tablename__ = "deployment_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Recommendation details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Security configuration
    security_level = Column(SQLAlchemyEnum(SecurityConfigLevel), nullable=False, default=SecurityConfigLevel.STANDARD)
    security_settings = Column(Text)  # JSON string of recommended security settings
    
    # Timing recommendations
    timing_recommendation = Column(SQLAlchemyEnum(DeploymentTimingRecommendation), nullable=False)
    timing_justification = Column(Text)
    recommended_window_start = Column(DateTime(timezone=True))
    recommended_window_end = Column(DateTime(timezone=True))
    
    # Cost optimization
    estimated_cost = Column(Float)
    cost_saving_potential = Column(Float)
    cost_justification = Column(Text)
    
    # Platform recommendations
    recommended_platform = Column(SQLAlchemyEnum(DeploymentPlatform))
    recommended_region = Column(SQLAlchemyEnum(DeploymentRegion))
    
    # Threat intelligence basis
    threat_assessment_summary = Column(Text)
    high_risk_threats_count = Column(Integer, default=0)
    medium_risk_threats_count = Column(Integer, default=0)
    low_risk_threats_count = Column(Integer, default=0)
    
    # Status and timestamps
    is_active = Column(Boolean, default=True)
    is_applied = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    applied_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User")  # No back_populates to avoid circular imports
    security_configurations = relationship("DeploymentSecurityConfig", back_populates="recommendation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DeploymentRecommendation(id={self.id}, title={self.title}, timing={self.timing_recommendation})>"


class SecurityConfigCategory(str, Enum):
    """Categories for security configurations."""
    NETWORK = "NETWORK"
    AUTHENTICATION = "AUTHENTICATION"
    ENCRYPTION = "ENCRYPTION"
    MONITORING = "MONITORING"
    COMPLIANCE = "COMPLIANCE"
    FIREWALL = "FIREWALL"
    WAF = "WEB_APPLICATION_FIREWALL"
    DDOS_PROTECTION = "DDOS_PROTECTION"
    IAM = "IDENTITY_ACCESS_MANAGEMENT"
    SECRETS_MANAGEMENT = "SECRETS_MANAGEMENT"


class DeploymentSecurityConfig(Base):
    """Model for storing detailed security configurations for deployments."""
    __tablename__ = "deployment_security_configs"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("deployment_recommendations.id"), nullable=False)
    
    # Configuration details
    category = Column(SQLAlchemyEnum(SecurityConfigCategory), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    configuration_value = Column(Text)  # Could be a JSON string for complex configurations
    
    # Threat basis
    related_threat_types = Column(String(255))  # Comma-separated threat types this config addresses
    
    # Status
    is_critical = Column(Boolean, default=False)
    is_applied = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    applied_at = Column(DateTime(timezone=True))
    
    # Relationships
    recommendation = relationship("DeploymentRecommendation", back_populates="security_configurations")
    
    def __repr__(self):
        return f"<DeploymentSecurityConfig(id={self.id}, category={self.category}, name={self.name})>"


class DeploymentHistory(Base):
    """Model for tracking deployment history."""
    __tablename__ = "deployment_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommendation_id = Column(Integer, ForeignKey("deployment_recommendations.id"), nullable=True)
    
    # Deployment details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    platform = Column(SQLAlchemyEnum(DeploymentPlatform))
    region = Column(SQLAlchemyEnum(DeploymentRegion))
    
    # Security information
    security_level = Column(SQLAlchemyEnum(SecurityConfigLevel))
    security_config_summary = Column(Text)
    
    # Success/failure information
    was_successful = Column(Boolean, default=True)
    failure_reason = Column(Text)
    
    # Cost information
    actual_cost = Column(Float)
    
    # Timestamps
    deployed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    recommendation = relationship("DeploymentRecommendation")
    
    def __repr__(self):
        return f"<DeploymentHistory(id={self.id}, title={self.title}, deployed_at={self.deployed_at})>"