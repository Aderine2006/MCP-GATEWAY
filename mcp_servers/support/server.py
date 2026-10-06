import asyncio
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Support MCP")
@mcp.tool()
def get_tickets(customer_id: str) -> str:
    return f"Tickets for {customer_id}: CRITICAL + OPEN"
if __name__ == "__main__":
    mcp.run()
