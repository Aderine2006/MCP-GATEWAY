import uuid
from fastapi import APIRouter, HTTPException
from typing import List

from ..schemas.tools import (
    ToolResponse,
    DiscoveryResponse,
    ToolListResponse,
    ToolSearchRequest,
    ToolSearchResponse
)
from ..schemas.requests import ExecuteRequest
from ..schemas.responses import RoutingResponse
from ..registry.service import ToolRegistryService
from ..router.intent_router import IntentRouter

router = APIRouter(prefix="/api/tools", tags=["tools"])


def get_registry_service() -> ToolRegistryService:
    """Dependency to get registry service (will be injected from main app)."""
    from ..main import registry_service
    return registry_service


def get_intent_router() -> IntentRouter:
    """Dependency to get intent router (will be injected from main app)."""
    from ..main import intent_router
    return intent_router


@router.get("", response_model=ToolListResponse)
async def list_tools():
    """List all registered tools."""
    registry = get_registry_service()
    tools = registry.get_tools()
    
    tool_responses = [
        ToolResponse(
            tool_id=tool.tool_id,
            name=tool.name,
            description=tool.description,
            input_schema=tool.input_schema,
            server_id=tool.server_id,
            server_name=tool.server_name,
            transport=tool.transport,
            endpoint=tool.endpoint,
            status=tool.status.value,
            health_status=tool.health_status,
            capabilities=tool.capabilities,
            last_discovered=tool.last_discovered
        )
        for tool in tools
    ]
    
    return ToolListResponse(tools=tool_responses, total=len(tool_responses))


@router.post("/discover", response_model=List[DiscoveryResponse])
async def discover_tools(server_id: str = None):
    """Discover tools from MCP servers."""
    registry = get_registry_service()
    results = await registry.discover_tools(server_id)
    return results


@router.post("/search", response_model=ToolSearchResponse)
async def search_tools(request: ToolSearchRequest):
    """Search tools by capability, name, or description."""
    registry = get_registry_service()
    tools = registry.search_tools(request.query)
    
    tool_responses = [
        ToolResponse(
            tool_id=tool.tool_id,
            name=tool.name,
            description=tool.description,
            input_schema=tool.input_schema,
            server_id=tool.server_id,
            server_name=tool.server_name,
            transport=tool.transport,
            endpoint=tool.endpoint,
            status=tool.status.value,
            health_status=tool.health_status,
            capabilities=tool.capabilities,
            last_discovered=tool.last_discovered
        )
        for tool in tools
    ]
    
    return ToolSearchResponse(
        tools=tool_responses,
        total=len(tool_responses),
        query=request.query
    )


@router.post("/execute", response_model=RoutingResponse)
async def execute_tool(request: ExecuteRequest):
    """Execute a specific tool by ID."""
    registry = get_registry_service()
    router = get_intent_router()
    
    tool = registry.get_tool(request.tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool not found: {request.tool_id}")
    
    # Check permission
    from ..router.routing_policy import RoutingPolicy, Permission
    policy = RoutingPolicy()
    permission = policy.check_permission("execute", tool.name)
    
    if permission == Permission.REQUIRES_CONFIRMATION and not request.force_execute:
        raise HTTPException(
            status_code=403,
            detail="Write operation requires confirmation. Set force_execute=true to proceed."
        )
    
    # Validate parameters
    is_valid, validation_error = policy.validate_parameters(
        request.parameters,
        tool.input_schema
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Parameter validation failed: {validation_error}"
        )
    
    # Execute
    try:
        result = await router._execute_tool(tool, request.parameters)
        
        return RoutingResponse(
            request_id=str(uuid.uuid4()),
            success=True,
            intent={"operation": "execute", "parameters": request.parameters},
            selected_tool={
                "name": tool.name,
                "description": tool.description,
                "server_id": tool.server_id,
                "server_name": tool.server_name
            },
            execution_result=result,
            routing_explanation=f"Tool '{tool.name}' executed directly."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")
