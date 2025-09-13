"""
Tests for response formatting utilities.
"""

import pytest
import json
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from response_formatter import ResponseFormatter


class TestResponseFormatter:
    """Test cases for response formatting functionality."""
    
    def test_success_response_basic(self):
        """Test basic success response formatting."""
        response = ResponseFormatter.success_response(
            data={"test": "data"},
            message="Test successful",
            count=1,
            operation="test"
        )
        
        assert response["success"] is True
        assert response["data"] == {"test": "data"}
        assert response["message"] == "Test successful"
        assert response["count"] == 1
        assert response["error"] is None
        assert response["operation"] == "test"
        assert "timestamp" in response
        
        # Validate timestamp format
        datetime.fromisoformat(response["timestamp"].replace('Z', '+00:00'))
    
    def test_error_response_basic(self):
        """Test basic error response formatting."""
        response = ResponseFormatter.error_response(
            error_msg="Something went wrong",
            operation="test operation",
            error_code="TEST_ERROR"
        )
        
        assert response["success"] is False
        assert response["data"] is None
        assert response["message"] == "Test operation failed"
        assert response["count"] == 0
        assert response["error"] == "Something went wrong"
        assert response["operation"] == "test operation"
        assert response["error_code"] == "TEST_ERROR"
        assert "timestamp" in response
    
    def test_create_response(self):
        """Test create operation response formatting."""
        created_record = {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com"
        }
        
        response = ResponseFormatter.create_response(created_record, "users")
        
        assert response["success"] is True
        assert response["data"] == created_record
        assert "created successfully in users" in response["message"]
        assert response["count"] == 1
        assert response["operation"] == "create"
        assert response["metadata"]["collection"] == "users"
        assert response["metadata"]["record_id"] == 1
    
    def test_read_response(self):
        """Test read operation response formatting."""
        records = [
            {"id": 1, "name": "User 1"},
            {"id": 2, "name": "User 2"}
        ]
        filters = {"status": "active"}
        
        response = ResponseFormatter.read_response(records, "users", filters)
        
        assert response["success"] is True
        assert response["data"] == records
        assert "retrieved 2 records from users" in response["message"]
        assert response["count"] == 2
        assert response["operation"] == "read"
        assert response["metadata"]["collection"] == "users"
        assert response["metadata"]["filters_applied"] == filters
    
    def test_update_response(self):
        """Test update operation response formatting."""
        updated_records = [{"id": 1, "name": "Updated User"}]
        filters = {"id": 1}
        updates = {"name": "Updated User"}
        
        response = ResponseFormatter.update_response(
            updated_records, "users", filters, updates
        )
        
        assert response["success"] is True
        assert response["data"] == updated_records
        assert "updated 1 records in users" in response["message"]
        assert response["count"] == 1
        assert response["operation"] == "update"
        assert response["metadata"]["collection"] == "users"
        assert response["metadata"]["filters_applied"] == filters
        assert response["metadata"]["updates_applied"] == updates
    
    def test_delete_response(self):
        """Test delete operation response formatting."""
        response = ResponseFormatter.delete_response(
            deleted_count=3,
            collection="users",
            filters={"status": "inactive"},
            soft_delete=False
        )
        
        assert response["success"] is True
        assert response["data"]["deleted_count"] == 3
        assert "deleted 3 records from users" in response["message"]
        assert response["count"] == 3
        assert response["operation"] == "delete"
        assert response["metadata"]["collection"] == "users"
        assert response["metadata"]["filters_applied"] == {"status": "inactive"}
        assert response["metadata"]["soft_delete"] is False
    
    def test_delete_response_soft_delete(self):
        """Test delete operation response formatting with soft delete."""
        response = ResponseFormatter.delete_response(
            deleted_count=2,
            collection="tasks",
            filters={"completed": True},
            soft_delete=True
        )
        
        assert "soft deleted 2 records from tasks" in response["message"]
        assert response["metadata"]["soft_delete"] is True
    
    def test_search_response(self):
        """Test search operation response formatting."""
        matching_records = [
            {"id": 1, "title": "Task 1", "status": "pending"},
            {"id": 2, "title": "Task 2", "status": "pending"}
        ]
        query = {"status": "pending"}
        
        response = ResponseFormatter.search_response(
            matching_records, "tasks", query
        )
        
        assert response["success"] is True
        assert response["data"] == matching_records
        assert "found 2 matching records in tasks" in response["message"]
        assert response["count"] == 2
        assert response["operation"] == "search"
        assert response["metadata"]["collection"] == "tasks"
        assert response["metadata"]["search_query"] == query
    
    def test_validate_response_structure_valid(self):
        """Test response structure validation with valid response."""
        valid_response = ResponseFormatter.success_response(
            data={"test": "data"},
            message="Test message",
            count=1,
            operation="test"
        )
        
        assert ResponseFormatter.validate_response_structure(valid_response) is True
    
    def test_validate_response_structure_missing_field(self):
        """Test response structure validation with missing required field."""
        invalid_response = {
            "success": True,
            "data": {"test": "data"},
            "message": "Test message",
            # Missing count, error, operation, timestamp
        }
        
        assert ResponseFormatter.validate_response_structure(invalid_response) is False
    
    def test_validate_response_structure_wrong_types(self):
        """Test response structure validation with wrong field types."""
        invalid_response = ResponseFormatter.success_response(
            data={"test": "data"},
            message="Test message",
            count=1,
            operation="test"
        )
        invalid_response["success"] = "true"  # Should be boolean
        
        assert ResponseFormatter.validate_response_structure(invalid_response) is False
    
    def test_validate_response_structure_inconsistent_success_error(self):
        """Test response structure validation with inconsistent success/error."""
        invalid_response = ResponseFormatter.success_response(
            data={"test": "data"},
            message="Test message",
            count=1,
            operation="test"
        )
        invalid_response["error"] = "Some error"  # Success=True but error is not None
        
        assert ResponseFormatter.validate_response_structure(invalid_response) is False
    
    def test_to_json_string(self):
        """Test JSON string conversion."""
        response = ResponseFormatter.success_response(
            data={"test": "data"},
            message="Test message",
            count=1,
            operation="test"
        )
        
        json_string = ResponseFormatter.to_json_string(response)
        
        # Should be valid JSON
        parsed = json.loads(json_string)
        assert parsed == response
        
        # Should be formatted with indentation
        assert "\n" in json_string
        assert "  " in json_string  # 2-space indentation
    
    def test_from_database_result_success(self):
        """Test conversion from database result to MCP response (success case)."""
        db_result = {
            "success": True,
            "data": {"id": 1, "name": "Test"},
            "message": "Record created",
            "count": 1,
            "error": None
        }
        
        response = ResponseFormatter.from_database_result(
            db_result, "create", "users"
        )
        
        assert response["success"] is True
        assert response["data"] == {"id": 1, "name": "Test"}
        assert response["message"] == "Record created"
        assert response["count"] == 1
        assert response["operation"] == "create"
        assert response["metadata"]["collection"] == "users"
    
    def test_from_database_result_error(self):
        """Test conversion from database result to MCP response (error case)."""
        db_result = {
            "success": False,
            "data": None,
            "message": "Operation failed",
            "count": 0,
            "error": "Database connection failed"
        }
        
        response = ResponseFormatter.from_database_result(
            db_result, "read", "products"
        )
        
        assert response["success"] is False
        assert response["data"] is None
        assert response["error"] == "Database connection failed"
        assert response["operation"] == "read"
        assert response["metadata"]["collection"] == "products"
    
    def test_response_with_metadata(self):
        """Test response formatting with additional metadata."""
        metadata = {
            "query_time_ms": 45,
            "cache_hit": False,
            "api_version": "1.0"
        }
        
        response = ResponseFormatter.success_response(
            data={"test": "data"},
            message="Test successful",
            count=1,
            operation="test",
            metadata=metadata
        )
        
        assert response["metadata"] == metadata
    
    def test_error_response_with_partial_data(self):
        """Test error response that includes partial data."""
        partial_data = {"partial": "results"}
        
        response = ResponseFormatter.error_response(
            error_msg="Connection timeout",
            operation="fetch data",
            error_code="TIMEOUT",
            data=partial_data
        )
        
        assert response["success"] is False
        assert response["data"] == partial_data
        assert response["error"] == "Connection timeout"
        assert response["error_code"] == "TIMEOUT"