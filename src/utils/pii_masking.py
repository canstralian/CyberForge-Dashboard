"""
PII Detection and Masking Utility.

This module provides functionality to detect and mask personally identifiable information (PII)
in text data, including sensitive information like:
- Email addresses
- Phone numbers
- Social security numbers
- Credit card numbers
- IP addresses
- Addresses
- Names
"""
import re
import logging
import json
from typing import Dict, List, Set, Tuple, Union, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class PIIDetector:
    """
    Class for detecting personally identifiable information (PII) in text.
    
    This detector uses regex patterns to identify common PII patterns.
    """
    
    def __init__(self) -> None:
        """Initialize PII detector with regex patterns"""
        
        # Email patterns
        self.email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        
        # Phone number patterns (various formats)
        self.phone_patterns = [
            re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),  # 555-555-5555, 555.555.5555, etc.
            re.compile(r"\b\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b"),  # (555) 555-5555
            re.compile(r"\b\+\d{1,3}\s?\(\d{1,3}\)\s?\d{3}[-.\s]?\d{4}\b"),  # +1 (555) 555-5555
            re.compile(r"\b\+\d{1,3}\s?\d{1,3}\s?\d{3,4}\s?\d{4}\b"),  # +1 555 555 5555
        ]
        
        # Social Security Number pattern
        self.ssn_pattern = re.compile(r"\b\d{3}[-]?\d{2}[-]?\d{4}\b")
        
        # Credit card number pattern (simplified)
        self.credit_card_pattern = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
        
        # IP address pattern
        self.ip_address_pattern = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
        
        # URL pattern
        self.url_pattern = re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+")
        
        # Date pattern (various formats)
        self.date_patterns = [
            re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),  # MM/DD/YYYY, DD/MM/YYYY
            re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b", re.IGNORECASE)  # January 1, 2020
        ]
        
        # Address pattern (simplified)
        self.address_pattern = re.compile(r"\b\d+\s+[A-Za-z0-9\s,]+(?:Avenue|Ave|Boulevard|Blvd|Circle|Cir|Court|Ct|Drive|Dr|Lane|Ln|Parkway|Pkwy|Place|Pl|Road|Rd|Square|Sq|Street|St|Way)\.?\b", re.IGNORECASE)
        
        # Name patterns (needs a list of names, simplified here)
        self.name_prefixes = ["Mr", "Mrs", "Ms", "Miss", "Dr", "Prof"]
        self.name_pattern = re.compile(r"\b(?:" + "|".join(self.name_prefixes) + r")\.\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b")
        
        # Map of patterns to PII types
        self.pattern_map = {
            "EMAIL": [self.email_pattern],
            "PHONE": self.phone_patterns,
            "SSN": [self.ssn_pattern],
            "CREDIT_CARD": [self.credit_card_pattern],
            "IP_ADDRESS": [self.ip_address_pattern],
            "URL": [self.url_pattern],
            "DATE": self.date_patterns,
            "ADDRESS": [self.address_pattern],
            "NAME": [self.name_pattern]
        }
    
    def detect(self, text: str) -> Dict[str, List[Tuple[int, int, str]]]:
        """
        Detect PII in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping PII types to lists of (start, end, value) tuples
        """
        if not text:
            return {}
            
        results = {}
        
        # Process each pattern type
        for pii_type, patterns in self.pattern_map.items():
            matches = []
            
            # Process each pattern for this type
            for pattern in patterns:
                for match in pattern.finditer(text):
                    start, end = match.span()
                    value = match.group()
                    matches.append((start, end, value))
            
            # If we found matches, add them to results
            if matches:
                results[pii_type] = sorted(matches, key=lambda x: x[0])
        
        return results
    
    def contains_pii(self, text: str) -> bool:
        """
        Check if text contains any PII.
        
        Args:
            text: Text to check
            
        Returns:
            True if PII is detected, False otherwise
        """
        return len(self.detect(text)) > 0
    
    def get_pii_types_found(self, text: str) -> Set[str]:
        """
        Get the types of PII found in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Set of PII types found
        """
        return set(self.detect(text).keys())


