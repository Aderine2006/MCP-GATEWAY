import uuid
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..observability.event_logger import log_event
from ..api.metrics import request_metrics

router = APIRouter(prefix="/api/rate-limit", tags=["rate_limit"])


def get_rate_limit_service():
    from ..main import rate_limit_service
    return rate_limit_service


class SimulateRequest(BaseModel):
    client_key: str = Field(default="customer-service-agent", description="Client or Agent Identifier")
    tool_name: str = Field(default="get_customer", description="Target Tool Name")
    max_rpm: int = Field(default=60, description="Max allowed Requests Per Minute")
    burst_count: int = Field(default=1, ge=1, le=20, description="Number of sequential requests to simulate")
    payload: Optional[Dict[str, Any]] = Field(default=None, description="Optional tool payload")


class RateLimitStatusResponse(BaseModel):
    webhook_url: str
    status: str
    total_requests: int
    allowed_requests: int
    blocked_requests: int
    history: List[Dict[str, Any]]


@router.get("/status", response_model=Dict[str, Any])
async def get_rate_limit_status():
    """Get live rate-limiter webhook status and recent history."""
    service = get_rate_limit_service()
    counters = service.get_counters()
    return {
        "status": "connected",
        **counters
    }


@router.post("/simulate", response_model=Dict[str, Any])
async def simulate_rate_limit(request: SimulateRequest):
    """Simulate single or burst traffic against the live n8n rate limiter webhook."""
    service = get_rate_limit_service()
    results = []

    for i in range(request.burst_count):
        res = await service.check_rate_limit(
            client_key=request.client_key,
            tool_name=request.tool_name,
            max_rpm=request.max_rpm,
            payload=request.payload or {"simulated": True, "seq": i + 1}
        )
        res["sequence"] = i + 1
        results.append(res)
        if request.burst_count > 1 and i < request.burst_count - 1:
            await asyncio.sleep(0.05)  # Slight spacing in burst

    allowed_count = sum(1 for r in results if r.get("is_allowed"))
    blocked_count = len(results) - allowed_count
    avg_latency = round(sum(r.get("duration_ms", 0) for r in results) / len(results), 2)

    # Update global metrics
    request_metrics["total_requests"] = request_metrics.get("total_requests", 0) + len(results)
    if blocked_count > 0:
        request_metrics["rate_limited_requests"] = request_metrics.get("rate_limited_requests", 0) + blocked_count

    # Log to Gateway activity timeline
    trace_id = str(uuid.uuid4())
    log_event({
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": request.client_key,
        "server": "n8n Rate Limiter",
        "type": "rate_limit_simulation",
        "status": "healthy" if blocked_count == 0 else "warning",
        "duration": avg_latency,
        "result": f"Simulated {request.burst_count} requests: {allowed_count} Allowed, {blocked_count} Blocked (Quota: {results[-1].get('remaining_quota', 'N/A')})",
        "error": "Rate limit exceeded" if blocked_count > 0 else None,
        "trace_id": trace_id,
    })

    return {
        "success": True,
        "burst_count": request.burst_count,
        "client_key": request.client_key,
        "tool_name": request.tool_name,
        "max_rpm": request.max_rpm,
        "allowed_count": allowed_count,
        "blocked_count": blocked_count,
        "average_duration_ms": avg_latency,
        "webhook_url": service.webhook_url,
        "results": results,
        "trace_id": trace_id
    }
