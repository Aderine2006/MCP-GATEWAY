import pytest
from datetime import datetime

from app.registry.models import RegisteredTool, ToolStatus, DiscoveryResult
from app.registry.repository import ToolRepository


def test_repository_upsert():
    """Test upserting a tool into the repository."""
    repo = ToolRepository()
    
    tool = RegisteredTool(
        tool_id="test-tool-1",
        name="get_customer",
        description="Get customer details",
        input_schema={"type": "object", "properties": {}},
        server_id="customer-mcp",
        server_name="Customer MCP",
        transport="stdio",
        status=ToolStatus.ACTIVE,
        capabilities=["read", "customer"]
    )
    
    result = repo.upsert(tool)
    assert result.tool_id == "test-tool-1"
    assert result.name == "get_customer"


def test_repository_get():
    """Test getting a tool by ID."""
    repo = ToolRepository()
    
    tool = RegisteredTool(
        tool_id="test-tool-2",
        name="get_tickets",
        description="Get support tickets",
        input_schema={"type": "object", "properties": {}},
        server_id="support-mcp",
        server_name="Support MCP",
        transport="stdio",
        status=ToolStatus.ACTIVE,
        capabilities=["read", "support"]
    )
    
    repo.upsert(tool)
    retrieved = repo.get("test-tool-2")
    
    assert retrieved is not None
    assert retrieved.name == "get_tickets"


def test_repository_get_by_name():
    """Test getting a tool by name."""
    repo = ToolRepository()
    
    tool = RegisteredTool(
        tool_id="test-tool-3",
        name="create_incident",
        description="Create an incident",
        input_schema={"type": "object", "properties": {}},
        server_id="incident-mcp",
        server_name="Incident MCP",
        transport="stdio",
        status=ToolStatus.ACTIVE,
        capabilities=["write", "incident"]
    )
    
    repo.upsert(tool)
    retrieved = repo.get_by_name("create_incident")
    
    assert retrieved is not None
    assert retrieved.tool_id == "test-tool-3"


def test_repository_list_all():
    """Test listing all tools."""
    repo = ToolRepository()
    
    tool1 = RegisteredTool(
        tool_id="test-tool-4",
        name="tool1",
        description="Tool 1",
        input_schema={"type": "object"},
        server_id="server1",
        server_name="Server 1",
        transport="stdio",
        capabilities=[]
    )
    
    tool2 = RegisteredTool(
        tool_id="test-tool-5",
        name="tool2",
        description="Tool 2",
        input_schema={"type": "object"},
        server_id="server2",
        server_name="Server 2",
        transport="stdio",
        capabilities=[]
    )
    
    repo.upsert(tool1)
    repo.upsert(tool2)
    
    tools = repo.list_all()
    assert len(tools) == 2


def test_repository_search():
    """Test searching tools by query."""
    repo = ToolRepository()
    
    tool1 = RegisteredTool(
        tool_id="test-tool-6",
        name="get_customer",
        description="Get customer details",
        input_schema={"type": "object"},
        server_id="customer-mcp",
        server_name="Customer MCP",
        transport="stdio",
        capabilities=["read", "customer"]
    )
    
    tool2 = RegisteredTool(
        tool_id="test-tool-7",
        name="get_tickets",
        description="Get support tickets",
        input_schema={"type": "object"},
        server_id="support-mcp",
        server_name="Support MCP",
        transport="stdio",
        capabilities=["read", "support"]
    )
    
    repo.upsert(tool1)
    repo.upsert(tool2)
    
    # Search for customer
    results = repo.search("customer")
    assert len(results) == 1
    assert results[0].name == "get_customer"
    
    # Search for read
    results = repo.search("read")
    assert len(results) == 2


def test_repository_update_status():
    """Test updating tool status."""
    repo = ToolRepository()
    
    tool = RegisteredTool(
        tool_id="test-tool-8",
        name="test_tool",
        description="Test tool",
        input_schema={"type": "object"},
        server_id="test-server",
        server_name="Test Server",
        transport="stdio",
        status=ToolStatus.ACTIVE,
        capabilities=[]
    )
    
    repo.upsert(tool)
    repo.update_status("test-tool-8", ToolStatus.UNHEALTHY)
    
    updated = repo.get("test-tool-8")
    assert updated.status == ToolStatus.UNHEALTHY


def test_repository_delete():
    """Test deleting a tool."""
    repo = ToolRepository()
    
    tool = RegisteredTool(
        tool_id="test-tool-9",
        name="test_tool",
        description="Test tool",
        input_schema={"type": "object"},
        server_id="test-server",
        server_name="Test Server",
        transport="stdio",
        capabilities=[]
    )
    
    repo.upsert(tool)
    assert repo.delete("test-tool-8") == False  # Wrong ID
    assert repo.delete("test-tool-9") == True  # Correct ID
    assert repo.get("test-tool-9") is None
