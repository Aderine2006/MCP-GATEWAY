import os
import time
import httpx
from typing import List, Dict, Any, Optional
import threading

DEFAULT_RATE_LIMIT_WEBHOOK_URL = os.getenv(
    "RATE_LIMIT_WEBHOOK_URL",
    "https://api.agents.snsihub.ai/webhook/rate-limiter"
)

class RateLimitService:
    """Enterprise rate-limit service integrating with the external n8n webhook.
    Enforces and tracks per-agent and per-tool RPM limits, keeping live metrics
    and simulation history for dashboard visualization.
    """

    def __init__(self, webhook_url: str = DEFAULT_RATE_LIMIT_WEBHOOK_URL):
        self.lock = threading.Lock()
        self.webhook_url = webhook_url
        self.counters: Dict[str, int] = {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
        }
        self.history: List[Dict[str, Any]] = []

    def record_request(self, allowed: bool, details: Optional[Dict[str, Any]] = None):
        with self.lock:
            self.counters["total_requests"] += 1
            if allowed:
                self.counters["allowed_requests"] += 1
            else:
                self.counters["blocked_requests"] += 1
            if details:
                self.history.insert(0, details)
                if len(self.history) > 50:
                    self.history.pop()

    def get_counters(self) -> Dict[str, Any]:
        with self.lock:
            return {
                **self.counters,
                "webhook_url": self.webhook_url,
                "history": list(self.history[:15])
            }

    async def check_rate_limit(
        self,
        client_key: str,
        tool_name: str,
        max_rpm: int = 60,
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query the external n8n rate limiter webhook."""
        start_time = time.time()
        body = {
            "client_key": client_key,
            "tool_name": tool_name,
            "max_rpm": max_rpm,
            "payload": payload or {}
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(
                    self.webhook_url,
                    json=body,
                    headers={"Content-Type": "application/json"}
                )
                duration_ms = round((time.time() - start_time) * 1000, 2)
                status_code = resp.status_code

                try:
                    resp_json = resp.json()
                except Exception:
                    resp_json = {"raw": resp.text}

                def clean_val(v):
                    if isinstance(v, str) and v.startswith("="):
                        return v[1:]
                    return v

                # Determine if allowed
                is_allowed = (status_code == 200) and (
                    resp_json.get("status") == "allowed" or "allowed" in str(resp_json).lower()
                )

                remaining = clean_val(resp_json.get("remaining_quota", resp.headers.get("X-RateLimit-Remaining", "N/A")))
                current_rpm = clean_val(resp_json.get("current_rpm", "N/A"))
                retry_after = clean_val(resp.headers.get("Retry-After", resp_json.get("retry_after_seconds", 0)))

                result = {
                    "client_key": client_key,
                    "tool_name": tool_name,
                    "max_rpm": max_rpm,
                    "status_code": status_code,
                    "is_allowed": is_allowed,
                    "remaining_quota": remaining,
                    "current_rpm": current_rpm,
                    "retry_after_seconds": retry_after,
                    "duration_ms": duration_ms,
                    "raw_response": resp_json,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }

                self.record_request(allowed=is_allowed, details=result)
                return result

        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            result = {
                "client_key": client_key,
                "tool_name": tool_name,
                "max_rpm": max_rpm,
                "status_code": 500,
                "is_allowed": True,  # Fail open gracefully
                "error": str(e),
                "duration_ms": duration_ms,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "fallback": True
            }
            self.record_request(allowed=True, details=result)
            return result
