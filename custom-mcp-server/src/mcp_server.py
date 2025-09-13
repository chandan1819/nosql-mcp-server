"""
Custom MCP Server with TinyDB integration.
Provides CRUD operations through MCP tools for users, tasks, and products collections.
"""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from mcp.server import FastMCP
from mcp.types import TextContent

from database.manager import DatabaseManager
from response_formatter import ResponseFormatter


class MCPServer:
    """
    Main MCP server class that provides database operations through MCP tools.
    Inherits functionality from the MCP SDK and integrates with DatabaseManager.
    """
    
    def __init__(self, db_path: str = "data/mcp_server.json"):
        """
        Initialize the MCP server with database connection.
        
        Args:
            db_path: Path to the TinyDB database file
        """
        self.db_path = db_path
        self.db_manager: Optional[DatabaseManager] = None
        self.server = FastMCP("custom-mcp-server")
        self.logger = logging.getLogger(__name__)
        
        # Configure logging
        self._setup_logging()
        
        # Register MCP tools
        self._register_tools()
    
    def _setup_logging(self) -> None:
        """
        Configure logging for the MCP server.
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stderr),
                logging.FileHandler('mcp_server.log')
            ]
        )
        self.logger.info("Logging configured for MCP server")
    
    async def initialize_database(self) -> None:
        """
        Initialize database connection and setup sample data.
        Handles connection errors gracefully.
        """
        try:
            self.logger.info(f"Initializing database connection to {self.db_path}")
            self.db_manager = DatabaseManager(self.db_path)
            
            if not self.db_manager.is_connected():
                raise ConnectionError("Failed to establish database connection")
            
            # Initialize sample data if database is empty
            sample_counts = self.db_manager.initialize_sample_data()
            if any(count > 0 for count in sample_counts.values()):
                self.logger.info(f"Initialized sample data: {sample_counts}")
            else:
                self.logger.info("Database already contains data, skipping sample data initialization")
            
            self.logger.info("Database initialization completed successfully")
            
        except Exception as e:
            error_msg = f"Database initialization failed: {str(e)}"
            self.logger.error(error_msg)
            raise ConnectionError(error_msg)
    
    async def shutdown_database(self) -> None:
        """
        Gracefully shutdown database connection.
        """
        try:
            if self.db_manager:
                self.db_manager.close()
                self.db_manager = None
                self.logger.info("Database connection closed successfully")
        except Exception as e:
            self.logger.warning(f"Error during database shutdown: {str(e)}")
    
    def _register_tools(self) -> None:
        """
        Register all MCP tools with the server.
        """
        self.logger.info("Registering MCP tools...")
        
        # Register create_record tool
        @self.server.tool()
        async def create_record(collection: str, data: dict) -> List[TextContent]:
            """
            Create a new record in the specified collection.
            
            Args:
                collection: Name of the collection ('users', 'tasks', 'products')
                data: Dictionary containing the record data
            """
            try:
                if not self.db_manager:
                    raise ConnectionError("Database not initialized")
                
                # Validate parameters
                if not collection:
                    raise ValueError("Collection name is required")
                
                if not isinstance(data, dict) or not data:
                    raise ValueError("Data must be a non-empty dictionary")
                
                # Perform the create operation
                db_result = self.db_manager.create_record(collection, data)
                
                # Format response using ResponseFormatter
                formatted_response = ResponseFormatter.from_database_result(
                    db_result, "create", collection
                )
                
                return [TextContent(
                    type="text",
                    text=ResponseFormatter.to_json_string(formatted_response)
                )]
                
            except Exception as e:
                error_response = ResponseFormatter.error_response(
                    error_msg=str(e),
                    operation="create record",
                    metadata={"collection": collection if 'collection' in locals() else "unknown"}
                )
                return [TextContent(
                    type="text",
                    text=ResponseFormatter.to_json_string(error_response)
                )]
        
        # Register read_records tool
        @self.server.tool()
        async def read_records(collection: str, filters: Optional[dict] = None) -> List[TextContent]:
            """
            Read records from the specified collection with optional filtering.
            
            Args:
                collection: Name of the collection ('users', 'tasks', 'products')
                filters: Optional dictionary of filter criteria
            """
            try:
                if not self.db_manager:
                    raise ConnectionError("Database not initialized")
                
                # Validate parameters
                if not collection:
                    raise ValueError("Collection name is required")
                
                # Perform the read operation
                db_result = self.db_manager.read_records(collection, filters)
                
                # Format response using ResponseFormatter
                formatted_response = ResponseFormatter.from_database_result(
                    db_result, "read", collection
                )
                
                return [TextContent(
                    type="text",
                    text=ResponseFormatter.to_json_string(formatted_response)
                )]
                
            except Exception as e:
                error_response = ResponseFormatter.error_response(
                    error_msg=str(e),
                    operation="read records",
                    metadata={"collection": collection if 'collection' in locals() else "unknown"}
                )
                return [TextContent(
                    type="text",
                    text=ResponseFormatter.to_json_string(error_response)
                )]
        
        # Register update_record tool
        @self.server.tool()
        async def update_record(collection: str, filters: dict, updates: dict) -> List[TextContent]:
            """
            Update records in the specified collection based on filter criteria.
            
            Args:
                collection: Name of the collection ('users', 'tasks', 'products')
                filters: Dictionary of filter criteria to identify records to update
                updates: Dictionary of field updates to apply
            """
            try:
                if not self.db_manager:
                    raise ConnectionError("Database not initialized")
                
                # Validate parameters
                if not collection:
                    raise ValueError("Collection name is required")
                
                if not isinstance(filters, dict) or not filters:
                    raise ValueError("Filters must be a non-empty dictionary")
                
                if not isinstance(updates, dict) or not updates:
                    raise ValueError("Updates must be a non-empty dictionary")
                
                # Perform the update operation
                db_result = self.db_manager.update_records(collection, filters, updates)
                
                # Format response using ResponseFormatter
                formatted_response = ResponseFormatter.from_database_result(
                    db_result, "update", collection
                )
                
                return [TextContent(
                    type="text",
                    text=ResponseFormatter.to_json_string(formatted_response)
                )]
                
            except Exception as e:
                error_response = ResponseFormatter.error_response(
                    error_msg=str(e),
                    operation="update record",
                    metadata={"collection": collection if 'collection' in locals() else "unknown"}
                )
                return [TextContent(
                    type="text",
                    text=ResponseFormatter.to_json_string(error_response)
                )]
        
        # Register delete_record tool
        @self.server.tool()
        async def delete_record(collection: str, filters: dict) -> List[TextContent]:
            """
            Delete records from the specified collection based on filter criteria.
            
            Args:
                collection: Name of the collection ('users', 'tasks', 'products')
                filters: Dictionary of filter criteria to identify records to delete
            """
            try:
                if not self.db_manager:
                    raise ConnectionError("Database not initialized")
                
                # Validate parameters
                if not collection:
                    raise ValueError("Collection name is required")
                
                if not isinstance(filters, dict) or not filters:
                    raise ValueError("Filters must be a non-empty dictionary for safety")
                
                # Perform the delete operation
                db_result = self.db_manager.delete_records(collection, filters)
                
                # Format response using ResponseFormatter
                formatted_response = ResponseFormatter.from_database_result(
                    db_result, "delete", collection
                )
                
                return [TextContent(
                    type="text",
                    text=ResponseFormatter.to_json_string(formatted_response)
                )]
                
            except Exception as e:
                error_response = ResponseFormatter.error_response(
                    error_msg=str(e),
                    operation="delete record",
                    metadata={"collection": collection if 'collection' in locals() else "unknown"}
                )
                return [TextContent(
                    type="text",
                    text=ResponseFormatter.to_json_string(error_response)
                )]
        
        # Register search_records tool
        @self.server.tool()
        async def search_records(collection: str, query: dict) -> List[TextContent]:
            """
            Advanced search with complex filtering capabilities.
            
            Args:
                collection: Name of the collection ('users', 'tasks', 'products')
                query: Dictionary specifying complex search criteria
            """
            try:
                if not self.db_manager:
                    raise ConnectionError("Database not initialized")
                
                # Validate parameters
                if not collection:
                    raise ValueError("Collection name is required")
                
                if not isinstance(query, dict) or not query:
                    raise ValueError("Query must be a non-empty dictionary")
                
                # Use read_records with the query as filters for advanced search
                db_result = self.db_manager.read_records(collection, query)
                
                # Format response using ResponseFormatter with search-specific formatting
                if db_result.get("success"):
                    formatted_response = ResponseFormatter.search_response(
                        matching_records=db_result.get("data", []),
                        collection=collection,
                        query=query
                    )
                else:
                    formatted_response = ResponseFormatter.error_response(
                        error_msg=db_result.get("error", "Search failed"),
                        operation="search",
                        metadata={"collection": collection, "query": query}
                    )
                
                return [TextContent(
                    type="text",
                    text=ResponseFormatter.to_json_string(formatted_response)
                )]
                
            except Exception as e:
                error_response = ResponseFormatter.error_response(
                    error_msg=str(e),
                    operation="search records",
                    metadata={"collection": collection if 'collection' in locals() else "unknown"}
                )
                return [TextContent(
                    type="text",
                    text=ResponseFormatter.to_json_string(error_response)
                )]
        
        self.logger.info("Successfully registered 5 MCP tools: create_record, read_records, update_record, delete_record, search_records")
    
    def _format_response(self, success: bool, data: Any = None, message: str = "", 
                        count: int = 0, error: Optional[str] = None) -> Dict[str, Any]:
        """
        Format consistent JSON responses for all MCP tools.
        
        Args:
            success: Whether the operation was successful
            data: The actual result data
            message: Human-readable message
            count: Number of records affected
            error: Error message if success is False
            
        Returns:
            Formatted response dictionary
        """
        return {
            "success": success,
            "data": data,
            "message": message,
            "count": count,
            "error": error
        }
    
    def _format_error_response(self, error_msg: str, operation: str = "operation") -> Dict[str, Any]:
        """
        Format error responses with consistent structure.
        
        Args:
            error_msg: Detailed error message
            operation: Name of the operation that failed
            
        Returns:
            Formatted error response dictionary
        """
        return self._format_response(
            success=False,
            data=None,
            message=f"{operation.capitalize()} failed",
            count=0,
            error=error_msg
        )
    
    async def run(self) -> None:
        """
        Start the MCP server and handle client connections.
        """
        try:
            self.logger.info("Starting MCP server...")
            
            # Initialize database connection
            await self.initialize_database()
            
            # Start the server using stdio transport
            self.logger.info("MCP server started successfully, waiting for client connections...")
            await self.server.run_stdio_async()
                
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal, stopping server...")
        except Exception as e:
            self.logger.error(f"Server error: {str(e)}")
            raise
        finally:
            await self.shutdown_database()
            self.logger.info("MCP server shutdown completed")
    
    @asynccontextmanager
    async def lifespan(self):
        """
        Async context manager for server lifecycle management.
        """
        try:
            await self.initialize_database()
            yield self
        finally:
            await self.shutdown_database()


async def main():
    """
    Main entry point for the MCP server.
    """
    try:
        # Create and run the MCP server
        mcp_server = MCPServer()
        await mcp_server.run()
        
    except Exception as e:
        logging.error(f"Failed to start MCP server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the server
    asyncio.run(main())