# n8n Workflows - Quick Start Guide

## Overview

Three n8n workflows for automating backend operations:
1. **Create MCP Server** - Automate MCP server registration
2. **External Tool Registry** - Register external tools without MCP compliance
3. **Configure AI Agent** - Configure agents with permissions and policies

## Quick Setup (5 Minutes)

### Step 1: Add Additional Database Tables

Run this SQL in your Supabase SQL Editor:

```sql
-- Agent tool permissions
CREATE TABLE IF NOT EXISTS agent_tool_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) NOT NULL,
    tool_id VARCHAR(255) NOT NULL,
    permission VARCHAR(50) DEFAULT 'execute',
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent policy mapping
CREATE TABLE IF NOT EXISTS agent_policy_mapping (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) NOT NULL,
    policy_name VARCHAR(255) NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent configuration
CREATE TABLE IF NOT EXISTS agent_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) UNIQUE NOT NULL,
    config_json JSONB NOT NULL,
    tool_permissions JSONB DEFAULT '[]'::jsonb,
    policy_ids JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Step 2: Configure n8n Environment Variables

In n8n Settings → Credentials → Add Credential → HTTP Header Auth:

**Credential Name**: Supabase

**Parameters**:
- Name: `apikey`
- Value: Your `SUPABASE_ANON_KEY` from .env file

In n8n Settings → Environment Variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anon key

### Step 3: Import Workflows

1. Open n8n
2. Click "Import from File"
3. Import each JSON file from `backend/n8n_workflows/`:
   - `create_mcp_server.json`
   - `external_tool_registry.json`
   - `configure_ai_agent.json`

### Step 4: Activate Workflows

For each workflow:
1. Open the workflow
2. Click "Activate"
3. Copy the webhook URL
4. Save the webhook URL for later use

### Step 5: Test a Workflow

**Test Create MCP Server**:
```bash
curl -X POST YOUR_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{
    "server_name": "Test Server",
    "transport": "http",
    "endpoint": "http://localhost:9000",
    "port": 9000
  }'
```

## Webhook URLs Reference

After activation, you'll get URLs like:
- Create MCP Server: `/webhook/create-mcp-server`
- External Tool Registry: `/webhook/register-tool`
- Configure AI Agent: `/webhook/configure-agent`

## Example Payloads

### Create MCP Server
```json
{
  "server_name": "Billing System MCP",
  "transport": "http",
  "endpoint": "http://billing.example.com:8080",
  "port": 8080
}
```

### External Tool Registry
```json
{
  "tool_name": "send_invoice_email",
  "description": "Send invoice via email",
  "input_schema": {
    "type": "object",
    "properties": {
      "invoice_id": {"type": "string"},
      "recipient": {"type": "string"}
    },
    "required": ["invoice_id", "recipient"]
  },
  "server_id": "customer-mcp",
  "capabilities": ["write", "email"]
}
```

### Configure AI Agent
```json
{
  "agent_id": "billing-agent",
  "agent_name": "Billing Assistant",
  "agent_type": "router",
  "description": "Handles billing-related requests",
  "config": {
    "model": "gpt-4",
    "temperature": 0.5
  },
  "allowed_tools": [
    "customer-mcp_get_customer",
    "customer-mcp_send_invoice_email"
  ],
  "policies": [
    {
      "name": "billing-policy",
      "rules": {
        "operations": ["read", "write"],
        "require_confirmation": true
      }
    }
  ]
}
```

## Common Issues

**Issue**: Webhook returns "Invalid server configuration"
**Fix**: Ensure all required fields are present in the JSON payload

**Issue**: Server not found error
**Fix**: Register the MCP server first using the Create MCP Server workflow

**Issue**: Database connection error
**Fix**: Verify Supabase credentials are configured in n8n

## Next Steps

1. Read the full README.md for detailed documentation
2. Add authentication to webhooks for production
3. Set up error notifications in n8n
4. Monitor workflow executions
5. Add custom validations as needed
