"""
Web scraper service for extracting data from dark web sites.
"""
import logging
import re
import trafilatura
from urllib.parse import urlparse
from typing import List, Dict, Any, Set, Optional, Tuple
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime

from src.services.tor_proxy import TorProxyService, TorProxyError

logger = logging.getLogger(__name__)

class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass

class WebScraper:
    """Web scraper for dark web sites."""
    
    def __init__(self, tor_proxy_service: Optional[TorProxyService] = None):
        """
        Initialize web scraper.
        
        Args:
            tor_proxy_service: Optional TorProxyService instance
        """
        self.tor_proxy = tor_proxy_service or TorProxyService()
        
        # Compile regex patterns for common indicators
        self.ip_pattern = re.compile(r'\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b')
        self.email_pattern = re.compile(r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b')
        self.btc_pattern = re.compile(r'\\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\\b')
        self.url_pattern = re.compile(r'\\bhttps?://(?:[-\\w.]|(?:%[\\da-fA-F]{2}))+\\b')
        self.onion_url_pattern = re.compile(r'\\b[a-z2-7]{16,56}\\.onion\\b')
        
        logger.info("Initialized web scraper")
    
    async def extract_content(self, url: str, use_tor: bool = False) -> Dict[str, Any]:
        """
        Extract content from a URL.
        
        Args:
            url: URL to scrape
            use_tor: Whether to use Tor proxy
            
        Returns:
            Dict with extracted content
        
        Raises:
            ScraperError: If error occurs during scraping
        """
        try:
            logger.info(f"Extracting content from URL: {url} (use_tor={use_tor})")
            
            # Get HTML content
            if use_tor or '.onion' in url:
                html_content = await self.tor_proxy.get_page(url)
            else:
                # Use trafilatura directly for clearnet sites
                html_content = trafilatura.fetch_url(url)
                
            if not html_content:
                raise ScraperError(f"No content retrieved from {url}")
            
            # Extract title
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.title.text.strip() if soup.title else "Unknown Title"
            
            # Extract main text content using trafilatura (better than BeautifulSoup for this)
            text_content = trafilatura.extract(html_content)
            
            # Extract metadata
            metadata = trafilatura.extract_metadata(html_content)
            meta_dict = metadata.asdict() if metadata else {}
            
            # Find indicators in the text
            indicators = self.extract_indicators(text_content or "")
            
            # Get links
            links = [a['href'] for a in soup.find_all('a', href=True)]
            
            return {
                "url": url,
                "title": title,
                "text_content": text_content,
                "html_content": html_content,
                "indicators": indicators,
                "links": links,
                "metadata": meta_dict,
                "timestamp": datetime.utcnow().isoformat()
            }
        except TorProxyError as e:
            logger.error(f"Tor proxy error while scraping {url}: {e}")
            raise ScraperError(f"Tor proxy error: {e}")
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}")
            raise ScraperError(f"Scraping error: {e}")
    
    def extract_indicators(self, text: str) -> Dict[str, List[str]]:
        """
        Extract potential indicators from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with indicator types and values
        """
        indicators = {
            "ip_addresses": list(set(re.findall(self.ip_pattern, text))),
            "email_addresses": list(set(re.findall(self.email_pattern, text))),
            "bitcoin_addresses": list(set(re.findall(self.btc_pattern, text))),
            "urls": list(set(re.findall(self.url_pattern, text))),
            "onion_urls": list(set(re.findall(self.onion_url_pattern, text)))
        }
        
        return indicators
    
    async def crawl(
        self, 
        start_url: str, 
        max_depth: int = 1, 
        max_pages: int = 10,
        keyword_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Crawl a site starting from a URL.
        
        Args:
            start_url: Starting URL
            max_depth: Maximum crawl depth
            max_pages: Maximum pages to crawl
            keyword_filter: Optional list of keywords to filter pages
            
        Returns:
            List of extracted page data
        """
        visited_urls = set()
        to_visit = [(start_url, 0)]  # (url, depth)
        results = []
        
        use_tor = '.onion' in start_url
        
        logger.info(f"Starting crawl from {start_url} (max_depth={max_depth}, max_pages={max_pages})")
        
        while to_visit and len(visited_urls) < max_pages:
            # Get next URL to visit
            current_url, depth = to_visit.pop(0)
            
            # Skip if already visited or depth exceeded
            if current_url in visited_urls or depth > max_depth:
                continue
                
            # Mark as visited
            visited_urls.add(current_url)
            
            try:
                # Extract content
                page_data = await self.extract_content(current_url, use_tor=use_tor)
                
                # Check if page matches keyword filter
                if keyword_filter and not self._matches_keywords(page_data.get("text_content", ""), keyword_filter):
                    continue
                    
                # Add to results
                results.append(page_data)
                
                # Add links to visit queue if within depth
                if depth < max_depth:
                    for link in page_data.get("links", []):
                        # Normalize URL
                        parsed_link = urlparse(link)
                        
                        # Skip empty links, fragments, or external links
                        if not parsed_link.netloc or parsed_link.fragment:
                            continue
                            
                        # Add to visit queue
                        to_visit.append((link, depth + 1))
            except Exception as e:
                logger.error(f"Error crawling {current_url}: {e}")
        
        logger.info(f"Crawl completed. Visited {len(visited_urls)} pages, extracted {len(results)} results.")
        return results
    
    def _matches_keywords(self, text: str, keywords: List[str]) -> bool:
        """
        Check if text matches any keywords.
        
        Args:
            text: Text to check
            keywords: List of keywords
            
        Returns:
            bool: True if matches any keyword
        """
        if not text or not keywords:
            return False
            
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)