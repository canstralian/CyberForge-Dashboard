"""
Tor proxy service for connecting to .onion sites and other dark web resources.
"""
import httpx
import socks
import logging
import os
from typing import Optional, Dict, Any, Union
import asyncio
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Tor SOCKS proxy default settings
TOR_PROXY_HOST = os.getenv("TOR_PROXY_HOST", "127.0.0.1")
TOR_PROXY_PORT = int(os.getenv("TOR_PROXY_PORT", "9050"))
TOR_PROXY_TIMEOUT = int(os.getenv("TOR_PROXY_TIMEOUT", "60"))

class TorProxyError(Exception):
    """Base exception for Tor proxy errors."""
    pass

class TorProxyConnectionError(TorProxyError):
    """Exception raised when unable to connect to Tor proxy."""
    pass

class TorProxyTimeoutError(TorProxyError):
    """Exception raised when Tor proxy request times out."""
    pass

class TorProxyService:
    """Service for connecting to .onion sites via Tor proxy."""
    
    def __init__(
        self,
        proxy_host: str = TOR_PROXY_HOST,
        proxy_port: int = TOR_PROXY_PORT,
        timeout: int = TOR_PROXY_TIMEOUT
    ):
        """
        Initialize Tor proxy service.
        
        Args:
            proxy_host: Tor proxy host
            proxy_port: Tor proxy port
            timeout: Request timeout in seconds
        """
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.timeout = timeout
        self.proxy_url = f"socks5://{proxy_host}:{proxy_port}"
        
        logger.info(f"Initialized Tor proxy service with proxy {self.proxy_url}")
    
    @asynccontextmanager
    async def _get_client(self):
        """
        Get an httpx client configured for Tor proxy.
        
        Yields:
            httpx.AsyncClient: Async HTTP client
        """
        transport = httpx.AsyncHTTPTransport(
            proxy=self.proxy_url,
            verify=False  # Often needed for .onion sites
        )
        
        async with httpx.AsyncClient(
            transport=transport,
            timeout=self.timeout,
            follow_redirects=True,
            http2=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0"
            }
        ) as client:
            yield client
    
    async def check_connection(self) -> bool:
        """
        Check if Tor proxy is available and working.
        
        Returns:
            bool: True if connection is successful
            
        Raises:
            TorProxyConnectionError: If unable to connect to Tor proxy
        """
        try:
            # Try connecting to check.torproject.org
            async with self._get_client() as client:
                response = await client.get("https://check.torproject.org/")
                
                # Check if we're using Tor
                return "Congratulations" in response.text and "Tor" in response.text
        except Exception as e:
            logger.error(f"Failed to connect to Tor proxy: {e}")
            raise TorProxyConnectionError(f"Failed to connect to Tor proxy: {e}")
    
    async def get_page(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get page content via Tor proxy.
        
        Args:
            url: URL to fetch
            headers: Optional request headers
            params: Optional query parameters
            
        Returns:
            str: Page content
            
        Raises:
            TorProxyConnectionError: If unable to connect to Tor proxy
            TorProxyTimeoutError: If request times out
        """
        try:
            logger.info(f"Fetching page via Tor proxy: {url}")
            
            async with self._get_client() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    params=params
                )
                
                response.raise_for_status()
                return response.text
        except httpx.TimeoutException as e:
            logger.error(f"Tor proxy request timed out: {e}")
            raise TorProxyTimeoutError(f"Tor proxy request timed out: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error with Tor proxy: {e}")
            raise TorProxyError(f"HTTP error with Tor proxy: {e}")
        except Exception as e:
            logger.error(f"Failed to fetch page via Tor proxy: {e}")
            raise TorProxyConnectionError(f"Failed to fetch page via Tor proxy: {e}")
    
    async def post_page(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Post to a page via Tor proxy.
        
        Args:
            url: URL to post to
            data: Form data
            json_data: JSON data
            headers: Optional request headers
            
        Returns:
            str: Response content
            
        Raises:
            TorProxyConnectionError: If unable to connect to Tor proxy
            TorProxyTimeoutError: If request times out
        """
        try:
            logger.info(f"Posting to page via Tor proxy: {url}")
            
            async with self._get_client() as client:
                response = await client.post(
                    url,
                    data=data,
                    json=json_data,
                    headers=headers
                )
                
                response.raise_for_status()
                return response.text
        except httpx.TimeoutException as e:
            logger.error(f"Tor proxy request timed out: {e}")
            raise TorProxyTimeoutError(f"Tor proxy request timed out: {e}")
        except Exception as e:
            logger.error(f"Failed to post to page via Tor proxy: {e}")
            raise TorProxyConnectionError(f"Failed to post to page via Tor proxy: {e}")