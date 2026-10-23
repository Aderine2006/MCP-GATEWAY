import threading
from typing import List, Dict

_events: List[Dict] = []
_lock = threading.Lock()

def log_event(event: Dict) -> None:
    """Append an event dictionary to the in‑memory store.
    Expected keys: event_id, timestamp, agent, server, type, status, duration, result, error, trace_id.
    """
    with _lock:
        _events.append(event)

def get_events(limit: int = 100, offset: int = 0) -> List[Dict]:
    """Return a slice of recent events, newest first.
    Pagination is simple: `offset` skips the most recent `offset` events, then returns up to `limit`.
    """
    with _lock:
        if offset:
            return list(reversed(_events))[:offset + limit][offset:]
        return list(reversed(_events))[:limit]
