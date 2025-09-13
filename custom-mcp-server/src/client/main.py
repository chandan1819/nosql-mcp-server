#!/usr/bin/env python3
"""
Main entry point for the Custom MCP Client demonstration.
This script provides the primary client entry point for running demonstrations.
"""

import sys
import os
import asyncio
import logging

# Add the parent src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from client.demo_client import MCPDemonstrationClient


async def main():
    """Main entry point for the demonstration script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Server CRUD Operations Demonstration")
    parser.add_argument("--quick", action="store_true", help="Run quick test without user interaction")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    demo_client = MCPDemonstrationClient()
    
    try:
        if args.quick:
            success = await demo_client.run_quick_test()
            sys.exit(0 if success else 1)
        else:
            await demo_client.run_demonstration()
    
    except KeyboardInterrupt:
        print("\n\nDemonstration interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nDemonstration failed with error: {str(e)}")
        logging.error(f"Demonstration failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())