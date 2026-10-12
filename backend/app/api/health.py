from fastapi import APIRouter

from ..schemas.responses import HealthResponse

router = APIRouter(prefix="/api/health", tags=["health"])


def get_registry_service():
    """Dependency to get registry service (will be injected from main app)."""
    from ..main import registry_service
    return registry_service


@router.get("", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    registry = get_registry_service()
    tools = registry.get_tools()
    
    return HealthResponse(
        status="ok",
        gateway_status="running",
        tools_registered=len(tools),
        servers_configured=len(registry.server_configs),
        message="Gateway is operational"
    )
