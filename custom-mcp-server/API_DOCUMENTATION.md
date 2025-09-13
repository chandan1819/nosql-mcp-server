# MCP Server API Documentation

This document provides comprehensive API documentation for all MCP tools available in the custom MCP server.

## Table of Contents

- [Overview](#overview)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Available Tools](#available-tools)
  - [create_record](#create_record)
  - [read_records](#read_records)
  - [update_record](#update_record)
  - [delete_record](#delete_record)
  - [search_records](#search_records)
- [Collections](#collections)
- [Query Syntax](#query-syntax)
- [Code Examples](#code-examples)
- [Client Integration](#client-integration)

## Overview

The custom MCP server provides five main tools for database operations:
- **create_record**: Insert new records
- **read_records**: Fetch records with optional filtering
- **update_record**: Modify existing records
- **delete_record**: Remove records
- **search_records**: Advanced search with complex queries

All tools operate on three collections: `users`, `tasks`, and `products`.

## Response Format

All tools return responses in a consistent JSON format:

```json
{
  "success": true,
  "data": "...",
  "message": "Operation completed successfully",
  "count": 1,
  "error": null
}
```

### Response Fields

- **success** (boolean): Indicates if the operation was successful
- **data** (any): The actual result data (records, counts, etc.)
- **message** (string): Human-readable description of the result
- **count** (integer): Number of records affected by the operation
- **error** (string|null): Error message if success is false

## Error Handling

When an operation fails, the response format is:

```json
{
  "success": false,
  "data": null,
  "message": "Operation failed",
  "count": 0,
  "error": "Detailed error description"
}
```

### Common Error Types

- **Invalid Collection**: Collection name not in ['users', 'tasks', 'products']
- **Validation Error**: Data doesn't meet schema requirements
- **Not Found**: No records match the specified criteria
- **Database Error**: Internal database operation failed

## Available Tools

### create_record

Creates a new record in the specified collection.

#### Parameters

- **collection** (string, required): Target collection name
- **data** (object, required): Record data to insert

#### Example Request

```json
{
  "tool": "create_record",
  "arguments": {
    "collection": "users",
    "data": {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "role": "developer"
    }
  }
}
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "id": 4,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "role": "developer",
    "created_at": "2024-01-15T10:30:00"
  },
  "message": "Record created successfully in users collection",
  "count": 1,
  "error": null
}
```

#### Validation Rules

**Users Collection:**
- `name`: Required string, 1-100 characters
- `email`: Required string, valid email format
- `role`: Required string, one of ['admin', 'user', 'developer', 'manager']

**Tasks Collection:**
- `title`: Required string, 1-200 characters
- `description`: Optional string, max 1000 characters
- `assigned_to`: Required integer, must be valid user ID
- `status`: Required string, one of ['pending', 'in_progress', 'completed', 'cancelled']
- `priority`: Required string, one of ['low', 'medium', 'high', 'urgent']
- `due_date`: Optional string, ISO date format

**Products Collection:**
- `name`: Required string, 1-100 characters
- `description`: Optional string, max 500 characters
- `price`: Required number, must be positive
- `category`: Required string, 1-50 characters
- `in_stock`: Required boolean

### read_records

Retrieves records from the specified collection with optional filtering.

#### Parameters

- **collection** (string, required): Target collection name
- **filters** (object, optional): Filter criteria for records

#### Example Request (All Records)

```json
{
  "tool": "read_records",
  "arguments": {
    "collection": "users"
  }
}
```

#### Example Request (With Filters)

```json
{
  "tool": "read_records",
  "arguments": {
    "collection": "tasks",
    "filters": {
      "status": "in_progress",
      "priority": "high"
    }
  }
}
```

#### Example Response

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Admin User",
      "email": "admin@example.com",
      "role": "admin",
      "created_at": "2024-01-15T09:00:00"
    },
    {
      "id": 2,
      "name": "Regular User",
      "email": "user@example.com",
      "role": "user",
      "created_at": "2024-01-15T09:15:00"
    }
  ],
  "message": "Retrieved 2 records from users collection",
  "count": 2,
  "error": null
}
```

### update_record

Updates existing records that match the specified criteria.

#### Parameters

- **collection** (string, required): Target collection name
- **filters** (object, required): Criteria to match records for update
- **updates** (object, required): New data to apply to matching records

#### Example Request

```json
{
  "tool": "update_record",
  "arguments": {
    "collection": "tasks",
    "filters": {
      "id": 1
    },
    "updates": {
      "status": "completed",
      "priority": "low"
    }
  }
}
```

#### Example Response

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Complete project setup",
      "description": "Set up the initial project structure",
      "assigned_to": 1,
      "status": "completed",
      "priority": "low",
      "created_at": "2024-01-15T09:00:00",
      "due_date": "2024-01-20T17:00:00"
    }
  ],
  "message": "Updated 1 record(s) in tasks collection",
  "count": 1,
  "error": null
}
```

### delete_record

Removes records that match the specified criteria.

#### Parameters

- **collection** (string, required): Target collection name
- **filters** (object, required): Criteria to match records for deletion

#### Example Request

```json
{
  "tool": "delete_record",
  "arguments": {
    "collection": "tasks",
    "filters": {
      "status": "cancelled"
    }
  }
}
```

#### Example Response

```json
{
  "success": true,
  "data": {
    "deleted_ids": [3, 5]
  },
  "message": "Deleted 2 record(s) from tasks collection",
  "count": 2,
  "error": null
}
```

### search_records

Performs advanced search with complex query syntax and multiple filter conditions.

#### Parameters

- **collection** (string, required): Target collection name
- **query** (object, required): Advanced query with operators and conditions

#### Example Request

```json
{
  "tool": "search_records",
  "arguments": {
    "collection": "products",
    "query": {
      "and": [
        {"price": {"gte": 10.0}},
        {"price": {"lte": 100.0}},
        {"in_stock": true}
      ]
    }
  }
}
```

#### Example Response

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Laptop",
      "description": "High-performance laptop",
      "price": 99.99,
      "category": "electronics",
      "in_stock": true,
      "created_at": "2024-01-15T09:00:00"
    }
  ],
  "message": "Found 1 record(s) matching search criteria",
  "count": 1,
  "error": null
}
```

## Collections

### Users Collection Schema

```json
{
  "id": "integer (auto-generated)",
  "name": "string (required, 1-100 chars)",
  "email": "string (required, valid email)",
  "role": "string (required, enum: admin|user|developer|manager)",
  "created_at": "string (auto-generated, ISO datetime)"
}
```

### Tasks Collection Schema

```json
{
  "id": "integer (auto-generated)",
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "assigned_to": "integer (required, valid user ID)",
  "status": "string (required, enum: pending|in_progress|completed|cancelled)",
  "priority": "string (required, enum: low|medium|high|urgent)",
  "created_at": "string (auto-generated, ISO datetime)",
  "due_date": "string (optional, ISO datetime)"
}
```

### Products Collection Schema

```json
{
  "id": "integer (auto-generated)",
  "name": "string (required, 1-100 chars)",
  "description": "string (optional, max 500 chars)",
  "price": "number (required, positive)",
  "category": "string (required, 1-50 chars)",
  "in_stock": "boolean (required)",
  "created_at": "string (auto-generated, ISO datetime)"
}
```

## Query Syntax

### Simple Filters

For `read_records`, `update_record`, and `delete_record`, use simple key-value pairs:

```json
{
  "status": "completed",
  "priority": "high"
}
```

### Advanced Search Queries

For `search_records`, use advanced query operators:

#### Logical Operators

- **and**: All conditions must be true
- **or**: At least one condition must be true
- **not**: Condition must be false

```json
{
  "and": [
    {"status": "in_progress"},
    {"priority": "high"}
  ]
}
```

#### Comparison Operators

- **eq**: Equal to (default if no operator specified)
- **ne**: Not equal to
- **gt**: Greater than
- **gte**: Greater than or equal to
- **lt**: Less than
- **lte**: Less than or equal to
- **contains**: String contains substring
- **in**: Value is in array

```json
{
  "price": {"gte": 10.0, "lte": 100.0},
  "category": {"in": ["electronics", "books"]},
  "name": {"contains": "laptop"}
}
```

#### Complex Query Example

```json
{
  "or": [
    {
      "and": [
        {"status": "in_progress"},
        {"priority": {"in": ["high", "urgent"]}}
      ]
    },
    {
      "and": [
        {"status": "pending"},
        {"due_date": {"lt": "2024-01-20T00:00:00"}}
      ]
    }
  ]
}
```

## Code Examples

### Python Client Example

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def demonstrate_crud_operations():
    # Connect to MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["run_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # Create a new user
            create_result = await session.call_tool(
                "create_record",
                {
                    "collection": "users",
                    "data": {
                        "name": "API Test User",
                        "email": "test@example.com",
                        "role": "developer"
                    }
                }
            )
            print(f"Created user: {create_result.content}")
            
            # Read all users
            read_result = await session.call_tool(
                "read_records",
                {"collection": "users"}
            )
            print(f"All users: {read_result.content}")
            
            # Update user
            update_result = await session.call_tool(
                "update_record",
                {
                    "collection": "users",
                    "filters": {"email": "test@example.com"},
                    "updates": {"role": "senior_developer"}
                }
            )
            print(f"Updated user: {update_result.content}")
            
            # Search with advanced query
            search_result = await session.call_tool(
                "search_records",
                {
                    "collection": "users",
                    "query": {
                        "role": {"contains": "developer"}
                    }
                }
            )
            print(f"Developers: {search_result.content}")
            
            # Delete user
            delete_result = await session.call_tool(
                "delete_record",
                {
                    "collection": "users",
                    "filters": {"email": "test@example.com"}
                }
            )
            print(f"Deleted user: {delete_result.content}")

# Run the example
asyncio.run(demonstrate_crud_operations())
```

### JavaScript Client Example

```javascript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function demonstrateCrudOperations() {
    // Create transport and client
    const transport = new StdioClientTransport({
        command: "python",
        args: ["run_server.py"]
    });
    
    const client = new Client({
        name: "mcp-client",
        version: "1.0.0"
    }, {
        capabilities: {}
    });
    
    await client.connect(transport);
    
    try {
        // Create a new task
        const createResult = await client.request({
            method: "tools/call",
            params: {
                name: "create_record",
                arguments: {
                    collection: "tasks",
                    data: {
                        title: "API Integration Task",
                        description: "Integrate with external API",
                        assigned_to: 1,
                        status: "pending",
                        priority: "medium",
                        due_date: "2024-01-25T17:00:00"
                    }
                }
            }
        });
        console.log("Created task:", createResult);
        
        // Read tasks with filters
        const readResult = await client.request({
            method: "tools/call",
            params: {
                name: "read_records",
                arguments: {
                    collection: "tasks",
                    filters: {
                        status: "pending",
                        assigned_to: 1
                    }
                }
            }
        });
        console.log("Pending tasks for user 1:", readResult);
        
        // Advanced search
        const searchResult = await client.request({
            method: "tools/call",
            params: {
                name: "search_records",
                arguments: {
                    collection: "tasks",
                    query: {
                        and: [
                            { status: { ne: "completed" } },
                            { priority: { in: ["high", "urgent"] } }
                        ]
                    }
                }
            }
        });
        console.log("High priority incomplete tasks:", searchResult);
        
    } finally {
        await client.close();
    }
}

demonstrateCrudOperations().catch(console.error);
```

## Client Integration

### Setting Up MCP Client

1. **Install MCP SDK**: `pip install mcp` (Python) or `npm install @modelcontextprotocol/sdk` (JavaScript)

2. **Create Server Parameters**:
   ```python
   server_params = StdioServerParameters(
       command="python",
       args=["path/to/run_server.py"]
   )
   ```

3. **Establish Connection**:
   ```python
   async with stdio_client(server_params) as (read, write):
       async with ClientSession(read, write) as session:
           await session.initialize()
           # Use session to call tools
   ```

### Best Practices

1. **Error Handling**: Always check the `success` field in responses
2. **Connection Management**: Use async context managers for proper cleanup
3. **Data Validation**: Validate data before sending to avoid server errors
4. **Batch Operations**: Use filters for bulk updates/deletes when possible
5. **Query Optimization**: Use specific filters to reduce data transfer

### Extending the Server

To add new tools to the server:

1. **Define the tool** in `src/mcp_server.py`:
   ```python
   @server.tool()
   async def my_custom_tool(param1: str, param2: int) -> dict:
       """Custom tool description"""
       try:
           # Tool implementation
           result = perform_custom_operation(param1, param2)
           return format_success_response(result, "Custom operation completed")
       except Exception as e:
           return format_error_response(str(e))
   ```

2. **Add validation** and error handling
3. **Update documentation** with new tool details
4. **Add tests** for the new functionality

This API documentation provides comprehensive guidance for integrating with and extending the custom MCP server.