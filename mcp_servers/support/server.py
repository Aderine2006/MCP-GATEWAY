from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Support MCP Server")

class TicketRequest(BaseModel):
    customer_id: str

@app.get("/tools")
def list_tools():
    return {
        "tools": [
            {
                "name": "get_tickets",
                "description": "Get support tickets for a customer",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string"}
                    },
                    "required": ["customer_id"]
                }
            }
        ]
    }

@app.post("/tools/get_tickets")
def get_tickets(request: TicketRequest):
    return {
        "result": f"Tickets for {request.customer_id}: CRITICAL + OPEN",
        "customer_id": request.customer_id,
        "tickets": [
            {"id": "T-001", "status": "CRITICAL", "subject": "Server outage"},
            {"id": "T-002", "status": "OPEN", "subject": "Billing inquiry"}
        ]
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
