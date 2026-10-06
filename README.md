# Enterprise MCP Gateway

## Product Overview
A single secure and intelligent access layer that lets AI agents discover, route, authenticate, execute, monitor, and recover interactions with multiple enterprise tools and MCP servers.

## Architecture
See the product vision inside the repository.

## Local Setup
Ensure you have Docker and Docker Compose installed.

```bash
docker compose up --build
```

### Services
- Frontend: http://localhost:3000
- Gateway: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Customer MCP: http://localhost:8001
- Support MCP: http://localhost:8002
- Incident MCP: http://localhost:8003
