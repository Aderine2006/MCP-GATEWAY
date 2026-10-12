# n8n Workflow Automation for Enterprise MCP Gateway

This directory contains n8n workflow JSON files for automating backend operations for the Enterprise MCP Gateway.

## Workflows

### 1. Create MCP Server

**Purpose**: Automate the creation and registration of new MCP servers in the system.

**Workflow Flow**:
```
Webhook Trigger
    ↓
Extract Parameters (server_name, transport, endpoint, port, command, args)
    ↓
Validate Configuration
    ├─ Invalid → Set Error Response → Respond to Webhook
    └─ Valid → Insert into Supabase (mcp_servers table)
                ↓
            Health Check (verify server is reachable)
                ↓
            Log Health Check (health_checks table)
                ↓
            Set Success Response
                ↓
            Respond to Webhook
```

**Input (via Webhook)**:
```json
{
  "server_name": "New MCP Server",
  "transport": "http",
  "endpoint": "http://localhost:9000",
  "port": 9000,
  "command": "python",
  "args": ["server.py"]
}
```

**Output**:
```json
{
  "server_id": "new-mcp-server-1234567890",
  "server_name": "New MCP Server",
  "transport": "http",
  "endpoint": "http://localhost:9000",
  "status": "created",
  "health_status": "healthy",
  "message": "MCP server created successfully"
}
```

**Validation Rules**:
- `server_name` must not be empty
- `transport` must be one of: `http`, `stdio`, `sse`
- For HTTP transport, `endpoint` must be provided
- For stdio transport, `command` must be provided

**Database Operations**:
1. Insert into `mcp_servers` table
2. Create initial health check record
3. Auto-generate `server_id` from server_name + timestamp

---

### 2. External Tool Registry

**Purpose**: Register external tools from third-party systems into the tool registry without requiring them to be MCP-compliant.

**Workflow Flow**:
```
Webhook Trigger
    ↓
Extract Tool Data (tool_name, description, input_schema, server_id, capabilities, tags)
    ↓
Validate Tool Data
    ├─ Invalid → Set Validation Error → Respond to Webhook
    └─ Valid → Verify Server Exists (check mcp_servers table)
                ├─ Server not found → Set Server Error → Respond to Webhook
                └─ Server exists → Register Tool in Supabase (tools table)
                                    ↓
                                Upsert Tool (handle duplicates gracefully)
                                    ↓
                                Set Success Response
                                    ↓
                                Respond to Webhook
```

**Input (via Webhook)**:
```json
{
  "tool_name": "external_api_call",
  "description": "Call external API endpoint",
  "input_schema": {
    "type": "object",
    "properties": {
      "endpoint": {"type": "string"},
      "method": {"type": "string"},
      "headers": {"type": "object"}
    },
    "required": ["endpoint", "method"]
  },
  "server_id": "customer-mcp",
  "capabilities": ["read", "api"],
  "tags": ["external", "http"]
}
```

**Output**:
```json
{
  "tool_id": "customer-mcp-external_api_call",
  "name": "external_api_call",
  "description": "Call external API endpoint",
  "server_id": "customer-mcp",
  "status": "registered",
  "message": "Tool registered successfully in external registry"
}
```

**Validation Rules**:
- `tool_name` must not be empty
- `description` must not be empty
- `input_schema` must be a valid JSON object
- `server_id` must exist in `mcp_servers` table

**Database Operations**:
1. Verify server exists in `mcp_servers`
2. Insert or update tool in `tools` table (upsert)
3. Handle duplicate tool IDs gracefully
4. Auto-generate `tool_id` from server_id + tool_name

**Use Cases**:
- Register external API endpoints as tools
- Add third-party integrations without MCP compliance
- Create wrapper tools for legacy systems
- Register tools from external tool catalogs

---

### 3. Configure AI Agent

**Purpose**: Configure AI agents with tool permissions, policies, and configuration settings.

