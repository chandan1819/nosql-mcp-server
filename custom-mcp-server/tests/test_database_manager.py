"""
Unit tests for the DatabaseManager class.
"""

import os
import tempfile
import pytest
from pathlib import Path
import sys

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from database.manager import DatabaseManager


class TestDatabaseManager:
    """Test cases for DatabaseManager class."""
    
    def setup_method(self):
        """Set up test database for each test."""
        # Create a temporary database file for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
    
    def teardown_method(self):
        """Clean up after each test."""
        self.db_manager.close()
        try:
            os.unlink(self.temp_db.name)
        except (PermissionError, FileNotFoundError):
            # On Windows, the file might still be locked
            pass
    
    def test_database_connection(self):
        """Test that database connection is established properly."""
        assert self.db_manager.is_connected()
        assert self.db_manager.db is not None
        assert self.db_manager.users is not None
        assert self.db_manager.tasks is not None
        assert self.db_manager.products is not None
    
    def test_get_collection_valid(self):
        """Test getting valid collections."""
        users_table = self.db_manager.get_collection('users')
        tasks_table = self.db_manager.get_collection('tasks')
        products_table = self.db_manager.get_collection('products')
        
        assert users_table is not None
        assert tasks_table is not None
        assert products_table is not None
    
    def test_get_collection_invalid(self):
        """Test getting invalid collection raises ValueError."""
        with pytest.raises(ValueError, match="Invalid collection name"):
            self.db_manager.get_collection('invalid_collection')
    
    def test_next_id_generation(self):
        """Test next ID generation for empty and populated collections."""
        # Test with empty collection
        next_id = self.db_manager.get_next_id('users')
        assert next_id == 1
        
        # Add a record and test again
        self.db_manager.users.insert({'id': 1, 'name': 'Test User'})
        next_id = self.db_manager.get_next_id('users')
        assert next_id == 2
        
        # Add another record with higher ID
        self.db_manager.users.insert({'id': 5, 'name': 'Test User 2'})
        next_id = self.db_manager.get_next_id('users')
        assert next_id == 6
    
    def test_sample_data_generation(self):
        """Test sample data generation methods."""
        users = self.db_manager.generate_sample_users()
        tasks = self.db_manager.generate_sample_tasks()
        products = self.db_manager.generate_sample_products()
        
        # Verify users data
        assert len(users) >= 3  # Requirement: 3+ records
        for user in users:
            assert 'id' in user
            assert 'name' in user
            assert 'email' in user
            assert 'role' in user
            assert 'created_at' in user
        
        # Verify tasks data
        assert len(tasks) >= 5  # Requirement: 5+ records
        for task in tasks:
            assert 'id' in task
            assert 'title' in task
            assert 'description' in task
            assert 'assigned_to' in task  # User assignment
            assert 'status' in task
            assert 'priority' in task
            assert 'created_at' in task
            assert 'due_date' in task
        
        # Verify products data
        assert len(products) >= 4  # Requirement: 4+ records
        for product in products:
            assert 'id' in product
            assert 'name' in product
            assert 'description' in product
            assert 'price' in product  # Pricing information
            assert 'category' in product
            assert 'in_stock' in product
            assert 'created_at' in product
    
    def test_initialize_sample_data(self):
        """Test sample data initialization."""
        result = self.db_manager.initialize_sample_data()
        
        # Verify return value
        assert 'users' in result
        assert 'tasks' in result
        assert 'products' in result
        assert result['users'] >= 3
        assert result['tasks'] >= 5
        assert result['products'] >= 4
        
        # Verify data was actually inserted
        assert len(self.db_manager.users.all()) >= 3
        assert len(self.db_manager.tasks.all()) >= 5
        assert len(self.db_manager.products.all()) >= 4
        
        # Test that running again doesn't duplicate data
        result2 = self.db_manager.initialize_sample_data()
        assert result2['users'] == 0  # No new records inserted
        assert result2['tasks'] == 0
        assert result2['products'] == 0
    
    def test_initialize_sample_data_force_reset(self):
        """Test sample data initialization with force reset."""
        # Initialize data first
        self.db_manager.initialize_sample_data()
        initial_users = len(self.db_manager.users.all())
        
        # Force reset and reinitialize
        result = self.db_manager.initialize_sample_data(force_reset=True)
        
        # Verify data was reset and reinserted
        assert result['users'] >= 3
        assert len(self.db_manager.users.all()) == initial_users
    
    def test_context_manager(self):
        """Test DatabaseManager as context manager."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        temp_db.close()
        
        try:
            with DatabaseManager(temp_db.name) as db:
                assert db.is_connected()
                db.initialize_sample_data()
                assert len(db.users.all()) >= 3
                # Store reference to check after context exit
                db_ref = db
            
            # Database should be closed after context exit
            # Note: TinyDB doesn't have a traditional connection, so we just verify
            # that the close method was called by checking if references are cleared
            assert db_ref.db is None
            assert db_ref.users is None
            assert db_ref.tasks is None
            assert db_ref.products is None
        finally:
            try:
                os.unlink(temp_db.name)
            except (PermissionError, FileNotFoundError):
                # On Windows, the file might still be locked
                pass


    def test_create_record_users_valid(self):
        """Test creating valid user records."""
        user_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'role': 'Developer'
        }
        
        result = self.db_manager.create_record('users', user_data)
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['error'] is None
        assert result['data']['name'] == 'John Doe'
        assert result['data']['email'] == 'john.doe@example.com'
        assert result['data']['role'] == 'Developer'
        assert 'id' in result['data']
        assert 'created_at' in result['data']
        
        # Verify record was actually inserted
        users = self.db_manager.users.all()
        assert len(users) == 1
        assert users[0]['name'] == 'John Doe'
    
    def test_create_record_users_auto_id(self):
        """Test auto-incrementing ID generation for users."""
        user1 = {'name': 'User 1', 'email': 'user1@example.com'}
        user2 = {'name': 'User 2', 'email': 'user2@example.com'}
        
        result1 = self.db_manager.create_record('users', user1)
        result2 = self.db_manager.create_record('users', user2)
        
        assert result1['success'] is True
        assert result2['success'] is True
        assert result1['data']['id'] == 1
        assert result2['data']['id'] == 2
    
    def test_create_record_users_default_role(self):
        """Test default role assignment for users."""
        user_data = {
            'name': 'Jane Doe',
            'email': 'jane.doe@example.com'
        }
        
        result = self.db_manager.create_record('users', user_data)
        
        assert result['success'] is True
        assert result['data']['role'] == 'User'  # Default role
    
    def test_create_record_users_invalid_email(self):
        """Test user creation with invalid email."""
        user_data = {
            'name': 'Invalid User',
            'email': 'invalid-email'
        }
        
        result = self.db_manager.create_record('users', user_data)
        
        assert result['success'] is False
        assert result['count'] == 0
        assert 'Invalid email format' in result['error']
    
    def test_create_record_users_missing_required_fields(self):
        """Test user creation with missing required fields."""
        # Missing name
        user_data = {'email': 'test@example.com'}
        result = self.db_manager.create_record('users', user_data)
        assert result['success'] is False
        assert 'name' in result['error']
        
        # Missing email
        user_data = {'name': 'Test User'}
        result = self.db_manager.create_record('users', user_data)
        assert result['success'] is False
        assert 'email' in result['error']
    
    def test_create_record_tasks_valid(self):
        """Test creating valid task records."""
        task_data = {
            'title': 'Test Task',
            'description': 'A test task',
            'assigned_to': 1,
            'status': 'pending',
            'priority': 'high'
        }
        
        result = self.db_manager.create_record('tasks', task_data)
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['data']['title'] == 'Test Task'
        assert result['data']['assigned_to'] == 1
        assert result['data']['status'] == 'pending'
        assert result['data']['priority'] == 'high'
        assert 'id' in result['data']
        assert 'created_at' in result['data']
    
    def test_create_record_tasks_defaults(self):
        """Test default values for task creation."""
        task_data = {'title': 'Minimal Task'}
        
        result = self.db_manager.create_record('tasks', task_data)
        
        assert result['success'] is True
        assert result['data']['status'] == 'pending'  # Default status
        assert result['data']['priority'] == 'medium'  # Default priority
    
    def test_create_record_tasks_invalid_status(self):
        """Test task creation with invalid status."""
        task_data = {
            'title': 'Test Task',
            'status': 'invalid_status'
        }
        
        result = self.db_manager.create_record('tasks', task_data)
        
        assert result['success'] is False
        assert 'Invalid status' in result['error']
    
    def test_create_record_tasks_invalid_priority(self):
        """Test task creation with invalid priority."""
        task_data = {
            'title': 'Test Task',
            'priority': 'invalid_priority'
        }
        
        result = self.db_manager.create_record('tasks', task_data)
        
        assert result['success'] is False
        assert 'Invalid priority' in result['error']
    
    def test_create_record_tasks_invalid_assigned_to(self):
        """Test task creation with invalid assigned_to."""
        task_data = {
            'title': 'Test Task',
            'assigned_to': 'not_a_number'
        }
        
        result = self.db_manager.create_record('tasks', task_data)
        
        assert result['success'] is False
        assert 'assigned_to must be a positive integer' in result['error']
    
    def test_create_record_products_valid(self):
        """Test creating valid product records."""
        product_data = {
            'name': 'Test Product',
            'description': 'A test product',
            'price': 99.99,
            'category': 'Test Category',
            'in_stock': True
        }
        
        result = self.db_manager.create_record('products', product_data)
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['data']['name'] == 'Test Product'
        assert result['data']['price'] == 99.99
        assert result['data']['category'] == 'Test Category'
        assert result['data']['in_stock'] is True
        assert 'id' in result['data']
        assert 'created_at' in result['data']
    
    def test_create_record_products_defaults(self):
        """Test default values for product creation."""
        product_data = {
            'name': 'Minimal Product',
            'price': 50.0
        }
        
        result = self.db_manager.create_record('products', product_data)
        
        assert result['success'] is True
        assert result['data']['in_stock'] is True  # Default in_stock
        assert result['data']['category'] == 'General'  # Default category
    
    def test_create_record_products_invalid_price(self):
        """Test product creation with invalid price."""
        # Negative price
        product_data = {
            'name': 'Test Product',
            'price': -10.0
        }
        
        result = self.db_manager.create_record('products', product_data)
        
        assert result['success'] is False
        assert 'Price cannot be negative' in result['error']
        
        # Non-numeric price
        product_data = {
            'name': 'Test Product',
            'price': 'not_a_number'
        }
        
        result = self.db_manager.create_record('products', product_data)
        
        assert result['success'] is False
        assert 'Price must be a valid number' in result['error']
    
    def test_create_record_products_missing_required_fields(self):
        """Test product creation with missing required fields."""
        # Missing name
        product_data = {'price': 99.99}
        result = self.db_manager.create_record('products', product_data)
        assert result['success'] is False
        assert 'name' in result['error']
        
        # Missing price
        product_data = {'name': 'Test Product'}
        result = self.db_manager.create_record('products', product_data)
        assert result['success'] is False
        assert 'price' in result['error']
    
    def test_create_record_invalid_collection(self):
        """Test creating record in invalid collection."""
        result = self.db_manager.create_record('invalid_collection', {'test': 'data'})
        
        assert result['success'] is False
        assert 'Invalid collection name' in result['error']
    
    def test_create_record_empty_data(self):
        """Test creating record with empty data."""
        result = self.db_manager.create_record('users', {})
        
        assert result['success'] is False
        assert 'Data cannot be empty' in result['error']
    
    def test_create_record_non_dict_data(self):
        """Test creating record with non-dictionary data."""
        result = self.db_manager.create_record('users', 'not_a_dict')
        
        assert result['success'] is False
        assert 'Data must be a dictionary' in result['error']
    
    def test_read_records_all_users(self):
        """Test reading all records from users collection."""
        # First create some test data
        self.db_manager.initialize_sample_data()
        
        result = self.db_manager.read_records('users')
        
        assert result['success'] is True
        assert result['count'] >= 3  # At least 3 sample users
        assert len(result['data']) >= 3
        assert result['error'] is None
        
        # Verify data structure
        for user in result['data']:
            assert 'id' in user
            assert 'name' in user
            assert 'email' in user
            assert 'role' in user
    
    def test_read_records_empty_collection(self):
        """Test reading from empty collection."""
        result = self.db_manager.read_records('users')
        
        assert result['success'] is True
        assert result['count'] == 0
        assert result['data'] == []
        assert result['error'] is None
    
    def test_read_records_simple_filter(self):
        """Test reading records with simple equality filter."""
        # Create test data
        user1 = {'name': 'Alice', 'email': 'alice@example.com', 'role': 'Admin'}
        user2 = {'name': 'Bob', 'email': 'bob@example.com', 'role': 'User'}
        
        self.db_manager.create_record('users', user1)
        self.db_manager.create_record('users', user2)
        
        # Filter by role
        result = self.db_manager.read_records('users', {'role': 'Admin'})
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['data'][0]['name'] == 'Alice'
        assert result['data'][0]['role'] == 'Admin'
    
    def test_read_records_multiple_filters(self):
        """Test reading records with multiple filter conditions."""
        # Create test data
        task1 = {'title': 'Task 1', 'status': 'pending', 'priority': 'high', 'assigned_to': 1}
        task2 = {'title': 'Task 2', 'status': 'pending', 'priority': 'low', 'assigned_to': 1}
        task3 = {'title': 'Task 3', 'status': 'completed', 'priority': 'high', 'assigned_to': 2}
        
        self.db_manager.create_record('tasks', task1)
        self.db_manager.create_record('tasks', task2)
        self.db_manager.create_record('tasks', task3)
        
        # Filter by status AND priority
        result = self.db_manager.read_records('tasks', {'status': 'pending', 'priority': 'high'})
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['data'][0]['title'] == 'Task 1'
    
    def test_read_records_complex_filter_greater_than(self):
        """Test reading records with greater than filter."""
        # Create test products
        product1 = {'name': 'Cheap Item', 'price': 10.0}
        product2 = {'name': 'Expensive Item', 'price': 100.0}
        
        self.db_manager.create_record('products', product1)
        self.db_manager.create_record('products', product2)
        
        # Filter by price > 50
        result = self.db_manager.read_records('products', {'price': {'gt': 50.0}})
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['data'][0]['name'] == 'Expensive Item'
    
    def test_read_records_complex_filter_in_list(self):
        """Test reading records with 'in' filter for multiple values."""
        # Create test data
        user1 = {'name': 'Admin User', 'email': 'admin@example.com', 'role': 'Admin'}
        user2 = {'name': 'Manager User', 'email': 'manager@example.com', 'role': 'Manager'}
        user3 = {'name': 'Regular User', 'email': 'user@example.com', 'role': 'User'}
        
        self.db_manager.create_record('users', user1)
        self.db_manager.create_record('users', user2)
        self.db_manager.create_record('users', user3)
        
        # Filter by role in ['Admin', 'Manager']
        result = self.db_manager.read_records('users', {'role': {'in': ['Admin', 'Manager']}})
        
        assert result['success'] is True
        assert result['count'] == 2
        roles = [user['role'] for user in result['data']]
        assert 'Admin' in roles
        assert 'Manager' in roles
        assert 'User' not in roles
    
    def test_read_records_complex_filter_contains(self):
        """Test reading records with contains filter."""
        # Create test data
        task1 = {'title': 'Implement authentication system'}
        task2 = {'title': 'Design user interface'}
        task3 = {'title': 'Write unit tests'}
        
        self.db_manager.create_record('tasks', task1)
        self.db_manager.create_record('tasks', task2)
        self.db_manager.create_record('tasks', task3)
        
        # Filter by title containing 'user'
        result = self.db_manager.read_records('tasks', {'title': {'contains': 'user'}})
        
        assert result['success'] is True
        assert result['count'] == 1
        assert 'user interface' in result['data'][0]['title']
    
    def test_read_records_filter_by_user_assignment(self):
        """Test filtering tasks by user assignment (requirement 3.2)."""
        # Create test data
        task1 = {'title': 'Task for User 1', 'assigned_to': 1}
        task2 = {'title': 'Task for User 2', 'assigned_to': 2}
        task3 = {'title': 'Another Task for User 1', 'assigned_to': 1}
        task4 = {'title': 'Unassigned Task'}  # No assigned_to
        
        self.db_manager.create_record('tasks', task1)
        self.db_manager.create_record('tasks', task2)
        self.db_manager.create_record('tasks', task3)
        self.db_manager.create_record('tasks', task4)
        
        # Filter tasks assigned to user 1
        result = self.db_manager.read_records('tasks', {'assigned_to': 1})
        
        assert result['success'] is True
        assert result['count'] == 2
        for task in result['data']:
            assert task['assigned_to'] == 1
    
    def test_read_records_no_matches(self):
        """Test reading records with filter that matches nothing."""
        # Create test data
        user1 = {'name': 'Alice', 'email': 'alice@example.com', 'role': 'User'}
        self.db_manager.create_record('users', user1)
        
        # Filter by non-existent role
        result = self.db_manager.read_records('users', {'role': 'NonExistentRole'})
        
        assert result['success'] is True
        assert result['count'] == 0
        assert result['data'] == []
    
    def test_read_records_invalid_collection(self):
        """Test reading from invalid collection."""
        result = self.db_manager.read_records('invalid_collection')
        
        assert result['success'] is False
        assert result['count'] == 0
        assert 'Invalid collection name' in result['error']
    
    def test_read_records_invalid_filter_operator(self):
        """Test reading with invalid filter operator."""
        user1 = {'name': 'Alice', 'email': 'alice@example.com'}
        self.db_manager.create_record('users', user1)
        
        # Use invalid operator
        result = self.db_manager.read_records('users', {'name': {'invalid_op': 'Alice'}})
        
        assert result['success'] is False
        assert 'Unsupported filter operator' in result['error']
    
    def test_update_records_single_field(self):
        """Test updating a single field in matching records."""
        # Create test data
        user1 = {'name': 'Alice', 'email': 'alice@example.com', 'role': 'User'}
        user2 = {'name': 'Bob', 'email': 'bob@example.com', 'role': 'User'}
        
        self.db_manager.create_record('users', user1)
        self.db_manager.create_record('users', user2)
        
        # Update role for Alice
        result = self.db_manager.update_records('users', {'name': 'Alice'}, {'role': 'Admin'})
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['data'][0]['name'] == 'Alice'
        assert result['data'][0]['role'] == 'Admin'
        
        # Verify Bob wasn't updated
        bob_result = self.db_manager.read_records('users', {'name': 'Bob'})
        assert bob_result['data'][0]['role'] == 'User'
    
    def test_update_records_multiple_fields(self):
        """Test updating multiple fields in matching records."""
        # Create test data
        task1 = {'title': 'Test Task', 'status': 'pending', 'priority': 'low'}
        self.db_manager.create_record('tasks', task1)
        
        # Update multiple fields
        updates = {'status': 'in_progress', 'priority': 'high'}
        result = self.db_manager.update_records('tasks', {'title': 'Test Task'}, updates)
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['data'][0]['status'] == 'in_progress'
        assert result['data'][0]['priority'] == 'high'
        assert result['data'][0]['title'] == 'Test Task'  # Unchanged
    
    def test_update_records_multiple_matches(self):
        """Test updating multiple records that match the filter."""
        # Create test data
        task1 = {'title': 'Task 1', 'status': 'pending', 'assigned_to': 1}
        task2 = {'title': 'Task 2', 'status': 'pending', 'assigned_to': 1}
        task3 = {'title': 'Task 3', 'status': 'completed', 'assigned_to': 2}
        
        self.db_manager.create_record('tasks', task1)
        self.db_manager.create_record('tasks', task2)
        self.db_manager.create_record('tasks', task3)
        
        # Update all pending tasks
        result = self.db_manager.update_records('tasks', {'status': 'pending'}, {'status': 'in_progress'})
        
        assert result['success'] is True
        assert result['count'] == 2
        
        # Verify all pending tasks were updated
        for task in result['data']:
            assert task['status'] == 'in_progress'
        
        # Verify completed task wasn't updated
        completed_result = self.db_manager.read_records('tasks', {'assigned_to': 2})
        assert completed_result['data'][0]['status'] == 'completed'
    
    def test_update_records_no_matches(self):
        """Test updating with filter that matches no records."""
        # Create test data
        user1 = {'name': 'Alice', 'email': 'alice@example.com', 'role': 'User'}
        self.db_manager.create_record('users', user1)
        
        # Try to update non-existent user
        result = self.db_manager.update_records('users', {'name': 'NonExistent'}, {'role': 'Admin'})
        
        assert result['success'] is True
        assert result['count'] == 0
        assert result['data'] == []
        assert 'No records found matching' in result['message']
    
    def test_update_records_complex_filter(self):
        """Test updating with complex filter criteria."""
        # Create test data
        product1 = {'name': 'Product 1', 'price': 50.0, 'category': 'Electronics'}
        product2 = {'name': 'Product 2', 'price': 150.0, 'category': 'Electronics'}
        product3 = {'name': 'Product 3', 'price': 75.0, 'category': 'Books'}
        
        self.db_manager.create_record('products', product1)
        self.db_manager.create_record('products', product2)
        self.db_manager.create_record('products', product3)
        
        # Update electronics products with price > 100
        filters = {'category': 'Electronics', 'price': {'gt': 100.0}}
        updates = {'in_stock': False}
        result = self.db_manager.update_records('products', filters, updates)
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['data'][0]['name'] == 'Product 2'
        assert result['data'][0]['in_stock'] is False
    
    def test_update_records_partial_update(self):
        """Test partial record updates (requirement 2.3)."""
        # Create test data
        user1 = {'name': 'Alice', 'email': 'alice@example.com', 'role': 'User'}
        self.db_manager.create_record('users', user1)
        
        # Update only the role, leaving other fields unchanged
        result = self.db_manager.update_records('users', {'name': 'Alice'}, {'role': 'Admin'})
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['data'][0]['name'] == 'Alice'  # Unchanged
        assert result['data'][0]['email'] == 'alice@example.com'  # Unchanged
        assert result['data'][0]['role'] == 'Admin'  # Updated
    
    def test_update_records_invalid_collection(self):
        """Test updating records in invalid collection."""
        result = self.db_manager.update_records('invalid_collection', {'id': 1}, {'field': 'value'})
        
        assert result['success'] is False
        assert result['count'] == 0
        assert 'Invalid collection name' in result['error']
    
    def test_update_records_no_filters(self):
        """Test updating without filters (should be prevented)."""
        user1 = {'name': 'Alice', 'email': 'alice@example.com'}
        self.db_manager.create_record('users', user1)
        
        # Try to update without filters
        result = self.db_manager.update_records('users', {}, {'role': 'Admin'})
        
        assert result['success'] is False
        assert 'Filters are required' in result['error']
    
    def test_update_records_empty_updates(self):
        """Test updating with empty updates dictionary."""
        user1 = {'name': 'Alice', 'email': 'alice@example.com'}
        self.db_manager.create_record('users', user1)
        
        # Try to update with empty updates
        result = self.db_manager.update_records('users', {'name': 'Alice'}, {})
        
        assert result['success'] is False
        assert 'Updates cannot be empty' in result['error']
    
    def test_update_records_protected_fields(self):
        """Test that protected fields cannot be updated."""
        user1 = {'name': 'Alice', 'email': 'alice@example.com'}
        self.db_manager.create_record('users', user1)
        
        # Try to update ID field
        result = self.db_manager.update_records('users', {'name': 'Alice'}, {'id': 999})
        assert result['success'] is False
        assert "Cannot update the 'id' field" in result['error']
        
        # Try to update created_at field
        result = self.db_manager.update_records('users', {'name': 'Alice'}, {'created_at': 'new_date'})
        assert result['success'] is False
        assert "Cannot update the 'created_at' field" in result['error']
    
    def test_update_records_user_validation(self):
        """Test user-specific validation during updates."""
        user1 = {'name': 'Alice', 'email': 'alice@example.com'}
        self.db_manager.create_record('users', user1)
        
        # Try to update with invalid email
        result = self.db_manager.update_records('users', {'name': 'Alice'}, {'email': 'invalid-email'})
        
        assert result['success'] is False
        assert 'Invalid email format' in result['error']
    
    def test_update_records_task_validation(self):
        """Test task-specific validation during updates."""
        task1 = {'title': 'Test Task'}
        self.db_manager.create_record('tasks', task1)
        
        # Try to update with invalid status
        result = self.db_manager.update_records('tasks', {'title': 'Test Task'}, {'status': 'invalid_status'})
        assert result['success'] is False
        assert 'Invalid status' in result['error']
        
        # Try to update with invalid priority
        result = self.db_manager.update_records('tasks', {'title': 'Test Task'}, {'priority': 'invalid_priority'})
        assert result['success'] is False
        assert 'Invalid priority' in result['error']
        
        # Try to update with invalid assigned_to
        result = self.db_manager.update_records('tasks', {'title': 'Test Task'}, {'assigned_to': 'not_a_number'})
        assert result['success'] is False
        assert 'assigned_to must be a positive integer' in result['error']
    
    def test_update_records_product_validation(self):
        """Test product-specific validation during updates."""
        product1 = {'name': 'Test Product', 'price': 50.0}
        self.db_manager.create_record('products', product1)
        
        # Try to update with invalid price
        result = self.db_manager.update_records('products', {'name': 'Test Product'}, {'price': -10.0})
        assert result['success'] is False
        assert 'Price cannot be negative' in result['error']
        
        # Try to update with non-numeric price
        result = self.db_manager.update_records('products', {'name': 'Test Product'}, {'price': 'not_a_number'})
        assert result['success'] is False
        assert 'Price must be a valid number' in result['error']
    
    def test_delete_records_single_record(self):
        """Test deleting a single record."""
        # Create test data
        user1 = {'name': 'Alice', 'email': 'alice@example.com', 'role': 'User'}
        user2 = {'name': 'Bob', 'email': 'bob@example.com', 'role': 'User'}
        
        self.db_manager.create_record('users', user1)
        self.db_manager.create_record('users', user2)
        
        # Delete Alice
        result = self.db_manager.delete_records('users', {'name': 'Alice'})
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['data'][0]['name'] == 'Alice'
        
        # Verify Alice was deleted and Bob remains
        remaining_users = self.db_manager.read_records('users')
        assert remaining_users['count'] == 1
        assert remaining_users['data'][0]['name'] == 'Bob'
    
    def test_delete_records_multiple_records(self):
        """Test deleting multiple records that match the filter."""
        # Create test data
        task1 = {'title': 'Task 1', 'status': 'completed', 'assigned_to': 1}
        task2 = {'title': 'Task 2', 'status': 'completed', 'assigned_to': 2}
        task3 = {'title': 'Task 3', 'status': 'pending', 'assigned_to': 1}
        
        self.db_manager.create_record('tasks', task1)
        self.db_manager.create_record('tasks', task2)
        self.db_manager.create_record('tasks', task3)
        
        # Delete all completed tasks
        result = self.db_manager.delete_records('tasks', {'status': 'completed'})
        
        assert result['success'] is True
        assert result['count'] == 2
        
        # Verify only pending task remains
        remaining_tasks = self.db_manager.read_records('tasks')
        assert remaining_tasks['count'] == 1
        assert remaining_tasks['data'][0]['status'] == 'pending'
    
    def test_delete_records_complex_filter(self):
        """Test deleting with complex filter criteria."""
        # Create test data
        product1 = {'name': 'Product 1', 'price': 50.0, 'category': 'Electronics', 'in_stock': False}
        product2 = {'name': 'Product 2', 'price': 150.0, 'category': 'Electronics', 'in_stock': True}
        product3 = {'name': 'Product 3', 'price': 75.0, 'category': 'Books', 'in_stock': False}
        
        self.db_manager.create_record('products', product1)
        self.db_manager.create_record('products', product2)
        self.db_manager.create_record('products', product3)
        
        # Delete out-of-stock electronics products
        filters = {'category': 'Electronics', 'in_stock': False}
        result = self.db_manager.delete_records('products', filters)
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['data'][0]['name'] == 'Product 1'
        
        # Verify correct products remain
        remaining_products = self.db_manager.read_records('products')
        assert remaining_products['count'] == 2
        names = [p['name'] for p in remaining_products['data']]
        assert 'Product 2' in names
        assert 'Product 3' in names
    
    def test_delete_records_no_matches(self):
        """Test deleting with filter that matches no records."""
        # Create test data
        user1 = {'name': 'Alice', 'email': 'alice@example.com', 'role': 'User'}
        self.db_manager.create_record('users', user1)
        
        # Try to delete non-existent user
        result = self.db_manager.delete_records('users', {'name': 'NonExistent'})
        
        assert result['success'] is True
        assert result['count'] == 0
        assert result['data'] == []
        assert 'No records found matching' in result['message']
        
        # Verify original record still exists
        remaining_users = self.db_manager.read_records('users')
        assert remaining_users['count'] == 1
    
    def test_delete_records_soft_delete(self):
        """Test soft delete functionality (requirement 2.4)."""
        # Create test data
        user1 = {'name': 'Alice', 'email': 'alice@example.com', 'role': 'User'}
        self.db_manager.create_record('users', user1)
        
        # Soft delete Alice
        result = self.db_manager.delete_records('users', {'name': 'Alice'}, soft_delete=True)
        
        assert result['success'] is True
        assert result['count'] == 1
        
        # Verify record still exists but is marked as deleted
        all_users = self.db_manager.read_records('users')
        assert all_users['count'] == 1
        assert all_users['data'][0]['deleted'] is True
        assert 'deleted_at' in all_users['data'][0]
    
    def test_delete_records_bulk_deletion_safety(self):
        """Test safety checks for bulk deletions."""
        # Create many test records
        for i in range(15):
            user_data = {'name': f'User {i}', 'email': f'user{i}@example.com', 'role': 'User'}
            self.db_manager.create_record('users', user_data)
        
        # Delete all users (should trigger safety warning but still work)
        result = self.db_manager.delete_records('users', {'role': 'User'})
        
        assert result['success'] is True
        assert result['count'] == 15
        
        # Verify all records were deleted
        remaining_users = self.db_manager.read_records('users')
        assert remaining_users['count'] == 0
    
    def test_delete_records_invalid_collection(self):
        """Test deleting from invalid collection."""
        result = self.db_manager.delete_records('invalid_collection', {'id': 1})
        
        assert result['success'] is False
        assert result['count'] == 0
        assert 'Invalid collection name' in result['error']
    
    def test_delete_records_no_filters(self):
        """Test deleting without filters (should be prevented)."""
        user1 = {'name': 'Alice', 'email': 'alice@example.com'}
        self.db_manager.create_record('users', user1)
        
        # Try to delete without filters
        result = self.db_manager.delete_records('users', {})
        
        assert result['success'] is False
        assert 'Filters are required' in result['error']
        
        # Verify record still exists
        remaining_users = self.db_manager.read_records('users')
        assert remaining_users['count'] == 1
    
    def test_delete_records_filter_by_user_assignment(self):
        """Test deleting tasks by user assignment."""
        # Create test data
        task1 = {'title': 'Task for User 1', 'assigned_to': 1}
        task2 = {'title': 'Task for User 2', 'assigned_to': 2}
        task3 = {'title': 'Another Task for User 1', 'assigned_to': 1}
        
        self.db_manager.create_record('tasks', task1)
        self.db_manager.create_record('tasks', task2)
        self.db_manager.create_record('tasks', task3)
        
        # Delete all tasks assigned to user 1
        result = self.db_manager.delete_records('tasks', {'assigned_to': 1})
        
        assert result['success'] is True
        assert result['count'] == 2
        
        # Verify only task for user 2 remains
        remaining_tasks = self.db_manager.read_records('tasks')
        assert remaining_tasks['count'] == 1
        assert remaining_tasks['data'][0]['assigned_to'] == 2
    
    def test_delete_records_with_price_filter(self):
        """Test deleting products with price-based filter."""
        # Create test data
        product1 = {'name': 'Cheap Item', 'price': 10.0}
        product2 = {'name': 'Expensive Item', 'price': 100.0}
        product3 = {'name': 'Medium Item', 'price': 50.0}
        
        self.db_manager.create_record('products', product1)
        self.db_manager.create_record('products', product2)
        self.db_manager.create_record('products', product3)
        
        # Delete products with price > 75
        result = self.db_manager.delete_records('products', {'price': {'gt': 75.0}})
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['data'][0]['name'] == 'Expensive Item'
        
        # Verify cheaper products remain
        remaining_products = self.db_manager.read_records('products')
        assert remaining_products['count'] == 2
        for product in remaining_products['data']:
            assert product['price'] <= 75.0


if __name__ == "__main__":
    pytest.main([__file__])