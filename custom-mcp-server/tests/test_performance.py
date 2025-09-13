"""
Performance tests for database operations and MCP server functionality.
Tests system behavior under load and measures performance metrics.
"""

import pytest
import time
import asyncio
import threading
import statistics
import sys
import os
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.manager import DatabaseManager
from mcp_server import MCPServer
from tests.test_factories import TestDataFactory, TestDatabaseFactory, MockDataGenerator


class PerformanceMetrics:
    """Utility class for collecting and analyzing performance metrics."""
    
    def __init__(self):
        self.measurements = []
    
    def add_measurement(self, operation: str, duration: float, success: bool = True, **metadata):
        """Add a performance measurement."""
        self.measurements.append({
            "operation": operation,
            "duration": duration,
            "success": success,
            "timestamp": time.time(),
            **metadata
        })
    
    def get_stats(self, operation: str = None) -> Dict[str, Any]:
        """Get performance statistics for an operation or all operations."""
        measurements = self.measurements
        if operation:
            measurements = [m for m in measurements if m["operation"] == operation]
        
        if not measurements:
            return {"count": 0}
        
        durations = [m["duration"] for m in measurements if m["success"]]
        success_count = sum(1 for m in measurements if m["success"])
        
        if not durations:
            return {"count": len(measurements), "success_rate": 0.0}
        
        return {
            "count": len(measurements),
            "success_count": success_count,
            "success_rate": success_count / len(measurements),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "avg_duration": statistics.mean(durations),
            "median_duration": statistics.median(durations),
            "total_duration": sum(durations)
        }
    
    def print_report(self):
        """Print a performance report."""
        operations = set(m["operation"] for m in self.measurements)
        
        print("\n" + "=" * 60)
        print("PERFORMANCE REPORT")
        print("=" * 60)
        
        for operation in sorted(operations):
            stats = self.get_stats(operation)
            print(f"\n{operation.upper()}:")
            print(f"  Count: {stats['count']}")
            print(f"  Success Rate: {stats['success_rate']:.1%}")
            if stats['success_count'] > 0:
                print(f"  Avg Duration: {stats['avg_duration']:.3f}s")
                print(f"  Min Duration: {stats['min_duration']:.3f}s")
                print(f"  Max Duration: {stats['max_duration']:.3f}s")
                print(f"  Median Duration: {stats['median_duration']:.3f}s")
        
        overall_stats = self.get_stats()
        print(f"\nOVERALL:")
        print(f"  Total Operations: {overall_stats['count']}")
        print(f"  Success Rate: {overall_stats['success_rate']:.1%}")
        if overall_stats['success_count'] > 0:
            print(f"  Total Time: {overall_stats['total_duration']:.3f}s")
            print(f"  Avg Duration: {overall_stats['avg_duration']:.3f}s")


