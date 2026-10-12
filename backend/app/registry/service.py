import asyncio
import logging
from typing import List, Optional
from datetime import datetime

from ..mcp.client import MCPClient, mcp_client_context
from ..mcp.models import MCPServerConfig, MCPTransport, MCPTool
from .models import RegisteredTool, ToolStatus, DiscoveryResult
from .repository import ToolRepository

logger = logging.getLogger(__name__)


class ToolRegistryService:
    """Service for discovering and managing MCP tools."""

    def __init__(self, repository: ToolRepository):
        self.repository = repository
        self.server_configs: List[MCPServerConfig] = []

    def register_server(self, config: MCPServerConfig):
        """Register an MCP server configuration."""
        self.server_configs.append(config)
        logger.info(f"Registered MCP server: {config.server_id}")

    async def discover_tools(self, server_id: Optional[str] = None) -> List[DiscoveryResult]:
        """Discover tools from MCP servers."""
        results = []
        
        configs_to_discover = []
        if server_id:
            configs_to_discover = [c for c in self.server_configs if c.server_id == server_id]
        else:
            configs_to_discover = self.server_configs

        for config in configs_to_discover:
            try:
                async with mcp_client_context(config) as client:
                    # Health check
                    is_healthy = await client.health_check()
                    
                    # List tools
                    mcp_tools = await client.list_tools()
                    
                    # Register discovered tools
                    for mcp_tool in mcp_tools:
                        # Convert input_schema to dict if it's a Pydantic model
                        if hasattr(mcp_tool.input_schema, 'model_dump'):
                            schema_dict = mcp_tool.input_schema.model_dump()
                        elif hasattr(mcp_tool.input_schema, 'dict'):
                            schema_dict = mcp_tool.input_schema.dict()
                        else:
                            schema_dict = mcp_tool.input_schema if isinstance(mcp_tool.input_schema, dict) else {}
                        
                        registered_tool = RegisteredTool(
                            tool_id=f"{config.server_id}_{mcp_tool.name}",
                            name=mcp_tool.name,
                            description=mcp_tool.description,
                            input_schema=schema_dict,
                            server_id=config.server_id,
                            server_name=config.server_name,
                            transport=config.transport.value,
                            endpoint=config.endpoint,
                            status=ToolStatus.ACTIVE if is_healthy else ToolStatus.UNHEALTHY,
                            health_status="healthy" if is_healthy else "unhealthy",
                            capabilities=self._extract_capabilities(mcp_tool)
                        )
                        self.repository.upsert(registered_tool)
                    
                    results.append(DiscoveryResult(
                        server_id=config.server_id,
                        tools_discovered=len(mcp_tools),
                        success=True
                    ))
                    logger.info(f"Discovered {len(mcp_tools)} tools from {config.server_id}")
                    
            except Exception as e:
                logger.error(f"Failed to discover tools from {config.server_id}: {e}")
                results.append(DiscoveryResult(
                    server_id=config.server_id,
                    tools_discovered=0,
                    success=False,
                    error_message=str(e)
                ))

        return results

    def _extract_capabilities(self, tool: MCPTool) -> List[str]:
        """Extract capabilities from tool name and description."""
        capabilities = []
        name_lower = tool.name.lower()
        desc_lower = tool.description.lower()
        
        # Common capability keywords
        capability_keywords = {
            "get": "read",
            "fetch": "read",
            "retrieve": "read",
            "find": "read",
            "search": "read",
            "list": "read",
            "create": "write",
            "add": "write",
            "insert": "write",
            "update": "write",
            "modify": "write",
            "edit": "write",
            "delete": "delete",
            "remove": "delete",
            "customer": "customer",
            "ticket": "support",
            "incident": "incident",
            "support": "support",
            "billing": "billing",
            "account": "account",
        }
        
        for keyword, capability in capability_keywords.items():
            if keyword in name_lower or keyword in desc_lower:
                if capability not in capabilities:
                    capabilities.append(capability)
        
        return capabilities

    def get_tools(self) -> List[RegisteredTool]:
        """Get all registered tools."""
        return self.repository.list_all()

    def get_tool(self, tool_id: str) -> Optional[RegisteredTool]:
        """Get a specific tool by ID."""
        return self.repository.get(tool_id)

    def search_tools(self, query: str) -> List[RegisteredTool]:
        """Search tools by capability, name, or description."""
        return self.repository.search(query)

    async def refresh_health(self):
        """Refresh health status of all tools."""
        for config in self.server_configs:
            try:
                async with mcp_client_context(config) as client:
                    is_healthy = await client.health_check()
                    health_status = "healthy" if is_healthy else "unhealthy"
                    status = ToolStatus.ACTIVE if is_healthy else ToolStatus.UNHEALTHY
                    
                    for tool in self.repository.list_by_server(config.server_id):
                        self.repository.update_health(tool.tool_id, health_status)
                        self.repository.update_status(tool.tool_id, status)
            except Exception as e:
                logger.error(f"Failed to refresh health for {config.server_id}: {e}")
                for tool in self.repository.list_by_server(config.server_id):
                    self.repository.update_health(tool.tool_id, "unreachable")
                    self.repository.update_status(tool.tool_id, ToolStatus.UNHEALTHY)
