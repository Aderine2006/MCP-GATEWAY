from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ToolStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNHEALTHY = "unhealthy"


class RegisteredTool(BaseModel):
    tool_id: str
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_id: str
    server_name: str
    transport: str
    endpoint: Optional[str] = None
    status: ToolStatus = ToolStatus.ACTIVE
    last_discovered: datetime = Field(default_factory=datetime.utcnow)
    health_status: str = "unknown"
    capabilities: List[str] = Field(default_factory=list)


class DiscoveryResult(BaseModel):
    server_id: str
    tools_discovered: int
    success: bool
    error_message: Optional[str] = None
