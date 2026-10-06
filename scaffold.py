import os

dirs = [
    "backend/app/api",
    "backend/app/auth",
    "backend/app/registry",
    "backend/app/router",
    "backend/app/mcp",
    "backend/app/credentials",
    "backend/app/rate_limit",
    "backend/app/cache",
    "backend/app/reliability",
    "backend/app/health",
    "backend/app/observability",
    "backend/app/transformation",
    "backend/app/database",
    "backend/app/schemas",
    "backend/tests",
    "mcp_servers/customer",
    "mcp_servers/support",
    "mcp_servers/incident",
    "database",
    "tests"
]

files = {
    "backend/app/main.py": "",
    "backend/app/config.py": "",
    "backend/app/dependencies.py": "",
    "backend/app/api/auth.py": "",
    "backend/app/api/tools.py": "",
    "backend/app/api/agents.py": "",
    "backend/app/api/requests.py": "",
    "backend/app/api/health.py": "",
    "backend/app/api/metrics.py": "",
    "backend/app/api/policies.py": "",
    "backend/app/auth/jwt.py": "",
    "backend/app/auth/rbac.py": "",
    "backend/app/auth/permissions.py": "",
    "backend/app/registry/models.py": "",
    "backend/app/registry/repository.py": "",
    "backend/app/registry/service.py": "",
    "backend/app/router/intent_router.py": "",
    "backend/app/router/capability_matcher.py": "",
    "backend/app/router/routing_policy.py": "",
    "backend/app/mcp/client.py": "",
    "backend/app/mcp/models.py": "",
    "backend/app/mcp/adapters.py": "",
    "backend/app/credentials/provider.py": "",
    "backend/app/credentials/mock_provider.py": "",
    "backend/app/rate_limit/limiter.py": "",
    "backend/app/cache/cache.py": "",
    "backend/app/reliability/retry.py": "",
    "backend/app/reliability/timeout.py": "",
    "backend/app/reliability/circuit_breaker.py": "",
    "backend/app/health/monitor.py": "",
    "backend/app/observability/logger.py": "",
    "backend/app/observability/metrics.py": "",
    "backend/app/observability/audit.py": "",
    "backend/app/transformation/transformer.py": "",
    "backend/app/database/models.py": "",
    "backend/app/database/session.py": "",
    "backend/app/database/seed.py": "",
    "backend/app/schemas/tools.py": "",
    "backend/app/schemas/agents.py": "",
    "backend/app/schemas/requests.py": "",
    "backend/app/schemas/responses.py": "",
    "backend/requirements.txt": "",
    "backend/Dockerfile": "",
    "mcp_servers/customer/server.py": "",
    "mcp_servers/support/server.py": "",
    "mcp_servers/incident/server.py": "",
    "database/seed.py": "",
    "docker-compose.yml": "",
    ".env.example": "",
    "README.md": "",
    "Makefile": ""
}

base_path = "."
for d in dirs:
    os.makedirs(os.path.join(base_path, d), exist_ok=True)

for f, content in files.items():
    with open(os.path.join(base_path, f), "w") as file:
        file.write(content)

print("Scaffolding completed.")
