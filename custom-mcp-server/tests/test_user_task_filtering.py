"""
Unit tests for user-specific task filtering functionality.
Tests the specialized methods for fetching tasks by user assignment.
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from database.manager import DatabaseManager


class TestUserTaskFiltering:
    """Test cases for user-specific task filtering functionality."""
    
    def setup_method(self):
        """Set up test database for each test."""
        # Create a temporary database file for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
        
        # Create test data
        self._create_test_data()
    
    def teardown_method(self):
        """Clean up after each test."""
        self.db_manager.close()
        try:
            os.unlink(self.temp_db.name)
        except (PermissionError, FileNotFoundError):
            pass
    
    def _create_test_data(self):
        """Create test data for user task filtering tests."""
        # Create test users
        users = [
            {"name": "Alice Johnson", "email": "alice@example.com", "role": "Manager"},
            {"name": "Bob Smith", "email": "bob@example.com", "role": "Developer"},
            {"name": "Carol Davis", "email": "carol@example.com", "role": "QA Engineer"},
            {"name": "David Wilson", "email": "david@example.com", "role": "DevOps"}
        ]
        
        for user in users:
            self.db_manager.create_record("users", user)
        
        # Create test tasks with various assignments and statuses
        tasks = [
            # Tasks for Alice (user_id: 1)
            {"title": "Project Planning", "status": "pending", "priority": "high", "assigned_to": 1},
            {"title": "Team Meeting", "status": "in_progress", "priority": "medium", "assigned_to": 1},
            {"title": "Budget Review", "status": "completed", "priority": "high", "assigned_to": 1},
            
            # Tasks for Bob (user_id: 2)
            {"title": "Feature Development", "status": "in_progress", "priority": "high", "assigned_to": 2},
            {"title": "Code Review", "status": "pending", "priority": "medium", "assigned_to": 2},
            {"title": "Bug Fixes", "status": "completed", "priority": "low", "assigned_to": 2},
            {"title": "API Integration", "status": "pending", "priority": "urgent", "assigned_to": 2},
            
            # Tasks for Carol (user_id: 3)
            {"title": "Test Planning", "status": "pending", "priority": "medium", "assigned_to": 3},
            {"title": "Automated Testing", "status": "in_progress", "priority": "high", "assigned_to": 3},
            
            # Tasks for David (user_id: 4)
            {"title": "Server Setup", "status": "completed", "priority": "high", "assigned_to": 4},
            
            # Unassigned tasks
            {"title": "Documentation Update", "status": "pending", "priority": "low"},
            {"title": "Research Task", "status": "pending", "priority": "medium"}
        ]
        
        for task in tasks:
            self.db_manager.create_record("tasks", task)
    
    def test_get_tasks_by_user_valid_user(self):
        """Test getting tasks for a valid user."""
        # Get tasks for Alice (user_id: 1)
        result = self.db_manager.get_tasks_by_user(1)
        
        assert result["success"] is True
        assert result["count"] == 3  # Alice has 3 tasks
        assert result["user_id"] == 1
        assert result["status_filter"] is None
        
        # Verify all tasks belong to Alice
        for task in result["data"]:
            assert task["assigned_to"] == 1
        
        # Verify task titles
        task_titles = [task["title"] for task in result["data"]]
        assert "Project Planning" in task_titles
        assert "Team Meeting" in task_titles
        assert "Budget Review" in task_titles
    
    def test_get_tasks_by_user_with_status_filter(self):
        """Test getting tasks for a user with status filtering."""
        # Get pending tasks for Bob (user_id: 2)
        result = self.db_manager.get_tasks_by_user(2, "pending")
        
        assert result["success"] is True
        assert result["count"] == 2  # Bob has 2 pending tasks
        assert result["user_id"] == 2
        assert result["status_filter"] == "pending"
        
        # Verify all tasks are pending and belong to Bob
        for task in result["data"]:
            assert task["assigned_to"] == 2
            assert task["status"] == "pending"
        
        # Verify task titles
        task_titles = [task["title"] for task in result["data"]]
        assert "Code Review" in task_titles
        assert "API Integration" in task_titles
    
    def test_get_tasks_by_user_no_tasks(self):
        """Test getting tasks for a user with no tasks."""
        # Create a new user with no tasks
        new_user = {"name": "Eve Brown", "email": "eve@example.com", "role": "Intern"}
        user_result = self.db_manager.create_record("users", new_user)
        new_user_id = user_result["data"]["id"]
        
        result = self.db_manager.get_tasks_by_user(new_user_id)
        
        assert result["success"] is True
        assert result["count"] == 0
        assert result["data"] == []
        assert result["user_id"] == new_user_id
    
    def test_get_tasks_by_user_nonexistent_user(self):
        """Test getting tasks for a non-existent user."""
        result = self.db_manager.get_tasks_by_user(999)
        
        assert result["success"] is True
        assert result["count"] == 0
        assert result["data"] == []
        assert result["user_id"] == 999
        assert "does not exist" in result["message"]
    
    def test_get_tasks_by_user_invalid_user_id(self):
        """Test getting tasks with invalid user_id."""
        # Test with negative user_id
        result = self.db_manager.get_tasks_by_user(-1)
        
        assert result["success"] is False
        assert "must be a positive integer" in result["error"]
        
        # Test with non-integer user_id
        result = self.db_manager.get_tasks_by_user("not_an_int")
        
        assert result["success"] is False
        assert "must be a positive integer" in result["error"]
    
    def test_get_tasks_by_user_invalid_status_filter(self):
        """Test getting tasks with invalid status filter."""
        result = self.db_manager.get_tasks_by_user(1, "invalid_status")
        
        assert result["success"] is False
        assert "Invalid status filter" in result["error"]
    
    def test_get_user_task_summary_valid_user(self):
        """Test getting task summary for a valid user."""
        # Get summary for Bob (user_id: 2) who has diverse tasks
        result = self.db_manager.get_user_task_summary(2)
        
        assert result["success"] is True
        assert result["count"] == 4  # Bob has 4 tasks total
        
        data = result["data"]
        assert data["user_id"] == 2
        assert data["user_exists"] is True
        assert data["total_tasks"] == 4
        
        # Check status breakdown
        status_counts = data["by_status"]
        assert status_counts["pending"] == 2
        assert status_counts["in_progress"] == 1
        assert status_counts["completed"] == 1
        
        # Check priority breakdown
        priority_counts = data["by_priority"]
        assert priority_counts["high"] == 1
        assert priority_counts["medium"] == 1
        assert priority_counts["low"] == 1
        assert priority_counts["urgent"] == 1
    
    def test_get_user_task_summary_nonexistent_user(self):
        """Test getting task summary for non-existent user."""
        result = self.db_manager.get_user_task_summary(999)
        
        assert result["success"] is True
        assert result["count"] == 0
        
        data = result["data"]
        assert data["user_id"] == 999
        assert data["user_exists"] is False
        assert data["total_tasks"] == 0
        assert data["by_status"] == {}
        assert data["by_priority"] == {}
    
    def test_get_user_task_summary_invalid_user_id(self):
        """Test getting task summary with invalid user_id."""
        result = self.db_manager.get_user_task_summary(-1)
        
        assert result["success"] is False
        assert "must be a positive integer" in result["error"]
    
    def test_get_tasks_by_multiple_users(self):
        """Test getting tasks for multiple users."""
        # Get tasks for Alice and Bob
        result = self.db_manager.get_tasks_by_multiple_users([1, 2])
        
        assert result["success"] is True
        assert result["count"] == 7  # Alice has 3, Bob has 4
        
        data = result["data"]
        assert data["user_ids"] == [1, 2]
        assert data["total_tasks"] == 7
        assert data["status_filter"] is None
        
        # Check tasks by user
        tasks_by_user = data["tasks_by_user"]
        assert len(tasks_by_user[1]) == 3  # Alice's tasks
        assert len(tasks_by_user[2]) == 4  # Bob's tasks
    
    def test_get_tasks_by_multiple_users_with_status_filter(self):
        """Test getting tasks for multiple users with status filter."""
        # Get pending tasks for Alice, Bob, and Carol
        result = self.db_manager.get_tasks_by_multiple_users([1, 2, 3], "pending")
        
        assert result["success"] is True
        assert result["count"] == 4  # Alice: 1, Bob: 2, Carol: 1
        
        data = result["data"]
        assert data["status_filter"] == "pending"
        
        # Verify all returned tasks are pending
        for user_tasks in data["tasks_by_user"].values():
            for task in user_tasks:
                assert task["status"] == "pending"
    
    def test_get_tasks_by_multiple_users_invalid_input(self):
        """Test getting tasks for multiple users with invalid input."""
        # Test with empty list
        result = self.db_manager.get_tasks_by_multiple_users([])
        
        assert result["success"] is False
        assert "must be a non-empty list" in result["error"]
        
        # Test with invalid user_id types
        result = self.db_manager.get_tasks_by_multiple_users([1, "invalid", 3])
        
        assert result["success"] is False
        assert "must be positive integers" in result["error"]
    
    def test_get_unassigned_tasks(self):
        """Test getting unassigned tasks."""
        result = self.db_manager.get_unassigned_tasks()
        
        assert result["success"] is True
        assert result["count"] == 2  # 2 unassigned tasks
        assert result["status_filter"] is None
        
        # Verify all tasks are unassigned
        for task in result["data"]:
            assert task.get("assigned_to") is None or "assigned_to" not in task
        
        # Verify task titles
        task_titles = [task["title"] for task in result["data"]]
        assert "Documentation Update" in task_titles
        assert "Research Task" in task_titles
    
    def test_get_unassigned_tasks_with_status_filter(self):
        """Test getting unassigned tasks with status filter."""
        result = self.db_manager.get_unassigned_tasks("pending")
        
        assert result["success"] is True
        assert result["count"] == 2  # Both unassigned tasks are pending
        assert result["status_filter"] == "pending"
        
        # Verify all tasks are unassigned and pending
        for task in result["data"]:
            assert task.get("assigned_to") is None or "assigned_to" not in task
            assert task["status"] == "pending"
    
    def test_get_unassigned_tasks_invalid_status(self):
        """Test getting unassigned tasks with invalid status filter."""
        result = self.db_manager.get_unassigned_tasks("invalid_status")
        
        assert result["success"] is False
        assert "Invalid status filter" in result["error"]
    
    def test_validate_user_exists(self):
        """Test user existence validation."""
        # Test with existing user
        assert self.db_manager._validate_user_exists(1) is True
        assert self.db_manager._validate_user_exists(2) is True
        
        # Test with non-existing user
        assert self.db_manager._validate_user_exists(999) is False
    
    def test_user_task_filtering_integration(self):
        """Test integration of user task filtering with advanced search."""
        # Test complex query combining user assignment and other criteria
        query = {
            "$and": [
                {"assigned_to": {"in": [1, 2]}},  # Alice or Bob
                {"priority": {"in": ["high", "urgent"]}},  # High or urgent priority
                {"status": {"ne": "completed"}}  # Not completed
            ]
        }
        
        result = self.db_manager.advanced_search("tasks", query)
        
        assert result["success"] is True
        assert result["count"] >= 2  # Should find at least 2 matching tasks
        
        # Verify all results match criteria
        for task in result["data"]:
            assert task["assigned_to"] in [1, 2]
            assert task["priority"] in ["high", "urgent"]
            assert task["status"] != "completed"
    
    def test_requirement_3_2_user_task_filtering(self):
        """Test requirement 3.2: filtering by user assignment."""
        # This test specifically validates requirement 3.2
        
        # Test 1: Filter tasks by specific user assignment
        user_1_tasks = self.db_manager.get_tasks_by_user(1)
        assert user_1_tasks["success"] is True
        assert all(task["assigned_to"] == 1 for task in user_1_tasks["data"])
        
        # Test 2: Filter tasks by user assignment with status
        user_2_pending = self.db_manager.get_tasks_by_user(2, "pending")
        assert user_2_pending["success"] is True
        assert all(task["assigned_to"] == 2 and task["status"] == "pending" 
                  for task in user_2_pending["data"])
        
        # Test 3: Advanced search with user assignment filter
        query = {"assigned_to": 3}
        user_3_tasks = self.db_manager.advanced_search("tasks", query)
        assert user_3_tasks["success"] is True
        assert all(task["assigned_to"] == 3 for task in user_3_tasks["data"])
        
        # Test 4: Multiple user assignment filter
        multi_user_query = {"assigned_to": {"in": [1, 2, 3]}}
        multi_user_tasks = self.db_manager.advanced_search("tasks", multi_user_query)
        assert multi_user_tasks["success"] is True
        assert all(task["assigned_to"] in [1, 2, 3] for task in multi_user_tasks["data"])
        
        self.db_manager.logger.info("Requirement 3.2 validation completed successfully")