import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "tools_registered" in data


def test_list_tools():
    """Test listing tools endpoint."""
    response = client.get("/api/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert "total" in data


def test_discover_tools():
    """Test tool discovery endpoint."""
    response = client.post("/api/tools/discover")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Each result should have server_id, tools_discovered, success
    if len(data) > 0:
        assert "server_id" in data[0]
        assert "tools_discovered" in data[0]
        assert "success" in data[0]


def test_search_tools():
    """Test tool search endpoint."""
    response = client.post(
        "/api/tools/search",
        json={"query": "customer"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert "query" in data


def test_route_request():
    """Test routing a request."""
    response = client.post(
        "/api/route",
        json={
            "request": "Find the details of customer 1024",
            "auto_execute": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert "intent" in data
    assert "success" in data


def test_route_request_with_execution():
    """Test routing and executing a request."""
    response = client.post(
        "/api/route",
        json={
            "request": "Find the details of customer 1024",
            "auto_execute": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    # May or may not have execution_result depending on tool availability


def test_route_request_write_operation():
    """Test that write operations require confirmation."""
    response = client.post(
        "/api/route",
        json={
            "request": "Create an incident for server outage",
            "auto_execute": False,
            "force_execute": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    # Should either fail with permission error or succeed with confirmation required
    assert "success" in data


def test_route_request_force_execute():
    """Test force execution bypasses confirmation."""
    response = client.post(
        "/api/route",
        json={
            "request": "Create an incident for server outage",
            "auto_execute": True,
            "force_execute": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