@pytest.mark.performance
class TestDatabasePerformance:
    """Performance tests for database operations."""
    
    def setup_method(self):
        """Set up test environment."""
        self.db_path = TestDatabaseFactory.create_temp_db()
        self.db_manager = DatabaseManager(self.db_path)
        self.metrics = PerformanceMetrics()
    
    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        TestDatabaseFactory.cleanup_temp_db(self.db_path)
        
        # Print performance report
        if hasattr(self, 'metrics'):
            self.metrics.print_report()
    
    def test_single_record_operations_performance(self):
        """Test performance of single record operations."""
        # Test CREATE performance
        user_data = TestDataFactory.create_user()
        
        start_time = time.time()
        create_result = self.db_manager.create_record("users", user_data)
        create_duration = time.time() - start_time
        
        self.metrics.add_measurement("create_single", create_duration, create_result["success"])
        
        assert create_result["success"]
        assert create_duration < 0.1, f"Single create took too long: {create_duration:.3f}s"
        
        user_id = create_result["data"]["id"]
        
        # Test READ performance
        start_time = time.time()
        read_result = self.db_manager.read_records("users", {"id": user_id})
        read_duration = time.time() - start_time
        
        self.metrics.add_measurement("read_single", read_duration, read_result["success"])
        
        assert read_result["success"]
        assert read_duration < 0.05, f"Single read took too long: {read_duration:.3f}s"
        
        # Test UPDATE performance
        start_time = time.time()
        update_result = self.db_manager.update_records("users", {"id": user_id}, {"role": "Updated"})
        update_duration = time.time() - start_time
        
        self.metrics.add_measurement("update_single", update_duration, update_result["success"])
        
        assert update_result["success"]
        assert update_duration < 0.1, f"Single update took too long: {update_duration:.3f}s"
        
        # Test DELETE performance
        start_time = time.time()
        delete_result = self.db_manager.delete_records("users", {"id": user_id})
        delete_duration = time.time() - start_time
        
        self.metrics.add_measurement("delete_single", delete_duration, delete_result["success"])
        
        assert delete_result["success"]
        assert delete_duration < 0.1, f"Single delete took too long: {delete_duration:.3f}s"
    
    def test_bulk_operations_performance(self):
        """Test performance of bulk operations."""
        # Prepare bulk data
        users_data = [MockDataGenerator.realistic_user() for _ in range(100)]
        tasks_data = [MockDataGenerator.realistic_task() for _ in range(200)]
        products_data = [MockDataGenerator.realistic_product() for _ in range(50)]
        
        # Test bulk CREATE performance
        start_time = time.time()
        
        user_ids = []
        for user_data in users_data:
            result = self.db_manager.create_record("users", user_data)
            if result["success"]:
                user_ids.append(result["data"]["id"])
        
        bulk_create_duration = time.time() - start_time
        self.metrics.add_measurement("bulk_create_users", bulk_create_duration, len(user_ids) == len(users_data))
        
        # Create tasks with user assignments
        start_time = time.time()
        
        task_ids = []
        for i, task_data in enumerate(tasks_data):
            if user_ids:
                task_data["assigned_to"] = user_ids[i % len(user_ids)]
            result = self.db_manager.create_record("tasks", task_data)
            if result["success"]:
                task_ids.append(result["data"]["id"])
        
        bulk_create_tasks_duration = time.time() - start_time
        self.metrics.add_measurement("bulk_create_tasks", bulk_create_tasks_duration, len(task_ids) == len(tasks_data))
        
        # Create products
        start_time = time.time()
        
        product_ids = []
        for product_data in products_data:
            result = self.db_manager.create_record("products", product_data)
            if result["success"]:
                product_ids.append(result["data"]["id"])
        
        bulk_create_products_duration = time.time() - start_time
        self.metrics.add_measurement("bulk_create_products", bulk_create_products_duration, len(product_ids) == len(products_data))
        
        # Test bulk READ performance
        start_time = time.time()
        all_users = self.db_manager.read_records("users")
        bulk_read_users_duration = time.time() - start_time
        self.metrics.add_measurement("bulk_read_users", bulk_read_users_duration, all_users["success"])
        
        start_time = time.time()
        all_tasks = self.db_manager.read_records("tasks")
        bulk_read_tasks_duration = time.time() - start_time
        self.metrics.add_measurement("bulk_read_tasks", bulk_read_tasks_duration, all_tasks["success"])
        
        start_time = time.time()
        all_products = self.db_manager.read_records("products")
        bulk_read_products_duration = time.time() - start_time
        self.metrics.add_measurement("bulk_read_products", bulk_read_products_duration, all_products["success"])
        
        # Verify results
        assert all_users["count"] == 100
        assert all_tasks["count"] == 200
        assert all_products["count"] == 50
        
        # Performance assertions
        assert bulk_create_duration < 5.0, f"Bulk user creation took too long: {bulk_create_duration:.3f}s"
        assert bulk_create_tasks_duration < 10.0, f"Bulk task creation took too long: {bulk_create_tasks_duration:.3f}s"
        assert bulk_read_users_duration < 1.0, f"Bulk user read took too long: {bulk_read_users_duration:.3f}s"
    
    def test_concurrent_operations_performance(self):
        """Test performance under concurrent load."""
        def create_user_batch(batch_id: int, batch_size: int = 10) -> List[Tuple[float, bool]]:
            """Create a batch of users and return timing results."""
            results = []
            for i in range(batch_size):
                user_data = TestDataFactory.create_user(name=f"Concurrent User {batch_id}-{i}")
                
                start_time = time.time()
                result = self.db_manager.create_record("users", user_data)
                duration = time.time() - start_time
                
                results.append((duration, result["success"]))
            
            return results
        
        # Run concurrent batches
        num_threads = 5
        batch_size = 20
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(create_user_batch, i, batch_size) for i in range(num_threads)]
            
            all_results = []
            for future in as_completed(futures):
                batch_results = future.result()
                all_results.extend(batch_results)
        
        total_duration = time.time() - start_time
        
        # Analyze results
        successful_operations = sum(1 for _, success in all_results if success)
        total_operations = len(all_results)
        operation_durations = [duration for duration, success in all_results if success]
        
        self.metrics.add_measurement("concurrent_operations", total_duration, 
                                   successful_operations == total_operations,
                                   operations_count=total_operations,
                                   success_rate=successful_operations/total_operations)
        
        # Verify results
        assert successful_operations == total_operations, f"Some concurrent operations failed: {successful_operations}/{total_operations}"
        assert total_duration < 10.0, f"Concurrent operations took too long: {total_duration:.3f}s"
        
        # Verify all users were created
        all_users = self.db_manager.read_records("users")
        assert all_users["count"] == total_operations
        
        # Performance metrics
        avg_operation_time = statistics.mean(operation_durations)
        max_operation_time = max(operation_durations)
        
        print(f"Concurrent performance metrics:")
        print(f"  Total operations: {total_operations}")
        print(f"  Total time: {total_duration:.3f}s")
        print(f"  Operations per second: {total_operations/total_duration:.1f}")
        print(f"  Avg operation time: {avg_operation_time:.3f}s")
        print(f"  Max operation time: {max_operation_time:.3f}s")
    
    def test_complex_query_performance(self):
        """Test performance of complex queries."""
        # Create test data with varied attributes
        users = []
        for i in range(50):
            user_data = MockDataGenerator.realistic_user()
            # Add some variation for testing
            if i % 5 == 0:
                user_data["role"] = "Manager"
            elif i % 3 == 0:
                user_data["role"] = "Senior Developer"
            result = self.db_manager.create_record("users", user_data)
            if result["success"]:
                users.append(result["data"])
        
        # Create tasks with various assignments and statuses
        for i in range(100):
            task_data = MockDataGenerator.realistic_task()
            if users:
                task_data["assigned_to"] = users[i % len(users)]["id"]
            # Vary status and priority for testing
            if i % 4 == 0:
                task_data["status"] = "completed"
                task_data["priority"] = "high"
            elif i % 3 == 0:
                task_data["status"] = "in_progress"
                task_data["priority"] = "urgent"
            
            self.db_manager.create_record("tasks", task_data)
        
        # Test various complex queries
        complex_queries = [
            # Simple equality
            {"status": "completed"},
            
            # Multiple conditions (AND)
            {"status": "in_progress", "priority": "high"},
            
            # OR conditions
            {"$or": [{"priority": "urgent"}, {"priority": "high"}]},
            
            # Complex nested query
            {
                "$and": [
                    {"status": {"in": ["pending", "in_progress"]}},
                    {
                        "$or": [
                            {"priority": "urgent"},
                            {"assigned_to": {"exists": True}}
                        ]
                    }
                ]
            },
            
            # Range query
            {"assigned_to": {"gt": 0}},
            
            # NOT condition
            {"$not": {"status": "cancelled"}}
        ]
        
        for i, query in enumerate(complex_queries):
            start_time = time.time()
            result = self.db_manager.advanced_search("tasks", query)
            duration = time.time() - start_time
            
            self.metrics.add_measurement(f"complex_query_{i}", duration, result["success"])
            
            assert result["success"], f"Complex query {i} failed: {result.get('error', 'Unknown error')}"
            assert duration < 0.5, f"Complex query {i} took too long: {duration:.3f}s"
    
    def test_memory_usage_under_load(self):
        """Test memory usage characteristics under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create a large dataset
        large_dataset_size = 500
        
        start_time = time.time()
        
        for i in range(large_dataset_size):
            # Create user
            user_data = MockDataGenerator.realistic_user()
            user_result = self.db_manager.create_record("users", user_data)
            
            # Create tasks for user
            if user_result["success"]:
                user_id = user_result["data"]["id"]
                for j in range(3):  # 3 tasks per user
                    task_data = MockDataGenerator.realistic_task(assigned_to=user_id)
                    self.db_manager.create_record("tasks", task_data)
            
            # Check memory every 100 operations
            if i % 100 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory
                
                # Memory shouldn't grow excessively
                assert memory_increase < 100, f"Memory usage increased too much: {memory_increase:.1f}MB"
        
        total_duration = time.time() - start_time
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        self.metrics.add_measurement("memory_load_test", total_duration, True,
                                   records_created=large_dataset_size * 4,  # users + 3 tasks each
                                   memory_increase_mb=memory_increase)
        
        # Verify data was created
        users_count = self.db_manager.read_records("users")["count"]
        tasks_count = self.db_manager.read_records("tasks")["count"]
        
        assert users_count == large_dataset_size
        assert tasks_count == large_dataset_size * 3
        
        print(f"Memory usage test:")
        print(f"  Records created: {large_dataset_size * 4}")
        print(f"  Time taken: {total_duration:.3f}s")
        print(f"  Memory increase: {memory_increase:.1f}MB")
        print(f"  Records per second: {(large_dataset_size * 4)/total_duration:.1f}")


@pytest.mark.performance
class TestMCPServerPerformance:
    """Performance tests for MCP server operations."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path."""
        path = TestDatabaseFactory.create_temp_db()
        yield path
        TestDatabaseFactory.cleanup_temp_db(path)
    
    def setup_method(self):
        """Set up test environment."""
        self.metrics = PerformanceMetrics()
    
    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'metrics'):
            self.metrics.print_report()
    
    @pytest.mark.asyncio
    async def test_mcp_tool_call_performance(self, temp_db_path):
        """Test performance of MCP tool calls."""
        server = MCPServer(db_path=temp_db_path)
        
        try:
            await server.initialize_database()
            
            # Test create tool performance
            user_data = TestDataFactory.create_user()
            
            start_time = time.time()
            create_result = await server.server.call_tool(
                "create_record",
                {"collection": "users", "data": user_data}
            )
            create_duration = time.time() - start_time
            
            self.metrics.add_measurement("mcp_create", create_duration, create_result is not None)
            
            assert create_result is not None
            assert create_duration < 0.2, f"MCP create took too long: {create_duration:.3f}s"
            
            # Test read tool performance
            start_time = time.time()
            read_result = await server.server.call_tool(
                "read_records",
                {"collection": "users"}
            )
            read_duration = time.time() - start_time
            
            self.metrics.add_measurement("mcp_read", read_duration, read_result is not None)
            
            assert read_result is not None
            assert read_duration < 0.2, f"MCP read took too long: {read_duration:.3f}s"
            
        finally:
            await server.shutdown_database()
    
    @pytest.mark.asyncio
    async def test_mcp_concurrent_tool_calls(self, temp_db_path):
        """Test performance of concurrent MCP tool calls."""
        server = MCPServer(db_path=temp_db_path)
        
        try:
            await server.initialize_database()
            
            async def create_user_via_mcp(user_id: int):
                """Create user via MCP tool call."""
                user_data = TestDataFactory.create_user(name=f"MCP User {user_id}")
                
                start_time = time.time()
                result = await server.server.call_tool(
                    "create_record",
                    {"collection": "users", "data": user_data}
                )
                duration = time.time() - start_time
                
                return duration, result is not None
            
            # Run concurrent MCP operations
            num_operations = 20
            
            start_time = time.time()
            tasks = [create_user_via_mcp(i) for i in range(num_operations)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_duration = time.time() - start_time
            
            # Analyze results
            successful_operations = 0
            operation_durations = []
            
            for result in results:
                if not isinstance(result, Exception):
                    duration, success = result
                    if success:
                        successful_operations += 1
                        operation_durations.append(duration)
            
            self.metrics.add_measurement("mcp_concurrent", total_duration,
                                       successful_operations == num_operations,
                                       operations_count=num_operations,
                                       success_rate=successful_operations/num_operations)
            
            # Verify results
            assert successful_operations == num_operations, f"Some MCP operations failed: {successful_operations}/{num_operations}"
            assert total_duration < 5.0, f"Concurrent MCP operations took too long: {total_duration:.3f}s"
            
            # Performance metrics
            if operation_durations:
                avg_operation_time = statistics.mean(operation_durations)
                max_operation_time = max(operation_durations)
                
                print(f"MCP concurrent performance:")
                print(f"  Operations: {num_operations}")
                print(f"  Total time: {total_duration:.3f}s")
                print(f"  Avg operation time: {avg_operation_time:.3f}s")
                print(f"  Max operation time: {max_operation_time:.3f}s")
                print(f"  Operations per second: {num_operations/total_duration:.1f}")
            
        finally:
            await server.shutdown_database()


if __name__ == "__main__":
    # Run performance tests with detailed output
    pytest.main([__file__, "-v", "-s", "-m", "performance", "--tb=short"])