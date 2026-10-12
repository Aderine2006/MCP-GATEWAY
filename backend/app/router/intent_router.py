import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

from ..registry.service import ToolRegistryService
from ..registry.models import RegisteredTool
from ..mcp.client import mcp_client_context
from ..mcp.models import MCPServerConfig, MCPTransport
from .capability_matcher import CapabilityMatcher
from .routing_policy import RoutingPolicy, Permission

logger = logging.getLogger(__name__)


class RoutingResult:
    """Result of a routing operation."""
    
    def __init__(
        self,
        request_id: str,
        success: bool,
        intent: Dict[str, Any],
        selected_tool: Optional[RegisteredTool] = None,
        execution_result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        routing_explanation: Optional[str] = None,
        execution_duration_ms: Optional[float] = None
    ):
        self.request_id = request_id
        self.success = success
        self.intent = intent
        self.selected_tool = selected_tool
        self.execution_result = execution_result
        self.error_message = error_message
        self.routing_explanation = routing_explanation
        self.execution_duration_ms = execution_duration_ms
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "request_id": self.request_id,
            "success": self.success,
            "intent": self.intent,
            "selected_tool": {
                "name": self.selected_tool.name,
                "description": self.selected_tool.description,
                "server_id": self.selected_tool.server_id,
                "server_name": self.selected_tool.server_name
            } if self.selected_tool else None,
            "execution_result": self.execution_result,
            "error_message": self.error_message,
            "routing_explanation": self.routing_explanation,
            "execution_duration_ms": self.execution_duration_ms,
            "timestamp": self.timestamp.isoformat()
        }


class IntentRouter:
    """Routes natural language requests to appropriate MCP tools."""

    def __init__(self, registry_service: ToolRegistryService):
        self.registry = registry_service
        self.matcher = CapabilityMatcher()
        self.policy = RoutingPolicy()
        self.server_configs: Dict[str, MCPServerConfig] = {}

    def register_server_config(self, config: MCPServerConfig):
        """Register MCP server configuration for execution."""
        self.server_configs[config.server_id] = config

    async def route_request(
        self,
        request: str,
        request_id: str,
        auto_execute: bool = False,
        force_execute: bool = False
    ) -> RoutingResult:
        """Route a natural language request to the appropriate tool."""
        start_time = time.time()
        
        try:
            # Step 1: Extract intent
            intent = self.matcher.extract_intent(request)
            logger.info(f"Extracted intent: {intent}")
            
            # Step 2: Get available tools
            tools = self.registry.get_tools()
            if not tools:
                return RoutingResult(
                    request_id=request_id,
                    success=False,
                    intent=intent,
                    error_message="No tools available in registry. Run tool discovery first."
                )
            
            # Step 3: Match tools
            candidates = self.matcher.match_tools(intent, tools)
            
            if not candidates:
                return RoutingResult(
                    request_id=request_id,
                    success=False,
                    intent=intent,
                    error_message=f"No suitable tool found for request: {request}"
                )
            
            # Step 4: Select best tool
            selected_tool, score = candidates[0]
            logger.info(f"Selected tool: {selected_tool.name} (score: {score:.2f})")
            
            # Step 5: Check permission
            permission = self.policy.check_permission(intent["operation"], selected_tool.name)
            
            if permission == Permission.DENIED:
                return RoutingResult(
                    request_id=request_id,
                    success=False,
                    intent=intent,
                    selected_tool=selected_tool,
                    error_message="Operation denied by policy"
                )
            
            if permission == Permission.REQUIRES_CONFIRMATION and not force_execute:
                return RoutingResult(
                    request_id=request_id,
                    success=False,
                    intent=intent,
                    selected_tool=selected_tool,
                    error_message="Write operation requires confirmation. Set force_execute=true to proceed.",
                    routing_explanation=f"Tool '{selected_tool.name}' matched with score {score:.2f} but requires confirmation for write operation."
                )
            
            # Step 6: Validate parameters
            is_valid, validation_error = self.policy.validate_parameters(
                intent["parameters"],
                selected_tool.input_schema
            )
            
            if not is_valid:
                return RoutingResult(
                    request_id=request_id,
                    success=False,
                    intent=intent,
                    selected_tool=selected_tool,
                    error_message=f"Parameter validation failed: {validation_error}"
                )
            
            # Step 7: Execute tool
            if auto_execute or force_execute:
                execution_result = await self._execute_tool(selected_tool, intent["parameters"])
                execution_duration = (time.time() - start_time) * 1000
                
                return RoutingResult(
                    request_id=request_id,
                    success=True,
                    intent=intent,
                    selected_tool=selected_tool,
                    execution_result=execution_result,
                    routing_explanation=f"Tool '{selected_tool.name}' matched with score {score:.2f} and executed successfully.",
                    execution_duration_ms=execution_duration
                )
            else:
                # Return routing result without execution
                return RoutingResult(
                    request_id=request_id,
                    success=True,
                    intent=intent,
                    selected_tool=selected_tool,
                    routing_explanation=f"Tool '{selected_tool.name}' matched with score {score:.2f}. Set auto_execute=true to execute.",
                    execution_duration_ms=(time.time() - start_time) * 1000
                )
            
        except Exception as e:
            logger.error(f"Error routing request: {e}")
            return RoutingResult(
                request_id=request_id,
                success=False,
                intent=intent if 'intent' in locals() else {},
                error_message=f"Routing error: {str(e)}"
            )

    async def _execute_tool(self, tool: RegisteredTool, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool via MCP client."""
        server_config = self.server_configs.get(tool.server_id)
        if not server_config:
            raise ValueError(f"No server configuration found for {tool.server_id}")
        
        async with mcp_client_context(server_config) as client:
            result = await client.call_tool(tool.name, parameters)
            return result
