from fastapi import APIRouter
from typing import List, Dict
from datetime import datetime

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("", response_model=List[Dict])
async def get_alerts():
    """Return active system alerts."""
    from ..main import registry_service
    from .metrics import request_metrics
    
    alerts: List[Dict] = []
    
    # Check servers health
    for cfg in registry_service.server_configs:
        tools = registry_service.repository.list_by_server(cfg.server_id)
        if not tools:
            alerts.append({
                "id": f"alert-undiscovered-{cfg.server_id}",
                "severity": "warning",
                "title": f"{cfg.server_name} Not Discovered",
                "message": f"Server {cfg.server_name} has 0 registered tools. Trigger discovery to populate.",
                "server_id": cfg.server_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "type": "server_offline"
            })
        else:
            unhealthy_count = sum(1 for t in tools if t.health_status != "healthy")
            if unhealthy_count > 0:
                alerts.append({
                    "id": f"alert-unhealthy-{cfg.server_id}",
                    "severity": "critical",
                    "title": f"{cfg.server_name} Unhealthy Tools",
                    "message": f"{unhealthy_count} tool(s) reported unhealthy on {cfg.server_name}.",
                    "server_id": cfg.server_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "type": "tool_unhealthy"
                })
                
    # Check failed requests
    failed = request_metrics.get("failed_requests", 0)
    if failed > 5:
        alerts.append({
            "id": "alert-failed-requests",
            "severity": "warning",
            "title": "Elevated Request Failures",
            "message": f"{failed} requests have failed execution. Review routing error logs.",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": "excessive_failures"
        })
        
    return alerts

