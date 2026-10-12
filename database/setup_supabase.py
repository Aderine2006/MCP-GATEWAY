"""
Supabase Database Setup Script

This script helps you set up your Supabase database for the Enterprise MCP Gateway.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from supabase import create_client
except ImportError:
    print("Error: supabase package not installed.")
    print("Run: pip install supabase")
    sys.exit(1)


def setup_database():
    """Set up the Supabase database by running the schema SQL."""
    
    # Get environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_ANON_KEY environment variables must be set.")
        print("\nPlease set them in your .env file:")
        print("  SUPABASE_URL=your_supabase_project_url")
        print("  SUPABASE_ANON_KEY=your_supabase_anon_key")
        sys.exit(1)
    
    print(f"Connecting to Supabase at {supabase_url}")
    
    # Read the schema SQL file
    schema_path = Path(__file__).parent / "supabase_schema.sql"
    if not schema_path.exists():
        print(f"Error: Schema file not found at {schema_path}")
        sys.exit(1)
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    print("Schema SQL loaded successfully.")
    print("\n" + "=" * 60)
    print("IMPORTANT: Manual Setup Required")
    print("=" * 60)
    print("\nDue to Supabase's SQL execution limitations, please follow these steps:")
    print("\n1. Go to your Supabase project dashboard")
    print("2. Navigate to the SQL Editor")
    print("3. Copy and paste the contents of 'database/supabase_schema.sql'")
    print("4. Click 'Run' to execute the schema")
    print("\nAfter running the schema, your database will be ready!")
    print("=" * 60)
    
    # Test connection
    try:
        client = create_client(supabase_url, supabase_key)
        print("\nTesting database connection...")
        
        # Try to query a table (will fail if schema not run)
        result = client.table("mcp_servers").select("*").limit(1).execute()
        print("✓ Database connection successful!")
        print(f"✓ Found {len(result.data)} MCP servers in database")
        
    except Exception as e:
        print(f"\nConnection test failed: {e}")
        print("This is expected if you haven't run the schema yet.")
        print("Please run the schema SQL in your Supabase SQL Editor.")


def verify_setup():
    """Verify that the database has been set up correctly."""
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_ANON_KEY environment variables must be set.")
        sys.exit(1)
    
    try:
        client = create_client(supabase_url, supabase_key)
        
        print("Verifying database setup...")
        print("-" * 60)
        
        # Check each table
        tables = [
            "mcp_servers",
            "tools",
            "requests",
            "routing",
            "executions",
            "health_checks",
            "users",
            "agents",
            "policies"
        ]
        
        for table in tables:
            try:
                result = client.table(table).select("*").limit(1).execute()
                count = len(result.data)
                print(f"[OK] Table '{table}' exists ({count} records)")
            except Exception as e:
                print(f"[FAIL] Table '{table}' not found or inaccessible: {e}")
        
        print("-" * 60)
        print("Verification complete!")
        
    except Exception as e:
        print(f"Error during verification: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Supabase Database Setup")
    parser.add_argument("--verify", action="store_true", help="Verify database setup")
    args = parser.parse_args()
    
    if args.verify:
        verify_setup()
    else:
        setup_database()
