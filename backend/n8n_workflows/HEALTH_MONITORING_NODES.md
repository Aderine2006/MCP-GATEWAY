# Health Monitoring & Alerting - Node Configuration Guide

This document provides detailed configuration for each node in the Health Monitoring & Alerting workflow.

## Node List

1. **Schedule Trigger** - Triggers workflow every 5 minutes
2. **Get MCP Servers** - Fetches all MCP servers from database
3. **Process Each Server** - Iterates through each server
4. **Health Check** - Performs HTTP health check on each server
5. **Check Health Status** - Evaluates health check response
6. **Log Healthy Status** - Logs successful health checks
7. **Log Unhealthy Status** - Logs failed health checks
8. **Alert on Unhealthy** - Determines if alert is needed
9. **Send Slack Alert** - Sends notification to Slack
10. **Merge Health Results** - Consolidates all results

---

## Node 1: Schedule Trigger

**Type**: `Schedule Trigger`
**Purpose**: Run workflow every 5 minutes

**Configuration**:
```json
{
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "minutes",
          "minutesInterval": 5
        }
      ]
    }
  }
}
```

**Alternative Schedule Options**:
- Every 1 minute: `{"field": "minutes", "minutesInterval": 1}`
- Every hour: `{"field": "hours", "hoursInterval": 1}`
- Cron expression: `{"field": "cronExpression", "expression": "*/5 * * * *"}`

---

## Node 2: Get MCP Servers

**Type**: `Postgres` (or `Supabase` node if available)
**Purpose**: Fetch all active MCP servers from database

**Configuration**:
```json
{
  "operation": "list",
  "resource": "database",
  "database": "postgres",
  "schema": "public",
  "table": "mcp_servers",
  "where": {
    "conditions": [
      {
        "column": "is_active",
        "condition": "equals",
        "value": true
      }
    ]
  }
}
```

**Alternative using HTTP Request**:
```json
{
  "method": "GET",
  "url": "{{$env.SUPABASE_URL}}/rest/mcp_servers?is_active=eq.true&select=*",
  "authentication": "genericCredentialType",
  "genericAuthType": "httpHeaderAuth",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "apikey",
        "value": "{{$env.SUPABASE_ANON_KEY}}"
      }
    ]
  }
}
```

---

## Node 3: Process Each Server

**Type**: `Split In Batches`
**Purpose**: Iterate through each server for individual health checks

**Configuration**:
```json
{
  "mode": "combine",
  "combinationMode": "multiplex",
  "options": {
    "batchSize": 1
  }
}
```

**Key Settings**:
- `batchSize: 1` - Process one server at a time
- `combinationMode: multiplex` - Process all items individually

---

## Node 4: Health Check

**Type**: `HTTP Request`
**Purpose**: Perform HTTP health check on MCP server endpoint

**Configuration**:
```json
{
  "url": "={{$json.endpoint}}/health",
  "method": "GET",
  "options": {
    "timeout": 10000,
    "response": {
      "response": {
        "fullResponse": false,
        "neverError": true
      }
    }
  }
}
```

**Important Options**:
- `timeout: 10000` - 10 second timeout
- `neverError: true` - Don't fail on 4xx/5xx status codes
- `fullResponse: false` - Only return body

**Expected Response**:
```json
{
  "status": "healthy"
}
```

---

## Node 5: Check Health Status

**Type**: `IF`
**Purpose**: Evaluate if health check was successful

**Configuration**:
```json
{
  "conditions": {
    "options": {
      "caseSensitive": true,
      "leftValue": "",
      "typeValidation": "strict"
    },
    "conditions": [
      {
        "id": "check_status",
        "leftValue": "={{$json.status}}",
        "rightValue": "200",
        "operator": {
          "type": "number",
          "operation": "equals"
        }
      }
    ],
    "combinator": "and"
  }
}
```

**Alternative Condition** (check response body):
```json
{
  "conditions": [
    {
      "leftValue": "={{$json.status}}",
      "rightValue": "200",
      "operator": {"type": "number", "operation": "equals"}
    },
    {
      "leftValue": "={{$json.body.status}}",
      "rightValue": "healthy",
      "operator": {"type": "string", "operation": "equals"}
    }
  ],
  "combinator": "and"
}
```

**Outputs**:
- **True** (output 0): Health check passed
- **False** (output 1): Health check failed

---

## Node 6: Log Healthy Status

**Type**: `HTTP Request` (to Supabase)
**Purpose**: Log successful health check to database

