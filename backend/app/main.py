from fastapi import FastAPI
app = FastAPI(title="Enterprise MCP Gateway")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Gateway is running"}
