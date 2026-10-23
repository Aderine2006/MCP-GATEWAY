import uuid
from fastapi import APIRouter

from ..schemas.requests import RouteRequest
from ..schemas.responses import RoutingResponse
from ..router.intent_router import IntentRouter

router = APIRouter(prefix="/api/route", tags=["routing"])


def get_intent_router() -> IntentRouter:
    """Dependency to get intent router (will be injected from main app)."""
    from ..main import intent_router
    return intent_router


@router.post("", response_model=RoutingResponse)
async def route_request(request: RouteRequest):
    """Route a natural language request to the appropriate tool."""
    router = get_intent_router()
    
    request_id = request.request_id or str(uuid.uuid4())
    
    result = await router.route_request(
        request=request.request,
        request_id=request_id,
        auto_execute=request.auto_execute,
        force_execute=request.force_execute
    )
    
    # Update metrics and log event
    from .metrics import request_metrics
    from ..observability.event_logger import log_event
    from datetime import datetime
    
    request_metrics["total_requests"] = request_metrics.get("total_requests", 0) + 1
    if result.success:
        request_metrics["successful_requests"] = request_metrics.get("successful_requests", 0) + 1
    else:
        request_metrics["failed_requests"] = request_metrics.get("failed_requests", 0) + 1
        
    log_event({
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": "Enterprise Gateway Router",
        "server": result.selected_tool.server_name if result.selected_tool else "System",
        "type": "route_and_execute" if request.auto_execute or request.force_execute else "route_intent",
        "status": "healthy" if result.success else "failed",
        "duration": getattr(result, "execution_duration_ms", 0) or 0,
        "result": result.routing_explanation or ("Executed tool " + (result.selected_tool.name if result.selected_tool else "")),
        "error": result.error_message,
        "trace_id": request_id,
    })
    
    return result.to_dict()
