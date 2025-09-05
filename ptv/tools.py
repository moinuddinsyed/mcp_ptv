"""
PTV MCP Server Tools Implementation.

This module contains all the tool definitions and handlers for the PTV MCP server.
"""

import json
import urllib.parse
from typing import List, Optional
from datetime import datetime

from .client import PTVClient, ROUTE_TYPES


async def get_departures(ptv_client: PTVClient, route_type: int, stop_id: int, max_results: int = 15, date_utc: Optional[str] = None) -> str:
    """
    Get departure times for all routes from a specific stop.
    
    Args:
        ptv_client: PTV API client instance
        route_type: Transport mode (0=Train, 1=Tram, 2=Bus, 3=V/Line, 4=Night Bus)
        stop_id: Identifier of the stop
        max_results: Maximum number of results (default 5)
        date_utc: Filter by date and time (ISO 8601 UTC format, optional)
    
    Returns:
        Formatted departure information
    """
    try:
        endpoint = f"/{ptv_client.config.api_version}/departures/route_type/{route_type}/stop/{stop_id}"
        params = {"max_results": max_results}
        if date_utc:
            params["date_utc"] = date_utc
        data = await ptv_client._make_request(endpoint, params)
        
        departures = data.get("departures", [])
        if not departures:
            return "No departures found for this stop."
        
        result = f"Departures from stop {stop_id} ({ROUTE_TYPES.get(route_type, 'Unknown')}):\n\n"
        
        for dep in departures[:max_results]:
            scheduled_time = dep.get("scheduled_departure_utc", "")
            estimated_time = dep.get("estimated_departure_utc", "")
            route_name = dep.get("route_id", "Unknown")
            platform = dep.get("platform_number", "")
            
            if estimated_time:
                time_str = f"Est: {estimated_time}"
            else:
                time_str = f"Sch: {scheduled_time}"
            
            platform_str = f" Platform {platform}" if platform else ""
            result += f"• Route {route_name} - {time_str}{platform_str}\n"
        
        return result
        
    except Exception as e:
        return f"Error getting departures: {str(e)}"


async def search_stops(ptv_client: PTVClient, search_term: str, route_types: Optional[List[int]] = None) -> str:
    """
    Search for stops by name.
    
    Args:
        ptv_client: PTV API client instance
        search_term: Search term for stop name
        route_types: Optional list of route types to filter by (currently disabled)
    
    Returns:
        List of matching stops
    """
    try:
        params = {}
        # TODO: route_types parameter not working properly, commented out for now
        # if route_types:
        #     params["route_types"] = route_types
        
        endpoint = f"/{ptv_client.config.api_version}/search/" + urllib.parse.quote(search_term)
        data = await ptv_client._make_request(endpoint, params)
        
        stops = data.get("stops", [])
        if not stops:
            return f"No stops found matching '{search_term}'."
        
        result = f"Stops matching '{search_term}':\n\n"
        
        for stop in stops[:10]:  # Limit to 10 results
            stop_name = stop.get("stop_name", "Unknown")
            stop_id = stop.get("stop_id", "")
            route_type = stop.get("route_type", "")
            route_type_name = ROUTE_TYPES.get(route_type, f"Type {route_type}")
            
            result += f"• {stop_name} (ID: {stop_id}) - {route_type_name}\n"
        
        return result
        
    except Exception as e:
        return f"Error searching stops: {str(e)}"


async def get_routes(ptv_client: PTVClient, route_name: Optional[str] = None, route_types: Optional[List[int]] = None) -> str:
    """
    Get routes, optionally filtered by name or transport mode.
    
    Args:
        ptv_client: PTV API client instance
        route_name: Optional route name to filter by
        route_types: Optional list of route types to filter by (currently disabled)
    
    Returns:
        List of routes
    """
    try:
        params = {}
        if route_name:
            params["route_name"] = route_name
        # TODO: route_types parameter not working properly, commented out for now
        # if route_types:
        #     params["route_types"] = route_types
        
        endpoint = f"/{ptv_client.config.api_version}/routes"
        data = await ptv_client._make_request(endpoint, params)
        
        routes = data.get("routes", [])
        if not routes:
            return "No routes found."
        
        result = "Available routes:\n\n"
        
        for route in routes[:20]:  # Limit to 20 results
            route_name = route.get("route_name", "Unknown")
            route_id = route.get("route_id", "")
            route_type = route.get("route_type", "")
            route_type_name = ROUTE_TYPES.get(route_type, f"Type {route_type}")
            
            result += f"• {route_name} (ID: {route_id}) - {route_type_name}\n"
        
        return result
        
    except Exception as e:
        return f"Error getting routes: {str(e)}"


