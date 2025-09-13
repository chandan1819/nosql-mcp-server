"""
MCP Client for demonstrating custom MCP server functionality.
Provides connection management and CRUD operation demonstrations.
"""

import asyncio
import json
import logging
import sys
import time
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


class MCPClient:
    """
    MCP client class that connects to the custom MCP server and demonstrates
    all CRUD operations with proper error handling and retry logic.
    """
    
    def __init__(self, server_command: List[str], max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize the MCP client with connection parameters.
        
        Args:
            server_command: Command to start the MCP server
            max_retries: Maximum number of connection retry attempts
            retry_delay: Delay between retry attempts in seconds
        """
        self.server_command = server_command
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session: Optional[ClientSession] = None
        self.logger = logging.getLogger(__name__)
        
        # Configure logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """
        Configure logging for the MCP client.
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger.info("Logging configured for MCP client")
    
    async def connect(self) -> bool:
        """
        Establish connection to the MCP server with retry logic.
        
        Returns:
            True if connection successful, False otherwise
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"Attempting to connect to MCP server (attempt {attempt}/{self.max_retries})")
                
                # Create server parameters
                server_params = StdioServerParameters(
                    command=self.server_command[0],
                    args=self.server_command[1:] if len(self.server_command) > 1 else []
                )
                
                # Create stdio client and session
                stdio_transport = stdio_client(server_params)
                self.session = await stdio_transport.__aenter__()
                
                # Initialize the session
                await self.session.initialize()
                
                self.logger.info("Successfully connected to MCP server")
                return True
                
            except Exception as e:
                self.logger.warning(f"Connection attempt {attempt} failed: {str(e)}")
                
                if attempt < self.max_retries:
                    self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    self.logger.error("All connection attempts failed")
                    return False
        
        return False
    
    async def disconnect(self) -> None:
        """
        Gracefully disconnect from the MCP server.
        """
        try:
            if self.session:
                # Note: The actual cleanup will be handled by the context manager
                # when we exit the stdio_client context
                self.session = None
                self.logger.info("Disconnected from MCP server")
        except Exception as e:
            self.logger.warning(f"Error during disconnect: {str(e)}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server and return the parsed response.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments to pass to the tool
            
        Returns:
            Parsed response from the server
            
        Raises:
            ConnectionError: If not connected to server
            Exception: If tool call fails
        """
        if not self.session:
            raise ConnectionError("Not connected to MCP server")
        
        try:
            self.logger.debug(f"Calling tool '{tool_name}' with arguments: {arguments}")
            
            # Call the tool
            result = await self.session.call_tool(tool_name, arguments)
            
            # Parse the response
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                parsed_response = json.loads(response_text)
                
                self.logger.debug(f"Tool '{tool_name}' response: {parsed_response}")
                return parsed_response
            else:
                raise Exception("Empty response from server")
                
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse server response: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Tool call '{tool_name}' failed: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    async def test_connection(self) -> bool:
        """
        Test the connection by listing available tools.
        
        Returns:
            True if connection test successful, False otherwise
        """
        try:
            if not self.session:
                return False
            
            # List available tools to test connection
            tools = await self.session.list_tools()
            
            self.logger.info(f"Connection test successful. Available tools: {[tool.name for tool in tools.tools]}")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
    
    @asynccontextmanager
    async def connection(self):
        """
        Async context manager for managing client connection lifecycle.
        """
        server_params = StdioServerParameters(
            command=self.server_command[0],
            args=self.server_command[1:] if len(self.server_command) > 1 else []
        )
        
        async with stdio_client(server_params) as (read, write):
            self.session = ClientSession(read, write)
            await self.session.initialize()
            
            try:
                yield self
            finally:
                await self.disconnect()
    
    # CRUD Demonstration Methods
    
    async def demonstrate_insert_operations(self) -> Dict[str, Any]:
        """
        Demonstrate INSERT operations on all collections.
        Creates new records in users, tasks, and products collections.
        
        Returns:
            Dictionary containing results of all insert operations
        """
        results = {
            "users": [],
            "tasks": [],
            "products": [],
            "summary": {"total_created": 0, "errors": []}
        }
        
        self.logger.info("=== Demonstrating INSERT Operations ===")
        
        # Sample data for demonstrations
        sample_users = [
            {
                "name": "Demo User 1",
                "email": "demo1@example.com",
                "role": "developer"
            },
            {
                "name": "Demo User 2", 
                "email": "demo2@example.com",
                "role": "manager"
            }
        ]
        
        sample_tasks = [
            {
                "title": "Demo Task 1",
                "description": "This is a demonstration task",
                "assigned_to": 1,
                "status": "pending",
                "priority": "medium",
                "due_date": "2024-12-31"
            },
            {
                "title": "Demo Task 2",
                "description": "Another demonstration task",
                "assigned_to": 2,
                "status": "in_progress", 
                "priority": "high",
                "due_date": "2024-11-30"
            }
        ]
        
        sample_products = [
            {
                "name": "Demo Product A",
                "description": "A sample product for demonstration",
                "price": 29.99,
                "category": "electronics",
                "in_stock": True
            },
            {
                "name": "Demo Product B",
                "description": "Another sample product",
                "price": 49.99,
                "category": "accessories",
                "in_stock": False
            }
        ]
        
        # Insert users
        for i, user_data in enumerate(sample_users, 1):
            try:
                self.logger.info(f"Creating user {i}: {user_data['name']}")
                response = await self.call_tool("create_record", {
                    "collection": "users",
                    "data": user_data
                })
                results["users"].append(response)
                
                if response.get("success"):
                    results["summary"]["total_created"] += 1
                    self.logger.info(f"✓ User created successfully: ID {response.get('data', {}).get('id', 'unknown')}")
                else:
                    error_msg = f"Failed to create user {i}: {response.get('error', 'Unknown error')}"
                    results["summary"]["errors"].append(error_msg)
                    self.logger.error(error_msg)
                    
            except Exception as e:
                error_msg = f"Exception creating user {i}: {str(e)}"
                results["summary"]["errors"].append(error_msg)
                self.logger.error(error_msg)
        
        # Insert tasks
        for i, task_data in enumerate(sample_tasks, 1):
            try:
                self.logger.info(f"Creating task {i}: {task_data['title']}")
                response = await self.call_tool("create_record", {
                    "collection": "tasks",
                    "data": task_data
                })
                results["tasks"].append(response)
                
                if response.get("success"):
                    results["summary"]["total_created"] += 1
                    self.logger.info(f"✓ Task created successfully: ID {response.get('data', {}).get('id', 'unknown')}")
                else:
                    error_msg = f"Failed to create task {i}: {response.get('error', 'Unknown error')}"
                    results["summary"]["errors"].append(error_msg)
                    self.logger.error(error_msg)
                    
            except Exception as e:
                error_msg = f"Exception creating task {i}: {str(e)}"
                results["summary"]["errors"].append(error_msg)
                self.logger.error(error_msg)
        
        # Insert products
        for i, product_data in enumerate(sample_products, 1):
            try:
                self.logger.info(f"Creating product {i}: {product_data['name']}")
                response = await self.call_tool("create_record", {
                    "collection": "products",
                    "data": product_data
                })
                results["products"].append(response)
                
                if response.get("success"):
                    results["summary"]["total_created"] += 1
                    self.logger.info(f"✓ Product created successfully: ID {response.get('data', {}).get('id', 'unknown')}")
                else:
                    error_msg = f"Failed to create product {i}: {response.get('error', 'Unknown error')}"
                    results["summary"]["errors"].append(error_msg)
                    self.logger.error(error_msg)
                    
            except Exception as e:
                error_msg = f"Exception creating product {i}: {str(e)}"
                results["summary"]["errors"].append(error_msg)
                self.logger.error(error_msg)
        
        self.logger.info(f"INSERT operations completed. Created {results['summary']['total_created']} records total.")
        if results["summary"]["errors"]:
            self.logger.warning(f"Encountered {len(results['summary']['errors'])} errors during INSERT operations")
        
        return results
    
    async def demonstrate_fetch_operations(self) -> Dict[str, Any]:
        """
        Demonstrate FETCH operations showing all records from each collection.
        
        Returns:
            Dictionary containing all fetched records from each collection
        """
        results = {
            "users": {"records": [], "count": 0},
            "tasks": {"records": [], "count": 0},
            "products": {"records": [], "count": 0},
            "summary": {"total_records": 0, "errors": []}
        }
        
        self.logger.info("=== Demonstrating FETCH Operations ===")
        
        collections = ["users", "tasks", "products"]
        
        for collection in collections:
            try:
                self.logger.info(f"Fetching all records from '{collection}' collection...")
                response = await self.call_tool("read_records", {
                    "collection": collection
                })
                
                if response.get("success"):
                    records = response.get("data", [])
                    count = len(records)
                    results[collection]["records"] = records
                    results[collection]["count"] = count
                    results["summary"]["total_records"] += count
                    
                    self.logger.info(f"✓ Fetched {count} records from '{collection}' collection")
                    
                    # Display sample of records (first 3)
                    for i, record in enumerate(records[:3]):
                        record_id = record.get("id", "unknown")
                        if collection == "users":
                            name = record.get("name", "Unknown")
                            email = record.get("email", "Unknown")
                            self.logger.info(f"  - User {record_id}: {name} ({email})")
                        elif collection == "tasks":
                            title = record.get("title", "Unknown")
                            status = record.get("status", "Unknown")
                            self.logger.info(f"  - Task {record_id}: {title} [{status}]")
                        elif collection == "products":
                            name = record.get("name", "Unknown")
                            price = record.get("price", 0)
                            self.logger.info(f"  - Product {record_id}: {name} (${price})")
                    
                    if count > 3:
                        self.logger.info(f"  ... and {count - 3} more records")
                        
                else:
                    error_msg = f"Failed to fetch from '{collection}': {response.get('error', 'Unknown error')}"
                    results["summary"]["errors"].append(error_msg)
                    self.logger.error(error_msg)
                    
            except Exception as e:
                error_msg = f"Exception fetching from '{collection}': {str(e)}"
                results["summary"]["errors"].append(error_msg)
                self.logger.error(error_msg)
        
        self.logger.info(f"FETCH operations completed. Retrieved {results['summary']['total_records']} records total.")
        if results["summary"]["errors"]:
            self.logger.warning(f"Encountered {len(results['summary']['errors'])} errors during FETCH operations")
        
        return results
    
    async def demonstrate_update_operations(self) -> Dict[str, Any]:
        """
        Demonstrate UPDATE operations with before/after display.
        Updates existing records and shows the changes.
        
        Returns:
            Dictionary containing results of update operations with before/after data
        """
        results = {
            "updates": [],
            "summary": {"total_updated": 0, "errors": []}
        }
        
        self.logger.info("=== Demonstrating UPDATE Operations ===")
        
        # Define update operations to demonstrate
        update_operations = [
            {
                "collection": "users",
                "filters": {"role": "developer"},
                "updates": {"role": "senior_developer"},
                "description": "Promote all developers to senior developers"
            },
            {
                "collection": "tasks", 
                "filters": {"status": "pending"},
                "updates": {"status": "in_progress", "priority": "high"},
                "description": "Update pending tasks to in-progress with high priority"
            },
            {
                "collection": "products",
                "filters": {"in_stock": False},
                "updates": {"in_stock": True, "price": 39.99},
                "description": "Restock out-of-stock products and update price"
            }
        ]
        
        for i, operation in enumerate(update_operations, 1):
            try:
                collection = operation["collection"]
                filters = operation["filters"]
                updates = operation["updates"]
                description = operation["description"]
                
                self.logger.info(f"Update operation {i}: {description}")
                
                # First, fetch records that match the filter to show "before" state
                self.logger.info(f"Fetching records matching filter: {filters}")
                before_response = await self.call_tool("read_records", {
                    "collection": collection,
                    "filters": filters
                })
                
                before_records = []
                if before_response.get("success"):
                    before_records = before_response.get("data", [])
                    self.logger.info(f"Found {len(before_records)} records to update")
                    
                    # Show before state
                    for record in before_records[:3]:  # Show first 3
                        record_id = record.get("id", "unknown")
                        self.logger.info(f"  Before - Record {record_id}: {record}")
                else:
                    self.logger.warning(f"Could not fetch before state: {before_response.get('error', 'Unknown error')}")
                
                # Perform the update
                self.logger.info(f"Applying updates: {updates}")
                update_response = await self.call_tool("update_record", {
                    "collection": collection,
                    "filters": filters,
                    "updates": updates
                })
                
                operation_result = {
                    "operation": i,
                    "description": description,
                    "collection": collection,
                    "filters": filters,
                    "updates": updates,
                    "before_records": before_records,
                    "update_response": update_response,
                    "after_records": []
                }
                
                if update_response.get("success"):
                    updated_count = update_response.get("count", 0)
                    results["summary"]["total_updated"] += updated_count
                    self.logger.info(f"✓ Successfully updated {updated_count} records")
                    
                    # Fetch records after update to show "after" state
                    if before_records:
                        # Use IDs from before records to fetch specific updated records
                        record_ids = [record.get("id") for record in before_records if record.get("id")]
                        if record_ids:
                            for record_id in record_ids[:3]:  # Show first 3
                                after_response = await self.call_tool("read_records", {
                                    "collection": collection,
                                    "filters": {"id": record_id}
                                })
                                
                                if after_response.get("success") and after_response.get("data"):
                                    after_record = after_response["data"][0]
                                    operation_result["after_records"].append(after_record)
                                    self.logger.info(f"  After  - Record {record_id}: {after_record}")
                    
                else:
                    error_msg = f"Failed to update records in '{collection}': {update_response.get('error', 'Unknown error')}"
                    results["summary"]["errors"].append(error_msg)
                    self.logger.error(error_msg)
                
                results["updates"].append(operation_result)
                
            except Exception as e:
                error_msg = f"Exception during update operation {i}: {str(e)}"
                results["summary"]["errors"].append(error_msg)
                self.logger.error(error_msg)
        
        self.logger.info(f"UPDATE operations completed. Updated {results['summary']['total_updated']} records total.")
        if results["summary"]["errors"]:
            self.logger.warning(f"Encountered {len(results['summary']['errors'])} errors during UPDATE operations")
        
        return results
    
    async def demonstrate_delete_operations(self) -> Dict[str, Any]:
        """
        Demonstrate DELETE operations with confirmation.
        Deletes specific records and verifies deletion.
        
        Returns:
            Dictionary containing results of delete operations
        """
        results = {
            "deletions": [],
            "summary": {"total_deleted": 0, "errors": []}
        }
        
        self.logger.info("=== Demonstrating DELETE Operations ===")
        
        # Define delete operations to demonstrate
        delete_operations = [
            {
                "collection": "tasks",
                "filters": {"status": "in_progress", "priority": "high"},
                "description": "Delete high-priority in-progress tasks"
            },
            {
                "collection": "products",
                "filters": {"category": "accessories"},
                "description": "Delete all accessory products"
            },
            {
                "collection": "users",
                "filters": {"role": "senior_developer"},
                "description": "Delete senior developer users"
            }
        ]
        
        for i, operation in enumerate(delete_operations, 1):
            try:
                collection = operation["collection"]
                filters = operation["filters"]
                description = operation["description"]
                
                self.logger.info(f"Delete operation {i}: {description}")
                
                # First, fetch records that match the filter to show what will be deleted
                self.logger.info(f"Fetching records to delete with filter: {filters}")
                before_response = await self.call_tool("read_records", {
                    "collection": collection,
                    "filters": filters
                })
                
                records_to_delete = []
                if before_response.get("success"):
                    records_to_delete = before_response.get("data", [])
                    self.logger.info(f"Found {len(records_to_delete)} records to delete")
                    
                    # Show records that will be deleted
                    for record in records_to_delete:
                        record_id = record.get("id", "unknown")
                        if collection == "users":
                            name = record.get("name", "Unknown")
                            self.logger.info(f"  Will delete User {record_id}: {name}")
                        elif collection == "tasks":
                            title = record.get("title", "Unknown")
                            self.logger.info(f"  Will delete Task {record_id}: {title}")
                        elif collection == "products":
                            name = record.get("name", "Unknown")
                            self.logger.info(f"  Will delete Product {record_id}: {name}")
                else:
                    self.logger.warning(f"Could not fetch records to delete: {before_response.get('error', 'Unknown error')}")
                
                # Perform the deletion
                self.logger.info(f"Proceeding with deletion...")
                delete_response = await self.call_tool("delete_record", {
                    "collection": collection,
                    "filters": filters
                })
                
                operation_result = {
                    "operation": i,
                    "description": description,
                    "collection": collection,
                    "filters": filters,
                    "records_before_delete": records_to_delete,
                    "delete_response": delete_response
                }
                
                if delete_response.get("success"):
                    deleted_count = delete_response.get("count", 0)
                    results["summary"]["total_deleted"] += deleted_count
                    self.logger.info(f"✓ Successfully deleted {deleted_count} records")
                    
                    # Verify deletion by trying to fetch the same records
                    if records_to_delete:
                        self.logger.info("Verifying deletion...")
                        verify_response = await self.call_tool("read_records", {
                            "collection": collection,
                            "filters": filters
                        })
                        
                        if verify_response.get("success"):
                            remaining_records = verify_response.get("data", [])
                            if len(remaining_records) == 0:
                                self.logger.info("✓ Deletion verified - no matching records found")
                            else:
                                self.logger.warning(f"⚠ {len(remaining_records)} records still exist after deletion")
                        else:
                            self.logger.warning(f"Could not verify deletion: {verify_response.get('error', 'Unknown error')}")
                    
                else:
                    error_msg = f"Failed to delete records from '{collection}': {delete_response.get('error', 'Unknown error')}"
                    results["summary"]["errors"].append(error_msg)
                    self.logger.error(error_msg)
                
                results["deletions"].append(operation_result)
                
            except Exception as e:
                error_msg = f"Exception during delete operation {i}: {str(e)}"
                results["summary"]["errors"].append(error_msg)
                self.logger.error(error_msg)
        
        self.logger.info(f"DELETE operations completed. Deleted {results['summary']['total_deleted']} records total.")
        if results["summary"]["errors"]:
            self.logger.warning(f"Encountered {len(results['summary']['errors'])} errors during DELETE operations")
        
        return results


# Connection test utility function
async def test_mcp_connection(server_command: List[str]) -> bool:
    """
    Utility function to test MCP server connection.
    
    Args:
        server_command: Command to start the MCP server
        
    Returns:
        True if connection successful, False otherwise
    """
    client = MCPClient(server_command)
    
    try:
        async with client.connection():
            return await client.test_connection()
    except Exception as e:
        logging.error(f"Connection test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Basic connection test
    async def main():
        server_cmd = ["python", "run_server.py"]
        success = await test_mcp_connection(server_cmd)
        
        if success:
            print("✓ MCP client connection test passed")
        else:
            print("✗ MCP client connection test failed")
            sys.exit(1)
    
    asyncio.run(main())