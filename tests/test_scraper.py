"""
Tests for web scraper service.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from src.services.scraper import WebScraper, ScraperError
from src.services.tor_proxy import TorProxyService, TorProxyError

@pytest.fixture
def mock_tor_proxy():
    """Mock TorProxyService."""
    mock = AsyncMock(spec=TorProxyService)
    mock.get_page = AsyncMock(return_value="<html><body><h1>Test Page</h1><p>Test content</p></body></html>")
    mock.check_connection = AsyncMock(return_value=True)
    return mock

@pytest.fixture
def mock_trafilatura():
    """Mock trafilatura module."""
    mock = MagicMock()
    mock.extract = MagicMock(return_value="Test content")
    mock.extract_metadata = MagicMock(return_value=MagicMock(asdict=MagicMock(return_value={"title": "Test Page"})))
    return mock

@pytest.mark.asyncio
async def test_extract_content_regular_url(mock_tor_proxy, monkeypatch):
    """Test extract content from regular URL."""
    # Setup mocks
    mock_fetch = MagicMock(return_value="<html><body><h1>Test Page</h1><p>Test content</p></body></html>")
    mock_extract = MagicMock(return_value="Test content")
    mock_extract_metadata = MagicMock(return_value=MagicMock(asdict=MagicMock(return_value={"title": "Test Page"})))
    
    monkeypatch.setattr("trafilatura.fetch_url", mock_fetch)
    monkeypatch.setattr("trafilatura.extract", mock_extract)
    monkeypatch.setattr("trafilatura.extract_metadata", mock_extract_metadata)
    
    # Create scraper with mock TorProxyService
    scraper = WebScraper(tor_proxy_service=mock_tor_proxy)
    
    # Test extract_content
    result = await scraper.extract_content("https://example.com", use_tor=False)
    
    # Verify results
    assert result["url"] == "https://example.com"
    assert result["title"] == "Test Page"
    assert result["text_content"] == "Test content"
    assert "html_content" in result
    assert "indicators" in result
    assert "links" in result
    assert "metadata" in result
    assert "timestamp" in result
    
    # Verify mocks called correctly
    mock_fetch.assert_called_once_with("https://example.com")
    mock_extract.assert_called_once()
    mock_extract_metadata.assert_called_once()
    mock_tor_proxy.get_page.assert_not_called()

@pytest.mark.asyncio
async def test_extract_content_onion_url(mock_tor_proxy):
    """Test extract content from .onion URL."""
    # Create scraper with mock TorProxyService
    scraper = WebScraper(tor_proxy_service=mock_tor_proxy)
    
    # Test extract_content
    result = await scraper.extract_content("http://example.onion", use_tor=True)
    
    # Verify results
    assert result["url"] == "http://example.onion"
    assert "title" in result
    assert "text_content" in result
    assert "html_content" in result
    assert "indicators" in result
    assert "links" in result
    
    # Verify mocks called correctly
    mock_tor_proxy.get_page.assert_called_once_with("http://example.onion")

@pytest.mark.asyncio
async def test_extract_content_error(mock_tor_proxy):
    """Test extract content error."""
    # Setup mock error
    mock_tor_proxy.get_page.side_effect = TorProxyError("Test error")
    
    # Create scraper with mock TorProxyService
    scraper = WebScraper(tor_proxy_service=mock_tor_proxy)
    
    # Test extract_content raises error
    with pytest.raises(ScraperError):
        await scraper.extract_content("http://example.onion", use_tor=True)
    
    # Verify mocks called correctly
    mock_tor_proxy.get_page.assert_called_once_with("http://example.onion")

@pytest.mark.asyncio
async def test_extract_indicators():
    """Test extract indicators."""
    # Create scraper
    scraper = WebScraper()
    
    # Test text with various indicators
    text = """
    IP addresses: 192.168.1.1, 10.0.0.1
    Email addresses: test@example.com, another@example.org
    Bitcoin addresses: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa, 3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy
    URLs: https://example.com, http://test.org
    Onion URLs: example123456789.onion, anotherexample.onion
    """
    
    # Extract indicators
    indicators = scraper.extract_indicators(text)
    
    # Verify results
    assert len(indicators["ip_addresses"]) == 2
    assert len(indicators["email_addresses"]) == 2
    assert len(indicators["bitcoin_addresses"]) == 2
    assert len(indicators["urls"]) == 2
    assert len(indicators["onion_urls"]) == 2

@pytest.mark.asyncio
async def test_crawl(mock_tor_proxy, monkeypatch):
    """Test crawl."""
    # Setup mocks for extract_content
    mock_extract_content = AsyncMock()
    mock_extract_content.return_value = {
        "url": "https://example.com",
        "title": "Test Page",
        "text_content": "Test content with keyword",
        "links": ["https://example.com/page1", "https://example.com/page2"]
    }
    
    # Create scraper with mock extract_content
    scraper = WebScraper(tor_proxy_service=mock_tor_proxy)
    scraper.extract_content = mock_extract_content
    
    # Test crawl
    results = await scraper.crawl(
        "https://example.com",
        max_depth=1,
        max_pages=2,
        keyword_filter=["keyword"]
    )
    
    # Verify results
    assert len(results) <= 2  # We set max_pages=2
    assert results[0]["url"] == "https://example.com"
    
    # Verify extract_content called
    assert mock_extract_content.call_count >= 1