"""
API schemas for data validation and serialization.
"""
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Pagination
class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Items per page")

# User schemas
class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    """User creation schema."""
    password: str

class UserUpdate(BaseModel):
    """User update schema."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    """User response schema."""
    id: int
    is_superuser: bool = False
    
    class Config:
        orm_mode = True

# Token schemas
class Token(BaseModel):
    """Token schema."""
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Token payload schema."""
    sub: Optional[int] = None

# Dark Web Content schemas
class DarkWebContentBase(BaseModel):
    """Base schema for dark web content."""
    url: str
    title: Optional[str] = None
    content: str
    content_type: str
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    language: Optional[str] = None

class DarkWebContentCreate(DarkWebContentBase):
    """Schema for creating dark web content."""
    relevance_score: float = 0.0
    sentiment_score: float = 0.0
    entity_data: Optional[str] = None

class DarkWebContentUpdate(BaseModel):
    """Schema for updating dark web content."""
    title: Optional[str] = None
    content_status: Optional[str] = None
    relevance_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    entity_data: Optional[str] = None

class DarkWebContentResponse(DarkWebContentBase):
    """Schema for dark web content response."""
    id: int
    domain: Optional[str] = None
    content_status: str
    scraped_at: datetime
    relevance_score: float
    sentiment_score: float
    entity_data: Optional[str] = None
    
    class Config:
        orm_mode = True

# Dark Web Mention schemas
class DarkWebMentionBase(BaseModel):
    """Base schema for dark web mention."""
    content_id: int
    keyword: str
    keyword_category: Optional[str] = None
    context: Optional[str] = None
    snippet: Optional[str] = None
    mention_type: Optional[str] = None

class DarkWebMentionCreate(DarkWebMentionBase):
    """Schema for creating dark web mention."""
    confidence: float = 0.0
    is_verified: bool = False

class DarkWebMentionUpdate(BaseModel):
    """Schema for updating dark web mention."""
    keyword_category: Optional[str] = None
    mention_type: Optional[str] = None
    confidence: Optional[float] = None
    is_verified: Optional[bool] = None

class DarkWebMentionResponse(DarkWebMentionBase):
    """Schema for dark web mention response."""
    id: int
    confidence: float
    is_verified: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

# Threat schemas
class ThreatBase(BaseModel):
    """Base schema for threat."""
    title: str
    description: str
    severity: str
    category: str

class ThreatCreate(ThreatBase):
    """Schema for creating threat."""
    status: str = "New"
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    affected_entity: Optional[str] = None
    affected_entity_type: Optional[str] = None
    confidence_score: float = 0.0
    risk_score: float = 0.0

class ThreatUpdate(BaseModel):
    """Schema for updating threat."""
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    affected_entity: Optional[str] = None
    affected_entity_type: Optional[str] = None
    confidence_score: Optional[float] = None
    risk_score: Optional[float] = None

class ThreatResponse(ThreatBase):
    """Schema for threat response."""
    id: int
    status: str
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    discovered_at: datetime
    affected_entity: Optional[str] = None
    affected_entity_type: Optional[str] = None
    confidence_score: float
    risk_score: float
    
    class Config:
        orm_mode = True

# Indicator schemas
class IndicatorBase(BaseModel):
    """Base schema for indicator."""
    threat_id: int
    value: str
    indicator_type: str
    description: Optional[str] = None

class IndicatorCreate(IndicatorBase):
    """Schema for creating indicator."""
    is_verified: bool = False
    context: Optional[str] = None
    source: Optional[str] = None
    confidence_score: float = 0.0

class IndicatorUpdate(BaseModel):
    """Schema for updating indicator."""
    description: Optional[str] = None
    is_verified: Optional[bool] = None
    context: Optional[str] = None
    source: Optional[str] = None
    confidence_score: Optional[float] = None

class IndicatorResponse(IndicatorBase):
    """Schema for indicator response."""
    id: int
    is_verified: bool
    context: Optional[str] = None
    source: Optional[str] = None
    confidence_score: float
    first_seen: datetime
    last_seen: datetime
    
    class Config:
        orm_mode = True

# Alert schemas
class AlertBase(BaseModel):
    """Base schema for alert."""
    title: str
    description: str
    severity: str
    category: str

class AlertCreate(AlertBase):
    """Schema for creating alert."""
    source_url: Optional[str] = None
    threat_id: Optional[int] = None
    mention_id: Optional[int] = None

class AlertUpdate(BaseModel):
    """Schema for updating alert."""
    status: str
    action_taken: Optional[str] = None
    assigned_to_id: Optional[int] = None
    is_read: Optional[bool] = None

class AlertResponse(AlertBase):
    """Schema for alert response."""
    id: int
    status: str
    generated_at: datetime
    source_url: Optional[str] = None
    is_read: bool
    threat_id: Optional[int] = None
    mention_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    action_taken: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# Report schemas
class ReportBase(BaseModel):
    """Base schema for report."""
    report_id: str
    title: str
    summary: str
    content: str
    report_type: str

class ReportCreate(ReportBase):
    """Schema for creating report."""
    status: str = "Draft"
    severity: Optional[str] = None
    publish_date: Optional[datetime] = None
    time_period_start: Optional[datetime] = None
    time_period_end: Optional[datetime] = None
    keywords: Optional[str] = None
    author_id: int
    threat_ids: List[int] = []

class ReportUpdate(BaseModel):
    """Schema for updating report."""
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    report_type: Optional[str] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    publish_date: Optional[datetime] = None
    time_period_start: Optional[datetime] = None
    time_period_end: Optional[datetime] = None
    keywords: Optional[str] = None
    threat_ids: Optional[List[int]] = None

class ReportResponse(ReportBase):
    """Schema for report response."""
    id: int
    status: str
    severity: Optional[str] = None
    publish_date: Optional[datetime] = None
    time_period_start: Optional[datetime] = None
    time_period_end: Optional[datetime] = None
    keywords: Optional[str] = None
    author_id: int
    
    class Config:
        orm_mode = True

# Statistics response schemas
class ThreatStatisticsResponse(BaseModel):
    """Schema for threat statistics response."""
    total_count: int
    severity_counts: Dict[str, int]
    status_counts: Dict[str, int]
    category_counts: Dict[str, int]
    time_series: List[Dict[str, Any]]
    from_date: str
    to_date: str

class ContentStatisticsResponse(BaseModel):
    """Schema for content statistics response."""
    total_count: int
    content_type_counts: Dict[str, int]
    content_status_counts: Dict[str, int]
    source_counts: Dict[str, int]
    time_series: List[Dict[str, Any]]
    from_date: str
    to_date: str