**Workflow Flow**:
```
Webhook Trigger
    ↓
Extract Agent Data (agent_id, agent_name, agent_type, description, config, allowed_tools, policies)
    ↓
Validate Agent Data
    ├─ Invalid → Set Validation Error → Respond to Webhook
    └─ Valid → Create/Update Agent in Supabase (agents table)
                ↓
            Check Tools Configuration
            ├─ Has tools → Process Allowed Tools (batch)
            │              ↓
            │          Grant Tool Permissions (agent_tool_permissions table)
            │              ↓
            │          Continue
            └─ No tools → Continue
                ↓
            Check Policies Configuration
            ├─ Has policies → Process Policies (batch)
            │                  ↓
            │              Create Policy (policies table)
            │                  ↓
            │              Link Policy to Agent (agent_policy_mapping table)
            │                  ↓
            │              Continue
            └─ No policies → Continue
                ↓
            Save Agent Configuration (agent_config table)
                ↓
            Register with Gateway (call gateway API)
                ↓
            Set Success Response
                ↓
            Respond to Webhook
```

**Input (via Webhook)**:
```json
{
  "agent_id": "customer-service-agent",
  "agent_name": "Customer Service Agent",
  "agent_type": "router",
  "description": "Handles customer-related requests",
  "config": {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000,
    "system_prompt": "You are a helpful customer service assistant."
  },
  "allowed_tools": [
    "customer-mcp_get_customer",
    "support-mcp_get_tickets"
  ],
  "policies": [
    {
      "name": "read-only",
      "rules": {
        "operations": ["read"],
        "require_confirmation": false
      }
    }
  ]
}
```

**Output**:
```json
{
  "agent_id": "customer-service-agent",
  "agent_name": "Customer Service Agent",
  "agent_type": "router",
  "status": "configured",
  "message": "AI agent configured successfully with tool permissions and policies",
  "tools_granted": 2,
  "policies_applied": 1
}
```

**Validation Rules**:
- `agent_id` must not be empty
- `agent_name` must not be empty
- `agent_type` must be one of: `router`, `registry`, `executor`, `custom`

**Database Operations**:
1. Create/update agent in `agents` table
2. Grant tool permissions in `agent_tool_permissions` table (if tools provided)
3. Create policies in `policies` table (if policies provided)
4. Link policies to agent in `agent_policy_mapping` table
5. Save complete configuration in `agent_config` table
6. Register agent with Gateway API

**Configuration Parameters**:
- `agent_type`: Determines agent role in the system
  - `router`: Routes requests to tools
  - `registry`: Manages tool discovery
  - `executor`: Executes tools
  - `custom`: Custom agent behavior
- `config`: Agent-specific configuration (model settings, prompts, etc.)
- `allowed_tools`: List of tool IDs the agent can access
- `policies`: Access control policies for the agent

---

## Setup Instructions

### 1. Prerequisites

- n8n instance (self-hosted or cloud)
- Supabase project with database schema deployed
- Environment variables configured in n8n:
  - `SUPABASE_URL`: Your Supabase project URL
  - `SUPABASE_ANON_KEY`: Your Supabase anon/public key

### 2. Import Workflows

1. Open n8n workflow editor
2. Click "Import from File"
3. Select the JSON file for each workflow
4. Configure environment variables in n8n credentials
5. Activate each workflow

### 3. Configure Webhooks

Each workflow has a webhook trigger. After activation:

1. Copy the webhook URL from n8n
2. Use it in your application to trigger the workflow

Example webhook URLs:
- Create MCP Server: `https://your-n8n-instance.com/webhook/create-mcp-server`
- External Tool Registry: `https://your-n8n-instance.com/webhook/register-tool`
- Configure AI Agent: `https://your-n8n-instance.com/webhook/configure-agent`

### 4. Additional Database Tables Required

For the workflows to work fully, add these tables to your Supabase schema:

```sql
-- Agent tool permissions
CREATE TABLE agent_tool_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) NOT NULL,
    tool_id VARCHAR(255) NOT NULL,
    permission VARCHAR(50) DEFAULT 'execute',
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent policy mapping
CREATE TABLE agent_policy_mapping (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) NOT NULL,
    policy_name VARCHAR(255) NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent configuration
CREATE TABLE agent_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) UNIQUE NOT NULL,
    config_json JSONB NOT NULL,
    tool_permissions JSONB DEFAULT '[]'::jsonb,
    policy_ids JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## Integration with Backend

### API Endpoints to Add

Add these endpoints to your FastAPI backend to work with n8n workflows:

```python
# backend/app/api/agents.py (extend existing file)

