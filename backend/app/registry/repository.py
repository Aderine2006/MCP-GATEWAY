from typing import Dict, List, Optional
from datetime import datetime
import uuid

from .models import RegisteredTool, ToolStatus


class ToolRepository:
    """In-memory repository for tool registry (MVP implementation)."""

    def __init__(self):
        self._tools: Dict[str, RegisteredTool] = {}

    def upsert(self, tool: RegisteredTool) -> RegisteredTool:
        """Insert or update a tool in the registry."""
        if not tool.tool_id:
            tool.tool_id = str(uuid.uuid4())
        
        tool.last_discovered = datetime.utcnow()
        self._tools[tool.tool_id] = tool
        return tool

    def get(self, tool_id: str) -> Optional[RegisteredTool]:
        """Get a tool by ID."""
        return self._tools.get(tool_id)

    def get_by_name(self, name: str) -> Optional[RegisteredTool]:
        """Get a tool by name."""
        for tool in self._tools.values():
            if tool.name == name:
                return tool
        return None

    def list_all(self) -> List[RegisteredTool]:
        """List all registered tools."""
        return list(self._tools.values())

    def list_by_server(self, server_id: str) -> List[RegisteredTool]:
        """List all tools from a specific server."""
        return [t for t in self._tools.values() if t.server_id == server_id]

    def search(self, query: str) -> List[RegisteredTool]:
        """Search tools by name or description."""
        query_lower = query.lower()
        results = []
        for tool in self._tools.values():
            if (query_lower in tool.name.lower() or 
                query_lower in tool.description.lower() or
                any(query_lower in cap.lower() for cap in tool.capabilities)):
                results.append(tool)
        return results

    def update_status(self, tool_id: str, status: ToolStatus) -> Optional[RegisteredTool]:
        """Update tool status."""
        tool = self._tools.get(tool_id)
        if tool:
            tool.status = status
            return tool
        return None

    def update_health(self, tool_id: str, health_status: str) -> Optional[RegisteredTool]:
        """Update tool health status."""
        tool = self._tools.get(tool_id)
        if tool:
            tool.health_status = health_status
            return tool
        return None

    def delete(self, tool_id: str) -> bool:
        """Delete a tool from the registry."""
        if tool_id in self._tools:
            del self._tools[tool_id]
            return True
        return False

    def clear(self):
        """Clear all tools from the registry."""
        self._tools.clear()