**Configuration**:
```json
{
  "method": "POST",
  "url": "{{$env.SUPABASE_URL}}/rest/health_checks",
  "authentication": "genericCredentialType",
  "genericAuthType": "httpHeaderAuth",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "apikey",
        "value": "{{$env.SUPABASE_ANON_KEY}}"
      },
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "bodyParameters": {
    "parameters": [
      {
        "name": "server_id",
        "value": "={{$('Process Each Server').item.json.server_id}}"
      },
      {
        "name": "status",
        "value": "healthy"
      },
      {
        "name": "response_time_ms",
        "value": "={{$json.executionTime}}"
      },
      {
        "name": "checked_at",
        "value": "={{$now}}"
      }
    ]
  }
}
```

---

## Node 7: Log Unhealthy Status

**Type**: `HTTP Request` (to Supabase)
**Purpose**: Log failed health check to database

**Configuration**:
```json
{
  "method": "POST",
  "url": "{{$env.SUPABASE_URL}}/rest/health_checks",
  "authentication": "genericCredentialType",
  "genericAuthType": "httpHeaderAuth",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "apikey",
        "value": "{{$env.SUPABASE_ANON_KEY}}"
      },
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "bodyParameters": {
    "parameters": [
      {
        "name": "server_id",
        "value": "={{$('Process Each Server').item.json.server_id}}"
      },
      {
        "name": "status",
        "value": "unhealthy"
      },
      {
        "name": "error_message",
        "value": "Health check failed with status {{$json.status}}"
      },
      {
        "name": "checked_at",
        "value": "={{$now}}"
      }
    ]
  }
}
```

---

## Node 8: Alert on Unhealthy

**Type**: `IF`
**Purpose**: Determine if alert should be sent (retry logic)

**Configuration**:
```json
{
  "conditions": {
    "options": {
      "caseSensitive": true,
      "leftValue": "",
      "typeValidation": "strict"
    },
    "conditions": [
      {
        "id": "check_unhealthy_count",
        "leftValue": "={{$json.error_message}}",
        "rightValue": "",
        "operator": {
          "type": "string",
          "operation": "isNotEmpty"
        }
      }
    ],
    "combinator": "and"
  }
}
```

**Advanced Version with Retry Count**:
```json
{
  "conditions": [
    {
      "leftValue": "={{$json.consecutive_failures}}",
      "rightValue": 3,
      "operator": {"type": "number", "operation": "gte"}
    }
  ],
  "combinator": "and"
}
```

**Logic**: Only alert after 3 consecutive failures

---

## Node 9: Send Slack Alert

**Type**: `Slack`
**Purpose**: Send alert notification to Slack channel

**Configuration**:
```json
{
  "channel": "#alerts",
  "text": "⚠️ MCP Server Unhealthy\n\nServer: {{$('Process Each Server').item.json.server_name}}\nServer ID: {{$('Process Each Server').item.json.server_id}}\nEndpoint: {{$('Process Each Server').item.json.endpoint}}\nError: {{$('Log Unhealthy Status').item.json.error_message}}\nTime: {{$now.format('yyyy-MM-dd HH:mm:ss')}}\n\nPlease investigate.",
  "username": "n8n-health-monitor",
  "iconEmoji": ":warning:"
}
```

**Required Setup**:
1. In n8n, go to Credentials → Add Credential → Slack API
2. Use "Slack Bot Token" authentication
3. Create a Slack app and install to your workspace
4. Add bot to target channel with `/invite @bot-name`

**Alternative: Send to Microsoft Teams**
```json
{
  "webhookUrl": "YOUR_TEAMS_WEBHOOK_URL",
  "content": {
    "@type": "MessageCard",
    "@context": "https://schema.org/extensions",
    "summary": "MCP Server Unhealthy",
    "themeColor": "FF0000",
    "title": "⚠️ MCP Server Health Alert",
    "sections": [
      {
        "facts": [
          {
            "name": "Server",
            "value": "{{$('Process Each Server').item.json.server_name}}"
          },
          {
            "name": "Endpoint",
            "value": "{{$('Process Each Server').item.json.endpoint}}"
          },
          {
            "name": "Time",
            "value": "{{$now.format('yyyy-MM-dd HH:mm:ss')}}"
          }
        ]
      }
    ]
  }
}
```

**Alternative: Send Email**
```json
{
  "subject": "⚠️ MCP Server Health Alert: {{$('Process Each Server').item.json.server_name}}",
  "email": "ops-team@company.com",
  "text": "MCP Server {{$('Process Each Server').item.json.server_name}} is unhealthy.\n\nServer ID: {{$('Process Each Server').item.json.server_id}}\nEndpoint: {{$('Process Each Server').item.json.endpoint}}\nError: {{$('Log Unhealthy Status').item.json.error_message}}\nTime: {{$now.format('yyyy-MM-dd HH:mm:ss')}}"
}
```