@router.post("/register")
async def register_agent(agent_data: AgentConfig):
    """Register an agent with the gateway."""
    # Store agent configuration in memory or database
    # Return success response
    pass

@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent configuration."""
    pass

@router.put("/{agent_id}")
async def update_agent(agent_id: str, agent_data: AgentConfig):
    """Update agent configuration."""
    pass
```

---

## Testing the Workflows

### Test Create MCP Server

```bash
curl -X POST https://your-n8n-instance.com/webhook/create-mcp-server \
  -H "Content-Type: application/json" \
  -d '{
    "server_name": "Test MCP Server",
    "transport": "http",
    "endpoint": "http://localhost:9000",
    "port": 9000
  }'
```

### Test External Tool Registry

```bash
curl -X POST https://your-n8n-instance.com/webhook/register-tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "test_tool",
    "description": "A test tool",
    "input_schema": {"type": "object", "properties": {}},
    "server_id": "customer-mcp",
    "capabilities": ["read"]
  }'
```

### Test Configure AI Agent

```bash
curl -X POST https://your-n8n-instance.com/webhook/configure-agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "test-agent",
    "agent_name": "Test Agent",
    "agent_type": "router",
    "description": "A test agent",
    "config": {"model": "gpt-4"},
    "allowed_tools": ["customer-mcp_get_customer"],
    "policies": []
  }'
```

---

## Error Handling

Each workflow includes comprehensive error handling:

1. **Validation Errors**: Returns structured error messages
2. **Server Not Found**: Validates MCP server exists before tool registration
3. **Duplicate Handling**: Uses upsert operations to handle duplicates gracefully
4. **Health Check Failures**: Logs failed health checks but continues registration

---

## Monitoring and Logging

All workflows perform database operations that can be monitored:

- Check `mcp_servers` table for server registration history
- Check `tools` table for tool registration history
- Check `health_checks` table for server health monitoring
- Check `agents` table for agent configuration history
- Check `requests` and `executions` tables for agent activity

---

## Security Considerations

1. **Webhook Security**: Add authentication to webhooks in production
2. **API Key Management**: Store Supabase keys in n8n credentials, not in workflows
3. **Input Validation**: All workflows validate input data before processing
4. **Policy Enforcement**: Agent configuration includes policy-based access control
5. **Audit Trail**: All operations are logged in database tables

---

## Extending Workflows

### Adding Custom Validations

Add additional validation nodes after the initial validation step:

```json
{
  "parameters": {
    "conditions": {
      "conditions": [
        {
          "id": "custom_validation",
          "leftValue": "={{ $json.custom_field }}",
          "rightValue": "expected_value",
          "operator": {"type": "string", "operation": "equals"}
        }
      ]
    }
  },
  "name": "Custom Validation",
  "type": "n8n-nodes-base.if"
}
```

### Adding Post-Processing

Add nodes after the success response to trigger additional actions:

- Send notifications (Slack, email)
- Update external systems
- Trigger other workflows
- Generate reports

---

## Troubleshooting

### Workflow Not Triggering

1. Check webhook URL is correct
2. Verify n8n instance is running
3. Check webhook is active in n8n
4. Test webhook with curl

### Database Connection Issues

1. Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set in n8n
2. Check Supabase project is active
3. Verify database schema is deployed
4. Check RLS policies allow writes

### Validation Errors

1. Check input JSON format
2. Verify required fields are present
3. Check field values match validation rules
4. Review workflow execution logs in n8n

---

## Next Steps

1. Deploy the additional database tables
2. Import workflows into n8n
3. Configure webhook authentication
4. Add API endpoints to backend
5. Test each workflow
6. Monitor execution logs
7. Set up error notifications
8. Document custom configurations