async def get_disruptions(ptv_client: PTVClient, route_types: Optional[List[int]] = None) -> str:
    """
    Get current service disruptions.
    
    Args:
        ptv_client: PTV API client instance
        route_types: Optional list of route types to filter by (currently disabled)
    
    Returns:
        Current service disruption information
    """
    try:
        params = {}
        # TODO: route_types parameter not working properly, commented out for now
        # if route_types:
        #     params["route_types"] = route_types
        
        endpoint = f"/{ptv_client.config.api_version}/disruptions"
        data = await ptv_client._make_request(endpoint, params)
        
        disruptions = data.get("disruptions", {})
        if not any(disruptions.values()):
            return "No current disruptions found."
        
        result = "Current Disruptions:\n\n"
        
        for mode, mode_disruptions in disruptions.items():
            if mode_disruptions:
                result += f"{mode.title()} Disruptions:\n"
                for disruption in mode_disruptions[:5]:  # Limit to 5 per mode
                    title = disruption.get("title", "Unknown")
                    description = disruption.get("description", "")
                    status = disruption.get("disruption_status", "")
                    
                    result += f"• {title}"
                    if status:
                        result += f" ({status})"
                    result += "\n"
                    if description:
                        result += f"  {description[:200]}...\n" if len(description) > 200 else f"  {description}\n"
                result += "\n"
        
        return result
        
    except Exception as e:
        return f"Error getting disruptions: {str(e)}"


async def get_route_types(ptv_client: PTVClient) -> str:
    """
    Get all available transport modes in Melbourne.
    
    Args:
        ptv_client: PTV API client instance
    
    Returns:
        List of available transport modes
    """
    try:
        endpoint = f"/{ptv_client.config.api_version}/route_types"
        data = await ptv_client._make_request(endpoint)
        
        route_types = data.get("route_types", [])
        
        result = "Available Transport Modes:\n\n"
        for rt in route_types:
            route_type_id = rt.get("route_type", "")
            route_type_name = rt.get("route_type_name", "Unknown")
            result += f"• {route_type_name} (ID: {route_type_id})\n"
        
        return result
        
    except Exception as e:
        return f"Error getting route types: {str(e)}"


# Resource handlers
async def get_route_types_resource(ptv_client: PTVClient) -> str:
    """Get route types data as JSON resource."""
    try:
        endpoint = f"/{ptv_client.config.api_version}/route_types"
        data = await ptv_client._make_request(endpoint)
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def get_config_resource(config) -> str:
    """Get PTV server configuration as JSON resource."""
    config_data = {
        "base_url": config.base_url,
        "dev_id": config.dev_id,
        "dev_key_configured": bool(config.dev_key),
        "route_types": ROUTE_TYPES,
        "timestamp": datetime.now().isoformat()
    }
    return json.dumps(config_data, indent=2)


# Prompt generators
def transport_query_prompt(location: str, transport_type: str = "any") -> str:
    """Generate a prompt for Melbourne transport queries."""
    prompts = {
        "train": f"Help me find train information for {location}. Include departures, any disruptions, and nearby stops.",
        "tram": f"Help me find tram information for {location}. Include stops, routes, and current service status.",
        "bus": f"Help me find bus information for {location}. Include nearby stops, routes, and any delays.",
        "any": f"Help me find public transport information for {location}. Include all available transport options, departures, and any service disruptions."
    }
    
    return prompts.get(transport_type.lower(), prompts["any"])


def journey_planner_prompt(origin: str, destination: str) -> str:
    """Generate a prompt for journey planning in Melbourne."""
    return f"""Help me plan a journey from {origin} to {destination} using Melbourne public transport. Please:

1. Find the best transport options (train, tram, bus)
2. Check for any current service disruptions
3. Provide departure times and estimated journey duration
4. Suggest alternative routes if available
5. Include any accessibility information if relevant

Use the PTV tools to get real-time information for this journey."""
