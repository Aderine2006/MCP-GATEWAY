"""
Supabase Database Client for Enterprise MCP Gateway

This module provides a Python client for interacting with Supabase database.
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

try:
    from supabase import create_client, Client
except ImportError:
    print("Supabase client not installed. Run: pip install supabase")
    raise


class SupabaseDB:
    """Supabase database client for Enterprise MCP Gateway."""
    
    def __init__(self):
        """Initialize Supabase client from environment variables."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_ANON_KEY environment variables must be set"
            )
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    # =====================================================
    # MCP Servers Operations
    # =====================================================
    
    async def create_mcp_server(
        self,
        server_id: str,
        server_name: str,
        transport: str,
        endpoint: Optional[str] = None,
        port: Optional[int] = None,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        is_active: bool = True
    ) -> Dict[str, Any]:
        """Create a new MCP server record."""
        data = {
            "server_id": server_id,
            "server_name": server_name,
            "transport": transport,
            "endpoint": endpoint,
            "port": port,
            "command": command,
            "args": args,
            "is_active": is_active
        }
        result = self.client.table("mcp_servers").insert(data).execute()
        return result.data[0] if result.data else None
    
    async def get_mcp_server(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get an MCP server by ID."""
        result = self.client.table("mcp_servers").select("*").eq("server_id", server_id).execute()
        return result.data[0] if result.data else None
    
    async def list_mcp_servers(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """List all MCP servers."""
        query = self.client.table("mcp_servers").select("*")
        if active_only:
            query = query.eq("is_active", True)
        result = query.execute()
        return result.data
    
    async def update_mcp_server(self, server_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an MCP server."""
        result = self.client.table("mcp_servers").update(updates).eq("server_id", server_id).execute()
        return result.data[0] if result.data else None
    
    async def delete_mcp_server(self, server_id: str) -> bool:
        """Delete an MCP server."""
        result = self.client.table("mcp_servers").delete().eq("server_id", server_id).execute()
        return len(result.data) > 0
    
    # =====================================================
    # Tools Operations
    # =====================================================
    
    async def create_tool(
        self,
        tool_id: str,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        server_id: str,
        server_name: str,
        transport: str,
        endpoint: Optional[str] = None,
        capabilities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new tool record."""
        data = {
            "tool_id": tool_id,
            "name": name,
            "description": description,
            "input_schema": input_schema,
            "server_id": server_id,
            "server_name": server_name,
            "transport": transport,
            "endpoint": endpoint,
            "capabilities": capabilities or [],
            "status": "active"
        }
        result = self.client.table("tools").insert(data).execute()
        return result.data[0] if result.data else None
    
    async def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get a tool by ID."""
        result = self.client.table("tools").select("*").eq("tool_id", tool_id).execute()
        return result.data[0] if result.data else None
    
    async def list_tools(
        self,
        server_id: Optional[str] = None,
        status: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """List tools with optional filters."""
        query = self.client.table("tools").select("*")
        
        if server_id:
            query = query.eq("server_id", server_id)
        if status:
            query = query.eq("status", status)
        if active_only:
            query = query.eq("status", "active")
        
        result = query.execute()
        return result.data
    
    async def upsert_tool(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update a tool."""
        tool_id = tool_data.get("tool_id")
        existing = await self.get_tool(tool_id)
        
        if existing:
            result = self.client.table("tools").update(tool_data).eq("tool_id", tool_id).execute()
            return result.data[0] if result.data else None
        else:
            result = self.client.table("tools").insert(tool_data).execute()
            return result.data[0] if result.data else None
    
    async def update_tool_status(self, tool_id: str, status: str, health_status: str = "unknown") -> Optional[Dict[str, Any]]:
        """Update tool status."""
        data = {
            "status": status,
            "health_status": health_status,
            "last_health_check": datetime.utcnow().isoformat()
        }
        result = self.client.table("tools").update(data).eq("tool_id", tool_id).execute()
        return result.data[0] if result.data else None
    
    async def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """Search tools by name, description, or capabilities."""
        # Using text search on name and description
        result = self.client.table("tools").select("*").or_(
            f"name.ilike.%{query}%,description.ilike.%{query}%"
        ).execute()
        return result.data
    
    # =====================================================
    # Requests Operations
    # =====================================================
    
    async def create_request(
        self,
        request_id: str,
        raw_request: str,
        detected_operation: str,
        detected_domain: str,
        extracted_parameters: Dict[str, Any],
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new request record."""
        data = {
            "request_id": request_id,
            "raw_request": raw_request,
            "detected_operation": detected_operation,
            "detected_domain": detected_domain,
            "extracted_parameters": extracted_parameters,
            "user_id": user_id,
            "agent_id": agent_id
        }
        result = self.client.table("requests").insert(data).execute()
        return result.data[0] if result.data else None
    
    async def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get a request by ID."""
        result = self.client.table("requests").select("*").eq("request_id", request_id).execute()
        return result.data[0] if result.data else None
    
    async def list_requests(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List requests with pagination."""
        query = self.client.table("requests").select("*").order("created_at", desc=True).range(offset, offset + limit - 1)
        
        if user_id:
            query = query.eq("user_id", user_id)
        
        result = query.execute()
        return result.data
    
    # =====================================================
    # Routing Operations
    # =====================================================
    
    async def create_routing(
        self,
        request_id: str,
        selected_tool_id: Optional[str],
        selected_server_id: Optional[str],
        routing_score: float,
        routing_explanation: str,
        candidates_matched: int,
        permission_granted: bool,
        permission_required: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a routing record."""
        data = {
            "request_id": request_id,
            "selected_tool_id": selected_tool_id,
            "selected_server_id": selected_server_id,
            "routing_score": routing_score,
            "routing_explanation": routing_explanation,
            "candidates_matched": candidates_matched,
            "permission_granted": permission_granted,
            "permission_required": permission_required
        }
        result = self.client.table("routing").insert(data).execute()
        return result.data[0] if result.data else None
    
    async def get_routing(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get routing info for a request."""
        result = self.client.table("routing").select("*").eq("request_id", request_id).execute()
        return result.data[0] if result.data else None
    
    # =====================================================
    # Executions Operations
    # =====================================================
    
    async def create_execution(
        self,
        request_id: str,
        tool_id: Optional[str],
        server_id: Optional[str],
        input_parameters: Dict[str, Any],
        execution_status: str = "pending"
    ) -> Dict[str, Any]:
        """Create a new execution record."""
        data = {
            "request_id": request_id,
            "tool_id": tool_id,
            "server_id": server_id,
            "input_parameters": input_parameters,
            "execution_status": execution_status,
            "started_at": datetime.utcnow().isoformat()
        }
        result = self.client.table("executions").insert(data).execute()
        return result.data[0] if result.data else None
    
    async def update_execution(
        self,
        execution_id: str,
        execution_status: str,
        output_result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_duration_ms: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Update an execution record."""
        data = {
            "execution_status": execution_status,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        if output_result:
            data["output_result"] = output_result
        if error_message:
            data["error_message"] = error_message
        if execution_duration_ms:
            data["execution_duration_ms"] = execution_duration_ms
        
        result = self.client.table("executions").update(data).eq("id", execution_id).execute()
        return result.data[0] if result.data else None
    
    async def list_executions(
        self,
        request_id: Optional[str] = None,
        tool_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List executions with filters."""
        query = self.client.table("executions").select("*").order("started_at", desc=True).limit(limit)
        
        if request_id:
            query = query.eq("request_id", request_id)
        if tool_id:
            query = query.eq("tool_id", tool_id)
        if status:
            query = query.eq("execution_status", status)
        
        result = query.execute()
        return result.data
    
    # =====================================================
    # Health Checks Operations
    # =====================================================
    
    async def create_health_check(
        self,
        server_id: str,
        status: str,
        response_time_ms: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a health check record."""
        data = {
            "server_id": server_id,
            "status": status,
            "response_time_ms": response_time_ms,
            "error_message": error_message,
            "checked_at": datetime.utcnow().isoformat()
        }
        result = self.client.table("health_checks").insert(data).execute()
        return result.data[0] if result.data else None
    
    async def get_latest_health_check(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest health check for a server."""
        result = self.client.table("health_checks").select("*").eq("server_id", server_id).order("checked_at", desc=True).limit(1).execute()
        return result.data[0] if result.data else None
    
    async def list_health_checks(
        self,
        server_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List health checks with filters."""
        query = self.client.table("health_checks").select("*").order("checked_at", desc=True).limit(limit)
        
        if server_id:
            query = query.eq("server_id", server_id)
        if status:
            query = query.eq("status", status)
        
        result = query.execute()
        return result.data
    
    # =====================================================
    # Analytics / Statistics
    # =====================================================
    
    async def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        all_executions = await self.list_executions(limit=10000)
        
        total = len(all_executions)
        successful = sum(1 for e in all_executions if e["execution_status"] == "success")
        failed = sum(1 for e in all_executions if e["execution_status"] == "failed")
        
        durations = [e.get("execution_duration_ms") for e in all_executions if e.get("execution_duration_ms")]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "average_duration_ms": avg_duration
        }
    
    async def get_tool_usage_stats(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get tool usage statistics."""
        all_executions = await self.list_executions(status="success", limit=10000)
        
        usage = {}
        for exe in all_executions:
            tool_id = exe.get("tool_id")
            if tool_id:
                usage[tool_id] = usage.get(tool_id, 0) + 1
        
        sorted_usage = sorted(usage.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [{"tool_id": k, "usage_count": v} for k, v in sorted_usage]


# Singleton instance
_db_instance: Optional[SupabaseDB] = None


def get_db() -> SupabaseDB:
    """Get or create the database singleton instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = SupabaseDB()
    return _db_instance
