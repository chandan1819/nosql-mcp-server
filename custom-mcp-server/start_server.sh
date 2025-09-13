#!/bin/bash

echo "Starting Custom MCP Server..."
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -f "venv/bin/python" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run setup.py first to create the environment."
    exit 1
fi

# Activate virtual environment and start server
venv/bin/python run_server.py

echo ""
echo "Server stopped."