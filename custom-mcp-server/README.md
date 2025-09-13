# NoSQL MCP Server

[![Tests](https://github.com/chandan1819/nosql-mcp-server/workflows/Tests/badge.svg)](https://github.com/chandan1819/nosql-mcp-server/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/chandan1819/nosql-mcp-server.svg)](https://github.com/chandan1819/nosql-mcp-server/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/chandan1819/nosql-mcp-server.svg)](https://github.com/chandan1819/nosql-mcp-server/network)

A Model Context Protocol (MCP) server implementation with NoSQL database integration using TinyDB. This server provides CRUD operations through MCP tools and includes a comprehensive demonstration client.

> 🚀 **Perfect for**: AI assistants, chatbots, data analysis, rapid prototyping, and educational projects

## 🚀 Quick Start (5 Minutes)

**New to this project? Start here!**

1. **Automated Setup**
   ```bash
   python setup.py
   ```
   This creates a virtual environment, installs dependencies, and initializes the database.

2. **Start the Server**
   ```bash
   python run_server.py
   ```
   Or use startup scripts: `start_server.bat` (Windows) or `./start_server.sh` (Linux/Mac)

3. **Run the Demo (in another terminal)**
   ```bash
   python demo_client.py
   ```
   Or use startup scripts: `start_client.bat` (Windows) or `./start_client.sh` (Linux/Mac)

4. **Quick Test (no interaction)**
   ```bash
   python demo_client.py --quick
   ```

**That's it!** The demo will show you INSERT, FETCH, UPDATE, and DELETE operations.

## Table of Contents

- [🚀 Quick Start](#-quick-start-5-minutes)
- [Prerequisites](#prerequisites)
- [Manual Installation](#manual-installation)
- [Database Setup](#database-setup)
- [Server Configuration](#server-configuration)
- [Running the Server](#running-the-server)
- [Running the Demo Client](#running-the-demo-client)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Package Distribution](#package-distribution)

## Prerequisites

Before installing and running the Custom MCP Server, ensure you have the following prerequisites:

### System Requirements

- **Python**: Version 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 512MB RAM available
- **Disk Space**: At least 100MB free space

### Python Installation

If you don't have Python installed:

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer and check "Add Python to PATH"
3. Verify installation: `python --version`

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python

# Or download from python.org
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install python3 python3-pip
```

### Verify Python Installation

```bash
python --version  # Should show Python 3.8+
pip --version     # Should show pip version
```

## Manual Installation

**Note: For quick setup, use `python setup.py` instead of these manual steps.**

### Step 1: Clone or Download the Project

If you have the project files, navigate to the `custom-mcp-server` directory:

```bash
cd custom-mcp-server
```

### Step 2: Create a Virtual Environment (Recommended)

Creating a virtual environment isolates the project dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

You should see `(venv)` in your command prompt when the virtual environment is active.

### Step 3: Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- `mcp>=1.0.0` - Model Context Protocol SDK
- `tinydb>=4.8.0` - Lightweight NoSQL database
- `pytest>=7.0.0` - Testing framework (for development)
- `pytest-asyncio>=0.21.0` - Async testing support

### Step 4: Verify Installation

Check that all dependencies are installed correctly:

```bash
pip list
```

You should see all the packages listed above.

## Database Setup

The Custom MCP Server uses TinyDB, a lightweight NoSQL database that stores data in JSON files.

### Automatic Database Initialization

The database will be automatically initialized when you first run the server. However, you can manually initialize it:

```bash
python src/database/init_db.py
```

This will:
1. Create the `data/` directory if it doesn't exist
2. Create `data/mcp_server.json` database file
3. Populate the database with sample data:
   - **Users**: 3 sample user records
   - **Tasks**: 5 sample task records with user assignments
   - **Products**: 4 sample product records with pricing

### Database File Location

The database file is stored at:
```
custom-mcp-server/data/mcp_server.json
```

### Sample Data Overview

After initialization, your database will contain:

**Users Collection:**
- Admin user, regular users with different roles
- Each user has: id, name, email, role, created_at

**Tasks Collection:**
- Various tasks assigned to different users
- Each task has: id, title, description, assigned_to, status, priority, created_at, due_date

**Products Collection:**
- Sample products with different categories
- Each product has: id, name, description, price, category, in_stock, created_at

### Manual Database Reset

To reset the database to its initial state:

```bash
# Remove existing database
rm data/mcp_server.json  # On Windows: del data\mcp_server.json

# Reinitialize
python src/database/init_db.py
```

## Server Configuration

### Default Configuration

The server runs with these default settings:
- **Database**: `data/mcp_server.json`
- **Logging Level**: INFO
- **Connection**: Stdio transport (standard for MCP)

### Environment Variables

You can customize the server behavior using environment variables:

```bash
# Set custom database path
export MCP_DB_PATH="custom/path/to/database.json"

# Set logging level (DEBUG, INFO, WARNING, ERROR)
export MCP_LOG_LEVEL="DEBUG"

# On Windows, use 'set' instead of 'export':
set MCP_DB_PATH=custom\path\to\database.json
set MCP_LOG_LEVEL=DEBUG
```

### Configuration Files

The server uses `pyproject.toml` for project configuration. You can modify settings there if needed.

## Running the Server

### Start the MCP Server

To start the server, run:

```bash
python run_server.py
```

You should see output similar to:
```
Starting Custom MCP Server...
Press Ctrl+C to stop the server
--------------------------------------------------
2024-01-15 10:30:00,123 - INFO - Database initialized successfully
2024-01-15 10:30:00,124 - INFO - MCP Server started successfully
2024-01-15 10:30:00,125 - INFO - Server ready to accept connections
```

### Server Startup Process

When the server starts, it:
1. Sets up the environment and creates necessary directories
2. Initializes the database (if not already done)
3. Loads sample data (if database is empty)
4. Starts the MCP server with all tools registered
5. Waits for client connections

### Stopping the Server

To stop the server:
- Press `Ctrl+C` in the terminal
- The server will shut down gracefully

### Server Logs

Server logs are displayed in the console and can be redirected to a file:

```bash
# Save logs to file
python run_server.py > server.log 2>&1

# View logs in real-time
python run_server.py | tee server.log
```

## Running the Demo Client

The demonstration client showcases all CRUD operations supported by the server.

### Interactive Demonstration

Run the full interactive demonstration:

```bash
python demo_client.py
```

This will:
1. Connect to the MCP server
2. Guide you through each operation type:
   - **INSERT**: Create new records
   - **FETCH**: Retrieve all records
   - **UPDATE**: Modify existing records
   - **DELETE**: Remove records
3. Show detailed results and allow you to skip operations
4. Provide before/after comparisons for updates

### Quick Test Mode

For automated testing without user interaction:

```bash
python demo_client.py --quick
```

This runs all operations automatically and reports success/failure.

### Verbose Mode

For detailed debugging information:

```bash
python demo_client.py --verbose
```

### Demo Client Logs

The demo client creates a log file `demo_client.log` with detailed operation logs.

## Project Structure

```
custom-mcp-server/
├── src/                          # Source code
│   ├── database/                 # Database management
│   │   ├── manager.py           # DatabaseManager class
│   │   ├── init_db.py           # Database initialization
│   │   └── query_parser.py      # Query parsing utilities
│   ├── mcp_server.py            # Main MCP server implementation
│   ├── mcp_client.py            # MCP client for demonstrations
│   └── response_formatter.py    # Response formatting utilities
├── tests/                        # Test suite
│   ├── test_database_manager.py # Database tests
│   ├── test_mcp_server.py       # Server tests
│   ├── test_mcp_client.py       # Client tests
│   └── ...                      # Additional test files
├── data/                         # Database files
│   └── mcp_server.json          # TinyDB database file
├── run_server.py                # Server startup script
├── demo_client.py               # Demonstration client
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "ModuleNotFoundError: No module named 'mcp'"

**Problem**: MCP SDK not installed or virtual environment not activated.

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. "Permission denied" when creating database

**Problem**: Insufficient permissions to create files in the data directory.

**Solution**:
```bash
# Create data directory manually
mkdir data

# On Linux/macOS, check permissions
chmod 755 data
```

#### 3. "Server connection failed" in demo client

**Problem**: MCP server not running or connection issues.

**Solution**:
1. Ensure the server is running: `python run_server.py`
2. Check for error messages in server output
3. Verify no other process is using the same resources
4. Try restarting both server and client

#### 4. "Database file corrupted" error

**Problem**: TinyDB database file is corrupted or invalid.

**Solution**:
```bash
# Backup existing database (if needed)
cp data/mcp_server.json data/mcp_server.json.backup

# Remove corrupted database
rm data/mcp_server.json

# Reinitialize
python src/database/init_db.py
```

#### 5. Python version compatibility issues

**Problem**: Using Python version < 3.8.

**Solution**:
- Upgrade Python to version 3.8 or higher
- Check version: `python --version`

#### 6. "Port already in use" or similar connection errors

**Problem**: Another process is interfering with MCP communication.

**Solution**:
1. Close other MCP servers or clients
2. Restart your terminal/command prompt
3. Check for background processes

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Look at server output and `demo_client.log`
2. **Verify setup**: Ensure all installation steps were completed
3. **Test components**: Run individual components to isolate issues
4. **Check dependencies**: Verify all required packages are installed

### Debug Mode

For detailed debugging information:

```bash
# Set debug logging
export MCP_LOG_LEVEL=DEBUG  # Windows: set MCP_LOG_LEVEL=DEBUG

# Run server with debug output
python run_server.py

# Run client with verbose output
python demo_client.py --verbose
```

## Development

### Running Tests

To run the test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_database_manager.py

# Run with coverage
pytest --cov=src
```

### Code Structure

- **DatabaseManager**: Handles all database operations
- **MCPServer**: Implements MCP protocol and tools
- **MCPClient**: Demonstration client for testing
- **Response Formatter**: Standardizes API responses

### Adding New Features

1. Add new tools to `src/mcp_server.py`
2. Update database schema in `src/database/manager.py`
3. Add tests in `tests/`
4. Update documentation

### Contributing

1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Test with both interactive and quick modes

## Package Distribution

### Creating a Distribution Package

To create a complete, distributable package:

```bash
python package.py
```

This creates:
- `dist/custom-mcp-server-v1.0.0.zip` - Complete package with all files
- `dist/custom-mcp-server-v1.0.0.tar.gz` - TAR.GZ version (Linux/Mac)

### Package Contents

The distribution package includes:
- Complete source code
- Setup and startup scripts
- Documentation and guides
- Test suite
- Configuration files
- Quick start guide

### Sharing the Package

1. Share the ZIP file with users
2. Users extract and run: `python setup.py`
3. Users follow the included `QUICK_START.md` guide

### Entry Points

The package provides multiple entry points:

**Main Entry Points:**
- `run_server.py` - Start the MCP server
- `demo_client.py` - Run the demonstration client
- `setup.py` - Automated environment setup

**Alternative Entry Points:**
- `src/server/main.py` - Direct server entry point
- `src/client/main.py` - Direct client entry point

**Startup Scripts:**
- `start_server.bat` / `start_server.sh` - Server startup
- `start_client.bat` / `start_client.sh` - Client startup