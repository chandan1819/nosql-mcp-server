"""
Comprehensive error handling tests for all components.
Tests various error scenarios and edge cases.
"""

import pytest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.manager import DatabaseManager
from mcp_server import MCPServer
from response_formatter import ResponseFormatter
from database.query_parser import QueryParser
from tests.test_factories import TestDataFactory, TestDatabaseFactory, TestUtilities


class TestDatabaseManagerErrorHandling:
    """Test error handling in DatabaseManager."""
    
    def setup_method(self):
        """Set up test database for each test."""
        self.db_path = TestDatabaseFactory.create_temp_db()
        self.db_manager = DatabaseManager(self.db_path)
    
    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        TestDatabaseFactory.cleanup_temp_db(self.db_path)
    
    def test_invalid_database_path(self):
        """Test initialization with invalid database path."""
        # Test with directory that doesn't exist (Windows compatible)
        invalid_path = os.path.join("Z:", "nonexistent", "path", "db.json")
        
        # Should not raise exception during initialization
        db_manager = DatabaseManager(invalid_path)
        
        # But should fail when trying to use the database
        with pytest.raises(Exception):
            db_manager.initialize_sample_data()
    
    def test_database_permission_error(self):
        """Test handling of permission errors."""
        # Create a read-only file to simulate permission error
        readonly_path = TestDatabaseFactory.create_temp_db()
        
        try:
            # Make file read-only (Windows compatible)
            os.chmod(readonly_path, 0o444)
            
            db_manager = DatabaseManager(readonly_path)
            
            # Operations should handle permission errors gracefully
            result = db_manager.create_record("users", TestDataFactory.create_user())
            
            # Should return error response instead of raising exception
            assert result["success"] is False
            assert "error" in result
            
        finally:
            # Restore write permissions for cleanup
            try:
                os.chmod(readonly_path, 0o666)
                os.unlink(readonly_path)
            except (PermissionError, FileNotFoundError):
                pass
    
    def test_corrupted_database_file(self):
        """Test handling of corrupted database file."""
        # Create a file with invalid JSON
        corrupted_path = TestDatabaseFactory.create_temp_db()
        
        try:
            with open(corrupted_path, 'w') as f:
                f.write("invalid json content {")
            
            # Should handle corrupted file gracefully
            db_manager = DatabaseManager(corrupted_path)
            result = db_manager.create_record("users", TestDataFactory.create_user())
            
            # Should either recover or return error response
            assert isinstance(result, dict)
            assert "success" in result
            
        finally:
            TestDatabaseFactory.cleanup_temp_db(corrupted_path)
    
    def test_create_record_with_none_data(self):
        """Test create_record with None data."""
        result = self.db_manager.create_record("users", None)
        
        TestUtilities.assert_response_structure(result, success=False)
        assert "Data cannot be None" in result["error"] or "Data must be a dictionary" in result["error"]
    
    def test_create_record_with_invalid_data_type(self):
        """Test create_record with invalid data types."""
        invalid_data_types = [
            "string_data",
            123,
            ["list", "data"],
            True,
            set(["set", "data"])
        ]
        
        for invalid_data in invalid_data_types:
            result = self.db_manager.create_record("users", invalid_data)
            TestUtilities.assert_response_structure(result, success=False)
            assert "must be a dictionary" in result["error"]
    
    def test_create_record_with_extremely_large_data(self):
        """Test create_record with extremely large data."""
        # Create data with very large string
        large_string = "x" * 1000000  # 1MB string
        large_data = TestDataFactory.create_user(name=large_string)
        
        result = self.db_manager.create_record("users", large_data)
        
        # Should either succeed or fail gracefully
        TestUtilities.assert_response_structure(result)
        if not result["success"]:
            assert "error" in result
    
    def test_read_records_with_malformed_filters(self):
        """Test read_records with malformed filter data."""
        malformed_filters = [
            {"field": {"invalid_operator": {"nested": "too_deep"}}},
            {"field": None},
            {"": "empty_field_name"},
            {123: "numeric_field_name"},
            {"field": {"gt": [1, 2, 3]}}  # Wrong type for gt operator
        ]
        
        for malformed_filter in malformed_filters:
            result = self.db_manager.read_records("users", malformed_filter)
            TestUtilities.assert_response_structure(result, success=False)
    
    def test_update_records_with_circular_reference(self):
        """Test update_records with circular reference in data."""
        # Create circular reference
        circular_data = {"name": "Test"}
        circular_data["self_ref"] = circular_data
        
        # First create a record to update
        user = TestDataFactory.create_user()
        self.db_manager.create_record("users", user)
        
        result = self.db_manager.update_records("users", {"name": user["name"]}, circular_data)
        
        # Should handle circular reference gracefully
        TestUtilities.assert_response_structure(result, success=False)
    
    def test_delete_records_with_empty_filters(self):
        """Test delete_records with empty filters (safety check)."""
        # Create test data
        user = TestDataFactory.create_user()
        self.db_manager.create_record("users", user)
        
        # Try to delete with empty filters (should be prevented for safety)
        result = self.db_manager.delete_records("users", {})
        
        TestUtilities.assert_response_structure(result, success=False)
        assert "Filters are required" in result["error"] or "safety" in result["error"].lower()
    
    def test_concurrent_database_access(self):
        """Test handling of concurrent database access."""
        import threading
        import time
        
        results = []
        errors = []
        
        def create_user_thread(thread_id):
            try:
                user_data = TestDataFactory.create_user(name=f"User {thread_id}")
                result = self.db_manager.create_record("users", user_data)
                results.append(result)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_user_thread, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"
        assert len(errors) == 0, f"Unexpected errors: {errors}"
        
        # All operations should have succeeded
        for result in results:
            TestUtilities.assert_response_structure(result, success=True)
    
    def test_memory_exhaustion_simulation(self):
        """Test behavior under simulated memory pressure."""
        # Create many large records to simulate memory pressure
        large_records = []
        
        try:
            for i in range(100):
                large_data = TestDataFactory.create_user(
                    name=f"User {i}",
                    description="x" * 10000  # 10KB per record
                )
                result = self.db_manager.create_record("users", large_data)
                
                if not result["success"]:
                    # If we hit memory limits, should fail gracefully
                    TestUtilities.assert_response_structure(result, success=False)
                    break
                
                large_records.append(result)
                
                # Stop if we've created enough records
                if len(large_records) >= 50:
                    break
                    
        except MemoryError:
            # Should handle memory errors gracefully
            pytest.skip("Memory exhaustion test hit actual memory limits")
    
    def test_database_file_deletion_during_operation(self):
        """Test handling of database file deletion during operation."""
        # Create some data first
        user = TestDataFactory.create_user()
        create_result = self.db_manager.create_record("users", user)
        assert create_result["success"] is True
        
        # Delete the database file while manager is still active
        try:
            os.unlink(self.db_path)
        except (PermissionError, FileNotFoundError):
            pytest.skip("Cannot delete database file during test")
        
        # Try to perform operations after file deletion
        result = self.db_manager.read_records("users")
        
        # Should handle missing file gracefully
        TestUtilities.assert_response_structure(result, success=False)


