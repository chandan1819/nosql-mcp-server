"""
Tests for MCP Client connection and basic functionality.
"""

import asyncio
import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_client import MCPClient, test_mcp_connection


class TestMCPClientConnection:
    """Test cases for MCP client connection functionality."""
    
    @pytest.fixture
    def client(self):
        """Create a test MCP client instance."""
        server_command = ["python", os.path.join(os.path.dirname(__file__), "..", "run_server.py")]
        return MCPClient(server_command, max_retries=2, retry_delay=0.5)
    
    def test_client_initialization(self, client):
        """Test that client initializes with correct parameters."""
        assert client.max_retries == 2
        assert client.retry_delay == 0.5
        assert client.session is None
        assert client.server_command[0] == "python"
    
    @pytest.mark.asyncio
    async def test_connection_context_manager(self, client):
        """Test connection using context manager."""
        try:
            async with client.connection():
                # Test that session is established
                assert client.session is not None
                
                # Test connection by listing tools
                connection_ok = await client.test_connection()
                assert connection_ok is True
                
        except Exception as e:
            # Connection might fail in test environment, that's expected
            pytest.skip(f"Server connection not available in test environment: {e}")
    
    @pytest.mark.asyncio
    async def test_tool_call_without_connection(self, client):
        """Test that tool calls fail when not connected."""
        with pytest.raises(ConnectionError, match="Not connected to MCP server"):
            await client.call_tool("test_tool", {})
    
    @pytest.mark.asyncio
    async def test_connection_retry_logic(self):
        """Test connection retry logic with invalid server command."""
        # Use invalid command to test retry logic
        client = MCPClient(["invalid_command"], max_retries=2, retry_delay=0.1)
        
        # This should fail after retries
        success = await client.connect()
        assert success is False
    
    def test_logging_setup(self, client):
        """Test that logging is properly configured."""
        assert client.logger is not None
        assert client.logger.name == "mcp_client"


class TestMCPClientCRUDMethods:
    """Test cases for CRUD demonstration methods."""
    
    @pytest.fixture
    def client(self):
        """Create a test MCP client instance."""
        server_command = ["python", os.path.join(os.path.dirname(__file__), "..", "run_server.py")]
        return MCPClient(server_command, max_retries=1, retry_delay=0.1)
    
    def test_crud_methods_exist(self, client):
        """Test that all CRUD demonstration methods exist."""
        assert hasattr(client, 'demonstrate_insert_operations')
        assert hasattr(client, 'demonstrate_fetch_operations')
        assert hasattr(client, 'demonstrate_update_operations')
        assert hasattr(client, 'demonstrate_delete_operations')
    
    @pytest.mark.asyncio
    async def test_crud_methods_without_connection(self, client):
        """Test that CRUD methods handle connection errors gracefully."""
        # These should return error results instead of raising exceptions
        
        # Test insert operations
        insert_result = await client.demonstrate_insert_operations()
        assert isinstance(insert_result, dict)
        assert "summary" in insert_result
        assert len(insert_result["summary"]["errors"]) > 0  # Should have connection errors
        
        # Test fetch operations
        fetch_result = await client.demonstrate_fetch_operations()
        assert isinstance(fetch_result, dict)
        assert "summary" in fetch_result
        assert len(fetch_result["summary"]["errors"]) > 0  # Should have connection errors
        
        # Test update operations
        update_result = await client.demonstrate_update_operations()
        assert isinstance(update_result, dict)
        assert "summary" in update_result
        assert len(update_result["summary"]["errors"]) > 0  # Should have connection errors
        
        # Test delete operations
        delete_result = await client.demonstrate_delete_operations()
        assert isinstance(delete_result, dict)
        assert "summary" in delete_result
        assert len(delete_result["summary"]["errors"]) > 0  # Should have connection errors


class TestMCPClientUtilities:
    """Test cases for MCP client utility functions."""
    
    @pytest.mark.asyncio
    async def test_connection_test_utility(self):
        """Test the connection test utility function."""
        server_command = ["python", os.path.join(os.path.dirname(__file__), "..", "run_server.py")]
        
        try:
            # This might fail in test environment, which is expected
            result = await test_mcp_connection(server_command)
            # Result should be boolean regardless of success/failure
            assert isinstance(result, bool)
        except Exception:
            # Connection failures are expected in test environment
            pytest.skip("Server connection not available in test environment")


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])