#!/bin/bash

echo "Starting MCP Client Demonstration..."
echo ""
echo "This will demonstrate all CRUD operations"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -f "venv/bin/python" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run setup.py first to create the environment."
    exit 1
fi

# Activate virtual environment and start client
venv/bin/python demo_client.py

echo ""
echo "Demonstration completed."