class TestMCPServerErrorHandling:
    """Test error handling in MCP Server."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path."""
        path = TestDatabaseFactory.create_temp_db()
        yield path
        TestDatabaseFactory.cleanup_temp_db(path)
    
    def test_server_initialization_with_invalid_path(self):
        """Test server initialization with invalid database path."""
        invalid_path = "Z:\\invalid\\path\\db.json"
        server = MCPServer(db_path=invalid_path)
        
        # Should initialize without error
        assert server.db_path == invalid_path
        assert server.db_manager is None
    
    @pytest.mark.asyncio
    async def test_database_initialization_failure(self):
        """Test handling of database initialization failure."""
        invalid_path = "Z:\\invalid\\path\\db.json"
        server = MCPServer(db_path=invalid_path)
        
        # Should raise appropriate error
        with pytest.raises(ConnectionError):
            await server.initialize_database()
    
    @pytest.mark.asyncio
    async def test_tool_execution_with_uninitialized_database(self, temp_db_path):
        """Test tool execution when database is not initialized."""
        server = MCPServer(db_path=temp_db_path)
        # Don't initialize database
        
        # Tool execution should handle uninitialized database
        result = await server.server.call_tool(
            "create_record",
            {"collection": "users", "data": TestDataFactory.create_user()}
        )
        
        # Should return error response
        assert result is not None
        content = result[0] if isinstance(result, tuple) else result
        response_text = content[0].text if hasattr(content[0], 'text') else str(content[0])
        assert "error" in response_text.lower() or "failed" in response_text.lower()
    
    @pytest.mark.asyncio
    async def test_tool_execution_with_invalid_json_parameters(self, temp_db_path):
        """Test tool execution with invalid JSON parameters."""
        server = MCPServer(db_path=temp_db_path)
        await server.initialize_database()
        
        try:
            # Test with parameters that can't be JSON serialized
            circular_ref = {"name": "test"}
            circular_ref["self"] = circular_ref
            
            result = await server.server.call_tool(
                "create_record",
                {"collection": "users", "data": circular_ref}
            )
            
            # Should handle gracefully
            assert result is not None
            
        finally:
            await server.shutdown_database()
    
    def test_response_formatting_with_invalid_data(self, temp_db_path):
        """Test response formatting with invalid data types."""
        server = MCPServer(db_path=temp_db_path)
        
        # Test with circular reference
        circular_data = {"test": "data"}
        circular_data["self"] = circular_data
        
        # Should handle circular references in response formatting
        try:
            response = server._format_response(
                success=True,
                data=circular_data,
                message="Test",
                count=1
            )
            # If it succeeds, data should be handled somehow
            assert isinstance(response, dict)
        except (ValueError, TypeError) as e:
            # If it fails, should be a known serialization error
            assert "circular" in str(e).lower() or "serialize" in str(e).lower()
    
    def test_logging_with_invalid_messages(self, temp_db_path):
        """Test logging system with invalid message types."""
        server = MCPServer(db_path=temp_db_path)
        
        # Test logging with various invalid types
        invalid_messages = [
            {"dict": "message"},
            ["list", "message"],
            123,
            None,
            object()
        ]
        
        for invalid_msg in invalid_messages:
            try:
                server.logger.info(invalid_msg)
                server.logger.error(invalid_msg)
                server.logger.warning(invalid_msg)
            except Exception as e:
                # Should not raise exceptions that break the application
                assert not isinstance(e, (SystemExit, KeyboardInterrupt))


