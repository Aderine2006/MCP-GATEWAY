import uuid
from fastapi import APIRouter
from typing import Dict

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

# Simple in‑memory request counters (shared with summary)
request_metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "rate_limited_requests": 0,
}

@router.get("/", response_model=Dict)
async def get_metrics():
    """Return basic request‑handling metrics for the dashboard.
    The counters are updated elsewhere (e.g., in the routing endpoint).
    """
    return request_metrics
