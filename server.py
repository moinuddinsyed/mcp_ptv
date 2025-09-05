#!/usr/bin/env python3
"""
FastMCP PTV Server - Melbourne Public Transport MCP Server.

A clean, modular MCP server that provides real-time access to PTV (Public Transport Victoria) data
including departures, stops, routes, and service disruptions.

Installation:
    uv run mcp install server.py
    
Usage:
    Ask Claude about Melbourne public transport:
    - "What are the next departures from Flinders Street Station?"
    - "Find me tram stops near Melbourne Central"
    - "Are there any current train disruptions?"
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

# Add the project directory to Python path for imports
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from mcp.server.fastmcp import FastMCP
from ptv.client import PTVConfig, PTVClient
from ptv import tools

# Create the FastMCP server
mcp = FastMCP("PTV Melbourne Transport")

# Initialize PTV client - don't validate credentials during import/installation
config = PTVConfig(validate_credentials=False)
ptv_client = None

def _ensure_ptv_client():
    """Lazy initialization of PTV client with credential validation."""
    global ptv_client
    if ptv_client is None:
        validated_config = PTVConfig(validate_credentials=True)
        ptv_client = PTVClient(validated_config)
    return ptv_client


@mcp.tool()
async def get_departures(route_type: int, stop_id: int, max_results: int = 5, date_utc: Optional[str] = None) -> str:
    """
    Get departure times for all routes from a specific stop.
    
    Args:
        route_type: Transport mode (0=Train, 1=Tram, 2=Bus, 3=V/Line, 4=Night Bus)
        stop_id: Identifier of the stop
        max_results: Maximum number of results (default 5)
        date_utc: Filter by date and time (ISO 8601 UTC format, e.g. "2025-08-31T14:00:00Z")
    
    Returns:
        Formatted departure information
    """
    return await tools.get_departures(_ensure_ptv_client(), route_type, stop_id, max_results, date_utc)


@mcp.tool()
async def search_stops(search_term: str, route_types: Optional[List[int]] = None) -> str:
    """
    Search for stops by name.
    
    Args:
        search_term: Search term for stop name
        route_types: Optional list of route types to filter by
    
    Returns:
        List of matching stops
    """
    return await tools.search_stops(_ensure_ptv_client(), search_term, route_types)


@mcp.tool()
async def get_routes(route_name: Optional[str] = None, route_types: Optional[List[int]] = None) -> str:
    """
    Get routes, optionally filtered by name or transport mode.
    
    Args:
        route_name: Optional route name to filter by
        route_types: Optional list of route types to filter by
    
    Returns:
        List of routes
    """
    return await tools.get_routes(_ensure_ptv_client(), route_name, route_types)


@mcp.tool()
async def get_disruptions(route_types: Optional[List[int]] = None) -> str:
    """
    Get current service disruptions.
    
    Args:
        route_types: Optional list of route types to filter by
    
    Returns:
        Current service disruption information
    """
    return await tools.get_disruptions(_ensure_ptv_client(), route_types)


@mcp.tool()
async def get_route_types() -> str:
    """
    Get all available transport modes in Melbourne.
    
    Returns:
        List of available transport modes
    """
    return await tools.get_route_types(_ensure_ptv_client())


@mcp.resource("ptv://route-types")
async def get_route_types_resource() -> str:
    """Get route types data as JSON resource."""
    return await tools.get_route_types_resource(_ensure_ptv_client())


@mcp.resource("ptv://config")
def get_config_resource() -> str:
    """Get PTV server configuration as JSON resource."""
    return tools.get_config_resource(config)


@mcp.prompt()
def transport_query(location: str, transport_type: str = "any") -> str:
    """Generate a prompt for Melbourne transport queries."""
    return tools.transport_query_prompt(location, transport_type)


@mcp.prompt()
def journey_planner(origin: str, destination: str) -> str:
    """Generate a prompt for journey planning in Melbourne."""
    return tools.journey_planner_prompt(origin, destination)


if __name__ == "__main__":
    # Set environment variables if not already set
    # os.environ.setdefault("PTV_DEV_ID", "XXXXXXXX")
    # os.environ.setdefault("PTV_DEV_KEY", "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXX")
    
    # Run the server
    mcp.run()