class TestResponseFormatterErrorHandling:
    """Test error handling in ResponseFormatter."""
    
    def test_success_response_with_invalid_data(self):
        """Test success response creation with invalid data types."""
        # Test with non-serializable data
        class NonSerializable:
            pass
        
        non_serializable = NonSerializable()
        
        # Should handle non-serializable data gracefully
        response = ResponseFormatter.success_response(
            data=non_serializable,
            message="Test",
            count=1,
            operation="test"
        )
        
        # Should either convert to string or handle gracefully
        assert isinstance(response, dict)
        assert "success" in response
    
    def test_error_response_with_none_error_message(self):
        """Test error response creation with None error message."""
        response = ResponseFormatter.error_response(
            error_msg=None,
            operation="test"
        )
        
        TestUtilities.assert_response_structure(response, success=False)
        assert response["error"] is not None  # Should provide default error message
    
    def test_response_validation_with_malformed_response(self):
        """Test response validation with malformed response data."""
        malformed_responses = [
            {},  # Empty response
            {"success": "true"},  # Wrong type for success
            {"success": True, "count": "1"},  # Wrong type for count
            {"success": True, "count": -1},  # Negative count
            {"success": True, "error": "error", "count": 1},  # Success=True but error present
            {"success": False, "error": None, "count": 0}  # Success=False but no error
        ]
        
        for malformed_response in malformed_responses:
            is_valid = ResponseFormatter.validate_response_structure(malformed_response)
            assert is_valid is False
    
    def test_json_serialization_with_complex_data(self):
        """Test JSON serialization with complex data structures."""
        complex_data = {
            "nested": {
                "deep": {
                    "structure": ["with", "arrays", {"and": "objects"}]
                }
            },
            "unicode": "测试数据",
            "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "numbers": [1, 2.5, -3, 0, float('inf')],
            "booleans": [True, False],
            "null_value": None
        }
        
        response = ResponseFormatter.success_response(
            data=complex_data,
            message="Complex data test",
            count=1,
            operation="test"
        )
        
        # Should be able to serialize to JSON
        json_string = ResponseFormatter.to_json_string(response)
        assert isinstance(json_string, str)
        
        # Should be able to parse back
        parsed = json.loads(json_string)
        assert isinstance(parsed, dict)
    
    def test_metadata_handling_with_invalid_types(self):
        """Test metadata handling with invalid data types."""
        invalid_metadata = {
            "function": lambda x: x,  # Non-serializable function
            "class": TestUtilities,  # Class object
            "module": sys  # Module object
        }
        
        # Should handle invalid metadata gracefully
        response = ResponseFormatter.success_response(
            data={"test": "data"},
            message="Test",
            count=1,
            operation="test",
            metadata=invalid_metadata
        )
        
        # Should either filter out invalid data or convert to string
        assert isinstance(response, dict)
        assert "metadata" in response


