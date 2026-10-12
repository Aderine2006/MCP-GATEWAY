-- =====================================================
-- Enterprise MCP Gateway - Supabase Database Schema
-- =====================================================
-- Run this in Supabase SQL Editor to create all tables
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- MCP Servers Table
-- =====================================================
CREATE TABLE mcp_servers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    server_id VARCHAR(255) UNIQUE NOT NULL,
    server_name VARCHAR(255) NOT NULL,
    transport VARCHAR(50) NOT NULL CHECK (transport IN ('stdio', 'sse', 'http')),
    endpoint VARCHAR(500),
    port INTEGER,
    command TEXT,
    args JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on server_id for faster lookups
CREATE INDEX idx_mcp_servers_server_id ON mcp_servers(server_id);

-- =====================================================
-- Tools Registry Table
-- =====================================================
CREATE TABLE tools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    input_schema JSONB NOT NULL,
    server_id VARCHAR(255) NOT NULL REFERENCES mcp_servers(server_id) ON DELETE CASCADE,
    server_name VARCHAR(255) NOT NULL,
    transport VARCHAR(50) NOT NULL,
    endpoint VARCHAR(500),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'unhealthy')),
    health_status VARCHAR(50) DEFAULT 'unknown',
    capabilities JSONB DEFAULT '[]'::jsonb,
    last_discovered TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_health_check TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX idx_tools_server_id ON tools(server_id);
CREATE INDEX idx_tools_status ON tools(status);
CREATE INDEX idx_tools_name ON tools(name);
CREATE INDEX idx_tools_capabilities ON tools USING GIN(capabilities);

-- =====================================================
-- Requests Table (Request History)
-- =====================================================
CREATE TABLE requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(255) UNIQUE NOT NULL,
    raw_request TEXT NOT NULL,
    detected_operation VARCHAR(50),
    detected_domain VARCHAR(50),
    extracted_parameters JSONB DEFAULT '{}'::jsonb,
    user_id VARCHAR(255),
    agent_id VARCHAR(255),
    source_ip VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_requests_request_id ON requests(request_id);
CREATE INDEX idx_requests_created_at ON requests(created_at DESC);
CREATE INDEX idx_requests_user_id ON requests(user_id);
CREATE INDEX idx_requests_operation ON requests(detected_operation);
CREATE INDEX idx_requests_domain ON requests(detected_domain);

-- =====================================================
-- Routing Table (Routing Decisions)
-- =====================================================
CREATE TABLE routing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(255) NOT NULL REFERENCES requests(request_id) ON DELETE CASCADE,
    selected_tool_id VARCHAR(255) REFERENCES tools(tool_id) ON DELETE SET NULL,
    selected_server_id VARCHAR(255) REFERENCES mcp_servers(server_id) ON DELETE SET NULL,
    routing_score DECIMAL(5,2),
    routing_explanation TEXT,
    candidates_matched INTEGER DEFAULT 0,
    permission_granted BOOLEAN DEFAULT true,
    permission_required VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_routing_request_id ON routing(request_id);
CREATE INDEX idx_routing_tool_id ON routing(selected_tool_id);
CREATE INDEX idx_routing_server_id ON routing(selected_server_id);

-- =====================================================
-- Executions Table (Tool Execution Results)
-- =====================================================
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(255) NOT NULL REFERENCES requests(request_id) ON DELETE CASCADE,
    routing_id UUID REFERENCES routing(id) ON DELETE SET NULL,
    tool_id VARCHAR(255) REFERENCES tools(tool_id) ON DELETE SET NULL,
    server_id VARCHAR(255) REFERENCES mcp_servers(server_id) ON DELETE SET NULL,
    execution_status VARCHAR(50) DEFAULT 'pending' CHECK (execution_status IN ('pending', 'success', 'failed', 'timeout')),
    input_parameters JSONB DEFAULT '{}'::jsonb,
    output_result JSONB,
    error_message TEXT,
    execution_duration_ms DECIMAL(10,2),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX idx_executions_request_id ON executions(request_id);
CREATE INDEX idx_executions_tool_id ON executions(tool_id);
CREATE INDEX idx_executions_status ON executions(execution_status);
CREATE INDEX idx_executions_started_at ON executions(started_at DESC);

-- =====================================================
-- Health Checks Table
-- =====================================================
CREATE TABLE health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    server_id VARCHAR(255) NOT NULL REFERENCES mcp_servers(server_id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'healthy' CHECK (status IN ('healthy', 'unhealthy', 'unreachable')),
    response_time_ms DECIMAL(10,2),
    error_message TEXT,
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_health_checks_server_id ON health_checks(server_id);
CREATE INDEX idx_health_checks_checked_at ON health_checks(checked_at DESC);
CREATE INDEX idx_health_checks_status ON health_checks(status);

-- =====================================================
-- Users Table (Optional - for authentication)
-- =====================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'agent')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_email ON users(email);

