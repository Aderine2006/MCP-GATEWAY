"""
Demonstration script for Enterprise MCP Gateway

This script demonstrates the end-to-end flow:
1. Discover tools from MCP servers
2. Route natural language requests to appropriate tools
3. Execute the selected tools

Usage:
    python demo.py
"""

import requests
import time
import json

API_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_json(data, indent=2):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent))


def health_check():
    """Check gateway health."""
    print_section("Health Check")
    response = requests.get(f"{API_URL}/api/health")
    print_json(response.json())
    return response.status_code == 200


def discover_tools():
    """Discover tools from MCP servers."""
    print_section("Tool Discovery")
    print("Discovering tools from MCP servers...")
    response = requests.post(f"{API_URL}/api/tools/discover")
    
    if response.status_code == 200:
        results = response.json()
        print(f"Discovery complete. Results from {len(results)} servers:")
        for result in results:
            status = "[OK]" if result["success"] else "[FAIL]"
            print(f"  {status} {result['server_id']}: {result['tools_discovered']} tools discovered")
            if not result["success"]:
                print(f"    Error: {result.get('error_message', 'Unknown')}")
        return True
    else:
        print(f"Discovery failed: {response.status_code}")
        return False


def list_tools():
    """List all registered tools."""
    print_section("Registered Tools")
    response = requests.get(f"{API_URL}/api/tools")
    
    if response.status_code == 200:
        data = response.json()
        tools = data.get("tools", [])
        print(f"Total tools registered: {data['total']}\n")
        
        for tool in tools:
            print(f"  • {tool['name']}")
            print(f"    Description: {tool['description']}")
            print(f"    Server: {tool['server_name']} ({tool['server_id']})")
            print(f"    Status: {tool['status']} | Health: {tool['health_status']}")
            print(f"    Capabilities: {', '.join(tool['capabilities'])}")
            print()
        return tools
    else:
        print(f"Failed to list tools: {response.status_code}")
        return []


def route_request(request_text, auto_execute=False, force_execute=False):
    """Route a natural language request."""
    print_section(f"Routing Request: '{request_text}'")
    
    payload = {
        "request": request_text,
        "auto_execute": auto_execute,
        "force_execute": force_execute
    }
    
    print(f"Parameters: auto_execute={auto_execute}, force_execute={force_execute}")
    print()
    
    response = requests.post(
        f"{API_URL}/api/route",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"Request ID: {result['request_id']}")
        print(f"Success: {result['success']}")
        print(f"\nDetected Intent:")
        print(f"  Operation: {result['intent']['operation']}")
        print(f"  Domain: {result['intent']['domain']}")
        print(f"  Parameters: {result['intent']['parameters']}")
        
        if result.get('selected_tool'):
            print(f"\nSelected Tool:")
            print(f"  Name: {result['selected_tool']['name']}")
            print(f"  Server: {result['selected_tool']['server_name']}")
        
        if result.get('routing_explanation'):
            print(f"\nRouting Explanation: {result['routing_explanation']}")
        
        if result.get('execution_result'):
            print(f"\nExecution Result:")
            print_json(result['execution_result'])
        
        if result.get('error_message'):
            print(f"\nError: {result['error_message']}")
        
        if result.get('execution_duration_ms'):
            print(f"\nExecution Duration: {result['execution_duration_ms']:.2f}ms")
        
        return result
    else:
        print(f"Routing failed: {response.status_code}")
        print(response.text)
        return None


def main():
    """Run the demonstration."""
    print("""
============================================================
          Enterprise MCP Gateway - Demonstration
============================================================
    """)
    
    # Check if gateway is running
    print("Checking if gateway is running...")
    try:
        if not health_check():
            print("\n[X] Gateway is not running. Please start the services first:")
            print("   python run_all.py")
            return
    except requests.exceptions.ConnectionError:
        print("\n[X] Cannot connect to gateway. Please start the services first:")
        print("   python run_all.py")
        return
    
    print("[OK] Gateway is running")
    
    # Discover tools
    time.sleep(1)
    if not discover_tools():
        print("\n[!] Tool discovery failed. Continuing with existing tools...")
    
    # List tools
    time.sleep(1)
    tools = list_tools()
    
    if not tools:
        print("\n[!] No tools available. Please ensure MCP servers are running.")
        return
    
    # Example requests
    example_requests = [
        ("Find the details of customer 1024", True, False),
        ("Search for open support tickets for customer 1024", True, False),
        ("Create incident for customer 1024 with title server outage and severity critical", False, True),
    ]
    
    print("\n" + "=" * 60)
    print("  Example Requests")
    print("=" * 60)
    
    for i, (request, auto_exec, force_exec) in enumerate(example_requests, 1):
        print(f"\n{i}. {request}")
        time.sleep(1)
        result = route_request(request, auto_exec, force_exec)
        
        if result and not result['success'] and not result.get('execution_result'):
            # Try with auto_execute for read operations
            if result['intent']['operation'] == 'read':
                print("\n  Retrying with auto_execute=True...")
                time.sleep(1)
                route_request(request, True, False)
    
    print("\n" + "=" * 60)
    print("  Demonstration Complete")
    print("=" * 60)
    print("\nTry the interactive frontend at: http://localhost:3000")
    print("API documentation available at: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
