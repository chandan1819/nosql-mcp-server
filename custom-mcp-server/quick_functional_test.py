#!/usr/bin/env python3
"""
Quick functional test for Custom MCP Server.
Tests core functionality without full client-server setup.
"""

import os
import sys
import json
from pathlib import Path

# Change to script directory and add src to path
script_dir = Path(__file__).parent
os.chdir(script_dir)
sys.path.insert(0, "src")

def print_status(message: str, status: str = "INFO") -> None:
    """Print a status message."""
    status_symbols = {
        "INFO": "ℹ",
        "SUCCESS": "✓",
        "WARNING": "⚠",
        "ERROR": "✗",
        "PROGRESS": "→"
    }
    symbol = status_symbols.get(status, "•")
    print(f"{symbol} {message}")

def test_database_operations():
    """Test basic database operations."""
    print_status("Testing database operations...", "PROGRESS")
    
    try:
        from database.manager import DatabaseManager
        
        # Use a test database
        test_db_path = "data/test_functional.json"
        
        with DatabaseManager(test_db_path) as db:
            # Test CREATE
            user_data = {
                "name": "Test User",
                "email": "test@example.com",
                "role": "user"
            }
            
            result = db.create_record("users", user_data)
            if not result.get("success"):
                print_status(f"CREATE failed: {result.get('error')}", "ERROR")
                return False
            
            user_id = result["data"]["id"]
            print_status(f"CREATE: Created user with ID {user_id}", "SUCCESS")
            
            # Test READ
            users = db.read_records("users")
            if not users or len(users) == 0:
                print_status("READ failed: No users found", "ERROR")
                return False
            
            print_status(f"READ: Found {len(users)} users", "SUCCESS")
            
            # Test UPDATE
            update_result = db.update_records("users", {"id": user_id}, {"role": "admin"})
            if update_result == 0:
                print_status("UPDATE failed: No records updated", "ERROR")
                return False
            
            print_status(f"UPDATE: Updated {update_result} records", "SUCCESS")
            
            # Test DELETE
            delete_result = db.delete_records("users", {"id": user_id})
            if delete_result == 0:
                print_status("DELETE failed: No records deleted", "ERROR")
                return False
            
            print_status(f"DELETE: Deleted {delete_result} records", "SUCCESS")
        
        # Clean up test database
        if Path(test_db_path).exists():
            Path(test_db_path).unlink()
        
        return True
        
    except Exception as e:
        print_status(f"Database test failed: {e}", "ERROR")
        return False

def test_response_formatter():
    """Test response formatting utilities."""
    print_status("Testing response formatter...", "PROGRESS")
    
    try:
        from response_formatter import ResponseFormatter
        
        # Test success response
        success_response = ResponseFormatter.success_response("Test data", "Operation successful", count=1)
        if not success_response.get("success"):
            print_status("Success response formatting failed", "ERROR")
            return False
        
        # Test error response
        error_response = ResponseFormatter.error_response("Test error", "ERROR_CODE")
        if error_response.get("success"):
            print_status("Error response formatting failed", "ERROR")
            return False
        
        print_status("Response formatter working correctly", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Response formatter test failed: {e}", "ERROR")
        return False

def test_query_parser():
    """Test query parsing functionality."""
    print_status("Testing query parser...", "PROGRESS")
    
    try:
        from database.query_parser import QueryParser
        
        parser = QueryParser()
        
        # Test simple query
        simple_query = {"name": "John"}
        parsed = parser.parse_query(simple_query)
        if parsed is None:
            print_status("Simple query parsing failed", "ERROR")
            return False
        
        # Test complex query
        complex_query = {"age": {"$gt": 18}, "status": "active"}
        parsed_complex = parser.parse_query(complex_query)
        if parsed_complex is None:
            print_status("Complex query parsing failed", "ERROR")
            return False
        
        print_status("Query parser working correctly", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Query parser test failed: {e}", "ERROR")
        return False

def test_database_initialization():
    """Test database initialization with sample data."""
    print_status("Testing database initialization...", "PROGRESS")
    
    try:
        from database.manager import DatabaseManager
        
        # Test with a temporary database
        test_db_path = "data/test_init.json"
        
        # Remove if exists
        if Path(test_db_path).exists():
            Path(test_db_path).unlink()
        
        # Initialize using DatabaseManager
        with DatabaseManager(test_db_path) as db:
            # This should create the database and initialize sample data
            db.initialize_sample_data()
            
            # Check if data was populated
            users = db.read_records("users")
            tasks = db.read_records("tasks")
            products = db.read_records("products")
            
            if len(users) < 3 or len(tasks) < 5 or len(products) < 4:
                print_status(f"Insufficient sample data: users={len(users)}, tasks={len(tasks)}, products={len(products)}", "ERROR")
                return False
        
        # Clean up
        if Path(test_db_path).exists():
            Path(test_db_path).unlink()
        
        print_status("Database initialization working correctly", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Database initialization test failed: {e}", "ERROR")
        return False

def main():
    """Run all functional tests."""
    print("=" * 60)
    print(" Custom MCP Server Functional Tests ")
    print("=" * 60)
    
    tests = [
        ("Database Operations", test_database_operations),
        ("Response Formatter", test_response_formatter),
        ("Query Parser", test_query_parser),
        ("Database Initialization", test_database_initialization)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_status(f"Test error: {e}", "ERROR")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f" Test Results: {passed} passed, {failed} failed ")
    print("=" * 60)
    
    if failed == 0:
        print_status("All functional tests passed! 🎉", "SUCCESS")
        print_status("Core functionality is working correctly.", "SUCCESS")
        return True
    else:
        print_status(f"{failed} test(s) failed.", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)