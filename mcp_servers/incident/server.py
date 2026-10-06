import asyncio
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Incident MCP")
@mcp.tool()
def create_incident(customer_id: str, title: str, severity: str) -> str:
    return f"Incident created for {customer_id}: {title} [{severity}]"
if __name__ == "__main__":
    mcp.run()