class TestQueryParserErrorHandling:
    """Test error handling in QueryParser."""
    
    def setup_method(self):
        """Set up parser for each test."""
        self.parser = QueryParser()
    
    def test_parse_query_with_invalid_operators(self):
        """Test parsing queries with invalid operators."""
        invalid_queries = [
            {"field": {"invalid_operator": "value"}},
            {"field": {"": "empty_operator"}},
            {"field": {123: "numeric_operator"}},
            {"field": {"operator": None}},
            {"field": {"nested": {"too": {"deep": "structure"}}}}
        ]
        
        for invalid_query in invalid_queries:
            with pytest.raises(ValueError):
                self.parser.parse_query(invalid_query)
    
    def test_parse_query_with_invalid_logical_operators(self):
        """Test parsing queries with invalid logical operators."""
        invalid_logical_queries = [
            {"$and": "not_a_list"},
            {"$or": {}},
            {"$not": []},
            {"$and": [{}]},  # Empty condition in AND
            {"$or": [None]},  # None condition in OR
            {"$invalid_logical": [{"field": "value"}]}
        ]
        
        for invalid_query in invalid_logical_queries:
            with pytest.raises(ValueError):
                self.parser.parse_query(invalid_query)
    
    def test_parse_query_with_type_mismatches(self):
        """Test parsing queries with type mismatches."""
        type_mismatch_queries = [
            {"field": {"gt": "not_a_number"}},  # gt expects number
            {"field": {"in": "not_a_list"}},  # in expects list
            {"field": {"between": "not_a_range"}},  # between expects list/tuple
            {"field": {"between": [1]}},  # between expects 2 values
            {"field": {"between": [1, 2, 3]}},  # between expects exactly 2 values
            {"field": {"exists": "not_a_boolean"}}  # exists expects boolean
        ]
        
        for invalid_query in type_mismatch_queries:
            with pytest.raises(ValueError):
                self.parser.parse_query(invalid_query)
    
    def test_parse_query_with_extremely_nested_structure(self):
        """Test parsing queries with extremely nested logical structures."""
        # Create deeply nested query
        nested_query = {"field": "value"}
        for i in range(100):  # Very deep nesting
            nested_query = {"$and": [nested_query, {"field2": f"value{i}"}]}
        
        # Should either parse successfully or fail gracefully
        try:
            result = self.parser.parse_query(nested_query)
            assert result is not None
        except (RecursionError, ValueError) as e:
            # Should handle deep nesting gracefully
            assert "recursion" in str(e).lower() or "nested" in str(e).lower() or "complex" in str(e).lower()
    
    def test_validate_query_syntax_with_edge_cases(self):
        """Test query syntax validation with edge cases."""
        edge_case_queries = [
            {"": "empty_field_name"},
            {None: "none_field_name"},
            {123: "numeric_field_name"},
            {"field": {"": "empty_operator"}},
            {"field": {None: "none_operator"}},
            {"field": {"op": ""}},  # Empty value
            {"field": {"op": None}},  # None value
        ]
        
        for edge_case_query in edge_case_queries:
            with pytest.raises((ValueError, TypeError)):
                self.parser.validate_query_syntax(edge_case_query)
    
    def test_get_supported_operators_consistency(self):
        """Test that supported operators are consistent with parser implementation."""
        operators = self.parser.get_supported_operators()
        
        # Test that all listed operators actually work
        for category, ops in operators.items():
            if category == "logical":
                continue  # Logical operators have different syntax
                
            for op in ops:
                test_query = {"test_field": {op: "test_value"}}
                
                try:
                    # Should not raise exception for supported operators
                    self.parser.validate_query_syntax(test_query)
                except ValueError as e:
                    # Some operators might need specific value types
                    if op in ["in", "not_in"]:
                        test_query = {"test_field": {op: ["test_value"]}}
                        self.parser.validate_query_syntax(test_query)
                    elif op in ["between"]:
                        test_query = {"test_field": {op: [1, 2]}}
                        self.parser.validate_query_syntax(test_query)
                    elif op in ["exists"]:
                        test_query = {"test_field": {op: True}}
                        self.parser.validate_query_syntax(test_query)
                    else:
                        raise e  # Re-raise if not a known special case


