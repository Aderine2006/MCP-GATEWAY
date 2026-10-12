import subprocess
import sys
import time
import os

def run_process(name, cmd, cwd):
    print(f"Starting {name}...")
    return subprocess.Popen(
        cmd,
        cwd=cwd,
        shell=True,
    )

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    processes = []
    try:
        # 1. Start Customer MCP (HTTP)
        processes.append(run_process(
            "Customer MCP", 
            f"{sys.executable} -m uvicorn server:app --host 127.0.0.1 --port 8001", 
            os.path.join(base_dir, "mcp_servers", "customer")
        ))
        
        # 2. Start Support MCP (HTTP)
        processes.append(run_process(
            "Support MCP", 
            f"{sys.executable} -m uvicorn server:app --host 127.0.0.1 --port 8002", 
            os.path.join(base_dir, "mcp_servers", "support")
        ))
        
        # 3. Start Incident MCP (HTTP)
        processes.append(run_process(
            "Incident MCP", 
            f"{sys.executable} -m uvicorn server:app --host 127.0.0.1 --port 8003", 
            os.path.join(base_dir, "mcp_servers", "incident")
        ))
        
        # 4. Start Gateway (FastAPI)
        processes.append(run_process(
            "Gateway API", 
            f"{sys.executable} -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload", 
            os.path.join(base_dir, "backend")
        ))
        
        # 5. Start Frontend (Next.js)
        processes.append(run_process(
            "Frontend Next.js", 
            "npm run dev", 
            os.path.join(base_dir, "frontend")
        ))
        
        print("\nAll services started! Press Ctrl+C to stop them all.\n")
        print("=" * 60)
        print("Enterprise MCP Gateway - All Services Running")
        print("=" * 60)
        print("- Frontend: http://localhost:3000")
        print("- Gateway API: http://localhost:8000")
        print("- API Docs: http://localhost:8000/docs")
        print("- Health Check: http://localhost:8000/api/health")
        print("- Customer MCP: http://localhost:8001")
        print("- Support MCP: http://localhost:8002")
        print("- Incident MCP: http://localhost:8003")
        print("=" * 60)
        print("\nExample requests to try:")
        print('1. "Find the details of customer 1024"')
        print('2. "Search for open support tickets"')
        print('3. "Create an incident for a server outage"')
        print("=" * 60)
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping all services...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait()
        print("All services stopped.")

if __name__ == "__main__":
    main()
