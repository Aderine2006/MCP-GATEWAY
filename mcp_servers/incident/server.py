from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Incident MCP Server")

class IncidentRequest(BaseModel):
    customer_id: str
    title: str
    severity: str

@app.get("/tools")
def list_tools():
    return {
        "tools": [
            {
                "name": "create_incident",
                "description": "Create a new incident",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string"},
                        "title": {"type": "string"},
                        "severity": {"type": "string"}
                    },
                    "required": ["customer_id", "title", "severity"]
                }
            }
        ]
    }

@app.post("/tools/create_incident")
def create_incident(request: IncidentRequest):
    return {
        "result": f"Incident created for {request.customer_id}: {request.title} [{request.severity}]",
        "incident_id": f"INC-{hash(request.title) % 10000}",
        "customer_id": request.customer_id,
        "title": request.title,
        "severity": request.severity,
        "status": "OPEN"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)