class PIIMasker:
    """
    Class for masking personally identifiable information (PII) in text.
    """
    
    def __init__(self, detector: Optional[PIIDetector] = None) -> None:
        """
        Initialize PII masker with detector.
        
        Args:
            detector: PIIDetector instance, or None to create a new one
        """
        self.detector = detector or PIIDetector()
        
        # Default masking strategies
        self.masking_strategies = {
            "EMAIL": self._mask_email,
            "PHONE": self._mask_phone,
            "SSN": self._mask_ssn,
            "CREDIT_CARD": self._mask_credit_card,
            "IP_ADDRESS": self._mask_ip_address,
            "URL": self._mask_url,
            "DATE": lambda x: "[DATE]",
            "ADDRESS": lambda x: "[ADDRESS]",
            "NAME": lambda x: "[NAME]"
        }
    
    def _mask_email(self, email: str) -> str:
        """Mask an email address"""
        parts = email.split("@")
        if len(parts) != 2:
            return "[EMAIL]"
            
        username, domain = parts
        
        # Mask username but preserve first character
        if len(username) > 1:
            masked_username = username[0] + "****"
        else:
            masked_username = "****"
            
        return f"{masked_username}@{domain}"
    
    def _mask_phone(self, phone: str) -> str:
        """Mask a phone number"""
        # Remove non-digit characters
        digits = "".join(char for char in phone if char.isdigit())
        
        # Determine how many digits to keep at the end
        if len(digits) <= 4:
            return "[PHONE]"
        else:
            return "****" + digits[-4:]
    
    def _mask_ssn(self, ssn: str) -> str:
        """Mask a social security number"""
        # Remove non-digit characters
        digits = "".join(char for char in ssn if char.isdigit())
        
        # Only keep last 4 digits
        if len(digits) != 9:
            return "[SSN]"
        else:
            return "XXX-XX-" + digits[-4:]
    
    def _mask_credit_card(self, cc: str) -> str:
        """Mask a credit card number"""
        # Remove non-digit characters
        digits = "".join(char for char in cc if char.isdigit())
        
        # Keep only first 4 and last 4 digits
        if len(digits) < 12:
            return "[CREDIT_CARD]"
        else:
            return digits[:4] + " **** **** " + digits[-4:]
    
    def _mask_ip_address(self, ip: str) -> str:
        """Mask an IP address"""
        octets = ip.split(".")
        if len(octets) != 4:
            return "[IP_ADDRESS]"
            
        # Mask last two octets
        return f"{octets[0]}.{octets[1]}.***.***"
    
    def _mask_url(self, url: str) -> str:
        """Mask a URL"""
        return "[URL]"
    
    def mask_text(self, text: str) -> str:
        """
        Mask PII in text.
        
        Args:
            text: Text to mask
            
        Returns:
            Text with PII masked
        """
        if not text:
            return text
            
        # Detect PII
        pii_detected = self.detector.detect(text)
        if not pii_detected:
            return text
            
        # Create a list of tuples (position, is_start, pii_type, original_value)
        # to mark start and end positions of PII
        markers = []
        for pii_type, matches in pii_detected.items():
            for start, end, value in matches:
                markers.append((start, True, pii_type, value))  # start marker
                markers.append((end, False, pii_type, value))  # end marker
        
        # Sort markers by position, with start markers coming before end markers at same position
        markers.sort(key=lambda x: (x[0], not x[1]))
        
        # Build masked text
        result = []
        last_pos = 0
        active_pii = {}  # Maps PII type to list of active PII values
        
        for pos, is_start, pii_type, value in markers:
            # Add text before this marker
            if pos > last_pos:
                result.append(text[last_pos:pos])
            
            if is_start:
                # Start of PII
                if pii_type not in active_pii:
                    active_pii[pii_type] = []
                active_pii[pii_type].append(value)
            else:
                # End of PII
                if pii_type in active_pii and active_pii[pii_type]:
                    # Get original value
                    original = active_pii[pii_type].pop()
                    
                    # Apply masking strategy if this is the end of the PII
                    if not active_pii[pii_type]:  # No more active PII of this type
                        mask_func = self.masking_strategies.get(pii_type, lambda x: f"[{pii_type}]")
                        masked = mask_func(original)
                        result.append(masked)
            
            last_pos = pos
        
        # Add remaining text
        if last_pos < len(text):
            result.append(text[last_pos:])
        
        return "".join(result)
    
    def mask_json(self, json_data: Union[Dict, List]) -> Union[Dict, List]:
        """
        Mask PII in JSON data.
        
        Args:
            json_data: JSON data to mask
            
        Returns:
            JSON data with PII masked
        """
        if isinstance(json_data, dict):
            return {k: self._mask_value(v) for k, v in json_data.items()}
        elif isinstance(json_data, list):
            return [self._mask_value(v) for v in json_data]
        else:
            return json_data
    
    def _mask_value(self, value: Any) -> Any:
        """
        Mask a value in JSON data.
        
        Args:
            value: Value to mask
            
        Returns:
            Masked value
        """
        if isinstance(value, str):
            return self.mask_text(value)
        elif isinstance(value, dict):
            return self.mask_json(value)
        elif isinstance(value, list):
            return [self._mask_value(v) for v in value]
        else:
            return value


# Factory function to get a configured PII detector
def get_pii_detector() -> PIIDetector:
    """Get a configured PII detector."""
    return PIIDetector()

# Factory function to get a configured PII masker
def get_pii_masker() -> PIIMasker:
    """Get a configured PII masker."""
    return PIIMasker()