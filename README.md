# MCP PTV Server

A [Model Context Protocol](https://github.com/modelcontextprotocol/python-sdk) server that provides AI assistants access to Melbourne's public transport data through the PTV (Public Transport Victoria) API. Query real-time departures, find stops, check disruptions, and get route information for trains, trams, buses, and V/Line services.

## What This Project Offers

- **Real-time departures** from any stop across Melbourne's transport network
- **Stop search** to find stations, tram stops, and bus stops by name
- **Route information** for all transport modes (train, tram, bus, V/Line)
- **Service disruptions** and alerts for current network issues
- **Transport mode data** with comprehensive coverage of Melbourne's public transport

All data comes directly from Public Transport Victoria's official API, providing accurate and up-to-date information.

## Prerequisites

- Python 3.10 or higher
- [uv package manager](https://docs.astral.sh/uv/)
- Claude Desktop (or another MCP-compatible AI assistant)
- **PTV API credentials** (free registration required)

## Getting PTV API Credentials

1. **Register for PTV API access**:
   - Visit [PTV Timetable API registration](https://www.ptv.vic.gov.au/footer/data-and-reporting/datasets/ptv-timetable-api/)
   - Fill out the registration form
   - You'll receive your `Developer ID` and `API Key` via email

2. **Set environment variables**:
   ```bash
   export PTV_DEV_ID="your_developer_id_here"
   export PTV_DEV_KEY="your_api_key_here"
   ```

## Installation & Usage

1. **Get your PTV API credentials** (see above section)

2. **Install the server with your credentials**:
   ```bash
   cd mcp_ptv
   uv run mcp install server.py --env-var PTV_DEV_ID=your_developer_id_here --env-var PTV_DEV_KEY=your_api_key_here
   ```

3. **Restart Claude Desktop**

4. **Start asking transport questions**:
   - *"What are the next departures from Flinders Street Station?"*
   - *"Find me tram stops near Melbourne Central"*
   - *"Are there any current train disruptions?"*
   - *"Show me all routes for the 86 tram"*

## What's Included

### Tools Available
- `get_departures` - Real-time departure times from any stop
- `search_stops` - Find stops by name across all transport modes  
- `get_routes` - Browse available routes with filtering options
- `get_disruptions` - Current service disruptions and alerts
- `get_route_types` - Transport mode information (Train, Tram, Bus, V/Line, Night Bus)

### Resources Available
1. **`ptv://route-types`** - JSON data of all transport modes
2. **`ptv://config`** - Server configuration and status information

### Prompts Available
1. **`transport_query`** - Generate transport information prompts
2. **`journey_planner`** - Create journey planning prompts

### Transport Coverage
- Metropolitan trains (including night services)
- Trams (including night trams)
- Metropolitan and regional buses
- V/Line regional train services

## Upcoming Improvements & Features

- Streamline the filtering with route type
- Resolve stop duplication issue in the API

---

*This is an unofficial implementation and is not affiliated with Public Transport Victoria.*

**Data Attribution**: Source: Licensed from Public Transport Victoria under a Creative Commons Attribution 4.0 International Licence.