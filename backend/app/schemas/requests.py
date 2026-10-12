from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class RouteRequest(BaseModel):
    request: str = Field(..., description="Natural language request to route")
    request_id: Optional[str] = Field(None, description="Optional request ID (auto-generated if not provided)")
    auto_execute: bool = Field(False, description="Automatically execute the selected tool")
    force_execute: bool = Field(False, description="Force execution even for write operations")


class ExecuteRequest(BaseModel):
    tool_id: str = Field(..., description="ID of the tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the tool")
    force_execute: bool = Field(False, description="Force execution even for write operations")
