"""
Celery tasks for background processing.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from sqlalchemy import delete, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.celery_app import app
from src.services.scraper import WebScraper
from src.api.database import get_db_session
from src.models.threat import Threat
from src.models.indicator import Indicator

# Configure logger
logger = logging.getLogger(__name__)

# Dark web sources to scan
DARKWEB_SOURCES = [
    # These would be your real dark web sources
    # For example, onion forum URLs, marketplace URLs, etc.
    # "http://example.onion/forum",
]

# Keywords to search for
KEYWORDS = [
    # Organization name, domain, etc.
    "example.com",
    "example organization",
    "example data leak",
]

@app.task
def scan_darkweb_sources():
    """
    Scan dark web sources for relevant information.
    
    This task runs periodically to scan dark web sources
    for mentions of the organization, data leaks, etc.
    """
    logger.info("Starting scheduled dark web scan")
    
    try:
        # Get async event loop
        loop = asyncio.get_event_loop()
        
        # Create scraper
        scraper = WebScraper()
        
        # Scan each source
        for source in DARKWEB_SOURCES:
            logger.info(f"Scanning source: {source}")
            
            # Run crawl
            results = loop.run_until_complete(
                scraper.crawl(
                    source,
                    max_depth=2,
                    max_pages=20,
                    keyword_filter=KEYWORDS
                )
            )
            
            # Process results
            for result in results:
                # Check for relevant information
                if _is_relevant(result):
                    # Create threat
                    _create_threat_from_result(result)
        
        logger.info("Completed scheduled dark web scan")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error in scheduled dark web scan: {e}")
        return {"status": "error", "message": str(e)}

@app.task
def update_threat_intelligence():
    """
    Update threat intelligence information.
    
    This task runs daily to update information about existing threats,
    verify indicators, and correlate related threats.
    """
    logger.info("Starting threat intelligence update")
    
    try:
        # Get async event loop
        loop = asyncio.get_event_loop()
        
        # Get database session
        session = loop.run_until_complete(get_db_session())
        
        # Update threat intelligence
        # This would involve more complex logic in a real implementation
        
        logger.info("Completed threat intelligence update")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error in threat intelligence update: {e}")
        return {"status": "error", "message": str(e)}

@app.task
def cleanup_old_data(days: int = 30):
    """
    Clean up old data.
    
    This task runs weekly to remove old data from the database.
    
    Args:
        days: Number of days to keep data
    """
    logger.info(f"Starting data cleanup (keeping data for {days} days)")
    
    try:
        # Get async event loop
        loop = asyncio.get_event_loop()
        
        # Get database session
        session = loop.run_until_complete(get_db_session())
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Delete old threats
        result = loop.run_until_complete(
            session.execute(
                delete(Threat).where(Threat.created_at < cutoff_date)
            )
        )
        
        loop.run_until_complete(session.commit())
        
        logger.info(f"Deleted {result.rowcount} old threats")
        
        logger.info("Completed data cleanup")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error in data cleanup: {e}")
        return {"status": "error", "message": str(e)}

@app.task
def process_page(url: str, use_tor: bool = False):
    """
    Process a single page.
    
    This is a utility task that can be called manually or
    from other tasks to process a single page.
    
    Args:
        url: URL to process
        use_tor: Whether to use Tor proxy
    """
    logger.info(f"Processing page: {url}")
    
    try:
        # Get async event loop
        loop = asyncio.get_event_loop()
        
        # Create scraper
        scraper = WebScraper()
        
        # Extract content
        result = loop.run_until_complete(
            scraper.extract_content(url, use_tor=use_tor)
        )
        
        # Process result
        if _is_relevant(result):
            _create_threat_from_result(result)
        
        logger.info(f"Completed processing page: {url}")
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Error processing page {url}: {e}")
        return {"status": "error", "message": str(e)}

def _is_relevant(result: Dict[str, Any]) -> bool:
    """
    Check if a result is relevant.
    
    Args:
        result: Result from scraper
        
    Returns:
        bool: True if relevant
    """
    # Check if text content contains any keywords
    text_content = result.get("text_content", "")
    
    if not text_content:
        return False
    
    # Check if any keywords are in the text
    text_lower = text_content.lower()
    
    for keyword in KEYWORDS:
        if keyword.lower() in text_lower:
            return True
    
    return False

def _create_threat_from_result(result: Dict[str, Any]) -> Optional[Threat]:
    """
    Create a threat from a result.
    
    Args:
        result: Result from scraper
        
    Returns:
        Optional[Threat]: Created threat
    """
    # Get async event loop
    loop = asyncio.get_event_loop()
    
    try:
        # Get database session
        session = loop.run_until_complete(get_db_session())
        
        # Create threat
        title = result.get("title", "Unknown Title")
        url = result.get("url", "")
        
        # Check if threat already exists
        existing = loop.run_until_complete(
            session.execute(
                select(Threat).where(Threat.source_url == url)
            )
        )
        existing_threat = existing.scalars().first()
        
        if existing_threat:
            logger.info(f"Threat already exists for URL: {url}")
            return existing_threat
        
        # Create new threat
        threat = Threat(
            title=title,
            description=f"Automatically detected threat from {url}",
            severity="MEDIUM",  # Default severity
            status="NEW",
            category="DARK_WEB_MENTION",
            source_url=url,
            source_name="Dark Web Scanner",
            source_type="Automated Scan",
            discovered_at=datetime.utcnow(),
            affected_entity="",  # Would need more logic to determine this
            confidence_score=0.7,  # Default confidence
            risk_score=0.5,  # Default risk
            raw_content=result.get("text_content", ""),
            meta_data=result
        )
        
        session.add(threat)
        loop.run_until_complete(session.commit())
        loop.run_until_complete(session.refresh(threat))
        
        # Create indicators
        indicators = result.get("indicators", {})
        
        for ip in indicators.get("ip_addresses", []):
            indicator = Indicator(
                value=ip,
                type="IP",
                description=f"IP address found in {url}",
                threat_id=threat.id,
                source="Dark Web Scanner"
            )
            session.add(indicator)
        
        for email in indicators.get("email_addresses", []):
            indicator = Indicator(
                value=email,
                type="EMAIL",
                description=f"Email address found in {url}",
                threat_id=threat.id,
                source="Dark Web Scanner"
            )
            session.add(indicator)
        
        for btc in indicators.get("bitcoin_addresses", []):
            indicator = Indicator(
                value=btc,
                type="BITCOIN_ADDRESS",
                description=f"Bitcoin address found in {url}",
                threat_id=threat.id,
                source="Dark Web Scanner"
            )
            session.add(indicator)
        
        loop.run_until_complete(session.commit())
        
        logger.info(f"Created new threat from URL: {url}")
        return threat
    except Exception as e:
        logger.error(f"Error creating threat from result: {e}")
        return None