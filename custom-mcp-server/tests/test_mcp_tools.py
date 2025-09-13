"""
Tests for MCP tools functionality.
"""

import pytest
import asyncio
import os
import tempfile
import sys
import json
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_server import MCPServer


class TestMCPTools:
    """Test cases for MCP tools functionality."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path for testing."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            temp_path = tmp.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    async def initialized_server(self, temp_db_path):
        """Create and initialize an MCP server for testing."""
        server = MCPServer(db_path=temp_db_path)
        await server.initialize_database()
        yield server
        await server.shutdown_database()
    
    @pytest.mark.asyncio
    async def test_create_record_tool_registration(self, initialized_server):
        """Test that create_record tool is properly registered."""
        # Check that the tool is registered
        tools = await initialized_server.server.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "create_record" in tool_names
    
    @pytest.mark.asyncio
    async def test_read_records_tool_registration(self, initialized_server):
        """Test that read_records tool is properly registered."""
        tools = await initialized_server.server.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "read_records" in tool_names
    
    @pytest.mark.asyncio
    async def test_update_record_tool_registration(self, initialized_server):
        """Test that update_record tool is properly registered."""
        tools = await initialized_server.server.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "update_record" in tool_names
    
    @pytest.mark.asyncio
    async def test_delete_record_tool_registration(self, initialized_server):
        """Test that delete_record tool is properly registered."""
        tools = await initialized_server.server.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "delete_record" in tool_names
    
    @pytest.mark.asyncio
    async def test_search_records_tool_registration(self, initialized_server):
        """Test that search_records tool is properly registered."""
        tools = await initialized_server.server.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "search_records" in tool_names
    
    @pytest.mark.asyncio
    async def test_all_required_tools_registered(self, initialized_server):
        """Test that all 5 required tools are registered."""
        tools = await initialized_server.server.list_tools()
        tool_names = [tool.name for tool in tools]
        
        required_tools = [
            "create_record",
            "read_records", 
            "update_record",
            "delete_record",
            "search_records"
        ]
        
        for tool_name in required_tools:
            assert tool_name in tool_names, f"Tool {tool_name} not found in registered tools"
        
        assert len(tool_names) == 5, f"Expected 5 tools, found {len(tool_names)}: {tool_names}"
    
    @pytest.mark.asyncio
    async def test_create_record_tool_execution(self, initialized_server):
        """Test create_record tool execution with valid data."""
        # Test data
        test_data = {
            "name": "Test User",
            "email": "test@example.com",
            "role": "Tester"
        }
        
        # Execute the tool using call_tool method
        result = await initialized_server.server.call_tool(
            "create_record",
            {"collection": "users", "data": test_data}
        )
        
        assert result is not None
        # Result is a tuple (content, metadata)
        content = result[0] if isinstance(result, tuple) else result
        assert len(content) == 1
        
        # Parse the JSON response
        import json
        response_data = json.loads(content[0].text)
        
        # Verify structured response format
        assert response_data["success"] is True
        assert response_data["operation"] == "create"
        assert "Record created successfully in users" in response_data["message"]
        assert response_data["count"] == 1
        assert response_data["data"]["name"] == "Test User"
        assert response_data["data"]["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_read_records_tool_execution(self, initialized_server):
        """Test read_records tool execution."""
        # Execute the tool to read all users
        result = await initialized_server.server.call_tool(
            "read_records",
            {"collection": "users"}
        )
        
        assert result is not None
        content = result[0] if isinstance(result, tuple) else result
        assert len(content) == 1
        
        # Parse the JSON response
        import json
        response_data = json.loads(content[0].text)
        
        # Verify structured response format
        assert response_data["success"] is True
        assert response_data["operation"] == "read"
        assert "retrieved" in response_data["message"]
        assert "users" in response_data["message"]
        assert response_data["count"] >= 0
        assert isinstance(response_data["data"], list)
    
    @pytest.mark.asyncio
    async def test_tool_parameter_validation(self, initialized_server):
        """Test that tools properly validate parameters."""
        from mcp.server.fastmcp.exceptions import ToolError
        
        # Test with missing collection parameter - should raise ToolError
        with pytest.raises(ToolError) as exc_info:
            await initialized_server.server.call_tool(
                "create_record",
                {"data": {"name": "Test"}}
            )
        
        assert "collection" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self, initialized_server):
        """Test that tools handle errors gracefully."""
        # Test with invalid collection name
        result = await initialized_server.server.call_tool(
            "create_record",
            {"collection": "invalid_collection", "data": {"test": "data"}}
        )
        
        assert result is not None
        content = result[0] if isinstance(result, tuple) else result
        assert len(content) == 1
        assert "failed" in content[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_update_record_tool_validation(self, initialized_server):
        """Test update_record tool parameter validation."""
        from mcp.server.fastmcp.exceptions import ToolError
        
        # Test with missing filters - should raise ToolError
        with pytest.raises(ToolError) as exc_info:
            await initialized_server.server.call_tool(
                "update_record",
                {"collection": "users", "updates": {"name": "Updated"}}
            )
        
        assert "filters" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_delete_record_tool_safety_checks(self, initialized_server):
        """Test delete_record tool safety checks."""
        from mcp.server.fastmcp.exceptions import ToolError
        
        # Test with missing filters (should fail for safety) - should raise ToolError
        with pytest.raises(ToolError) as exc_info:
            await initialized_server.server.call_tool(
                "delete_record",
                {"collection": "users"}
            )
        
        assert "filters" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_search_records_tool_execution(self, initialized_server):
        """Test search_records tool execution."""
        # Execute search with query
        result = await initialized_server.server.call_tool(
            "search_records",
            {"collection": "users", "query": {"role": "Project Manager"}}
        )
        
        assert result is not None
        content = result[0] if isinstance(result, tuple) else result
        assert len(content) == 1
        
        # Parse the JSON response
        import json
        response_data = json.loads(content[0].text)
        
        # Verify structured response format
        assert response_data["success"] is True
        assert response_data["operation"] == "search"
        assert "found" in response_data["message"]
        assert "matching records" in response_data["message"]
        assert response_data["count"] >= 0
        assert isinstance(response_data["data"], list)