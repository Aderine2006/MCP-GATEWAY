# Enterprise MCP Gateway

## Product Overview
A single secure and intelligent access layer that lets AI agents discover, route, authenticate, execute, monitor, and recover interactions with multiple enterprise tools and MCP servers.

## Features

### Tool Registry Agent
- Discovers tools from multiple MCP servers via stdio transport
- Maintains centralized tool registry with capabilities, schemas, and health status
- Supports tool registration, updates, and duplicate-safe upserts
- Tracks discovery timestamps and tool availability
- Handles unreachable servers gracefully

### Intent-to-Tool Router Agent
- Accepts natural-language user requests
- Extracts intent, required capability, parameters, and operation type
- Matches requests to tools using keyword-based analysis (with LLM fallback if configured)
- Ranks candidates by capability compatibility and server health
- Enforces authorization policies before execution
- Validates input parameters against tool schemas
- Returns execution results with routing traces

### API Endpoints
- `GET /api/health` - Gateway and tool registry health
- `GET /api/tools` - List all registered tools
- `POST /api/tools/discover` - Refresh tool discovery from MCP servers
- `POST /api/tools/search` - Search tools by capability/name/description
- `POST /api/route` - Route natural language request to appropriate tool
- `POST /api/tools/execute` - Execute a specific tool by ID

## Architecture

The system consists of:
- **Frontend**: Next.js dashboard for natural language requests and tool visualization
- **Gateway**: FastAPI backend with Tool Registry and Intent Router agents
- **MCP Servers**: Three independent MCP servers (Customer, Support, Incident)
- **Transport**: stdio-based communication with FastMCP servers

## Local Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Installation

1. Clone the repository and navigate to the project directory

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
cd ..
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

4. Copy environment example:
```bash
cp .env.example .env
```

### Running All Services

The easiest way to start all services is using the provided script:

```bash
python run_all.py
```

This will start:
- Customer MCP Server (stdio)
- Support MCP Server (stdio)
- Incident MCP Server (stdio)
- Gateway API (FastAPI on port 8000)
- Frontend (Next.js on port 3000)

### Running Services Individually

**Backend (Gateway API):**
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**MCP Servers (for development):**
```bash
# Customer MCP
cd mcp_servers/customer
python server.py

# Support MCP
cd mcp_servers/support
python server.py

# Incident MCP
cd mcp_servers/incident
python server.py
```

### Using Docker

Ensure you have Docker and Docker Compose installed.

```bash
docker compose up --build
```

## Service URLs

- Frontend: http://localhost:3000
- Gateway API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

## Example Usage

### Via Frontend
1. Open http://localhost:3000
2. Click "Discover Tools" to register available MCP tools
3. Enter a natural language request, e.g.:
   - "Find the details of customer 1024"
   - "Search for open support tickets"
   - "Create an incident for a server outage"
4. Click "Route Request" to analyze and select the appropriate tool
5. Enable "Auto Execute" to automatically execute the selected tool
6. Enable "Force Execute" to bypass confirmation for write operations

### Via API

**Discover tools:**
```bash
curl -X POST http://localhost:8000/api/tools/discover
```

**List tools:**
```bash
curl http://localhost:8000/api/tools
```

**Route a request:**
```bash
curl -X POST http://localhost:8000/api/route \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Find the details of customer 1024",
    "auto_execute": true
  }'
```

**Search tools:**
```bash
curl -X POST http://localhost:8000/api/tools/search \
  -H "Content-Type: application/json" \
  -d '{"query": "customer"}'
```

## Testing

Run the test suite:

```bash
cd backend
pytest tests/
```

Tests cover:
- Tool repository operations
- Intent extraction and matching
- Permission checking and parameter validation
- API integration tests

## Configuration

### Environment Variables

Create a `.env` file in the project root (see `.env.example`):

- `NEXT_PUBLIC_API_URL`: Gateway API URL (default: http://localhost:8000)
- `API_HOST`: Gateway host (default: 127.0.0.1)
- `API_PORT`: Gateway port (default: 8000)
- `OPENAI_API_KEY`: Optional LLM API key for enhanced intent extraction

### Adding New MCP Servers

To add a new MCP server:

1. Create the server in `mcp_servers/<server-name>/server.py`
2. Register the server configuration in `backend/app/main.py`:
```python
new_config = MCPServerConfig(
    server_id="new-mcp",
    server_name="New MCP",
    transport=MCPTransport.STDIO,
    command=python_executable,
    args=[str(base_dir / "mcp_servers" / "new" / "server.py")]
)
registry_service.register_server(new_config)
intent_router.register_server_config(new_config)
```

## Security

- Write operations require confirmation by default
- Force execution flag bypasses confirmation (use with caution)
- Input validation against tool schemas
- Health checks before tool execution
- No automatic retries of non-idempotent operations
- Secrets are never exposed in API responses

## Development

### Project Structure
```
enterprise-mcp-gateway/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── mcp/          # MCP client and models
│   │   ├── registry/     # Tool Registry Agent
│   │   ├── router/       # Intent Router Agent
│   │   ├── schemas/      # Pydantic schemas
│   │   └── main.py       # FastAPI application
│   ├── tests/            # Test suite
│   └── requirements.txt
├── frontend/
│   ├── app/              # Next.js app
│   └── package.json
├── mcp_servers/          # MCP server implementations
│   ├── customer/
│   ├── support/
│   └── incident/
├── run_all.py            # Startup script
└── README.md
```

## Troubleshooting

**Tools not discovered:**
- Ensure MCP servers are running before starting the gateway
- Check that Python executable path is correct in main.py
- Verify MCP server scripts are executable

**Routing fails:**
- Run tool discovery first via the frontend or API
- Check that tools are in "active" status
- Verify request contains clear intent keywords

**Frontend can't connect to API:**
- Check NEXT_PUBLIC_API_URL in frontend environment
- Verify gateway is running on port 8000
- Check CORS settings in main.py
