# Supabase Database Setup for Enterprise MCP Gateway

This directory contains the database schema and client for integrating Supabase with the Enterprise MCP Gateway.

## Quick Start

### 1. Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Create a new project
4. Wait for the project to be ready (usually 1-2 minutes)

### 2. Get Your Credentials

From your Supabase project dashboard:
1. Go to **Settings** → **API**
2. Copy the **Project URL** (this is your `SUPABASE_URL`)
3. Copy the **anon/public** key (this is your `SUPABASE_ANON_KEY`)

### 3. Set Environment Variables

Add these to your `.env` file in the project root:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
USE_SUPABASE=true
```

### 4. Run the Database Schema

#### Option A: Using Supabase Dashboard (Recommended)

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor** (in the left sidebar)
3. Click **New Query**
4. Copy the entire contents of `database/supabase_schema.sql`
5. Paste it into the SQL Editor
6. Click **Run** (or press Ctrl+Enter)

The schema will create:
- 9 tables (mcp_servers, tools, requests, routing, executions, health_checks, users, agents, policies)
- 3 views (active_tools_view, request_history_view, server_health_view)
- Indexes for performance
- Row Level Security (RLS) policies
- Sample data for testing

#### Option B: Using the Setup Script

```bash
python database/setup_supabase.py
```

This will verify your connection and provide instructions for running the schema manually.

### 5. Verify the Setup

```bash
python database/setup_supabase.py --verify
```

This will check that all tables were created successfully.

## Database Schema

### Tables

#### `mcp_servers`
Stores configuration for MCP servers.
- `server_id`: Unique identifier for the server
- `server_name`: Human-readable name
- `transport`: Communication method (stdio, sse, http)
- `endpoint`: Server endpoint URL
- `port`: Server port number
- `is_active`: Whether the server is active

#### `tools`
Stores discovered tools from MCP servers.
- `tool_id`: Unique identifier for the tool
- `name`: Tool name
- `description`: Tool description
- `input_schema`: JSON schema for tool parameters
- `server_id`: Reference to MCP server
- `capabilities`: List of tool capabilities
- `status`: Tool status (active, inactive, unhealthy)
- `health_status`: Current health status

#### `requests`
Stores natural language request history.
- `request_id`: Unique request identifier
- `raw_request`: Original user request
- `detected_operation`: Extracted operation type
- `detected_domain`: Extracted domain
- `extracted_parameters`: Parsed parameters
- `user_id`: User who made the request
- `created_at`: Timestamp

#### `routing`
Stores routing decisions.
- `request_id`: Reference to request
- `selected_tool_id`: Tool that was selected
- `selected_server_id`: Server that was selected
- `routing_score`: Confidence score for the routing decision
- `routing_explanation`: Explanation of why this tool was selected
- `permission_granted`: Whether permission was granted
- `permission_required`: Type of permission required

#### `executions`
Stores tool execution results.
- `request_id`: Reference to request
- `tool_id`: Tool that was executed
- `server_id`: Server that executed the tool
- `execution_status`: Status (pending, success, failed, timeout)
- `input_parameters`: Parameters passed to the tool
- `output_result`: Tool output
- `error_message`: Error message if failed
- `execution_duration_ms`: Execution time in milliseconds

#### `health_checks`
Stores health check history for servers.
- `server_id`: Reference to MCP server
- `status`: Health status (healthy, unhealthy, unreachable)
- `response_time_ms`: Response time
- `error_message`: Error message if unhealthy
- `checked_at`: Timestamp

#### `users`
Stores user information (optional, for authentication).
- `user_id`: Unique user identifier
- `email`: User email
- `name`: User name
- `role`: User role (admin, user, agent)

#### `agents`
Stores AI agent information (optional).
- `agent_id`: Unique agent identifier
- `agent_name`: Agent name
- `agent_type`: Agent type
- `description`: Agent description
- `config`: Agent configuration

#### `policies`
Stores authorization policies (optional).
- `policy_name`: Policy name
- `policy_type`: Policy type (tool_access, operation_type, resource_based)
- `rules`: Policy rules (JSON)
- `is_active`: Whether policy is active

### Views

#### `active_tools_view`
Shows all active tools with server information.

#### `request_history_view`
Shows request history with routing and execution info.

#### `server_health_view`
Shows health status summary for all servers.

## Using the Python Client

```python
from database.supabase_client import get_db

# Get database instance
db = get_db()

# Create an MCP server
await db.create_mcp_server(
    server_id="customer-mcp",
    server_name="Customer MCP Server",
    transport="http",
    endpoint="http://127.0.0.1:8001",
    port=8001
)

# List all tools
tools = await db.list_tools(active_only=True)

# Create a request
await db.create_request(
    request_id="req-123",
    raw_request="Find customer 1024",
    detected_operation="read",
    detected_domain="customer",
    extracted_parameters={"customer_id": "1024"}
)

# Get execution statistics
stats = await db.get_execution_stats()
print(f"Success rate: {stats['success_rate']}%")
```

## Common Queries

### Get all active tools
```sql
SELECT * FROM active_tools_view;
```

### Get request history
```sql
SELECT * FROM request_history_view ORDER BY created_at DESC LIMIT 10;
```

### Get server health status
```sql
SELECT * FROM server_health_view;
```

### Get execution statistics
```sql
SELECT 
    COUNT(*) as total_executions,
    AVG(execution_duration_ms) as avg_duration,
    SUM(CASE WHEN execution_status = 'success' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN execution_status = 'failed' THEN 1 ELSE 0 END) as failed
FROM executions;
```

### Get most used tools
```sql
SELECT 
    tool_id,
    COUNT(*) as usage_count
FROM executions
WHERE execution_status = 'success'
GROUP BY tool_id
ORDER BY usage_count DESC
LIMIT 10;
```

## Security

The schema includes Row Level Security (RLS) policies. For the MVP, all read and write operations are allowed. For production:

1. Update RLS policies to restrict access based on user roles
2. Use the `SUPABASE_SERVICE_ROLE_KEY` for admin operations
3. Implement proper authentication in your application

## Troubleshooting

### Connection Issues
- Verify your `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct
- Check that your Supabase project is active
- Ensure the schema has been run in the SQL Editor

### Table Not Found Errors
- Run the schema SQL in the Supabase SQL Editor
- Use `python database/setup_supabase.py --verify` to check setup

### Permission Errors
- Check RLS policies in Supabase dashboard
- Ensure your API key has the necessary permissions

## Next Steps

1. Run the schema in Supabase SQL Editor
2. Update your `.env` file with Supabase credentials
3. Integrate the Supabase client into your backend code
4. Update the Tool Registry Agent to use Supabase instead of in-memory storage
5. Update the Intent Router to log requests and executions to Supabase

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://supabase.com/docs/reference/python)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
