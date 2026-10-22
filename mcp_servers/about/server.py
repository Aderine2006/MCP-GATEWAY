from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="About MCP Server")

class InfoRequest(BaseModel):
    topic: str

@app.get("/tools")
def list_tools():
    return {
        "tools": [
            {
                "name": "get_system_info",
                "description": "Get system information and details",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_version",
                "description": "Get version information for components",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "component": {"type": "string"}
                    },
                    "required": []
                }
            }
        ]
    }

@app.post("/tools/get_system_info")
def get_system_info():
    return {
        "result": "System Information",
        "system": "Enterprise MCP Gateway",
        "version": "1.0.0",
        "environment": "production",
        "uptime": "72h 15m 30s",
        "components": ["Gateway", "Tool Registry", "Intent Router", "3 MCP Servers"]
    }

@app.post("/tools/get_version")
def get_version(request: InfoRequest):
    component = request.topic or "system"
    return {
        "result": f"Version information for {component}",
        "component": component,
        "version": "1.0.0",
        "last_updated": "2024-01-01"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8004)
