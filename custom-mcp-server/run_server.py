#!/usr/bin/env python3
"""
Startup script for the Custom MCP Server.
This script provides an easy way to start the MCP server with proper error handling.
"""

import sys
import os
import asyncio
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server import MCPServer


def setup_environment():
    """
    Set up the environment for running the MCP server.
    """
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


async def main():
    """
    Main function to start the MCP server.
    """
    try:
        print("Starting Custom MCP Server...")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Set up environment
        setup_environment()
        
        # Create and run the server
        server = MCPServer()
        await server.run()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        logging.error(f"Server startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())