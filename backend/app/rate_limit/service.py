from typing import List, Dict
import threading

class RateLimitService:
    """Simple in‑memory rate‑limit tracker.
    In a real system this would enforce limits per client/IP.
    Here we only expose current counters for the dashboard.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.counters: Dict[str, int] = {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
        }

    def record_request(self, allowed: bool):
        with self.lock:
            self.counters["total_requests"] += 1
            if allowed:
                self.counters["allowed_requests"] += 1
            else:
                self.counters["blocked_requests"] += 1

    def get_counters(self) -> Dict[str, int]:
        with self.lock:
            return dict(self.counters)
