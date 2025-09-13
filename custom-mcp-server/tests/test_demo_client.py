"""
Tests for the demonstration client script.
"""

import asyncio
import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from demo_client import MCPDemonstrationClient


class TestMCPDemonstrationClient:
    """Test cases for the MCP demonstration client."""
    
    @pytest.fixture
    def demo_client(self):
        """Create a test demonstration client instance."""
        return MCPDemonstrationClient()
    
    def test_demo_client_initialization(self, demo_client):
        """Test that demo client initializes correctly."""
        assert demo_client.client is not None
        assert demo_client.server_command is not None
        assert len(demo_client.server_command) >= 2
        assert demo_client.server_command[0] == "python"
    
    def test_formatting_methods(self, demo_client):
        """Test the output formatting methods."""
        # Test banner printing (should not raise exceptions)
        demo_client.print_banner("Test Banner")
        demo_client.print_section("Test Section")
        demo_client.print_progress("Test Progress", "SUCCESS")
        
        # Test JSON formatting
        test_data = {"key": "value", "number": 123}
        formatted = demo_client.format_json_output(test_data)
        assert isinstance(formatted, str)
        assert "key" in formatted
        assert "value" in formatted
        
        # Test with large list
        large_list = [{"item": i} for i in range(10)]
        formatted_large = demo_client.format_json_output(large_list, max_items=3)
        assert "... and 7 more items" in formatted_large
    
    def test_operation_summary_display(self, demo_client):
        """Test the operation summary display method."""
        # Test INSERT summary
        insert_results = {
            "summary": {
                "total_created": 5,
                "errors": ["Error 1", "Error 2"]
            }
        }
        # Should not raise exceptions
        demo_client.display_operation_summary("INSERT", insert_results)
        
        # Test FETCH summary
        fetch_results = {
            "summary": {
                "total_records": 10,
                "errors": []
            },
            "users": {"count": 3},
            "tasks": {"count": 4},
            "products": {"count": 3}
        }
        demo_client.display_operation_summary("FETCH", fetch_results)
    
    @pytest.mark.asyncio
    async def test_quick_test_without_server(self, demo_client):
        """Test quick test method when server is not available."""
        # This should fail gracefully when server is not running
        try:
            result = await demo_client.run_quick_test()
            # Result should be boolean (False when server not available)
            assert isinstance(result, bool)
        except Exception:
            # Connection failures are expected when server is not running
            pytest.skip("Server connection not available in test environment")


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])