-- =====================================================
-- Agents Table (Optional - for AI agent management)
-- =====================================================
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) UNIQUE NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    agent_type VARCHAR(100),
    description TEXT,
    config JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_agents_agent_id ON agents(agent_id);
CREATE INDEX idx_agents_type ON agents(agent_type);

-- =====================================================
-- Policies Table (Optional - for routing authorization)
-- =====================================================
CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_name VARCHAR(255) UNIQUE NOT NULL,
    policy_type VARCHAR(50) CHECK (policy_type IN ('tool_access', 'operation_type', 'resource_based')),
    rules JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_policies_name ON policies(policy_name);
CREATE INDEX idx_policies_type ON policies(policy_type);
CREATE INDEX idx_policies_active ON policies(is_active);

-- =====================================================
-- Triggers for updated_at timestamps
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_mcp_servers_updated_at BEFORE UPDATE ON mcp_servers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tools_updated_at BEFORE UPDATE ON tools
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_policies_updated_at BEFORE UPDATE ON policies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- Insert Sample Data (Optional)
-- =====================================================

-- Insert sample MCP servers
INSERT INTO mcp_servers (server_id, server_name, transport, endpoint, port, is_active) VALUES
('customer-mcp', 'Customer MCP Server', 'http', 'http://127.0.0.1', 8001, true),
('support-mcp', 'Support MCP Server', 'http', 'http://127.0.0.1', 8002, true),
('incident-mcp', 'Incident MCP Server', 'http', 'http://127.0.0.1', 8003, true)
ON CONFLICT (server_id) DO NOTHING;

-- Insert sample tools (will be populated by discovery)
-- Note: These are examples - actual tools will be discovered dynamically
INSERT INTO tools (tool_id, name, description, input_schema, server_id, server_name, transport, endpoint, status, capabilities) VALUES
('customer-mcp_get_customer', 'get_customer', 'Get customer details by ID', 
 '{"type": "object", "properties": {"customer_id": {"type": "string"}}, "required": ["customer_id"]}',
 'customer-mcp', 'Customer MCP Server', 'http', 'http://127.0.0.1:8001', 'active', 
 '["read", "customer"]'::jsonb),
('support-mcp_get_tickets', 'get_tickets', 'Get support tickets for a customer',
 '{"type": "object", "properties": {"customer_id": {"type": "string"}}, "required": ["customer_id"]}',
 'support-mcp', 'Support MCP Server', 'http', 'http://127.0.0.1:8002', 'active',
 '["read", "support", "customer"]'::jsonb),
('incident-mcp_create_incident', 'create_incident', 'Create a new incident',
 '{"type": "object", "properties": {"customer_id": {"type": "string"}, "title": {"type": "string"}, "severity": {"type": "string"}}, "required": ["customer_id", "title", "severity"]}',
 'incident-mcp', 'Incident MCP Server', 'http', 'http://127.0.0.1:8003', 'active',
 '["write", "incident"]'::jsonb)
ON CONFLICT (tool_id) DO NOTHING;

-- Insert sample user
INSERT INTO users (user_id, email, name, role) VALUES
('demo-user', 'demo@example.com', 'Demo User', 'admin')
ON CONFLICT (user_id) DO NOTHING;

-- Insert sample agent
INSERT INTO agents (agent_id, agent_name, agent_type, description) VALUES
('tool-registry-agent', 'Tool Registry Agent', 'registry', 'Discovers and manages MCP tools'),
('intent-router-agent', 'Intent Router Agent', 'router', 'Routes natural language requests to appropriate tools')
ON CONFLICT (agent_id) DO NOTHING;

-- Insert sample policy
INSERT INTO policies (policy_name, policy_type, rules) VALUES
('default-write-confirmation', 'operation_type', 
 '{"operations": ["create", "update", "delete"], "require_confirmation": true}'::jsonb)
ON CONFLICT (policy_name) DO NOTHING;

-- =====================================================
-- Row Level Security (RLS) Policies
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE mcp_servers ENABLE ROW LEVEL SECURITY;
ALTER TABLE tools ENABLE ROW LEVEL SECURITY;
ALTER TABLE requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE routing ENABLE ROW LEVEL SECURITY;
ALTER TABLE executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE policies ENABLE ROW LEVEL SECURITY;

