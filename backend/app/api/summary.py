import uuid
from fastapi import APIRouter
from typing import List, Dict

router = APIRouter(prefix="/api/summary", tags=["summary"])

from app.api.metrics import request_metrics  # shared metrics dict

def get_registry_service():
    from ..main import registry_service
    return registry_service

@router.get("", response_model=Dict)
@router.get("/", response_model=Dict)
async def get_summary():
    """Aggregated dashboard data.
    Returns tool counts, server health, request metrics, agents, and active alerts.
    """
    registry = get_registry_service()
    tools = registry.get_tools()
    
    # Servers details
    servers = []
    for cfg in registry.server_configs:
        server_tools = registry.repository.list_by_server(cfg.server_id)
        status = "offline"
        if server_tools:
            if all(t.health_status == "healthy" for t in server_tools):
                status = "healthy"
            else:
                status = "warning"
                
        servers.append({
            "server_id": cfg.server_id,
            "server_name": cfg.server_name,
            "endpoint": cfg.endpoint,
            "transport": cfg.transport.value if hasattr(cfg.transport, "value") else str(cfg.transport),
            "status": status,
            "tools_count": len(server_tools),
        })

    from .agents import agents_db
    from .alerts import get_alerts
    from ..observability.event_logger import get_events
    
    alerts = await get_alerts()
    events = get_events(limit=10)
    
    return {
        "gateway_status": "healthy",
        "total_tools": len(tools),
        "active_tools": len([t for t in tools if t.status == "active" or getattr(t, "health_status", "") == "healthy"]),
        "servers": servers,
        "request_metrics": request_metrics,
        "agents_count": len(agents_db),
        "active_agents_count": sum(1 for a in agents_db.values() if a.get("status") in ["operational", "running"]),
        "alerts": alerts,
        "recent_events": events,
    }
