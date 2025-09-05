"""
PTV API Client Implementation.

This module handles authentication and communication with the PTV Timetable API.
"""

import hashlib
import hmac
import logging
import os
import urllib.parse
from typing import Any, Dict, Optional

import httpx


logger = logging.getLogger(__name__)


# Route type constants
ROUTE_TYPES = {
    0: "Train",
    1: "Tram", 
    2: "Bus",
    3: "V/Line",
    4: "Night Bus"
}


class PTVConfig:
    """Configuration for PTV API access."""
    
    def __init__(self, validate_credentials: bool = True):
        self.base_url = "https://timetableapi.ptv.vic.gov.au"
        self.api_version = os.getenv("PTV_API_VERSION", "v3")
        self.dev_id = os.getenv("PTV_DEV_ID")
        self.dev_key = os.getenv("PTV_DEV_KEY")
        
        if validate_credentials and (not self.dev_id or not self.dev_key):
            raise ValueError(
                "PTV API credentials are required. Please set PTV_DEV_ID and PTV_DEV_KEY environment variables. "
                "Get your credentials from https://www.vic.gov.au/public-transport-timetable-api"
            )


class PTVClient:
    """Client for interacting with PTV Timetable API."""
    
    def __init__(self, config: PTVConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _generate_signature(self, request_url: str) -> str:
        """Generate HMAC signature for PTV API authentication."""
        key = self.config.dev_key.encode('utf-8')
        raw = request_url.encode('utf-8')
        signature = hmac.new(key, raw, hashlib.sha1).hexdigest()
        return signature.upper()
    
    def _build_url(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Build complete URL with authentication for PTV API."""
        # Add dev_id to params
        if params is None:
            params = {}
        params['devid'] = self.config.dev_id
        
        # Build request URL without signature
        query_string = urllib.parse.urlencode(params)
        request_url = f"{endpoint}?{query_string}"
        
        # Generate signature
        signature = self._generate_signature(request_url)
        
        # Add signature to URL
        final_url = f"{self.config.base_url}{request_url}&signature={signature}"
        return final_url
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make authenticated request to PTV API."""
        url = self._build_url(endpoint, params)
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
