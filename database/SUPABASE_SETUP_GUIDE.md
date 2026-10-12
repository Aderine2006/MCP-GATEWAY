# Supabase Database Integration - Quick Setup Guide

## What You Need to Do

### Step 1: Create Supabase Project
1. Go to https://supabase.com
2. Create a new project (free tier is fine)
3. Wait for project to be ready (1-2 minutes)

### Step 2: Get Credentials
From your Supabase dashboard:
- Go to Settings → API
- Copy **Project URL** → This is `SUPABASE_URL`
- Copy **anon/public key** → This is `SUPABASE_ANON_KEY`

### Step 3: Update .env File
Add to your `.env` file:
```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
USE_SUPABASE=true
```

### Step 4: Run Database Schema
1. Go to your Supabase project dashboard
2. Click **SQL Editor** in the left sidebar
3. Click **New Query**
4. Open `database/supabase_schema.sql` and copy all its contents
5. Paste into the SQL Editor
6. Click **Run** button

### Step 5: Verify Setup
```bash
python database/setup_supabase.py --verify
```

## Database Schema Overview

The schema includes 9 tables:

1. **mcp_servers** - MCP server configurations
2. **tools** - Discovered tools from MCP servers
3. **requests** - Natural language request history
4. **routing** - Routing decisions and tool selection
5. **executions** - Tool execution results
6. **health_checks** - Server health monitoring
7. **users** - User management (optional)
8. **agents** - AI agent management (optional)
9. **policies** - Authorization policies (optional)

Plus 3 views for common queries:
- `active_tools_view` - All active tools with server info
- `request_history_view` - Request history with routing/execution
- `server_health_view` - Server health status summary

## Files Provided

1. **database/supabase_schema.sql** - Complete database schema (run this in Supabase SQL Editor)
2. **database/supabase_client.py** - Python client for database operations
3. **database/setup_supabase.py** - Setup and verification script
4. **database/README.md** - Detailed documentation

## Integration with Backend

To integrate Supabase into your backend:

1. Install the Supabase Python client:
```bash
pip install supabase
```

2. Update `backend/requirements.txt` to include `supabase`

3. Modify `backend/app/registry/repository.py` to use Supabase instead of in-memory storage

4. Modify `backend/app/router/intent_router.py` to log requests and executions to Supabase

Example usage:
```python
from database.supabase_client import get_db

db = get_db()

# Log a request
await db.create_request(
    request_id="req-123",
    raw_request="Find customer 1024",
    detected_operation="read",
    detected_domain="customer",
    extracted_parameters={"customer_id": "1024"}
)

# Log an execution
await db.create_execution(
    request_id="req-123",
    tool_id="customer-mcp_get_customer",
    server_id="customer-mcp",
    input_parameters={"customer_id": "1024"},
    execution_status="success"
)
```

## Sample Data

The schema includes sample data:
- 3 MCP servers (customer, support, incident)
- 3 tools (get_customer, get_tickets, create_incident)
- 1 demo user
- 2 agents (Tool Registry, Intent Router)
- 1 policy (write operation confirmation)

You can remove or modify this data as needed.

## Security Notes

- RLS policies are set to allow all access for MVP
- For production, update RLS policies based on your security requirements
- Use `SUPABASE_SERVICE_ROLE_KEY` for admin operations (never expose this to clients)
- Consider implementing proper authentication with Supabase Auth

## Support

If you encounter issues:
1. Check the detailed README in `database/README.md`
2. Verify your Supabase credentials in .env
3. Ensure the schema was run successfully in SQL Editor
4. Use the verification script to check setup

## Next Steps After Setup

1. Test the database connection with the Python client
2. Update the Tool Registry to persist tools to Supabase
3. Update the Intent Router to log all requests
4. Add health check logging to Supabase
5. Build analytics dashboard using the views provided
