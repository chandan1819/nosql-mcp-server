#!/usr/bin/env python3
"""
Simple test to verify MCP server functionality
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_client import MCPClient

async def simple_test():
    """Run a simple connection test"""
    print("Testing MCP server connection...")
    
    server_command = [
        "python", 
        os.path.join(os.path.dirname(__file__), "run_server.py")
    ]
    
    client = MCPClient(server_command, max_retries=1, retry_delay=1.0)
    
    try:
        print("Attempting to connect...")
        async with client.connection():
            print("Connected successfully!")
            
            # Test connection
            connection_ok = await client.test_connection()
            if connection_ok:
                print("✓ Connection test passed")
                return True
            else:
                print("✗ Connection test failed")
                return False
                
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(simple_test())
    sys.exit(0 if result else 1)