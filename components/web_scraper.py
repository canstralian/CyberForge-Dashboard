"""
Web scraper component for Streamlit frontend.
This integrates with the backend scraper service.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import re
import asyncio
import httpx
from typing import Dict, Any, List, Optional
import json
import sys
import os

# Add the src directory to the path so we can import the services
sys.path.append(os.path.abspath('.'))

try:
    from src.services.scraper import WebScraper
    from src.services.tor_proxy import TorProxyService
except ImportError:
    # Fallback if imports fail - we'll use a simplified version
    WebScraper = None
    TorProxyService = None

# Check if Tor is running
def is_tor_running() -> bool:
    """Check if Tor service is running and accessible."""
    try:
        with httpx.Client(timeout=3) as client:
            response = client.get("http://127.0.0.1:9050")
            return True
    except Exception:
        return False

# Create a scraper instance
async def get_scraper():
    """Get a configured scraper instance."""
    if WebScraper and TorProxyService:
        try:
            tor_proxy = TorProxyService()
            # Check if Tor is accessible
            is_connected = await tor_proxy.check_connection()
            if is_connected:
                return WebScraper(tor_proxy_service=tor_proxy)
        except Exception as e:
            st.error(f"Error connecting to Tor: {e}")
    
    # If we can't connect to Tor or imports failed, return None
    return None

async def extract_content(url: str, use_tor: bool = False) -> Dict[str, Any]:
    """
    Extract content from a URL using the backend scraper.
    
    Args:
        url (str): URL to scrape
        use_tor (bool): Whether to use Tor proxy
        
    Returns:
        Dict[str, Any]: Extracted content
    """
    scraper = await get_scraper()
    
    if scraper:
        try:
            return await scraper.extract_content(url, use_tor=use_tor)
        except Exception as e:
            st.error(f"Error extracting content: {e}")
            return {
                "url": url,
                "title": "Error extracting content",
                "text_content": f"Failed to extract content: {e}",
                "indicators": {},
                "links": []
            }
    else:
        # Fallback to simulated data if scraper is unavailable
        st.warning("Advanced scraping functionality unavailable. Using limited extraction.")
        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(url)
                return {
                    "url": url,
                    "title": f"Content from {url}",
                    "text_content": response.text[:1000] + "...",
                    "indicators": {},
                    "links": []
                }
        except Exception as e:
            return {
                "url": url,
                "title": "Error fetching content",
                "text_content": f"Failed to fetch content: {e}",
                "indicators": {},
                "links": []
            }

def render_indicators(indicators: Dict[str, List[str]]):
    """
    Render extracted indicators in a formatted way.
    
    Args:
        indicators (Dict[str, List[str]]): Dictionary of indicator types and values
    """
    if not indicators:
        st.info("No indicators found in the content.")
        return
    
    # Create tabs for different indicator types
    tabs = st.tabs([
        f"IP Addresses ({len(indicators.get('ip_addresses', []))})",
        f"Emails ({len(indicators.get('email_addresses', []))})",
        f"Bitcoin ({len(indicators.get('bitcoin_addresses', []))})",
        f"URLs ({len(indicators.get('urls', []))})",
        f"Onion URLs ({len(indicators.get('onion_urls', []))})"
    ])
    
    # IP Addresses
    with tabs[0]:
        if indicators.get('ip_addresses'):
            st.markdown("#### Extracted IP Addresses")
            ip_df = pd.DataFrame(indicators['ip_addresses'], columns=["IP Address"])
            st.dataframe(ip_df, use_container_width=True)
        else:
            st.info("No IP addresses found.")
    
    # Email Addresses
    with tabs[1]:
        if indicators.get('email_addresses'):
            st.markdown("#### Extracted Email Addresses")
            email_df = pd.DataFrame(indicators['email_addresses'], columns=["Email"])
            st.dataframe(email_df, use_container_width=True)
        else:
            st.info("No email addresses found.")
    
    # Bitcoin Addresses
    with tabs[2]:
        if indicators.get('bitcoin_addresses'):
            st.markdown("#### Extracted Bitcoin Addresses")
            btc_df = pd.DataFrame(indicators['bitcoin_addresses'], columns=["Bitcoin Address"])
            st.dataframe(btc_df, use_container_width=True)
        else:
            st.info("No Bitcoin addresses found.")
    
    # URLs
    with tabs[3]:
        if indicators.get('urls'):
            st.markdown("#### Extracted URLs")
            url_df = pd.DataFrame(indicators['urls'], columns=["URL"])
            st.dataframe(url_df, use_container_width=True)
        else:
            st.info("No URLs found.")
    
    # Onion URLs
    with tabs[4]:
        if indicators.get('onion_urls'):
            st.markdown("#### Extracted Onion URLs")
            onion_df = pd.DataFrame(indicators['onion_urls'], columns=["Onion URL"])
            st.dataframe(onion_df, use_container_width=True)
        else:
            st.info("No onion URLs found.")

def create_keyword_highlight(text: str, keywords: Optional[List[str]] = None) -> str:
    """
    Highlight keywords in text for display.
    
    Args:
        text (str): Text content to highlight
        keywords (Optional[List[str]]): Keywords to highlight
        
    Returns:
        str: HTML with highlighted keywords
    """
    if not text or not keywords:
        return text
    
    # Escape HTML
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    
    # Highlight keywords
    for keyword in keywords:
        if not keyword.strip():
            continue
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        text = pattern.sub(f'<span style="background-color: #E74C3C40; padding: 0 2px; border-radius: 3px;">{keyword}</span>', text)
    
    return text

def render_web_scraper_ui():
    """Render the web scraper user interface."""
    st.title("Dark Web Intelligence Gathering")
    
    # Check if Tor is accessible
    if is_tor_running():
        st.success("Tor service is available for .onion sites")
    else:
        st.warning("Tor service not detected. Limited to clearnet sites only.")
    
    # Create UI layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Content Extraction & Analysis")
        
        # URL input
        url = st.text_input(
            "Enter URL to analyze",
            value="https://example.com",
            help="Enter a URL to scrape and analyze. For .onion sites, ensure Tor is configured."
        )
        
        # Options
        use_tor = st.checkbox(
            "Use Tor proxy",
            value='.onion' in url,
            help="Use Tor proxy for accessing .onion sites or for anonymity"
        )
        
        # Keyword highlighting
        keywords_input = st.text_area(
            "Keywords to highlight (one per line)",
            value="example\ndata\nbreach",
            help="Enter keywords to highlight in the extracted content"
        )
        keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()]
        
        # Extract button
        extract_button = st.button("Extract Content")
        
    with col2:
        st.markdown("### Analysis Options")
        
        analysis_tabs = st.radio(
            "Analysis Type",
            ["Text Analysis", "Indicators", "Sentiment Analysis", "Entity Recognition"],
            help="Select the type of analysis to perform on the extracted content"
        )
        
        st.markdown("### Monitoring")
        monitoring_options = st.multiselect(
            "Add to monitoring list",
            ["IP Addresses", "Email Addresses", "Bitcoin Addresses", "URLs", "Onion URLs"],
            default=["IP Addresses", "URLs"],
            help="Select which indicator types to monitor"
        )
        
        alert_threshold = st.slider(
            "Alert Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.05,
            help="Set the confidence threshold for alerts"
        )
    
    # Handle content extraction
    if extract_button:
        with st.spinner("Extracting content..."):
            # Run the async extraction
            content_data = asyncio.run(extract_content(url, use_tor=use_tor))
            
            # Store results in session state
            st.session_state.extracted_content = content_data
            
            # Success message
            st.success(f"Content extracted from {url}")
    
    # Display extracted content if available
    if 'extracted_content' in st.session_state:
        content_data = st.session_state.extracted_content
        
        # Display content in tabs
        content_tabs = st.tabs(["Extracted Text", "Indicators", "Metadata", "Raw HTML"])
        
        # Extracted text tab
        with content_tabs[0]:
            st.markdown(f"### {content_data.get('title', 'Extracted Content')}")
            st.info(f"Source: {content_data.get('url')}")
            
            # Highlight keywords in text
            highlighted_text = create_keyword_highlight(
                content_data.get('text_content', 'No content extracted'),
                keywords
            )
            
            st.markdown(f"""
            <div style="border: 1px solid #3498DB; border-radius: 5px; padding: 15px; 
                 background-color: #1A1A1A; height: 400px; overflow-y: auto;">
                {highlighted_text}
            </div>
            """, unsafe_allow_html=True)
        
        # Indicators tab
        with content_tabs[1]:
            render_indicators(content_data.get('indicators', {}))
        
        # Metadata tab
        with content_tabs[2]:
            st.markdown("### Document Metadata")
            
            metadata = content_data.get('metadata', {})
            if metadata:
                for key, value in metadata.items():
                    if value:
                        st.markdown(f"**{key}:** {value}")
            else:
                st.info("No metadata available")
        
        # Raw HTML tab
        with content_tabs[3]:
            st.markdown("### Raw HTML")
            with st.expander("Show Raw HTML"):
                st.code(content_data.get('html_content', 'No HTML content available'), language="html")
    
    # Additional informational UI elements
    st.markdown("---")
    st.markdown("### About Dark Web Intelligence")
    st.markdown("""
    This tool allows you to extract and analyze content from both clearnet and dark web sites.
    For .onion sites, make sure Tor is properly configured.
    
    **Features:**
    - Extract and analyze content from any URL
    - Highlight keywords of interest
    - Identify indicators of compromise (IoCs)
    - Add indicators to monitoring list
    """)