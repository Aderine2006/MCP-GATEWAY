import pytest

from app.router.capability_matcher import CapabilityMatcher
from app.router.routing_policy import RoutingPolicy, Permission
from app.registry.models import RegisteredTool, ToolStatus


def test_capability_matcher_extract_intent():
    """Test intent extraction from natural language."""
    matcher = CapabilityMatcher()
    
    # Test customer read request
    intent = matcher.extract_intent("Find the details of customer 1024")
    assert intent["operation"] == "read"
    assert intent["domain"] == "customer"
    assert intent["parameters"]["customer_id"] == "1024"
    
    # Test support request
    intent = matcher.extract_intent("Search for open support tickets")
    assert intent["operation"] == "read"
    assert intent["domain"] == "support"
    
    # Test incident creation
    intent = matcher.extract_intent("Create an incident for a server outage")
    assert intent["operation"] == "write"
    assert intent["domain"] == "incident"


def test_capability_matcher_match_tools():
    """Test matching tools to intent."""
    matcher = CapabilityMatcher()
    
    tools = [
        RegisteredTool(
            tool_id="tool-1",
            name="get_customer",
            description="Get customer details",
            input_schema={"type": "object"},
            server_id="customer-mcp",
            server_name="Customer MCP",
            transport="stdio",
            status=ToolStatus.ACTIVE,
            capabilities=["read", "customer"]
        ),
        RegisteredTool(
            tool_id="tool-2",
            name="get_tickets",
            description="Get support tickets",
            input_schema={"type": "object"},
            server_id="support-mcp",
            server_name="Support MCP",
            transport="stdio",
            status=ToolStatus.ACTIVE,
            capabilities=["read", "support"]
        ),
        RegisteredTool(
            tool_id="tool-3",
            name="create_incident",
            description="Create an incident",
            input_schema={"type": "object"},
            server_id="incident-mcp",
            server_name="Incident MCP",
            transport="stdio",
            status=ToolStatus.INACTIVE,  # Inactive, should not match
            capabilities=["write", "incident"]
        )
    ]
    
    intent = matcher.extract_intent("Find the details of customer 1024")
    candidates = matcher.match_tools(intent, tools)
    
    assert len(candidates) > 0
    assert candidates[0][0].name == "get_customer"
    assert candidates[0][1] > 0  # Score should be positive


def test_capability_matcher_no_match():
    """Test when no tools match."""
    matcher = CapabilityMatcher()
    
    tools = [
        RegisteredTool(
            tool_id="tool-1",
            name="get_customer",
            description="Get customer details",
            input_schema={"type": "object"},
            server_id="customer-mcp",
            server_name="Customer MCP",
            transport="stdio",
            status=ToolStatus.ACTIVE,
            capabilities=["read", "customer"]
        )
    ]
    
    intent = matcher.extract_intent("Perform some unrelated operation")
    candidates = matcher.match_tools(intent, tools)
    
    # Should have no matches or very low scores
    assert len(candidates) == 0 or candidates[0][1] < 0.1


def test_routing_policy_check_permission():
    """Test permission checking."""
    policy = RoutingPolicy()
    
    # Read operations should be allowed
    assert policy.check_permission("read", "get_customer") == Permission.ALLOWED
    
    # Write operations should require confirmation
    assert policy.check_permission("create", "create_incident") == Permission.REQUIRES_CONFIRMATION
    assert policy.check_permission("update", "modify_customer") == Permission.REQUIRES_CONFIRMATION
    assert policy.check_permission("delete", "remove_ticket") == Permission.REQUIRES_CONFIRMATION


def test_routing_policy_validate_parameters():
    """Test parameter validation."""
    policy = RoutingPolicy()
    
    schema = {
        "type": "object",
        "properties": {
            "customer_id": {"type": "string"},
            "severity": {"type": "string"}
        },
        "required": ["customer_id"]
    }
    
    # Valid parameters
    is_valid, error = policy.validate_parameters(
        {"customer_id": "1024", "severity": "high"},
        schema
    )
    assert is_valid is True
    assert error is None
    
    # Missing required parameter
    is_valid, error = policy.validate_parameters(
        {"severity": "high"},
        schema
    )
    assert is_valid is False
    assert "customer_id" in error
    
    # Wrong type
    is_valid, error = policy.validate_parameters(
        {"customer_id": 1024},  # Should be string
        schema
    )
    assert is_valid is False
    assert "string" in error