---

## Node 10: Merge Health Results

**Type**: `Merge`
**Purpose**: Consolidate all health check results

**Configuration**:
```json
{
  "mode": "combine",
  "combinationMode": "merge",
  "options": {
    "cloning": {
      "cloneItems": false
    }
  }
}
```

**Purpose**: Merges all processed server results into a single output for final reporting

---

## Workflow Connections

```
Schedule Trigger
    ↓
Get MCP Servers
    ↓
Process Each Server (loop)
    ↓
Health Check
    ↓
Check Health Status
    ├─ True → Log Healthy Status → Merge Health Results
    └─ False → Log Unhealthy Status → Alert on Unhealthy
                               ├─ True → Send Slack Alert → Merge Health Results
                               └─ False → Merge Health Results
```

---

## Environment Variables Required

Add these to n8n environment variables:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
```

---

## Additional Database Table (if not exists)

The workflow uses a `health_checks` table. Add this to your schema:

```sql
CREATE TABLE IF NOT EXISTS health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    server_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('healthy', 'unhealthy')),
    response_time_ms INTEGER,
    error_message TEXT,
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_health_checks_server_id ON health_checks(server_id);
CREATE INDEX IF NOT EXISTS idx_health_checks_checked_at ON health_checks(checked_at);
```

---

## Testing the Workflow

### Test Individual Nodes

1. **Test Get MCP Servers**:
   - Run node and verify it returns server list
   - Check `server_id`, `server_name`, `endpoint` fields

2. **Test Health Check**:
   - Manually test with: `curl http://localhost:8001/health`
   - Verify response: `{"status": "healthy"}`

3. **Test Slack Alert**:
   - Use Slack webhook tester
   - Verify message format

### Test Full Workflow

1. **Stop one MCP server** to simulate failure:
   ```bash
   # Find and stop customer-mcp
   taskkill /F /PID <customer-mcp-pid>
   ```

2. **Activate workflow** in n8n

3. **Wait 5 minutes** for next schedule

4. **Check Slack** for alert

5. **Restart server** and verify healthy status logged

---

## Advanced Features to Add

### 1. Retry Logic
Add a Wait node before alert:
```
Log Unhealthy Status
    ↓
Wait 30 seconds
    ↓
Retry Health Check
    ↓
Check if still unhealthy
    ├─ Yes → Send Alert
    └─ No → Log as recovered
```

### 2. Escalation Logic
```
Alert on Unhealthy
    ↓
Check time since first failure
    ├─ < 5 minutes → Wait 5 minutes
    ├─ 5-15 minutes → Send to Slack
    ├─ 15-30 minutes → Send email to on-call
    └─ > 30 minutes → Send PagerDuty alert
```

### 3. Auto-Recovery
```
Alert on Unhealthy
    ↓
Attempt auto-restart (if container-based)
    ↓
Check if recovered
    ├─ Yes → Log recovery
    └─ No → Escalate
```

### 4. Historical Analysis
Add a node to analyze trends:
```
Merge Health Results
    ↓
Analyze health check history (last 24 hours)
    ↓
Calculate uptime percentage
    ↓
Send daily health report
```

---

## Troubleshooting

### Issue: Health check always fails

**Possible causes**:
1. Wrong endpoint URL in database
2. Server not running
3. Firewall blocking connection
4. Timeout too short

**Solution**:
- Verify endpoint in `mcp_servers` table
- Test endpoint manually with curl
- Increase timeout in HTTP Request node
- Check server logs

### Issue: Slack alerts not sending

**Possible causes**:
1. Invalid Slack bot token
2. Bot not in channel
3. Channel name incorrect

**Solution**:
- Verify bot token in n8n credentials
- Invite bot to channel: `/invite @bot-name`
- Check channel name (remove # if needed)

### Issue: Database insert fails

**Possible causes**:
1. Wrong Supabase URL/key
2. Table doesn't exist
3. Permission denied

**Solution**:
- Verify environment variables
- Run health_checks table creation SQL
- Check RLS policies in Supabase

---

## Monitoring Dashboard Query

Create a Supabase dashboard query to visualize health data:

```sql
SELECT
    server_id,
    status,
    COUNT(*) as check_count,
    AVG(response_time_ms) as avg_response_time,
    MAX(checked_at) as last_check
FROM health_checks
WHERE checked_at > NOW() - INTERVAL '1 hour'
GROUP BY server_id, status
ORDER BY server_id, status;
```

This will show health check statistics for the last hour.
