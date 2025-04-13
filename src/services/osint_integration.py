"""
OSINT Integration Service

This service connects to various OSINT sources and correlates data with
dark web intelligence already in our database.
"""
import os
import json
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.dark_web_content import DarkWebContent
from src.models.threat import Threat, ThreatSeverity, ThreatCategory, ThreatStatus
from src.models.indicator import Indicator, IndicatorType
from src.api.services.threat_service import create_threat, add_indicator_to_threat, get_threat_by_id

# Configure logging
logger = logging.getLogger(__name__)

class OSINTSource:
    """Base class for OSINT data sources"""
    name: str = "base_source"
    
    async def fetch_data(self, query: str) -> List[Dict[str, Any]]:
        """
        Fetch data from the OSINT source.
        
        Args:
            query: Search query
            
        Returns:
            List of data items from the source
        """
        raise NotImplementedError("Subclasses must implement fetch_data")
    
    async def enrich_indicator(self, indicator_value: str, indicator_type: str) -> Dict[str, Any]:
        """
        Enrich an indicator with additional context.
        
        Args:
            indicator_value: The indicator value
            indicator_type: The indicator type
            
        Returns:
            Dictionary with enrichment data
        """
        raise NotImplementedError("Subclasses must implement enrich_indicator")


class VirusTotalSource(OSINTSource):
    """VirusTotal OSINT source"""
    name: str = "virustotal"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("VIRUSTOTAL_API_KEY")
        if not self.api_key:
            logger.warning("VirusTotal API key not provided")
    
    async def fetch_data(self, query: str) -> List[Dict[str, Any]]:
        """
        Fetch data from VirusTotal.
        
        Args:
            query: Search query
            
        Returns:
            List of data items from VirusTotal
        """
        if not self.api_key:
            logger.error("VirusTotal API key not available")
            return []
        
        try:
            # Example implementation - adjust according to actual VirusTotal API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.virustotal.com/api/v3/intelligence/search",
                    params={"query": query},
                    headers={"x-apikey": self.api_key},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
                else:
                    logger.error(f"VirusTotal API error: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching data from VirusTotal: {e}")
            return []
    
    async def enrich_indicator(self, indicator_value: str, indicator_type: str) -> Dict[str, Any]:
        """
        Enrich an indicator with VirusTotal data.
        
        Args:
            indicator_value: The indicator value
            indicator_type: The indicator type
            
        Returns:
            Dictionary with enrichment data
        """
        if not self.api_key:
            logger.error("VirusTotal API key not available")
            return {}
        
        url_path = ""
        if indicator_type.lower() == "domain":
            url_path = f"domains/{indicator_value}"
        elif indicator_type.lower() == "ip_address":
            url_path = f"ip_addresses/{indicator_value}"
        elif indicator_type.lower() == "url":
            # URL requires base64 encoding according to VT API
            import base64
            encoded_url = base64.urlsafe_b64encode(indicator_value.encode()).decode().strip("=")
            url_path = f"urls/{encoded_url}"
        elif indicator_type.lower() == "hash":
            url_path = f"files/{indicator_value}"
        else:
            logger.warning(f"Unsupported indicator type for VirusTotal: {indicator_type}")
            return {}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.virustotal.com/api/v3/{url_path}",
                    headers={"x-apikey": self.api_key},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Extract relevant information for our platform
                    result = {
                        "source": "virustotal",
                        "last_analysis_stats": data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {}),
                        "reputation": data.get("data", {}).get("attributes", {}).get("reputation", 0),
                        "last_analysis_date": data.get("data", {}).get("attributes", {}).get("last_analysis_date", None),
                    }
                    
                    # Add type-specific data
                    if indicator_type.lower() == "domain" or indicator_type.lower() == "ip_address":
                        result["asn"] = data.get("data", {}).get("attributes", {}).get("asn", None)
                        result["as_owner"] = data.get("data", {}).get("attributes", {}).get("as_owner", None)
                        result["country"] = data.get("data", {}).get("attributes", {}).get("country", None)
                    
                    return result
                else:
                    logger.error(f"VirusTotal API error: {response.status_code} - {response.text}")
                    return {"source": "virustotal", "error": f"API error: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error enriching indicator from VirusTotal: {e}")
            return {"source": "virustotal", "error": str(e)}


