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
        # 1. Start Customer MCP
        processes.append(run_process(
            "Customer MCP", 
            f"{sys.executable} server.py", 
            os.path.join(base_dir, "mcp_servers", "customer")
        ))
        
        # 2. Start Support MCP
        processes.append(run_process(
            "Support MCP", 
            f"{sys.executable} server.py", 
            os.path.join(base_dir, "mcp_servers", "support")
        ))
        
        # 3. Start Incident MCP
        processes.append(run_process(
            "Incident MCP", 
            f"{sys.executable} server.py", 
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
        print("- Frontend: http://localhost:3000")
        print("- Gateway API Docs: http://localhost:8000/docs")
        
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
