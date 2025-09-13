# MCP Client Demonstration

This directory contains a comprehensive demonstration client for the custom MCP server that showcases all CRUD operations.

## Files

- `demo_client.py` - Main demonstration script with interactive interface
- `src/mcp_client.py` - MCP client library with connection management and CRUD methods
- `tests/test_mcp_client.py` - Unit tests for the MCP client
- `tests/test_demo_client.py` - Unit tests for the demonstration script

## Running the Demonstration

### Interactive Mode (Recommended)

Run the full interactive demonstration:

```bash
python demo_client.py
```

This will:
1. Connect to the MCP server
2. Walk you through each CRUD operation with explanations
3. Allow you to skip operations if desired
4. Show detailed results and before/after comparisons
5. Provide clear progress indicators and summaries

### Quick Test Mode

Run a non-interactive test of all operations:

```bash
python demo_client.py --quick
```

This will:
- Test all CRUD operations automatically
- Show pass/fail status for each operation
- Exit with code 0 on success, 1 on failure
- Perfect for automated testing

### Verbose Mode

Enable detailed logging:

```bash
python demo_client.py --verbose
```

## What the Demonstration Shows

### 1. INSERT Operations
- Creates sample users, tasks, and products
- Shows successful record creation with generated IDs
- Demonstrates error handling for invalid data

### 2. FETCH Operations
- Retrieves all records from each collection
- Displays record counts and sample data
- Shows filtering capabilities

### 3. UPDATE Operations
- Modifies existing records based on criteria
- Shows before/after comparisons
- Demonstrates bulk updates

### 4. DELETE Operations
- Removes records matching specific criteria
- Shows confirmation of what will be deleted
- Verifies deletion was successful

## Sample Output

```
================================================================================
                    MCP Server CRUD Operations Demonstration                    
================================================================================

This demonstration will showcase all CRUD operations of the custom MCP server:
• INSERT: Create new records in all collections
• FETCH:  Retrieve and display all records
• UPDATE: Modify existing records with before/after comparison
• DELETE: Remove records with confirmation

Ready to start the demonstration? (or 's' to skip): 

------------------------------------------------------------
 Establishing Connection to MCP Server 
------------------------------------------------------------
[10:30:15] → Connecting to MCP server...
[10:30:16] ✓ Successfully connected to MCP server!
[10:30:16] ✓ Connection test passed

Proceed with INSERT operations? (or 's' to skip): 

------------------------------------------------------------
 INSERT Operations - Creating New Records 
------------------------------------------------------------
[10:30:20] → Starting INSERT operations...
[10:30:20] ℹ Creating user 1: Demo User 1
[10:30:21] ✓ User created successfully: ID 4
[10:30:21] ℹ Creating user 2: Demo User 2
[10:30:21] ✓ User created successfully: ID 5
...
```

## Error Handling

The demonstration client includes comprehensive error handling:

- **Connection Failures**: Automatic retry with exponential backoff
- **Server Errors**: Graceful handling with detailed error messages
- **User Interruption**: Clean shutdown on Ctrl+C
- **Invalid Responses**: JSON parsing error handling

## Logging

All operations are logged to `demo_client.log` with timestamps and detailed information for debugging purposes.

## Requirements

- Python 3.7+
- MCP Python SDK (`mcp>=1.0.0`)
- Running MCP server (started with `python run_server.py`)

## Testing

Run the client tests:

```bash
python -m pytest tests/test_mcp_client.py -v
python -m pytest tests/test_demo_client.py -v
```

## Extending the Client

The `MCPClient` class in `src/mcp_client.py` can be extended with additional methods:

```python
from mcp_client import MCPClient

# Create client instance
client = MCPClient(["python", "run_server.py"])

# Use in async context
async with client.connection():
    # Call individual CRUD methods
    insert_results = await client.demonstrate_insert_operations()
    fetch_results = await client.demonstrate_fetch_operations()
    
    # Or call tools directly
    response = await client.call_tool("create_record", {
        "collection": "users",
        "data": {"name": "New User", "email": "user@example.com"}
    })
```

This demonstration client serves as both a testing tool and an example of how to integrate with the custom MCP server.