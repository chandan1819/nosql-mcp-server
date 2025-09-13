"""
Integration tests for complete CRUD workflows and client-server interactions.
Tests end-to-end functionality across all components.
"""

import pytest
import asyncio
import tempfile
import os
import sys
import time
import json
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.manager import DatabaseManager
from mcp_server import MCPServer
from mcp_client import MCPClient
from response_formatter import ResponseFormatter
from database.query_parser import QueryParser
from tests.test_factories import TestDataFactory, TestDatabaseFactory, TestUtilities, MockDataGenerator


class TestEndToEndCRUDWorkflows:
    """Test complete CRUD workflows from start to finish."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.db_path = TestDatabaseFactory.create_temp_db()
        self.db_manager = DatabaseManager(self.db_path)
    
    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        TestDatabaseFactory.cleanup_temp_db(self.db_path)
    
    def test_complete_user_lifecycle(self):
        """Test complete user lifecycle: create, read, update, delete."""
        # 1. CREATE - Add a new user
        user_data = TestDataFactory.create_user(
            name="Integration Test User",
            email="integration@test.com",
            role="Tester"
        )
        
        create_result = self.db_manager.create_record("users", user_data)
        TestUtilities.assert_response_structure(create_result, success=True)
        TestUtilities.assert_record_structure(create_result["data"], "users")
        
        user_id = create_result["data"]["id"]
        assert user_id > 0
        
        # 2. READ - Fetch the created user
        read_result = self.db_manager.read_records("users", {"id": user_id})
        TestUtilities.assert_response_structure(read_result, success=True)
        assert read_result["count"] == 1
        assert read_result["data"][0]["name"] == "Integration Test User"
        assert read_result["data"][0]["email"] == "integration@test.com"
        
        # 3. UPDATE - Modify the user
        update_result = self.db_manager.update_records(
            "users",
            {"id": user_id},
            {"role": "Senior Tester", "email": "senior.integration@test.com"}
        )
        TestUtilities.assert_response_structure(update_result, success=True)
        assert update_result["count"] == 1
        assert update_result["data"][0]["role"] == "Senior Tester"
        assert update_result["data"][0]["email"] == "senior.integration@test.com"
        assert update_result["data"][0]["name"] == "Integration Test User"  # Unchanged
        
        # 4. READ - Verify update
        verify_result = self.db_manager.read_records("users", {"id": user_id})
        TestUtilities.assert_response_structure(verify_result, success=True)
        assert verify_result["data"][0]["role"] == "Senior Tester"
        assert verify_result["data"][0]["email"] == "senior.integration@test.com"
        
        # 5. DELETE - Remove the user
        delete_result = self.db_manager.delete_records("users", {"id": user_id})
        TestUtilities.assert_response_structure(delete_result, success=True)
        assert delete_result["count"] == 1
        
        # 6. READ - Verify deletion
        final_result = self.db_manager.read_records("users", {"id": user_id})
        TestUtilities.assert_response_structure(final_result, success=True)
        assert final_result["count"] == 0
        assert final_result["data"] == []
    
    def test_complete_task_workflow_with_user_assignment(self):
        """Test complete task workflow including user assignment."""
        # First create a user to assign tasks to
        user_data = TestDataFactory.create_user(name="Task Owner", email="owner@test.com")
        user_result = self.db_manager.create_record("users", user_data)
        user_id = user_result["data"]["id"]
        
        # Create a task assigned to the user
        task_data = TestDataFactory.create_task(
            title="Integration Test Task",
            assigned_to=user_id,
            status="pending",
            priority="high"
        )
        
        create_result = self.db_manager.create_record("tasks", task_data)
        TestUtilities.assert_response_structure(create_result, success=True)
        TestUtilities.assert_record_structure(create_result["data"], "tasks")
        
        task_id = create_result["data"]["id"]
        assert create_result["data"]["assigned_to"] == user_id
        
        # Update task status through workflow
        statuses = ["pending", "in_progress", "completed"]
        for status in statuses[1:]:  # Skip pending as it's already set
            update_result = self.db_manager.update_records(
                "tasks",
                {"id": task_id},
                {"status": status}
            )
            TestUtilities.assert_response_structure(update_result, success=True)
            assert update_result["data"][0]["status"] == status
        
        # Test filtering tasks by user assignment
        user_tasks = self.db_manager.read_records("tasks", {"assigned_to": user_id})
        TestUtilities.assert_response_structure(user_tasks, success=True)
        assert user_tasks["count"] == 1
        assert user_tasks["data"][0]["assigned_to"] == user_id
        
        # Test filtering tasks by status
        completed_tasks = self.db_manager.read_records("tasks", {"status": "completed"})
        TestUtilities.assert_response_structure(completed_tasks, success=True)
        assert completed_tasks["count"] == 1
        assert completed_tasks["data"][0]["status"] == "completed"
    
    def test_complete_product_inventory_workflow(self):
        """Test complete product inventory management workflow."""
        # Create multiple products
        products_data = [
            TestDataFactory.create_product(name="Product A", price=100.0, category="Electronics", in_stock=True),
            TestDataFactory.create_product(name="Product B", price=50.0, category="Electronics", in_stock=False),
            TestDataFactory.create_product(name="Product C", price=25.0, category="Books", in_stock=True)
        ]
        
        product_ids = []
        for product_data in products_data:
            result = self.db_manager.create_record("products", product_data)
            TestUtilities.assert_response_structure(result, success=True)
            product_ids.append(result["data"]["id"])
        
        # Test inventory queries
        # 1. All products
        all_products = self.db_manager.read_records("products")
        TestUtilities.assert_response_structure(all_products, success=True)
        assert all_products["count"] == 3
        
        # 2. In-stock products only
        in_stock = self.db_manager.read_records("products", {"in_stock": True})
        TestUtilities.assert_response_structure(in_stock, success=True)
        assert in_stock["count"] == 2
        
        # 3. Products by category
        electronics = self.db_manager.read_records("products", {"category": "Electronics"})
        TestUtilities.assert_response_structure(electronics, success=True)
        assert electronics["count"] == 2
        
        # 4. Price range queries
        expensive = self.db_manager.read_records("products", {"price": {"gt": 75.0}})
        TestUtilities.assert_response_structure(expensive, success=True)
        assert expensive["count"] == 1
        assert expensive["data"][0]["name"] == "Product A"
        
        # Update inventory status
        restock_result = self.db_manager.update_records(
            "products",
            {"in_stock": False},
            {"in_stock": True}
        )
        TestUtilities.assert_response_structure(restock_result, success=True)
        assert restock_result["count"] == 1  # Product B should be restocked
        
        # Verify all products are now in stock
        all_in_stock = self.db_manager.read_records("products", {"in_stock": True})
        TestUtilities.assert_response_structure(all_in_stock, success=True)
        assert all_in_stock["count"] == 3
    
    def test_complex_multi_collection_workflow(self):
        """Test complex workflow involving multiple collections."""
        # Create users
        users = [
            TestDataFactory.create_user(name="Manager", role="Manager"),
            TestDataFactory.create_user(name="Developer 1", role="Developer"),
            TestDataFactory.create_user(name="Developer 2", role="Developer")
        ]
        
        user_ids = []
        for user_data in users:
            result = self.db_manager.create_record("users", user_data)
            user_ids.append(result["data"]["id"])
        
        manager_id, dev1_id, dev2_id = user_ids
        
        # Create tasks assigned to different users
        tasks = [
            TestDataFactory.create_task(title="Design System", assigned_to=manager_id, priority="high"),
            TestDataFactory.create_task(title="Implement Feature A", assigned_to=dev1_id, priority="medium"),
            TestDataFactory.create_task(title="Implement Feature B", assigned_to=dev2_id, priority="medium"),
            TestDataFactory.create_task(title="Code Review", assigned_to=manager_id, priority="low")
        ]
        
        task_ids = []
        for task_data in tasks:
            result = self.db_manager.create_record("tasks", task_data)
            task_ids.append(result["data"]["id"])
        
        # Create products that might be related to the project
        products = [
            TestDataFactory.create_product(name="Development License", price=500.0, category="Software"),
            TestDataFactory.create_product(name="Testing Tools", price=200.0, category="Software")
        ]
        
        for product_data in products:
            self.db_manager.create_record("products", product_data)
        
        # Complex queries across collections
        # 1. All tasks assigned to managers
        manager_tasks = self.db_manager.read_records("tasks", {"assigned_to": manager_id})
        TestUtilities.assert_response_structure(manager_tasks, success=True)
        assert manager_tasks["count"] == 2
        
        # 2. All high priority tasks
        high_priority = self.db_manager.read_records("tasks", {"priority": "high"})
        TestUtilities.assert_response_structure(high_priority, success=True)
        assert high_priority["count"] == 1
        
        # 3. All developers
        developers = self.db_manager.read_records("users", {"role": "Developer"})
        TestUtilities.assert_response_structure(developers, success=True)
        assert developers["count"] == 2
        
        # 4. Software products
        software = self.db_manager.read_records("products", {"category": "Software"})
        TestUtilities.assert_response_structure(software, success=True)
        assert software["count"] == 2
        
        # Simulate project completion workflow
        # 1. Complete all development tasks
        dev_complete = self.db_manager.update_records(
            "tasks",
            {"assigned_to": {"in": [dev1_id, dev2_id]}},
            {"status": "completed"}
        )
        TestUtilities.assert_response_structure(dev_complete, success=True)
        assert dev_complete["count"] == 2
        
        # 2. Update manager tasks to in_progress
        mgr_progress = self.db_manager.update_records(
            "tasks",
            {"assigned_to": manager_id},
            {"status": "in_progress"}
        )
        TestUtilities.assert_response_structure(mgr_progress, success=True)
        assert mgr_progress["count"] == 2
        
        # Verify final state
        completed_tasks = self.db_manager.read_records("tasks", {"status": "completed"})
        in_progress_tasks = self.db_manager.read_records("tasks", {"status": "in_progress"})
        
        assert completed_tasks["count"] == 2
        assert in_progress_tasks["count"] == 2


class TestMCPServerIntegration:
    """Test MCP server integration with database and tools."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path."""
        path = TestDatabaseFactory.create_temp_db()
        yield path
        TestDatabaseFactory.cleanup_temp_db(path)
    
    @pytest.mark.asyncio
    async def test_mcp_server_full_lifecycle(self, temp_db_path):
        """Test complete MCP server lifecycle."""
        server = MCPServer(db_path=temp_db_path)
        
        try:
            # Initialize server
            await server.initialize_database()
            assert server.db_manager is not None
            assert server.db_manager.is_connected()
            
            # Test tool registration
            tools = await server.server.list_tools()
            tool_names = [tool.name for tool in tools]
            
            required_tools = ["create_record", "read_records", "update_record", "delete_record", "search_records"]
            for tool_name in required_tools:
                assert tool_name in tool_names
            
            # Test create operation
            user_data = TestDataFactory.create_user()
            create_result = await server.server.call_tool(
                "create_record",
                {"collection": "users", "data": user_data}
            )
            
            assert create_result is not None
            content = create_result[0] if isinstance(create_result, tuple) else create_result
            response_text = content[0].text
            response_data = json.loads(response_text)
            
            assert response_data["success"] is True
            assert response_data["operation"] == "create"
            assert response_data["count"] == 1
            
            # Test read operation
            read_result = await server.server.call_tool(
                "read_records",
                {"collection": "users"}
            )
            
            content = read_result[0] if isinstance(read_result, tuple) else read_result
            response_text = content[0].text
            response_data = json.loads(response_text)
            
            assert response_data["success"] is True
            assert response_data["operation"] == "read"
            assert response_data["count"] >= 1
            
        finally:
            await server.shutdown_database()
    
    @pytest.mark.asyncio
    async def test_mcp_server_error_handling_integration(self, temp_db_path):
        """Test MCP server error handling in integrated scenarios."""
        server = MCPServer(db_path=temp_db_path)
        
        try:
            await server.initialize_database()
            
            # Test with invalid collection
            invalid_result = await server.server.call_tool(
                "create_record",
                {"collection": "invalid_collection", "data": {"test": "data"}}
            )
            
            content = invalid_result[0] if isinstance(invalid_result, tuple) else invalid_result
            response_text = content[0].text
            
            # Should contain error information
            assert "error" in response_text.lower() or "failed" in response_text.lower()
            
            # Test with invalid data
            invalid_data_result = await server.server.call_tool(
                "create_record",
                {"collection": "users", "data": TestDataFactory.create_invalid_user()}
            )
            
            content = invalid_data_result[0] if isinstance(invalid_data_result, tuple) else invalid_data_result
            response_text = content[0].text
            response_data = json.loads(response_text)
            
            assert response_data["success"] is False
            assert response_data["error"] is not None
            
        finally:
            await server.shutdown_database()
    
    @pytest.mark.asyncio
    async def test_mcp_server_concurrent_operations(self, temp_db_path):
        """Test MCP server handling concurrent operations."""
        server = MCPServer(db_path=temp_db_path)
        
        try:
            await server.initialize_database()
            
            # Create multiple concurrent operations
            async def create_user(user_id):
                user_data = TestDataFactory.create_user(name=f"Concurrent User {user_id}")
                return await server.server.call_tool(
                    "create_record",
                    {"collection": "users", "data": user_data}
                )
            
            # Run concurrent operations
            tasks = [create_user(i) for i in range(5)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All operations should succeed
            successful_operations = 0
            for result in results:
                if not isinstance(result, Exception):
                    content = result[0] if isinstance(result, tuple) else result
                    response_text = content[0].text
                    response_data = json.loads(response_text)
                    if response_data["success"]:
                        successful_operations += 1
            
            assert successful_operations == 5
            
            # Verify all users were created
            read_result = await server.server.call_tool("read_records", {"collection": "users"})
            content = read_result[0] if isinstance(read_result, tuple) else read_result
            response_text = content[0].text
            response_data = json.loads(response_text)
            
            assert response_data["count"] == 5
            
        finally:
            await server.shutdown_database()


class TestClientServerIntegration:
    """Test client-server integration scenarios."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path."""
        path = TestDatabaseFactory.create_temp_db()
        yield path
        TestDatabaseFactory.cleanup_temp_db(path)
    
    def test_client_server_communication_mock(self, temp_db_path):
        """Test client-server communication with mocked server."""
        # Create a mock server command that would work in test environment
        mock_server_command = ["python", "-c", "print('Mock MCP Server')"]
        client = MCPClient(mock_server_command, max_retries=1, retry_delay=0.1)
        
        # Test client initialization
        assert client.max_retries == 1
        assert client.retry_delay == 0.1
        assert client.session is None
    
    @pytest.mark.asyncio
    async def test_client_crud_operations_without_server(self):
        """Test client CRUD operations when server is not available."""
        # Use invalid command to simulate server unavailability
        client = MCPClient(["invalid_command"], max_retries=1, retry_delay=0.1)
        
        # Test that operations return error results instead of raising exceptions
        insert_result = await client.demonstrate_insert_operations()
        assert isinstance(insert_result, dict)
        assert "summary" in insert_result
        assert len(insert_result["summary"]["errors"]) > 0
        
        fetch_result = await client.demonstrate_fetch_operations()
        assert isinstance(fetch_result, dict)
        assert "summary" in fetch_result
        assert len(fetch_result["summary"]["errors"]) > 0
        
        update_result = await client.demonstrate_update_operations()
        assert isinstance(update_result, dict)
        assert "summary" in update_result
        assert len(update_result["summary"]["errors"]) > 0
        
        delete_result = await client.demonstrate_delete_operations()
        assert isinstance(delete_result, dict)
        assert "summary" in delete_result
        assert len(delete_result["summary"]["errors"]) > 0


class TestPerformanceIntegration:
    """Test performance characteristics of integrated system."""
    
    def setup_method(self):
        """Set up test environment."""
        self.db_path = TestDatabaseFactory.create_temp_db()
        self.db_manager = DatabaseManager(self.db_path)
    
    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        TestDatabaseFactory.cleanup_temp_db(self.db_path)
    
    @pytest.mark.performance
    def test_bulk_operations_performance(self):
        """Test performance of bulk operations."""
        # Create large dataset
        users_data = [MockDataGenerator.realistic_user() for _ in range(100)]
        tasks_data = [MockDataGenerator.realistic_task() for _ in range(200)]
        products_data = [MockDataGenerator.realistic_product() for _ in range(50)]
        
        # Measure bulk insert performance
        start_time = time.time()
        
        user_ids = []
        for user_data in users_data:
            result = self.db_manager.create_record("users", user_data)
            if result["success"]:
                user_ids.append(result["data"]["id"])
        
        for task_data in tasks_data:
            if user_ids:
                task_data["assigned_to"] = user_ids[len(user_ids) % len(user_ids)]
            self.db_manager.create_record("tasks", task_data)
        
        for product_data in products_data:
            self.db_manager.create_record("products", product_data)
        
        insert_time = time.time() - start_time
        
        # Measure bulk read performance
        start_time = time.time()
        
        all_users = self.db_manager.read_records("users")
        all_tasks = self.db_manager.read_records("tasks")
        all_products = self.db_manager.read_records("products")
        
        read_time = time.time() - start_time
        
        # Verify results
        assert all_users["count"] == 100
        assert all_tasks["count"] == 200
        assert all_products["count"] == 50
        
        # Performance assertions (adjust thresholds as needed)
        assert insert_time < 10.0, f"Bulk insert took too long: {insert_time:.2f}s"
        assert read_time < 2.0, f"Bulk read took too long: {read_time:.2f}s"
        
        print(f"Performance metrics:")
        print(f"  - Bulk insert (350 records): {insert_time:.2f}s")
        print(f"  - Bulk read (350 records): {read_time:.2f}s")
    
    @pytest.mark.performance
    def test_complex_query_performance(self):
        """Test performance of complex queries."""
        # Create test data
        users = [MockDataGenerator.realistic_user() for _ in range(50)]
        user_ids = []
        for user_data in users:
            result = self.db_manager.create_record("users", user_data)
            if result["success"]:
                user_ids.append(result["data"]["id"])
        
        # Create tasks with various assignments
        for i in range(100):
            task_data = MockDataGenerator.realistic_task()
            if user_ids:
                task_data["assigned_to"] = user_ids[i % len(user_ids)]
            self.db_manager.create_record("tasks", task_data)
        
        # Test complex query performance
        start_time = time.time()
        
        # Complex query with multiple conditions
        complex_query = {
            "$and": [
                {"status": {"in": ["pending", "in_progress"]}},
                {"priority": {"ne": "low"}},
                {"assigned_to": {"exists": True}}
            ]
        }
        
        result = self.db_manager.advanced_search("tasks", complex_query)
        
        query_time = time.time() - start_time
        
        # Verify result
        TestUtilities.assert_response_structure(result, success=True)
        assert result["count"] >= 0
        
        # Performance assertion
        assert query_time < 1.0, f"Complex query took too long: {query_time:.2f}s"
        
        print(f"Complex query performance: {query_time:.3f}s")


class TestDataConsistencyIntegration:
    """Test data consistency across operations."""
    
    def setup_method(self):
        """Set up test environment."""
        self.db_path = TestDatabaseFactory.create_temp_db()
        self.db_manager = DatabaseManager(self.db_path)
    
    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        TestDatabaseFactory.cleanup_temp_db(self.db_path)
    
    def test_referential_integrity_simulation(self):
        """Test simulated referential integrity between collections."""
        # Create users
        user_data = TestDataFactory.create_user(name="Task Owner")
        user_result = self.db_manager.create_record("users", user_data)
        user_id = user_result["data"]["id"]
        
        # Create tasks assigned to the user
        task_data = TestDataFactory.create_task(title="User Task", assigned_to=user_id)
        task_result = self.db_manager.create_record("tasks", task_data)
        task_id = task_result["data"]["id"]
        
        # Verify relationship
        user_tasks = self.db_manager.read_records("tasks", {"assigned_to": user_id})
        assert user_tasks["count"] == 1
        assert user_tasks["data"][0]["id"] == task_id
        
        # Test "cascade" behavior simulation
        # If we were to delete the user, we should handle related tasks
        related_tasks = self.db_manager.read_records("tasks", {"assigned_to": user_id})
        
        # In a real system, we might unassign tasks or delete them
        # Here we'll unassign them
        if related_tasks["count"] > 0:
            unassign_result = self.db_manager.update_records(
                "tasks",
                {"assigned_to": user_id},
                {"assigned_to": None}
            )
            assert unassign_result["success"] is True
        
        # Now delete the user
        delete_result = self.db_manager.delete_records("users", {"id": user_id})
        assert delete_result["success"] is True
        
        # Verify tasks are unassigned
        orphaned_tasks = self.db_manager.read_records("tasks", {"id": task_id})
        assert orphaned_tasks["count"] == 1
        assert orphaned_tasks["data"][0]["assigned_to"] is None
    
    def test_transaction_like_behavior(self):
        """Test transaction-like behavior for related operations."""
        # Simulate a transaction: create user and assign multiple tasks
        user_data = TestDataFactory.create_user(name="Project Manager")
        user_result = self.db_manager.create_record("users", user_data)
        
        if not user_result["success"]:
            # If user creation fails, don't create tasks
            pytest.skip("User creation failed, skipping task creation")
        
        user_id = user_result["data"]["id"]
        
        # Create multiple related tasks
        task_titles = ["Plan Project", "Assign Resources", "Monitor Progress"]
        created_tasks = []
        
        for title in task_titles:
            task_data = TestDataFactory.create_task(title=title, assigned_to=user_id)
            task_result = self.db_manager.create_record("tasks", task_data)
            
            if task_result["success"]:
                created_tasks.append(task_result["data"]["id"])
            else:
                # In a real transaction, we'd rollback
                # Here we'll clean up what we created
                for task_id in created_tasks:
                    self.db_manager.delete_records("tasks", {"id": task_id})
                self.db_manager.delete_records("users", {"id": user_id})
                pytest.fail("Task creation failed, simulated rollback")
        
        # Verify all tasks were created and assigned
        user_tasks = self.db_manager.read_records("tasks", {"assigned_to": user_id})
        assert user_tasks["count"] == len(task_titles)
        
        # Verify task titles
        created_titles = [task["title"] for task in user_tasks["data"]]
        for title in task_titles:
            assert title in created_titles


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])