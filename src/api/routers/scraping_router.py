from fastapi import APIRouter, Depends, HTTPException, status, Body, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from src.api.database import get_db
from src.api.auth import get_current_user
from src.api.schemas import User, CrawlRequest, CrawlResult
from src.services.scraper import WebScraper, ScraperError
from src.services.tor_proxy import TorProxyService, TorProxyError

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/scraping",
    tags=["scraping"],
    responses={404: {"description": "Not found"}}
)

# Initialize services
scraper = WebScraper()

@router.post("/test-tor", response_model=Dict[str, Any])
async def test_tor_connection(
    current_user: User = Depends(get_current_user)
):
    """
    Test Tor connection.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict[str, Any]: Connection status
    """
    try:
        tor_proxy = TorProxyService()
        is_connected = await tor_proxy.check_connection()
        
        return {
            "status": "success",
            "is_connected": is_connected,
            "timestamp": datetime.utcnow().isoformat()
        }
    except TorProxyError as e:
        logger.error(f"Tor proxy error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tor proxy error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error testing Tor connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/scrape", response_model=Dict[str, Any])
async def scrape_page(
    url: str,
    use_tor: bool = Body(False),
    current_user: User = Depends(get_current_user)
):
    """
    Scrape a single page.
    
    Args:
        url: URL to scrape
        use_tor: Whether to use Tor proxy
        current_user: Current authenticated user
        
    Returns:
        Dict[str, Any]: Scraped content
    """
    try:
        result = await scraper.extract_content(url, use_tor=use_tor)
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except ScraperError as e:
        logger.error(f"Scraper error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraper error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error scraping page: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/crawl", response_model=Dict[str, Any])
async def crawl_site(
    crawl_request: CrawlRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Crawl a site.
    
    Args:
        crawl_request: Crawl request data
        background_tasks: Background tasks
        current_user: Current authenticated user
        
    Returns:
        Dict[str, Any]: Crawl status
    """
    # For longer crawls, we add them as background tasks
    # This prevents timeouts on the API request
    
    # Start crawl in background
    if crawl_request.max_depth > 1 or '.onion' in crawl_request.url:
        # Add to background tasks
        background_tasks.add_task(
            scraper.crawl,
            crawl_request.url,
            max_depth=crawl_request.max_depth,
            max_pages=50,
            keyword_filter=crawl_request.keywords
        )
        
        return {
            "status": "started",
            "message": "Crawl started in background",
            "timestamp": datetime.utcnow().isoformat()
        }
    else:
        # For simple crawls, we perform them synchronously
        try:
            results = await scraper.crawl(
                crawl_request.url,
                max_depth=crawl_request.max_depth,
                max_pages=10,
                keyword_filter=crawl_request.keywords
            )
            
            return {
                "status": "completed",
                "results": results,
                "count": len(results),
                "timestamp": datetime.utcnow().isoformat()
            }
        except ScraperError as e:
            logger.error(f"Scraper error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Scraper error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error crawling site: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred: {str(e)}"
            )