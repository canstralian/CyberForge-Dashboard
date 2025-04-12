from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

# Base models
class BaseSchema(BaseModel):
    """Base model for all schemas."""
    class Config:
        from_attributes = True
        populate_by_name = True

# Authentication schemas
class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for token data."""
    username: Optional[str] = None

class UserBase(BaseSchema):
    """Base schema for user data."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    """Schema for user creation."""
    password: str

class UserUpdate(BaseSchema):
    """Schema for user update."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    """Schema for user response."""
    id: int
    created_at: datetime
    updated_at: datetime

class UserInDB(User):
    """Schema for user in database."""
    hashed_password: str

# Threat schemas
class ThreatSeverity(str, Enum):
    """Enum for threat severity levels."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class ThreatStatus(str, Enum):
    """Enum for threat status."""
    NEW = "New"
    INVESTIGATING = "Investigating"
    CONFIRMED = "Confirmed"
    MITIGATED = "Mitigated"
    RESOLVED = "Resolved"
    FALSE_POSITIVE = "False Positive"

class ThreatCategory(str, Enum):
    """Enum for threat categories."""
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

class ThreatBase(BaseSchema):
    """Base schema for threat data."""
    title: str
    description: str
    severity: ThreatSeverity
    status: ThreatStatus = ThreatStatus.NEW
    category: ThreatCategory
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    affected_entity: Optional[str] = None
    affected_entity_type: Optional[str] = None
    confidence_score: float = 0.0
    risk_score: float = 0.0
    raw_content: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class ThreatCreate(ThreatBase):
    """Schema for threat creation."""
    pass

class ThreatUpdate(BaseSchema):
    """Schema for threat update."""
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[ThreatSeverity] = None
    status: Optional[ThreatStatus] = None
    category: Optional[ThreatCategory] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    affected_entity: Optional[str] = None
    affected_entity_type: Optional[str] = None
    confidence_score: Optional[float] = None
    risk_score: Optional[float] = None
    raw_content: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class Threat(ThreatBase):
    """Schema for threat response."""
    id: int
    created_at: datetime
    updated_at: datetime
    discovered_at: datetime

# Indicator schemas
class IndicatorType(str, Enum):
    """Enum for indicator types."""
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

class IndicatorBase(BaseSchema):
    """Base schema for indicator data."""
    value: str
    type: IndicatorType
    description: Optional[str] = None
    threat_id: Optional[int] = None
    is_verified: bool = False
    context: Optional[str] = None
    source: Optional[str] = None

class IndicatorCreate(IndicatorBase):
    """Schema for indicator creation."""
    pass

class IndicatorUpdate(BaseSchema):
    """Schema for indicator update."""
    value: Optional[str] = None
    type: Optional[IndicatorType] = None
    description: Optional[str] = None
    threat_id: Optional[int] = None
    is_verified: Optional[bool] = None
    verified_at: Optional[datetime] = None
    context: Optional[str] = None
    source: Optional[str] = None

class Indicator(IndicatorBase):
    """Schema for indicator response."""
    id: int
    created_at: datetime
    updated_at: datetime
    first_seen: datetime
    last_seen: datetime
    verified_at: Optional[datetime] = None

# Request and response schemas for dark web crawling
class CrawlRequest(BaseSchema):
    """Schema for crawl request."""
    url: str
    max_depth: int = 1
    keywords: List[str] = []
    is_onion: bool = False

class CrawlResult(BaseSchema):
    """Schema for crawl result."""
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    extracted_indicators: Optional[List[Dict[str, Any]]] = None
    crawl_time: datetime
    status: str
    error: Optional[str] = None

# Pagination and filtering
class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)

class ThreatFilter(BaseModel):
    """Schema for threat filtering."""
    severity: Optional[List[ThreatSeverity]] = None
    status: Optional[List[ThreatStatus]] = None
    category: Optional[List[ThreatCategory]] = None
    search: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None

class IndicatorFilter(BaseModel):
    """Schema for indicator filtering."""
    type: Optional[List[IndicatorType]] = None
    is_verified: Optional[bool] = None
    search: Optional[str] = None
    threat_id: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None