class AlienVaultOTXSource(OSINTSource):
    """AlienVault OTX OSINT source"""
    name: str = "alienvault_otx"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ALIENVAULT_OTX_API_KEY")
        if not self.api_key:
            logger.warning("AlienVault OTX API key not provided")
    
    async def fetch_data(self, query: str) -> List[Dict[str, Any]]:
        """
        Fetch data from AlienVault OTX.
        
        Args:
            query: Search query
            
        Returns:
            List of data items from AlienVault OTX
        """
        if not self.api_key:
            logger.error("AlienVault OTX API key not available")
            return []
        
        try:
            # Example implementation - adjust according to actual OTX API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://otx.alienvault.com/api/v1/search/pulses",
                    params={"q": query},
                    headers={"X-OTX-API-KEY": self.api_key},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
                else:
                    logger.error(f"AlienVault OTX API error: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching data from AlienVault OTX: {e}")
            return []
    
    async def enrich_indicator(self, indicator_value: str, indicator_type: str) -> Dict[str, Any]:
        """
        Enrich an indicator with AlienVault OTX data.
        
        Args:
            indicator_value: The indicator value
            indicator_type: The indicator type
            
        Returns:
            Dictionary with enrichment data
        """
        if not self.api_key:
            logger.error("AlienVault OTX API key not available")
            return {}
        
        section_type = ""
        if indicator_type.lower() == "domain":
            section_type = "domain"
        elif indicator_type.lower() == "ip_address":
            section_type = "IPv4"
        elif indicator_type.lower() == "url":
            section_type = "url"
        elif indicator_type.lower() == "hash":
            if len(indicator_value) == 32:
                section_type = "md5"
            elif len(indicator_value) == 40:
                section_type = "sha1"
            elif len(indicator_value) == 64:
                section_type = "sha256"
            else:
                logger.warning(f"Unknown hash type for length {len(indicator_value)}")
                return {}
        else:
            logger.warning(f"Unsupported indicator type for AlienVault OTX: {indicator_type}")
            return {}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://otx.alienvault.com/api/v1/indicators/{section_type}/{indicator_value}/general",
                    headers={"X-OTX-API-KEY": self.api_key},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract relevant information
                    result = {
                        "source": "alienvault_otx",
                        "pulse_count": data.get("pulse_info", {}).get("count", 0),
                        "pulses": [
                            {
                                "name": pulse.get("name"),
                                "tags": pulse.get("tags", []),
                                "created": pulse.get("created"),
                                "author": pulse.get("author", {}).get("username")
                            }
                            for pulse in data.get("pulse_info", {}).get("pulses", [])[:5]  # Limit to 5 pulses
                        ],
                        "reputation": data.get("reputation", 0),
                    }
                    
                    return result
                else:
                    logger.error(f"AlienVault OTX API error: {response.status_code} - {response.text}")
                    return {"source": "alienvault_otx", "error": f"API error: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error enriching indicator from AlienVault OTX: {e}")
            return {"source": "alienvault_otx", "error": str(e)}


