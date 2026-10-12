from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Customer MCP Server")

class CustomerRequest(BaseModel):
    customer_id: str

@app.get("/tools")
def list_tools():
    return {
        "tools": [
            {
                "name": "get_customer",
                "description": "Get customer details by ID",
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

@app.post("/tools/get_customer")
def get_customer(request: CustomerRequest):
    return {
        "result": f"Customer {request.customer_id}: Arjun Kumar",
        "customer_id": request.customer_id,
        "name": "Arjun Kumar",
        "email": "arjun.kumar@example.com",
        "status": "active"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
