from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ToolResponse(BaseModel):
    tool_id: str
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_id: str
    server_name: str
    transport: str
    endpoint: Optional[str] = None
    status: str
    health_status: str
    capabilities: List[str]
    last_discovered: datetime


class DiscoveryResponse(BaseModel):
    server_id: str
    tools_discovered: int
    success: bool
    error_message: Optional[str] = None


class ToolListResponse(BaseModel):
    tools: List[ToolResponse]
    total: int


class ToolSearchRequest(BaseModel):
    query: str = Field(..., description="Search query for tools")


class ToolSearchResponse(BaseModel):
    tools: List[ToolResponse]
    total: int
    query: str
