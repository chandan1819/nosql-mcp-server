"""
Tests for the MCP Server foundation.
"""

import pytest
import asyncio
import os
import tempfile
import sys
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_server import MCPServer


class TestMCPServerFoundation:
    """Test cases for MCP server foundation functionality."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path for testing."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            temp_path = tmp.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_server_initialization(self, temp_db_path):
        """Test that the MCP server initializes correctly."""
        server = MCPServer(db_path=temp_db_path)
        
        assert server.db_path == temp_db_path
        assert server.db_manager is None  # Not initialized until async method called
        assert server.server is not None
        assert server.logger is not None
    
    @pytest.mark.asyncio
    async def test_database_initialization(self, temp_db_path):
        """Test database initialization."""
        server = MCPServer(db_path=temp_db_path)
        
        await server.initialize_database()
        
        assert server.db_manager is not None
        assert server.db_manager.is_connected()
        
        # Cleanup
        await server.shutdown_database()
    
    @pytest.mark.asyncio
    async def test_database_shutdown(self, temp_db_path):
        """Test database shutdown."""
        server = MCPServer(db_path=temp_db_path)
        
        await server.initialize_database()
        assert server.db_manager is not None
        
        await server.shutdown_database()
        assert server.db_manager is None
    
    @pytest.mark.asyncio
    async def test_database_initialization_error_handling(self):
        """Test error handling during database initialization."""
        # Use an invalid path to trigger an error (Windows compatible)
        invalid_path = "Z:\\invalid\\path\\that\\does\\not\\exist\\db.json"
        server = MCPServer(db_path=invalid_path)
        
        with pytest.raises(ConnectionError):
            await server.initialize_database()
    
    def test_response_formatting(self, temp_db_path):
        """Test response formatting utilities."""
        server = MCPServer(db_path=temp_db_path)
        
        # Test success response
        success_response = server._format_response(
            success=True,
            data={"test": "data"},
            message="Operation successful",
            count=1
        )
        
        expected_success = {
            "success": True,
            "data": {"test": "data"},
            "message": "Operation successful",
            "count": 1,
            "error": None
        }
        
        assert success_response == expected_success
        
        # Test error response
        error_response = server._format_error_response(
            error_msg="Something went wrong",
            operation="test operation"
        )
        
        expected_error = {
            "success": False,
            "data": None,
            "message": "Test operation failed",
            "count": 0,
            "error": "Something went wrong"
        }
        
        assert error_response == expected_error
    
    @pytest.mark.asyncio
    async def test_lifespan_context_manager(self, temp_db_path):
        """Test the lifespan context manager."""
        server = MCPServer(db_path=temp_db_path)
        
        async with server.lifespan() as managed_server:
            assert managed_server.db_manager is not None
            assert managed_server.db_manager.is_connected()
        
        # After context exit, database should be closed
        assert server.db_manager is None
    
    def test_logging_setup(self, temp_db_path):
        """Test that logging is properly configured."""
        server = MCPServer(db_path=temp_db_path)
        
        # Check that logger is configured
        assert server.logger is not None
        assert server.logger.name == 'mcp_server'
        
        # Check that logging handlers are set up
        root_logger = server.logger.parent
        assert len(root_logger.handlers) > 0