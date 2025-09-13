"""
Response formatting utilities for consistent MCP tool responses.
Provides standardized JSON response structures with success/failure indicators.
"""

import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone


class ResponseFormatter:
    """
    Utility class for formatting consistent JSON responses across all MCP tools.
    Ensures all responses follow the same structure and include proper metadata.
    """
    
    @staticmethod
    def success_response(
        data: Any = None,
        message: str = "Operation completed successfully",
        count: int = 0,
        operation: str = "operation",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format a successful operation response.
        
        Args:
            data: The actual result data
            message: Human-readable success message
            count: Number of records affected
            operation: Name of the operation performed
            metadata: Additional metadata to include
            
        Returns:
            Formatted success response dictionary
        """
        response = {
            "success": True,
            "data": data,
            "message": message,
            "count": count,
            "error": None,
            "operation": operation,
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        if metadata:
            response["metadata"] = metadata
            
        return response
    
    @staticmethod
    def error_response(
        error_msg: str,
        operation: str = "operation",
        error_code: Optional[str] = None,
        data: Any = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format an error response with detailed error information.
        
        Args:
            error_msg: Detailed error message
            operation: Name of the operation that failed
            error_code: Optional error code for categorization
            data: Any partial data that was retrieved before error
            metadata: Additional metadata to include
            
        Returns:
            Formatted error response dictionary
        """
        response = {
            "success": False,
            "data": data,
            "message": f"{operation.capitalize()} failed",
            "count": 0,
            "error": error_msg,
            "operation": operation,
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        if error_code:
            response["error_code"] = error_code
            
        if metadata:
            response["metadata"] = metadata
            
        return response
    
    @staticmethod
    def create_response(
        created_record: Dict[str, Any],
        collection: str
    ) -> Dict[str, Any]:
        """
        Format a response for record creation operations.
        
        Args:
            created_record: The newly created record
            collection: Name of the collection
            
        Returns:
            Formatted create response
        """
        return ResponseFormatter.success_response(
            data=created_record,
            message=f"Record created successfully in {collection}",
            count=1,
            operation="create",
            metadata={"collection": collection, "record_id": created_record.get("id")}
        )
    
    @staticmethod
    def read_response(
        records: List[Dict[str, Any]],
        collection: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format a response for record read operations.
        
        Args:
            records: List of retrieved records
            collection: Name of the collection
            filters: Filters that were applied
            
        Returns:
            Formatted read response
        """
        metadata = {"collection": collection}
        if filters:
            metadata["filters_applied"] = filters
            
        return ResponseFormatter.success_response(
            data=records,
            message=f"Successfully retrieved {len(records)} records from {collection}",
            count=len(records),
            operation="read",
            metadata=metadata
        )
    
    @staticmethod
    def update_response(
        updated_records: List[Dict[str, Any]],
        collection: str,
        filters: Dict[str, Any],
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format a response for record update operations.
        
        Args:
            updated_records: List of updated records
            collection: Name of the collection
            filters: Filters used to identify records
            updates: Updates that were applied
            
        Returns:
            Formatted update response
        """
        return ResponseFormatter.success_response(
            data=updated_records,
            message=f"Successfully updated {len(updated_records)} records in {collection}",
            count=len(updated_records),
            operation="update",
            metadata={
                "collection": collection,
                "filters_applied": filters,
                "updates_applied": updates
            }
        )
    
    @staticmethod
    def delete_response(
        deleted_count: int,
        collection: str,
        filters: Dict[str, Any],
        soft_delete: bool = False
    ) -> Dict[str, Any]:
        """
        Format a response for record deletion operations.
        
        Args:
            deleted_count: Number of records deleted
            collection: Name of the collection
            filters: Filters used to identify records
            soft_delete: Whether soft delete was used
            
        Returns:
            Formatted delete response
        """
        delete_type = "soft deleted" if soft_delete else "deleted"
        
        return ResponseFormatter.success_response(
            data={"deleted_count": deleted_count},
            message=f"Successfully {delete_type} {deleted_count} records from {collection}",
            count=deleted_count,
            operation="delete",
            metadata={
                "collection": collection,
                "filters_applied": filters,
                "soft_delete": soft_delete
            }
        )
    
    @staticmethod
    def search_response(
        matching_records: List[Dict[str, Any]],
        collection: str,
        query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format a response for search operations.
        
        Args:
            matching_records: List of records matching the search
            collection: Name of the collection
            query: Search query that was executed
            
        Returns:
            Formatted search response
        """
        return ResponseFormatter.success_response(
            data=matching_records,
            message=f"Search completed: found {len(matching_records)} matching records in {collection}",
            count=len(matching_records),
            operation="search",
            metadata={
                "collection": collection,
                "search_query": query
            }
        )
    
    @staticmethod
    def validate_response_structure(response: Dict[str, Any]) -> bool:
        """
        Validate that a response follows the expected structure.
        
        Args:
            response: Response dictionary to validate
            
        Returns:
            True if response structure is valid, False otherwise
        """
        required_fields = ["success", "data", "message", "count", "error", "operation", "timestamp"]
        
        # Check all required fields are present
        for field in required_fields:
            if field not in response:
                return False
        
        # Validate field types
        if not isinstance(response["success"], bool):
            return False
            
        if not isinstance(response["message"], str):
            return False
            
        if not isinstance(response["count"], int):
            return False
            
        if not isinstance(response["operation"], str):
            return False
            
        if not isinstance(response["timestamp"], str):
            return False
        
        # Validate success/error consistency
        if response["success"] and response["error"] is not None:
            return False
            
        if not response["success"] and response["error"] is None:
            return False
        
        return True
    
    @staticmethod
    def to_json_string(response: Dict[str, Any], indent: int = 2) -> str:
        """
        Convert response dictionary to formatted JSON string.
        
        Args:
            response: Response dictionary
            indent: JSON indentation level
            
        Returns:
            Formatted JSON string
        """
        return json.dumps(response, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def from_database_result(db_result: Dict[str, Any], operation: str, collection: str) -> Dict[str, Any]:
        """
        Convert a database manager result to a standardized MCP response.
        
        Args:
            db_result: Result from DatabaseManager operation
            operation: Type of operation performed
            collection: Collection name
            
        Returns:
            Standardized MCP response
        """
        if db_result.get("success", False):
            return ResponseFormatter.success_response(
                data=db_result.get("data"),
                message=db_result.get("message", f"{operation.capitalize()} completed successfully"),
                count=db_result.get("count", 0),
                operation=operation,
                metadata={"collection": collection}
            )
        else:
            return ResponseFormatter.error_response(
                error_msg=db_result.get("error", "Unknown error occurred"),
                operation=operation,
                data=db_result.get("data"),
                metadata={"collection": collection}
            )