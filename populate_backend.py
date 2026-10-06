import os

files = {
    "backend/requirements.txt": """fastapi
uvicorn
pydantic
sqlalchemy
pyjwt
httpx
pytest
mcp
""",
    "backend/Dockerfile": """FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "backend/app/main.py": """from fastapi import FastAPI
app = FastAPI(title="Enterprise MCP Gateway")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Gateway is running"}
""",
    "mcp_servers/customer/Dockerfile": """FROM python:3.12-slim
WORKDIR /app
RUN pip install mcp
COPY mcp_servers/customer/server.py .
CMD ["python", "server.py"]
""",
    "mcp_servers/customer/server.py": """import asyncio
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Customer MCP")
@mcp.tool()
def get_customer(customer_id: str) -> str:
    return f"Customer {customer_id}: Arjun Kumar"
if __name__ == "__main__":
    mcp.run()
""",
    "mcp_servers/support/Dockerfile": """FROM python:3.12-slim
WORKDIR /app
RUN pip install mcp
COPY mcp_servers/support/server.py .
CMD ["python", "server.py"]
""",
    "mcp_servers/support/server.py": """import asyncio
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Support MCP")
@mcp.tool()
def get_tickets(customer_id: str) -> str:
    return f"Tickets for {customer_id}: CRITICAL + OPEN"
if __name__ == "__main__":
    mcp.run()
""",
    "mcp_servers/incident/Dockerfile": """FROM python:3.12-slim
WORKDIR /app
RUN pip install mcp
COPY mcp_servers/incident/server.py .
CMD ["python", "server.py"]
""",
    "mcp_servers/incident/server.py": """import asyncio
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Incident MCP")
@mcp.tool()
def create_incident(customer_id: str, title: str, severity: str) -> str:
    return f"Incident created for {customer_id}: {title} [{severity}]"
if __name__ == "__main__":
    mcp.run()
"""
}

base_path = "d:/MCP GATEWAY/enterprise-mcp-gateway"
for f, content in files.items():
    path = os.path.join(base_path, f)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as file:
        file.write(content)

print("Backend boilerplate generated.")