-- Allow all reads (for MVP - adjust based on your security requirements)
CREATE POLICY "Allow read access to all" ON mcp_servers FOR SELECT USING (true);
CREATE POLICY "Allow read access to all" ON tools FOR SELECT USING (true);
CREATE POLICY "Allow read access to all" ON requests FOR SELECT USING (true);
CREATE POLICY "Allow read access to all" ON routing FOR SELECT USING (true);
CREATE POLICY "Allow read access to all" ON executions FOR SELECT USING (true);
CREATE POLICY "Allow read access to all" ON health_checks FOR SELECT USING (true);
CREATE POLICY "Allow read access to all" ON users FOR SELECT USING (true);
CREATE POLICY "Allow read access to all" ON agents FOR SELECT USING (true);
CREATE POLICY "Allow read access to all" ON policies FOR SELECT USING (true);

-- Allow all writes (for MVP - adjust based on your security requirements)
CREATE POLICY "Allow write access to all" ON mcp_servers FOR ALL USING (true);
CREATE POLICY "Allow write access to all" ON tools FOR ALL USING (true);
CREATE POLICY "Allow write access to all" ON requests FOR ALL USING (true);
CREATE POLICY "Allow write access to all" ON routing FOR ALL USING (true);
CREATE POLICY "Allow write access to all" ON executions FOR ALL USING (true);
CREATE POLICY "Allow write access to all" ON health_checks FOR ALL USING (true);
CREATE POLICY "Allow write access to all" ON users FOR ALL USING (true);
CREATE POLICY "Allow write access to all" ON agents FOR ALL USING (true);
CREATE POLICY "Allow write access to all" ON policies FOR ALL USING (true);

-- =====================================================
-- Views for Common Queries
-- =====================================================

-- View: Active tools with server info
CREATE VIEW active_tools_view AS
SELECT 
    t.tool_id,
    t.name,
    t.description,
    t.input_schema,
    t.capabilities,
    t.status,
    t.health_status,
    t.last_discovered,
    s.server_id as mcp_server_id,
    s.server_name as mcp_server_name,
    s.transport,
    s.endpoint
FROM tools t
JOIN mcp_servers s ON t.server_id = s.server_id
WHERE t.status = 'active' AND s.is_active = true;

-- View: Request history with routing info
CREATE VIEW request_history_view AS
SELECT 
    r.request_id,
    r.raw_request,
    r.detected_operation,
    r.detected_domain,
    r.extracted_parameters,
    r.created_at,
    rtg.selected_tool_id,
    rtg.selected_server_id,
    rtg.routing_score,
    rtg.permission_granted,
    exe.execution_status,
    exe.execution_duration_ms
FROM requests r
LEFT JOIN routing rtg ON r.request_id = rtg.request_id
LEFT JOIN executions exe ON r.request_id = exe.request_id
ORDER BY r.created_at DESC;

-- View: Server health summary
CREATE VIEW server_health_view AS
SELECT 
    s.server_id,
    s.server_name,
    s.transport,
    s.endpoint,
    s.is_active,
    COUNT(h.id) as total_health_checks,
    SUM(CASE WHEN h.status = 'healthy' THEN 1 ELSE 0 END) as healthy_checks,
    SUM(CASE WHEN h.status = 'unhealthy' THEN 1 ELSE 0 END) as unhealthy_checks,
    MAX(h.checked_at) as last_check_at,
    h.status as current_status
FROM mcp_servers s
LEFT JOIN health_checks h ON s.server_id = h.server_id
GROUP BY s.server_id, s.server_name, s.transport, s.endpoint, s.is_active, h.status, h.checked_at
ORDER BY s.server_id;

-- =====================================================
-- Useful Queries
-- =====================================================

-- Get all active tools
-- SELECT * FROM active_tools_view;

-- Get request history for a specific user
-- SELECT * FROM request_history_view WHERE user_id = 'demo-user' LIMIT 10;

-- Get health status of all servers
-- SELECT * FROM server_health_view;

-- Get execution statistics
-- SELECT 
--     COUNT(*) as total_executions,
--     AVG(execution_duration_ms) as avg_duration,
--     SUM(CASE WHEN execution_status = 'success' THEN 1 ELSE 0 END) as successful,
--     SUM(CASE WHEN execution_status = 'failed' THEN 1 ELSE 0 END) as failed
-- FROM executions;

-- Get most used tools
-- SELECT 
--     tool_id,
--     COUNT(*) as usage_count
-- FROM executions
-- WHERE execution_status = 'success'
-- GROUP BY tool_id
-- ORDER BY usage_count DESC
-- LIMIT 10;

-- =====================================================
-- End of Schema
-- =====================================================