class OSINTIntegrationService:
    """Service for integrating OSINT data with dark web intelligence"""
    
    def __init__(self):
        """Initialize OSINT integration service with available sources"""
        self.sources = {
            "virustotal": VirusTotalSource(),
            "alienvault_otx": AlienVaultOTXSource(),
        }
        
        # Check which sources are available (have API keys)
        self.available_sources = []
        for name, source in self.sources.items():
            if hasattr(source, "api_key") and source.api_key:
                self.available_sources.append(name)
        
        if not self.available_sources:
            logger.warning("No OSINT sources are available. Please provide API keys.")
    
    async def enrich_threat(
        self, 
        db: AsyncSession, 
        threat_id: int,
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Enrich a threat with OSINT data.
        
        Args:
            db: Database session
            threat_id: ID of the threat to enrich
            sources: List of sources to use (defaults to all available)
            
        Returns:
            Dictionary with enrichment results
        """
        # Get the threat
        threat = await get_threat_by_id(db, threat_id)
        if not threat:
            logger.error(f"Threat with ID {threat_id} not found")
            return {"error": f"Threat with ID {threat_id} not found"}
        
        # Use all available sources if not specified
        if not sources:
            sources = self.available_sources
        else:
            # Filter out unavailable sources
            sources = [s for s in sources if s in self.available_sources]
        
        if not sources:
            logger.warning("No available OSINT sources to use for enrichment")
            return {"error": "No available OSINT sources to use for enrichment"}
        
        enrichment_results = {}
        
        # Fetch OSINT data related to the threat title and description
        search_query = f"{threat.title} {threat.description}"
        
        for source_name in sources:
            source = self.sources[source_name]
            try:
                source_data = await source.fetch_data(search_query)
                enrichment_results[source_name] = {
                    "query_results": source_data,
                    "indicators": {}
                }
                
                # Extract and add indicators from source data
                extracted_indicators = self._extract_indicators_from_source(source_name, source_data)
                if extracted_indicators:
                    # Add indicators to the threat
                    for ind in extracted_indicators:
                        try:
                            indicator = await add_indicator_to_threat(
                                db=db,
                                threat_id=threat_id,
                                value=ind["value"],
                                indicator_type=ind["type"],
                                description=ind.get("description", f"Extracted from {source_name}"),
                                source=source_name,
                                confidence_score=ind.get("confidence", 0.7),
                            )
                            
                            # Enrich the indicator with more details from the source
                            enrichment_data = await source.enrich_indicator(ind["value"], ind["type"])
                            
                            # Store enrichment data (could be stored in the database as well)
                            enrichment_results[source_name]["indicators"][ind["value"]] = enrichment_data
                            
                        except Exception as e:
                            logger.error(f"Error adding indicator from {source_name}: {e}")
                            enrichment_results[source_name]["errors"] = enrichment_results[source_name].get("errors", []) + [str(e)]
                
            except Exception as e:
                logger.error(f"Error enriching threat with {source_name}: {e}")
                enrichment_results[source_name] = {"error": str(e)}
        
        return enrichment_results
    
    def _extract_indicators_from_source(self, source_name: str, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract indicators from source data.
        
        Args:
            source_name: Name of the source
            source_data: Data from the source
            
        Returns:
            List of extracted indicators
        """
        indicators = []
        
        if source_name == "virustotal":
            # Extract indicators from VirusTotal data
            for item in source_data:
                # Extract IOCs based on VirusTotal's data structure
                attributes = item.get("attributes", {})
                
                # Extract URLs
                for url in attributes.get("urls", []):
                    indicators.append({
                        "value": url,
                        "type": "URL",
                        "confidence": 0.8,
                        "description": f"URL found in VirusTotal analysis of {item.get('id', 'unknown sample')}"
                    })
                
                # Extract domains
                for domain in attributes.get("domains", []):
                    indicators.append({
                        "value": domain,
                        "type": "DOMAIN",
                        "confidence": 0.8,
                        "description": f"Domain found in VirusTotal analysis of {item.get('id', 'unknown sample')}"
                    })
                
                # Extract IP addresses
                for ip in attributes.get("ip_addresses", []):
                    indicators.append({
                        "value": ip,
                        "type": "IP_ADDRESS",
                        "confidence": 0.8,
                        "description": f"IP address found in VirusTotal analysis of {item.get('id', 'unknown sample')}"
                    })
                
                # Extract hashes
                for hash_type in ["md5", "sha1", "sha256"]:
                    hash_value = attributes.get(hash_type)
                    if hash_value:
                        indicators.append({
                            "value": hash_value,
                            "type": "HASH",
                            "confidence": 0.9,
                            "description": f"{hash_type.upper()} hash found in VirusTotal"
                        })
        
        elif source_name == "alienvault_otx":
            # Extract indicators from AlienVault OTX data
            for pulse in source_data:
                # Extract indicators from pulse
                for indicator in pulse.get("indicators", []):
                    ind_type = indicator.get("type", "").upper()
                    ind_value = indicator.get("indicator", "")
                    
                    if ind_type and ind_value:
                        # Map OTX types to our indicator types
                        if ind_type in ["DOMAIN", "HOSTNAME"]:
                            ind_type = "DOMAIN"
                        elif ind_type in ["IPV4", "IPV6"]:
                            ind_type = "IP_ADDRESS"
                        elif ind_type in ["MD5", "SHA1", "SHA256"]:
                            ind_type = "HASH"
                        elif ind_type in ["URL"]:
                            ind_type = "URL"
                        else:
                            # Skip unsupported types
                            continue
                        
                        indicators.append({
                            "value": ind_value,
                            "type": ind_type,
                            "confidence": 0.7,
                            "description": f"Indicator from AlienVault OTX pulse: {pulse.get('name', 'Unknown')}"
                        })
        
        return indicators
    
    async def correlate_with_dark_web_content(
        self, 
        db: AsyncSession, 
        content_id: int,
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Correlate dark web content with OSINT data and create threats if significant correlations are found.
        
        Args:
            db: Database session
            content_id: ID of the dark web content to correlate
            sources: List of sources to use (defaults to all available)
            
        Returns:
            Dictionary with correlation results
        """
        from src.api.services.dark_web_content_service import get_content_by_id, create_threat_from_content
        
        # Get the content
        content = await get_content_by_id(db, content_id)
        if not content:
            logger.error(f"Content with ID {content_id} not found")
            return {"error": f"Content with ID {content_id} not found"}
        
        # Use all available sources if not specified
        if not sources:
            sources = self.available_sources
        else:
            # Filter out unavailable sources
            sources = [s for s in sources if s in self.available_sources]
        
        if not sources:
            logger.warning("No available OSINT sources to use for correlation")
            return {"error": "No available OSINT sources to use for correlation"}
        
        correlation_results = {}
        
        # Create a search query from the content
        search_query = f"{content.title or ''} {content.content[:500]}"  # Limit content length for API
        
        # Collect OSINT data from all sources
        osint_data = {}
        for source_name in sources:
            source = self.sources[source_name]
            try:
                source_data = await source.fetch_data(search_query)
                osint_data[source_name] = source_data
                correlation_results[source_name] = {"data_count": len(source_data)}
            except Exception as e:
                logger.error(f"Error fetching data from {source_name}: {e}")
                correlation_results[source_name] = {"error": str(e)}
        
        # Analyze the correlation between dark web content and OSINT data
        correlation_score = self._calculate_correlation_score(content, osint_data)
        correlation_results["correlation_score"] = correlation_score
        
        # If correlation is significant, create a threat
        if correlation_score > 0.6:  # Threshold for significant correlation
            try:
                # Determine severity based on correlation score
                severity = ThreatSeverity.MEDIUM
                if correlation_score > 0.8:
                    severity = ThreatSeverity.HIGH
                elif correlation_score < 0.7:
                    severity = ThreatSeverity.LOW
                
                # Create a threat from the content
                threat = await create_threat_from_content(
                    db=db,
                    content_id=content_id,
                    title=f"Correlated Threat: {content.title or 'Unnamed content'}",
                    description=f"Threat created due to significant correlation with OSINT data. " +
                               f"Content URL: {content.url}",
                    severity=severity,
                    category=ThreatCategory.DARK_WEB_MENTION,
                    confidence_score=correlation_score
                )
                
                correlation_results["created_threat_id"] = threat.id
                correlation_results["osint_enrichment"] = await self.enrich_threat(db, threat.id, sources)
                
            except Exception as e:
                logger.error(f"Error creating threat from correlated content: {e}")
                correlation_results["threat_creation_error"] = str(e)
        
        return correlation_results
    
    def _calculate_correlation_score(
        self, 
        content: DarkWebContent, 
        osint_data: Dict[str, List[Dict[str, Any]]]
    ) -> float:
        """
        Calculate correlation score between dark web content and OSINT data.
        
        Args:
            content: Dark web content
            osint_data: OSINT data from various sources
            
        Returns:
            Correlation score (0-1)
        """
        # This is a simplified scoring algorithm - in a real implementation,
        # this would use more sophisticated NLP and entity matching techniques
        
        # Extract text from content
        content_text = f"{content.title or ''} {content.content or ''}"
        content_words = set(self._tokenize_text(content_text))
        
        total_score = 0.0
        source_count = 0
        
        for source_name, source_data in osint_data.items():
            if not source_data:
                continue
                
            source_count += 1
            source_score = 0.0
            
            for item in source_data:
                # Extract text from OSINT item based on source type
                item_text = ""
                
                if source_name == "virustotal":
                    item_text = json.dumps(item.get("attributes", {}))
                elif source_name == "alienvault_otx":
                    pulse_text = [
                        item.get("name", ""),
                        item.get("description", ""),
                        " ".join(item.get("tags", [])),
                        " ".join([i.get("indicator", "") for i in item.get("indicators", [])])
                    ]
                    item_text = " ".join(pulse_text)
                
                item_words = set(self._tokenize_text(item_text))
                
                # Calculate Jaccard similarity
                if not item_words or not content_words:
                    continue
                    
                intersection = len(content_words.intersection(item_words))
                union = len(content_words.union(item_words))
                
                if union > 0:
                    similarity = intersection / union
                    source_score = max(source_score, similarity)
            
            # Add source score to total
            total_score += source_score
        
        # Calculate final score
        final_score = 0.0
        if source_count > 0:
            final_score = total_score / source_count
        
        # Apply a sigmoid function to normalize score
        import math
        normalized_score = 1 / (1 + math.exp(-10 * (final_score - 0.3)))
        
        return normalized_score
    
    def _tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text into words for comparison.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        if not text:
            return []
            
        # Simple tokenization - in a real implementation, this would be more sophisticated
        import re
        
        # Convert to lowercase and split by non-alphanumeric characters
        tokens = re.findall(r'\w+', text.lower())
        
        # Filter out common words and very short tokens
        stop_words = {
            "the", "a", "an", "and", "or", "but", "if", "because", "as", "what",
            "is", "in", "on", "at", "to", "for", "with", "by", "about", "of"
        }
        tokens = [t for t in tokens if t not in stop_words and len(t) > 2]
        
        return tokens


# Factory function to get a configured service
def get_osint_integration_service() -> OSINTIntegrationService:
    """Get a configured OSINT integration service."""
    return OSINTIntegrationService()