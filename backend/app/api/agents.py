from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/agents", tags=["agents"])

class AgentModel(BaseModel):
    agent_id: str
    agent_name: str
    agent_type: str  # router, registry, executor, custom
    description: str
    status: str = "operational"  # operational, idle, degraded, offline
    allowed_tools: List[str] = []
    policies: List[str] = []
    rate_limit_rpm: int = 120
    request_count: int = 0
    success_rate: float = 99.4
    last_active: Optional[str] = None

# Default enterprise configured agents
agents_db: Dict[str, Dict[str, Any]] = {
    "customer-service-agent": {
        "agent_id": "customer-service-agent",
        "agent_name": "Customer Service Agent",
        "agent_type": "router",
        "description": "Primary router handling customer lookups, account status inquiries, and user profiles.",
        "status": "operational",
        "allowed_tools": ["customer-mcp_get_customer", "customer-mcp_list_customers"],
        "policies": ["read-only-pii", "rate-limit-default"],
        "rate_limit_rpm": 120,
        "request_count": 428,
        "success_rate": 99.8,
        "last_active": "Just now",
    },
    "incident-response-agent": {
        "agent_id": "incident-response-agent",
        "agent_name": "Incident Response Agent",
        "agent_type": "executor",
        "description": "Automated incident triage, severity escalation, and PagerDuty notification dispatch.",
        "status": "operational",
        "allowed_tools": ["incident-mcp_create_incident", "incident-mcp_list_incidents"],
        "policies": ["admin-audit-log", "urgent-escalation"],
        "rate_limit_rpm": 60,
        "request_count": 139,
        "success_rate": 98.6,
        "last_active": "2 mins ago",
    },
    "support-triage-agent": {
        "agent_id": "support-triage-agent",
        "agent_name": "Support Triage Agent",
        "agent_type": "router",
        "description": "Ticket ingestion and automatic routing to Tier-2 support and engineering specialists.",
        "status": "operational",
        "allowed_tools": ["support-mcp_search_tickets", "support-mcp_get_ticket"],
        "policies": ["standard-support-access"],
        "rate_limit_rpm": 180,
        "request_count": 312,
        "success_rate": 100.0,
        "last_active": "5 mins ago",
    },
    "it-automation-agent": {
        "agent_id": "it-automation-agent",
        "agent_name": "IT Automation Agent",
        "agent_type": "custom",
        "description": "Infrastructure automation assistant querying system capabilities and health.",
        "status": "idle",
        "allowed_tools": ["about-mcp_get_info", "about-mcp_get_version"],
        "policies": ["internal-network-only"],
        "rate_limit_rpm": 90,
        "request_count": 87,
        "success_rate": 100.0,
        "last_active": "14 mins ago",
    },
}

@router.get("", response_model=List[Dict[str, Any]])
async def list_agents():
    """List all configured enterprise AI agents."""
    return list(agents_db.values())

@router.get("/{agent_id}", response_model=Dict[str, Any])
async def get_agent(agent_id: str):
    """Get single agent by ID."""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]

@router.post("", response_model=Dict[str, Any])
async def create_or_update_agent(agent: AgentModel):
    """Register or update an AI agent configuration."""
    data = agent.model_dump()
    data["last_active"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    agents_db[agent.agent_id] = data
    return data

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent configuration."""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    del agents_db[agent_id]
    return {"status": "deleted", "agent_id": agent_id}
