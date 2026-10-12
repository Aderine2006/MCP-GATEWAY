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
    
    return result.to_dict()
