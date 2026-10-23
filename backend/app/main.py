import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.registry.service import ToolRegistryService
from app.registry.repository import ToolRepository
from app.router.intent_router import IntentRouter
from app.mcp.models import MCPServerConfig, MCPTransport
from app.api.tools import router as tools_router
from app.api.route import router as route_router
from app.api.health import router as health_router
from app.api.summary import router as summary_router
from app.api.metrics import router as metrics_router
from app.api.alerts import router as alerts_router
from app.api.events import router as events_router
from app.api.agents import router as agents_router
from app.rate_limit.service import RateLimitService

# Initialize services
repository = ToolRepository()
registry_service = ToolRegistryService(repository)
intent_router = IntentRouter(registry_service)

# Register MCP server configurations (HTTP-based for MVP)
# Customer MCP Server
customer_config = MCPServerConfig(
    server_id="customer-mcp",
    server_name="Customer MCP",
    transport=MCPTransport.HTTP,
    endpoint="http://127.0.0.1:8001"
)
registry_service.register_server(customer_config)
intent_router.register_server_config(customer_config)

# Support MCP Server
support_config = MCPServerConfig(
    server_id="support-mcp",
    server_name="Support MCP",
    transport=MCPTransport.HTTP,
    endpoint="http://127.0.0.1:8002"
)
registry_service.register_server(support_config)
intent_router.register_server_config(support_config)

# Incident MCP Server
incident_config = MCPServerConfig(
    server_id="incident-mcp",
    server_name="Incident MCP",
    transport=MCPTransport.HTTP,
    endpoint="http://127.0.0.1:8003"
)
registry_service.register_server(incident_config)
intent_router.register_server_config(incident_config)

# About MCP Server
about_config = MCPServerConfig(
    server_id="about-mcp",
    server_name="About MCP",
    transport=MCPTransport.HTTP,
    endpoint="http://127.0.0.1:8004"
)
registry_service.register_server(about_config)
intent_router.register_server_config(about_config)

# Create FastAPI app
app = FastAPI(
    title="Enterprise MCP Gateway",
    description="Intelligent access layer for AI agents to discover, route, and execute MCP tools",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tools_router)
app.include_router(route_router)
app.include_router(health_router)
app.include_router(summary_router)
app.include_router(metrics_router)
app.include_router(alerts_router)
app.include_router(events_router)
app.include_router(agents_router)

@app.on_event("startup")
async def startup_event():
    """Initialize tool discovery on startup."""
    print("Starting tool discovery...")
    await registry_service.discover_tools()
    print("Tool discovery complete.")

@app.get("/")
async def root():
    return {
        "message": "Enterprise MCP Gateway",
        "version": "1.0.0",
        "docs": "/docs"
    }
