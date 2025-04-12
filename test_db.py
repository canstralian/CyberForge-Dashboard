"""
Test script to check database connectivity.
"""
import asyncio
import os
from src.database_init import ensure_database_initialized
from src.streamlit_database import (
    add_dark_web_content, get_dark_web_contents,
    add_threat, get_threats_df,
    add_alert, get_alerts_df
)
from src.models.dark_web_content import ContentType
from src.models.threat import ThreatSeverity, ThreatCategory, ThreatStatus
from src.models.alert import AlertCategory, AlertStatus
from datetime import datetime

def test_database():
    """Test database connectivity and operations."""
    print("Testing database functionality...")
    
    # Initialize database
    db_initialized = ensure_database_initialized()
    print(f"Database initialized: {db_initialized}")
    
    if not db_initialized:
        print("Failed to initialize database. Exiting.")
        return
    
    # Test adding dark web content
    print("\nAdding test dark web content...")
    content = add_dark_web_content(
        url="https://exampleforum.onion/thread/12345",
        content="This is a test dark web content with sensitive information.",
        title="Test Dark Web Content",
        content_type=ContentType.FORUM_POST,
        source_name="Example Forum",
        source_type="Dark Web Forum"
    )
    print(f"Content added with ID: {content.id if content else 'Failed'}")
    
    # Test getting dark web content
    print("\nRetrieving dark web content...")
    content_df = get_dark_web_contents(page=1, size=10)
    print(f"Retrieved {len(content_df)} content records:")
    if not content_df.empty:
        print(content_df[['id', 'title', 'url', 'content_type']].head())
    
    # Test adding a threat
    print("\nAdding test threat...")
    threat = add_threat(
        title="Test Threat",
        description="This is a test threat description",
        severity=ThreatSeverity.MEDIUM,
        category=ThreatCategory.DARK_WEB_MENTION,
        status=ThreatStatus.NEW,
        source_url="https://exampleforum.onion/thread/12345",
        source_name="Example Forum",
        affected_entity="Test Organization",
        confidence_score=0.75
    )
    print(f"Threat added with ID: {threat.id if threat else 'Failed'}")
    
    # Test getting threats
    print("\nRetrieving threats...")
    threat_df = get_threats_df(page=1, size=10)
    print(f"Retrieved {len(threat_df)} threat records:")
    if not threat_df.empty:
        print(threat_df[['id', 'title', 'severity', 'status']].head())
    
    # Test adding an alert
    print("\nAdding test alert...")
    alert = add_alert(
        title="Test Alert",
        description="This is a test alert description",
        severity=ThreatSeverity.MEDIUM,
        category=AlertCategory.DARK_WEB_MENTION,
        source_url="https://exampleforum.onion/thread/12345",
        threat_id=threat.id if threat else None
    )
    print(f"Alert added with ID: {alert.id if alert else 'Failed'}")
    
    # Test getting alerts
    print("\nRetrieving alerts...")
    alert_df = get_alerts_df(page=1, size=10)
    print(f"Retrieved {len(alert_df)} alert records:")
    if not alert_df.empty:
        print(alert_df[['id', 'title', 'severity', 'status']].head())
    
    print("\nDatabase test completed successfully!")

if __name__ == "__main__":
    test_database()