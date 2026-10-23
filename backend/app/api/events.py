import uuid
from fastapi import APIRouter
from typing import List, Dict

router = APIRouter(prefix="/api/events", tags=["events"])

@router.get("/", response_model=List[Dict])
async def list_events(limit: int = 100, offset: int = 0):
    """Return recent events for the activity feed.
    The in‑memory logger stores events as plain dictionaries.
    """
    from ..observability.event_logger import get_events
    return get_events(limit=limit, offset=offset)
