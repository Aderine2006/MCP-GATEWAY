import asyncio
import httpx
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import logging

from .models import MCPTool, MCPServerConfig, MCPTransport

logger = logging.getLogger(__name__)


class MCPClient:
    """HTTP client for communicating with MCP servers."""

    def __init__(self, server_config: MCPServerConfig):
        self.config = server_config
        self.client: Optional[httpx.AsyncClient] = None

    async def start(self):
        """Initialize the HTTP client."""
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"Initialized HTTP client for {self.config.server_id}")

    async def stop(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            logger.info(f"Closed HTTP client for {self.config.server_id}")

    async def list_tools(self) -> List[MCPTool]:
        """List available tools from the MCP server."""
        try:
            if not self.client:
                raise RuntimeError("HTTP client not initialized")
            
            if not self.config.endpoint:
                raise ValueError("Endpoint required for HTTP transport")
            
            response = await self.client.get(f"{self.config.endpoint}/tools")
            response.raise_for_status()
            
            data = response.json()
            tools = []
            
            for tool_data in data.get("tools", []):
                tool = MCPTool(
                    name=tool_data.get("name", ""),
                    description=tool_data.get("description", ""),
                    input_schema=tool_data.get("inputSchema", {}),
                    server_id=self.config.server_id,
                    server_name=self.config.server_name,
                    transport=self.config.transport,
                    endpoint=self.config.endpoint
                )
                tools.append(tool)
            
            return tools
        except Exception as e:
            logger.error(f"Error listing tools from {self.config.server_id}: {e}")
            return []

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool on the MCP server."""
        try:
            if not self.client:
                raise RuntimeError("HTTP client not initialized")
            
            if not self.config.endpoint:
                raise ValueError("Endpoint required for HTTP transport")
            
            response = await self.client.post(
                f"{self.config.endpoint}/tools/{tool_name}",
                json=arguments
            )
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if the MCP server is healthy."""
        try:
            if not self.client or not self.config.endpoint:
                return False
            
            response = await self.client.get(f"{self.config.endpoint}/health")
            return response.status_code == 200
        except Exception:
            return False


@asynccontextmanager
async def mcp_client_context(server_config: MCPServerConfig):
    """Context manager for MCP client lifecycle."""
    client = MCPClient(server_config)
    try:
        await client.start()
        yield client
    finally:
        await client.stop()
