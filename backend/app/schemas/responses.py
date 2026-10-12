from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class RoutingResponse(BaseModel):
    request_id: str
    success: bool
    intent: Dict[str, Any]
    selected_tool: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    routing_explanation: Optional[str] = None
    execution_duration_ms: Optional[float] = None
    timestamp: datetime


class HealthResponse(BaseModel):
    status: str
    gateway_status: str
    tools_registered: int
    servers_configured: int
    message: str
