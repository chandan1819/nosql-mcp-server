"""
Test data factories and utilities for creating consistent test data.
"""

import tempfile
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random
import string


class TestDataFactory:
    """Factory class for creating test data."""
    
    @staticmethod
    def create_user(
        name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a test user record."""
        if name is None:
            name = f"Test User {random.randint(1, 1000)}"
        if email is None:
            username = name.lower().replace(" ", ".")
            email = f"{username}@example.com"
        if role is None:
            role = random.choice(["User", "Admin", "Manager", "Developer"])
        
        user_data = {
            "name": name,
            "email": email,
            "role": role,
            "created_at": datetime.now().isoformat(),
            **kwargs
        }
        return user_data
    
    @staticmethod
    def create_task(
        title: Optional[str] = None,
        assigned_to: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a test task record."""
        if title is None:
            title = f"Test Task {random.randint(1, 1000)}"
        if status is None:
            status = random.choice(["pending", "in_progress", "completed", "cancelled"])
        if priority is None:
            priority = random.choice(["low", "medium", "high", "urgent"])
        
        task_data = {
            "title": title,
            "description": f"Description for {title}",
            "status": status,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            **kwargs
        }
        
        if assigned_to is not None:
            task_data["assigned_to"] = assigned_to
            
        return task_data
    
    @staticmethod
    def create_product(
        name: Optional[str] = None,
        price: Optional[float] = None,
        category: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a test product record."""
        if name is None:
            name = f"Test Product {random.randint(1, 1000)}"
        if price is None:
            price = round(random.uniform(10.0, 500.0), 2)
        if category is None:
            category = random.choice(["Electronics", "Books", "Clothing", "Home", "Sports"])
        
        product_data = {
            "name": name,
            "description": f"Description for {name}",
            "price": price,
            "category": category,
            "in_stock": random.choice([True, False]),
            "created_at": datetime.now().isoformat(),
            **kwargs
        }
        return product_data
    
    @staticmethod
    def create_users_batch(count: int = 5) -> List[Dict[str, Any]]:
        """Create a batch of test users."""
        return [TestDataFactory.create_user() for _ in range(count)]
    
    @staticmethod
    def create_tasks_batch(count: int = 5, user_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """Create a batch of test tasks."""
        tasks = []
        for i in range(count):
            task_data = TestDataFactory.create_task()
            if user_ids:
                task_data["assigned_to"] = random.choice(user_ids)
            tasks.append(task_data)
        return tasks
    
    @staticmethod
    def create_products_batch(count: int = 5) -> List[Dict[str, Any]]:
        """Create a batch of test products."""
        return [TestDataFactory.create_product() for _ in range(count)]
    
    @staticmethod
    def create_invalid_user() -> Dict[str, Any]:
        """Create an invalid user record for testing validation."""
        return {
            "name": "",  # Invalid: empty name
            "email": "invalid-email",  # Invalid: bad email format
            "role": "InvalidRole"  # Invalid: not in allowed roles
        }
    
    @staticmethod
    def create_invalid_task() -> Dict[str, Any]:
        """Create an invalid task record for testing validation."""
        return {
            "title": "",  # Invalid: empty title
            "status": "invalid_status",  # Invalid: not in allowed statuses
            "priority": "invalid_priority",  # Invalid: not in allowed priorities
            "assigned_to": "not_a_number"  # Invalid: should be integer
        }
    
    @staticmethod
    def create_invalid_product() -> Dict[str, Any]:
        """Create an invalid product record for testing validation."""
        return {
            "name": "",  # Invalid: empty name
            "price": -10.0,  # Invalid: negative price
            "category": ""  # Invalid: empty category
        }


class TestDatabaseFactory:
    """Factory for creating test databases."""
    
    @staticmethod
    def create_temp_db() -> str:
        """Create a temporary database file and return its path."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        temp_db.close()
        return temp_db.name
    
    @staticmethod
    def cleanup_temp_db(db_path: str) -> None:
        """Clean up a temporary database file."""
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except (PermissionError, FileNotFoundError):
            # On Windows, the file might still be locked
            pass


class TestUtilities:
    """Utility functions for testing."""
    
    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """Generate a random string of specified length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_random_email() -> str:
        """Generate a random email address."""
        username = TestUtilities.generate_random_string(8)
        domain = random.choice(["example.com", "test.org", "demo.net"])
        return f"{username}@{domain}"
    
    @staticmethod
    def assert_response_structure(response: Dict[str, Any], success: bool = True) -> None:
        """Assert that a response has the expected structure."""
        required_fields = ["success", "data", "message", "count", "error"]
        
        for field in required_fields:
            assert field in response, f"Response missing required field: {field}"
        
        assert isinstance(response["success"], bool), "success field must be boolean"
        assert isinstance(response["count"], int), "count field must be integer"
        assert response["count"] >= 0, "count field must be non-negative"
        
        if success:
            assert response["success"] is True, "Expected successful response"
            assert response["error"] is None, "Successful response should have no error"
        else:
            assert response["success"] is False, "Expected failed response"
            assert response["error"] is not None, "Failed response should have error message"
            assert isinstance(response["error"], str), "Error field must be string"
    
    @staticmethod
    def assert_record_structure(record: Dict[str, Any], collection: str) -> None:
        """Assert that a record has the expected structure for its collection."""
        # Common fields for all records
        assert "id" in record, "Record must have id field"
        assert "created_at" in record, "Record must have created_at field"
        assert isinstance(record["id"], int), "id field must be integer"
        assert record["id"] > 0, "id field must be positive"
        
        # Collection-specific fields
        if collection == "users":
            required_fields = ["name", "email", "role"]
            for field in required_fields:
                assert field in record, f"User record missing required field: {field}"
            assert "@" in record["email"], "User email must be valid format"
            
        elif collection == "tasks":
            required_fields = ["title", "status", "priority"]
            for field in required_fields:
                assert field in record, f"Task record missing required field: {field}"
            assert record["status"] in ["pending", "in_progress", "completed", "cancelled"]
            assert record["priority"] in ["low", "medium", "high", "urgent"]
            
        elif collection == "products":
            required_fields = ["name", "price", "category", "in_stock"]
            for field in required_fields:
                assert field in record, f"Product record missing required field: {field}"
            assert isinstance(record["price"], (int, float)), "Product price must be numeric"
            assert record["price"] >= 0, "Product price must be non-negative"
            assert isinstance(record["in_stock"], bool), "in_stock field must be boolean"
    
    @staticmethod
    def create_test_scenario(name: str, description: str = "") -> Dict[str, Any]:
        """Create a test scenario descriptor."""
        return {
            "name": name,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "id": TestUtilities.generate_random_string(8)
        }


class MockDataGenerator:
    """Generator for creating realistic mock data."""
    
    FIRST_NAMES = ["Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Henry", "Ivy", "Jack"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    COMPANIES = ["TechCorp", "DataSoft", "CloudSys", "WebDev Inc", "AppBuilder", "CodeCraft", "DevTools", "SoftWorks"]
    TASK_PREFIXES = ["Implement", "Design", "Fix", "Update", "Create", "Test", "Deploy", "Review", "Optimize", "Refactor"]
    TASK_SUBJECTS = ["authentication system", "user interface", "database schema", "API endpoints", "test suite", "documentation", "deployment pipeline", "error handling"]
    PRODUCT_CATEGORIES = ["Electronics", "Books", "Clothing", "Home & Garden", "Sports", "Toys", "Health", "Beauty"]
    
    @classmethod
    def realistic_user(cls) -> Dict[str, Any]:
        """Generate a realistic user record."""
        first_name = random.choice(cls.FIRST_NAMES)
        last_name = random.choice(cls.LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(['company.com', 'email.org', 'work.net'])}"
        
        return TestDataFactory.create_user(
            name=full_name,
            email=email,
            role=random.choice(["User", "Admin", "Manager", "Developer", "Analyst"])
        )
    
    @classmethod
    def realistic_task(cls, assigned_to: Optional[int] = None) -> Dict[str, Any]:
        """Generate a realistic task record."""
        prefix = random.choice(cls.TASK_PREFIXES)
        subject = random.choice(cls.TASK_SUBJECTS)
        title = f"{prefix} {subject}"
        
        return TestDataFactory.create_task(
            title=title,
            assigned_to=assigned_to,
            status=random.choice(["pending", "in_progress", "completed"]),
            priority=random.choice(["low", "medium", "high"])
        )
    
    @classmethod
    def realistic_product(cls) -> Dict[str, Any]:
        """Generate a realistic product record."""
        category = random.choice(cls.PRODUCT_CATEGORIES)
        adjective = random.choice(["Premium", "Deluxe", "Standard", "Basic", "Professional", "Advanced"])
        name = f"{adjective} {category[:-1]} Item"  # Remove 's' from category
        
        # Price based on category
        price_ranges = {
            "Electronics": (50, 500),
            "Books": (10, 50),
            "Clothing": (20, 200),
            "Home & Garden": (15, 300),
            "Sports": (25, 400),
            "Toys": (5, 100),
            "Health": (10, 150),
            "Beauty": (8, 80)
        }
        
        min_price, max_price = price_ranges.get(category, (10, 100))
        price = round(random.uniform(min_price, max_price), 2)
        
        return TestDataFactory.create_product(
            name=name,
            price=price,
            category=category
        )