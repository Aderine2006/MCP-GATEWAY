from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum


class MCPTransport(str, Enum):
    STDIO = "stdio"
    SSE = "sse"
    HTTP = "http"


class MCPToolSchema(BaseModel):
    type: str = "object"
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)


class MCPTool(BaseModel):
    name: str
    description: str
    input_schema: Union[Dict[str, Any], MCPToolSchema]
    server_id: str
    server_name: str
    transport: MCPTransport
    endpoint: Optional[str] = None
    health_status: str = "unknown"
    last_discovered: datetime = Field(default_factory=datetime.utcnow)


class MCPServerConfig(BaseModel):
    server_id: str
    server_name: str
    transport: MCPTransport
    command: Optional[str] = None
    args: Optional[List[str]] = None
    endpoint: Optional[str] = None
    port: Optional[int] = None
