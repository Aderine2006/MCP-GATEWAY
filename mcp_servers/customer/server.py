import asyncio
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Customer MCP")
@mcp.tool()
def get_customer(customer_id: str) -> str:
    return f"Customer {customer_id}: Arjun Kumar"
if __name__ == "__main__":
    mcp.run()