class TestIntegrationErrorHandling:
    """Test error handling in integrated scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        self.db_path = TestDatabaseFactory.create_temp_db()
        self.db_manager = DatabaseManager(self.db_path)
    
    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        TestDatabaseFactory.cleanup_temp_db(self.db_path)
    
    def test_end_to_end_error_propagation(self):
        """Test that errors propagate correctly through the entire stack."""
        # Create invalid data that should fail at database level
        invalid_user = TestDataFactory.create_invalid_user()
        
        # Test error propagation through database manager
        db_result = self.db_manager.create_record("users", invalid_user)
        TestUtilities.assert_response_structure(db_result, success=False)
        
        # Test error propagation through response formatter
        formatted_response = ResponseFormatter.from_database_result(
            db_result, "create", "users"
        )
        TestUtilities.assert_response_structure(formatted_response, success=False)
        
        # Errors should be preserved through the chain
        assert formatted_response["error"] is not None
        assert formatted_response["success"] is False
    
    def test_recovery_after_errors(self):
        """Test system recovery after encountering errors."""
        # Cause an error
        invalid_data = TestDataFactory.create_invalid_user()
        error_result = self.db_manager.create_record("users", invalid_data)
        assert error_result["success"] is False
        
        # System should recover and handle valid operations
        valid_data = TestDataFactory.create_user()
        success_result = self.db_manager.create_record("users", valid_data)
        TestUtilities.assert_response_structure(success_result, success=True)
        
        # Should be able to read the valid record
        read_result = self.db_manager.read_records("users")
        TestUtilities.assert_response_structure(read_result, success=True)
        assert read_result["count"] == 1
    
    def test_error_handling_under_load(self):
        """Test error handling when system is under load."""
        import threading
        import time
        
        results = []
        
        def mixed_operations_thread(thread_id):
            """Perform mix of valid and invalid operations."""
            thread_results = []
            
            for i in range(10):
                if i % 3 == 0:
                    # Invalid operation
                    invalid_data = TestDataFactory.create_invalid_user()
                    result = self.db_manager.create_record("users", invalid_data)
                    thread_results.append(("invalid", result))
                else:
                    # Valid operation
                    valid_data = TestDataFactory.create_user(name=f"User {thread_id}-{i}")
                    result = self.db_manager.create_record("users", valid_data)
                    thread_results.append(("valid", result))
                
                time.sleep(0.01)  # Small delay
            
            results.append(thread_results)
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=mixed_operations_thread, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Analyze results
        total_operations = 0
        successful_operations = 0
        failed_operations = 0
        
        for thread_results in results:
            for operation_type, result in thread_results:
                total_operations += 1
                TestUtilities.assert_response_structure(result)
                
                if result["success"]:
                    successful_operations += 1
                    # Valid operations should succeed
                    assert operation_type == "valid"
                else:
                    failed_operations += 1
                    # Invalid operations should fail
                    assert operation_type == "invalid"
        
        # Should have processed all operations
        assert total_operations == 30  # 3 threads * 10 operations each
        assert successful_operations > 0
        assert failed_operations > 0
        assert successful_operations + failed_operations == total_operations