"""
Database Manager for TinyDB operations.
Provides CRUD operations and connection handling for the MCP server.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from tinydb import TinyDB, Query
from tinydb.table import Table
from .query_parser import QueryParser


class DatabaseManager:
    """
    Database manager class that handles TinyDB operations.
    Provides methods for accessing users, tasks, and products collections
    with proper error handling.
    """
    
    def __init__(self, db_path: str = "data/mcp_server.json"):
        """
        Initialize the DatabaseManager with TinyDB connection.
        
        Args:
            db_path: Path to the TinyDB JSON file
        """
        self.db_path = db_path
        self.db: Optional[TinyDB] = None
        self.users: Optional[Table] = None
        self.tasks: Optional[Table] = None
        self.products: Optional[Table] = None
        self.logger = logging.getLogger(__name__)
        self.query_parser = QueryParser()
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database connection
        self._connect()
    
    def _connect(self) -> None:
        """
        Establish connection to TinyDB and initialize table references.
        Handles connection errors gracefully.
        """
        try:
            self.db = TinyDB(self.db_path)
            self.users = self.db.table('users')
            self.tasks = self.db.table('tasks')
            self.products = self.db.table('products')
            self.logger.info(f"Successfully connected to database at {self.db_path}")
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            raise ConnectionError(f"Database connection failed: {str(e)}")
    
    def get_collection(self, collection_name: str) -> Table:
        """
        Get a table reference by collection name.
        
        Args:
            collection_name: Name of the collection ('users', 'tasks', 'products')
            
        Returns:
            TinyDB Table object
            
        Raises:
            ValueError: If collection name is invalid
        """
        collections = {
            'users': self.users,
            'tasks': self.tasks,
            'products': self.products
        }
        
        if collection_name not in collections:
            raise ValueError(f"Invalid collection name: {collection_name}. "
                           f"Valid options: {list(collections.keys())}")
        
        collection = collections[collection_name]
        if collection is None:
            raise ConnectionError("Database not properly initialized")
            
        return collection
    
    def is_connected(self) -> bool:
        """
        Check if database connection is active.
        
        Returns:
            True if connected, False otherwise
        """
        return self.db is not None and all([
            self.users is not None,
            self.tasks is not None,
            self.products is not None
        ])
    
    def close(self) -> None:
        """
        Close the database connection.
        """
        if self.db is not None:
            try:
                # TinyDB doesn't have a close method, but we can clear references
                self.db = None
                self.users = None
                self.tasks = None
                self.products = None
                self.logger.info("Database connection closed")
            except Exception as e:
                self.logger.warning(f"Error closing database: {str(e)}")
                self.db = None
                self.users = None
                self.tasks = None
                self.products = None
    
    def get_next_id(self, collection_name: str) -> int:
        """
        Generate the next available ID for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Next available integer ID
        """
        try:
            collection = self.get_collection(collection_name)
            records = collection.all()
            if not records:
                return 1
            
            # Find the maximum ID and add 1
            max_id = max(record.get('id', 0) for record in records)
            return max_id + 1
        except Exception as e:
            self.logger.error(f"Error generating next ID for {collection_name}: {str(e)}")
            raise
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def generate_sample_users(self) -> List[Dict[str, Any]]:
        """
        Generate sample user data for testing and demonstration.
        
        Returns:
            List of user dictionaries with realistic data
        """
        sample_users = [
            {
                "id": 1,
                "name": "Alice Johnson",
                "email": "alice.johnson@example.com",
                "role": "Project Manager",
                "created_at": "2024-01-15T09:00:00Z"
            },
            {
                "id": 2,
                "name": "Bob Smith",
                "email": "bob.smith@example.com",
                "role": "Software Developer",
                "created_at": "2024-01-16T10:30:00Z"
            },
            {
                "id": 3,
                "name": "Carol Davis",
                "email": "carol.davis@example.com",
                "role": "QA Engineer",
                "created_at": "2024-01-17T14:15:00Z"
            },
            {
                "id": 4,
                "name": "David Wilson",
                "email": "david.wilson@example.com",
                "role": "DevOps Engineer",
                "created_at": "2024-01-18T11:45:00Z"
            }
        ]
        return sample_users
    
    def generate_sample_tasks(self) -> List[Dict[str, Any]]:
        """
        Generate sample task data with user assignments.
        
        Returns:
            List of task dictionaries with user assignments
        """
        sample_tasks = [
            {
                "id": 1,
                "title": "Implement user authentication",
                "description": "Create login and registration functionality with JWT tokens",
                "assigned_to": 2,  # Bob Smith
                "status": "in_progress",
                "priority": "high",
                "created_at": "2024-01-20T09:00:00Z",
                "due_date": "2024-02-15T17:00:00Z"
            },
            {
                "id": 2,
                "title": "Design database schema",
                "description": "Create comprehensive database design for the application",
                "assigned_to": 1,  # Alice Johnson
                "status": "completed",
                "priority": "high",
                "created_at": "2024-01-18T10:00:00Z",
                "due_date": "2024-01-25T17:00:00Z"
            },
            {
                "id": 3,
                "title": "Write unit tests for API endpoints",
                "description": "Create comprehensive test suite for all REST API endpoints",
                "assigned_to": 3,  # Carol Davis
                "status": "pending",
                "priority": "medium",
                "created_at": "2024-01-22T11:30:00Z",
                "due_date": "2024-02-20T17:00:00Z"
            },
            {
                "id": 4,
                "title": "Set up CI/CD pipeline",
                "description": "Configure automated testing and deployment pipeline",
                "assigned_to": 4,  # David Wilson
                "status": "in_progress",
                "priority": "medium",
                "created_at": "2024-01-21T14:00:00Z",
                "due_date": "2024-02-10T17:00:00Z"
            },
            {
                "id": 5,
                "title": "Create user documentation",
                "description": "Write comprehensive user guide and API documentation",
                "assigned_to": 1,  # Alice Johnson
                "status": "pending",
                "priority": "low",
                "created_at": "2024-01-23T16:00:00Z",
                "due_date": "2024-03-01T17:00:00Z"
            },
            {
                "id": 6,
                "title": "Performance optimization",
                "description": "Optimize database queries and API response times",
                "assigned_to": 2,  # Bob Smith
                "status": "pending",
                "priority": "medium",
                "created_at": "2024-01-24T13:00:00Z",
                "due_date": "2024-02-28T17:00:00Z"
            }
        ]
        return sample_tasks
    
    def generate_sample_products(self) -> List[Dict[str, Any]]:
        """
        Generate sample product data with pricing information.
        
        Returns:
            List of product dictionaries with pricing
        """
        sample_products = [
            {
                "id": 1,
                "name": "Wireless Bluetooth Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "price": 199.99,
                "category": "Electronics",
                "in_stock": True,
                "created_at": "2024-01-10T12:00:00Z"
            },
            {
                "id": 2,
                "name": "Ergonomic Office Chair",
                "description": "Comfortable office chair with lumbar support and adjustable height",
                "price": 349.99,
                "category": "Furniture",
                "in_stock": True,
                "created_at": "2024-01-11T15:30:00Z"
            },
            {
                "id": 3,
                "name": "Mechanical Keyboard",
                "description": "RGB backlit mechanical keyboard with blue switches",
                "price": 129.99,
                "category": "Electronics",
                "in_stock": False,
                "created_at": "2024-01-12T10:15:00Z"
            },
            {
                "id": 4,
                "name": "Standing Desk Converter",
                "description": "Adjustable standing desk converter for healthier work habits",
                "price": 299.99,
                "category": "Furniture",
                "in_stock": True,
                "created_at": "2024-01-13T14:45:00Z"
            },
            {
                "id": 5,
                "name": "4K Webcam",
                "description": "Ultra HD webcam with auto-focus and built-in microphone",
                "price": 89.99,
                "category": "Electronics",
                "in_stock": True,
                "created_at": "2024-01-14T11:20:00Z"
            }
        ]
        return sample_products
    
    def initialize_sample_data(self, force_reset: bool = False) -> Dict[str, int]:
        """
        Initialize the database with sample data for all collections.
        
        Args:
            force_reset: If True, clear existing data before inserting samples
            
        Returns:
            Dictionary with count of records inserted for each collection
        """
        try:
            result = {"users": 0, "tasks": 0, "products": 0}
            
            # Clear existing data if force_reset is True
            if force_reset:
                self.users.truncate()
                self.tasks.truncate()
                self.products.truncate()
                self.logger.info("Cleared existing data from all collections")
            
            # Initialize users collection
            if len(self.users.all()) == 0:
                sample_users = self.generate_sample_users()
                self.users.insert_multiple(sample_users)
                result["users"] = len(sample_users)
                self.logger.info(f"Inserted {len(sample_users)} sample users")
            else:
                self.logger.info("Users collection already has data, skipping initialization")
            
            # Initialize tasks collection
            if len(self.tasks.all()) == 0:
                sample_tasks = self.generate_sample_tasks()
                self.tasks.insert_multiple(sample_tasks)
                result["tasks"] = len(sample_tasks)
                self.logger.info(f"Inserted {len(sample_tasks)} sample tasks")
            else:
                self.logger.info("Tasks collection already has data, skipping initialization")
            
            # Initialize products collection
            if len(self.products.all()) == 0:
                sample_products = self.generate_sample_products()
                self.products.insert_multiple(sample_products)
                result["products"] = len(sample_products)
                self.logger.info(f"Inserted {len(sample_products)} sample products")
            else:
                self.logger.info("Products collection already has data, skipping initialization")
            
            self.logger.info("Sample data initialization completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error initializing sample data: {str(e)}")
            raise
    
    def create_record(self, collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record in the specified collection.
        
        Args:
            collection_name: Name of the collection ('users', 'tasks', 'products')
            data: Dictionary containing the record data
            
        Returns:
            Dictionary with operation result including the created record
            
        Raises:
            ValueError: If collection name is invalid or data validation fails
            ConnectionError: If database is not connected
        """
        try:
            # Validate collection name
            collection = self.get_collection(collection_name)
            
            # Validate and prepare data
            validated_data = self._validate_create_data(collection_name, data)
            
            # Auto-generate ID if not provided
            if 'id' not in validated_data or validated_data['id'] is None:
                validated_data['id'] = self.get_next_id(collection_name)
            
            # Add created_at timestamp if not provided
            if 'created_at' not in validated_data:
                validated_data['created_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            
            # Insert the record
            doc_id = collection.insert(validated_data)
            
            # Retrieve the inserted record
            inserted_record = collection.get(doc_id=doc_id)
            
            self.logger.info(f"Successfully created record in {collection_name} with ID {validated_data['id']}")
            
            return {
                "success": True,
                "data": inserted_record,
                "message": f"Record created successfully in {collection_name}",
                "count": 1,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Failed to create record in {collection_name}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "data": None,
                "message": "Record creation failed",
                "count": 0,
                "error": error_msg
            }
    
    def _validate_create_data(self, collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data for record creation based on collection schema.
        
        Args:
            collection_name: Name of the collection
            data: Data to validate
            
        Returns:
            Validated and cleaned data dictionary
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        if not data:
            raise ValueError("Data cannot be empty")
        
        # Make a copy to avoid modifying the original
        validated_data = data.copy()
        
        # Collection-specific validation
        if collection_name == 'users':
            return self._validate_user_data(validated_data)
        elif collection_name == 'tasks':
            return self._validate_task_data(validated_data)
        elif collection_name == 'products':
            return self._validate_product_data(validated_data)
        else:
            # Generic validation for unknown collections
            return validated_data
    
    def _validate_user_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user data according to schema."""
        required_fields = ['name', 'email']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Required field '{field}' is missing or empty")
        
        # Validate email format (basic check)
        email = data['email']
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise ValueError("Invalid email format")
        
        # Set default role if not provided
        if 'role' not in data or not data['role']:
            data['role'] = 'User'
        
        return data
    
    def _validate_task_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate task data according to schema."""
        required_fields = ['title']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Required field '{field}' is missing or empty")
        
        # Set defaults for optional fields
        if 'status' not in data:
            data['status'] = 'pending'
        
        if 'priority' not in data:
            data['priority'] = 'medium'
        
        # Validate status values
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'archived']
        if data['status'] not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        # Validate priority values
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if data['priority'] not in valid_priorities:
            raise ValueError(f"Invalid priority. Must be one of: {valid_priorities}")
        
        # Validate assigned_to if provided
        if 'assigned_to' in data and data['assigned_to'] is not None:
            if not isinstance(data['assigned_to'], int) or data['assigned_to'] <= 0:
                raise ValueError("assigned_to must be a positive integer (user ID)")
        
        return data
    
    def _validate_product_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate product data according to schema."""
        required_fields = ['name', 'price']
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"Required field '{field}' is missing or None")
        
        # Validate price
        try:
            price = float(data['price'])
        except (ValueError, TypeError):
            raise ValueError("Price must be a valid number")
        
        if price < 0:
            raise ValueError("Price cannot be negative")
        
        data['price'] = price
        
        # Set defaults for optional fields
        if 'in_stock' not in data:
            data['in_stock'] = True
        
        if 'category' not in data:
            data['category'] = 'General'
        
        return data
    
    def read_records(self, collection_name: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Read records from the specified collection with optional filtering.
        
        Args:
            collection_name: Name of the collection ('users', 'tasks', 'products')
            filters: Optional dictionary of filter criteria
            
        Returns:
            Dictionary with operation result including the found records
            
        Raises:
            ValueError: If collection name is invalid
            ConnectionError: If database is not connected
        """
        try:
            # Validate collection name
            collection = self.get_collection(collection_name)
            
            # Apply filters if provided
            if filters:
                records = self._apply_filters(collection, filters)
            else:
                records = collection.all()
            
            self.logger.info(f"Successfully read {len(records)} records from {collection_name}")
            
            return {
                "success": True,
                "data": records,
                "message": f"Successfully retrieved {len(records)} records from {collection_name}",
                "count": len(records),
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Failed to read records from {collection_name}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "data": [],
                "message": "Record retrieval failed",
                "count": 0,
                "error": error_msg
            }
    
    def _apply_filters(self, collection: Table, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply filter criteria to a collection query using advanced query parser.
        
        Args:
            collection: TinyDB table to query
            filters: Dictionary of filter criteria (supports advanced syntax)
            
        Returns:
            List of records matching the filter criteria
        """
        if not filters:
            return collection.all()
        
        try:
            # Use the advanced query parser to build the query
            parsed_query = self.query_parser.parse_query(filters)
            
            if parsed_query is None:
                return collection.all()
            
            return collection.search(parsed_query)
            
        except ValueError as e:
            # If advanced parsing fails, fall back to legacy parsing for backward compatibility
            self.logger.warning(f"Advanced query parsing failed, falling back to legacy: {str(e)}")
            return self._apply_legacy_filters(collection, filters)
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            raise
    
    def _apply_legacy_filters(self, collection: Table, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Legacy filter application for backward compatibility.
        
        Args:
            collection: TinyDB table to query
            filters: Dictionary of filter criteria
            
        Returns:
            List of records matching the filter criteria
        """
        # Build query conditions using the old method
        query_conditions = []
        Query_obj = Query()
        
        for field, value in filters.items():
            if isinstance(value, dict):
                # Handle complex filter conditions
                query_conditions.extend(self._parse_complex_filter(Query_obj, field, value))
            else:
                # Simple equality filter
                query_conditions.append(Query_obj[field] == value)
        
        # Combine all conditions with AND logic
        if len(query_conditions) == 1:
            final_query = query_conditions[0]
        else:
            final_query = query_conditions[0]
            for condition in query_conditions[1:]:
                final_query = final_query & condition
        
        return collection.search(final_query)
    
    def _parse_complex_filter(self, Query_obj: Query, field: str, filter_spec: Dict[str, Any]) -> List:
        """
        Parse complex filter specifications into TinyDB query conditions.
        
        Args:
            Query_obj: TinyDB Query object
            field: Field name to filter on
            filter_spec: Dictionary specifying the filter operation
            
        Returns:
            List of query conditions
        """
        conditions = []
        
        for operator, value in filter_spec.items():
            if operator == 'eq' or operator == 'equals':
                conditions.append(Query_obj[field] == value)
            elif operator == 'ne' or operator == 'not_equals':
                conditions.append(Query_obj[field] != value)
            elif operator == 'gt' or operator == 'greater_than':
                conditions.append(Query_obj[field] > value)
            elif operator == 'gte' or operator == 'greater_than_or_equal':
                conditions.append(Query_obj[field] >= value)
            elif operator == 'lt' or operator == 'less_than':
                conditions.append(Query_obj[field] < value)
            elif operator == 'lte' or operator == 'less_than_or_equal':
                conditions.append(Query_obj[field] <= value)
            elif operator == 'contains':
                conditions.append(Query_obj[field].search(value))
            elif operator == 'in':
                if isinstance(value, list):
                    # Create OR condition for multiple values
                    in_conditions = [Query_obj[field] == v for v in value]
                    if len(in_conditions) == 1:
                        conditions.append(in_conditions[0])
                    else:
                        in_query = in_conditions[0]
                        for cond in in_conditions[1:]:
                            in_query = in_query | cond
                        conditions.append(in_query)
                else:
                    conditions.append(Query_obj[field] == value)
            elif operator == 'exists':
                if value:
                    conditions.append(Query_obj[field].exists())
                else:
                    conditions.append(~Query_obj[field].exists())
            else:
                raise ValueError(f"Unsupported filter operator: {operator}")
        
        return conditions
    
    def update_records(self, collection_name: str, filters: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update records in the specified collection based on filter criteria.
        
        Args:
            collection_name: Name of the collection ('users', 'tasks', 'products')
            filters: Dictionary of filter criteria to identify records to update
            updates: Dictionary of field updates to apply
            
        Returns:
            Dictionary with operation result including count of updated records
            
        Raises:
            ValueError: If collection name is invalid or validation fails
            ConnectionError: If database is not connected
        """
        try:
            # Validate collection name
            collection = self.get_collection(collection_name)
            
            # Validate filters
            if not filters:
                raise ValueError("Filters are required for update operations to prevent accidental bulk updates")
            
            # Validate and prepare update data
            validated_updates = self._validate_update_data(collection_name, updates)
            
            # Find records that match the filter
            matching_records = self._apply_filters(collection, filters)
            
            if not matching_records:
                self.logger.info(f"No records found matching filters in {collection_name}")
                return {
                    "success": True,
                    "data": [],
                    "message": f"No records found matching the specified criteria in {collection_name}",
                    "count": 0,
                    "error": None
                }
            
            # Build query for update
            query_conditions = []
            Query_obj = Query()
            
            for field, value in filters.items():
                if isinstance(value, dict):
                    query_conditions.extend(self._parse_complex_filter(Query_obj, field, value))
                else:
                    query_conditions.append(Query_obj[field] == value)
            
            # Combine conditions with AND logic
            if len(query_conditions) == 1:
                final_query = query_conditions[0]
            else:
                final_query = query_conditions[0]
                for condition in query_conditions[1:]:
                    final_query = final_query & condition
            
            # Perform the update
            updated_doc_ids = collection.update(validated_updates, final_query)
            updated_count = len(updated_doc_ids) if isinstance(updated_doc_ids, list) else updated_doc_ids
            
            # Get updated records for response
            updated_records = self._apply_filters(collection, filters)
            
            self.logger.info(f"Successfully updated {updated_count} records in {collection_name}")
            
            return {
                "success": True,
                "data": updated_records,
                "message": f"Successfully updated {updated_count} records in {collection_name}",
                "count": updated_count,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Failed to update records in {collection_name}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "data": [],
                "message": "Record update failed",
                "count": 0,
                "error": error_msg
            }
    
    def _validate_update_data(self, collection_name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data for record updates based on collection schema.
        
        Args:
            collection_name: Name of the collection
            updates: Update data to validate
            
        Returns:
            Validated update data dictionary
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(updates, dict):
            raise ValueError("Updates must be a dictionary")
        
        if not updates:
            raise ValueError("Updates cannot be empty")
        
        # Make a copy to avoid modifying the original
        validated_updates = updates.copy()
        
        # Don't allow updating ID field
        if 'id' in validated_updates:
            raise ValueError("Cannot update the 'id' field")
        
        # Don't allow updating created_at field
        if 'created_at' in validated_updates:
            raise ValueError("Cannot update the 'created_at' field")
        
        # Collection-specific validation
        if collection_name == 'users':
            return self._validate_user_update_data(validated_updates)
        elif collection_name == 'tasks':
            return self._validate_task_update_data(validated_updates)
        elif collection_name == 'products':
            return self._validate_product_update_data(validated_updates)
        else:
            # Generic validation for unknown collections
            return validated_updates
    
    def _validate_user_update_data(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user update data according to schema."""
        # Validate email format if provided
        if 'email' in updates and updates['email']:
            email = updates['email']
            if '@' not in email or '.' not in email.split('@')[-1]:
                raise ValueError("Invalid email format")
        
        return updates
    
    def _validate_task_update_data(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Validate task update data according to schema."""
        # Validate status values if provided
        if 'status' in updates:
            valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'archived']
            if updates['status'] not in valid_statuses:
                raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        # Validate priority values if provided
        if 'priority' in updates:
            valid_priorities = ['low', 'medium', 'high', 'urgent']
            if updates['priority'] not in valid_priorities:
                raise ValueError(f"Invalid priority. Must be one of: {valid_priorities}")
        
        # Validate assigned_to if provided
        if 'assigned_to' in updates and updates['assigned_to'] is not None:
            if not isinstance(updates['assigned_to'], int) or updates['assigned_to'] <= 0:
                raise ValueError("assigned_to must be a positive integer (user ID)")
        
        return updates
    
    def _validate_product_update_data(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Validate product update data according to schema."""
        # Validate price if provided
        if 'price' in updates:
            try:
                price = float(updates['price'])
            except (ValueError, TypeError):
                raise ValueError("Price must be a valid number")
            
            if price < 0:
                raise ValueError("Price cannot be negative")
            
            updates['price'] = price
        
        return updates
    
    def delete_records(self, collection_name: str, filters: Dict[str, Any], soft_delete: bool = False) -> Dict[str, Any]:
        """
        Delete records from the specified collection based on filter criteria.
        
        Args:
            collection_name: Name of the collection ('users', 'tasks', 'products')
            filters: Dictionary of filter criteria to identify records to delete
            soft_delete: If True, mark records as deleted instead of removing them
            
        Returns:
            Dictionary with operation result including count of deleted records
            
        Raises:
            ValueError: If collection name is invalid or validation fails
            ConnectionError: If database is not connected
        """
        try:
            # Validate collection name
            collection = self.get_collection(collection_name)
            
            # Validate filters
            if not filters:
                raise ValueError("Filters are required for delete operations to prevent accidental bulk deletions")
            
            # Find records that match the filter before deletion
            matching_records = self._apply_filters(collection, filters)
            
            if not matching_records:
                self.logger.info(f"No records found matching filters in {collection_name}")
                return {
                    "success": True,
                    "data": [],
                    "message": f"No records found matching the specified criteria in {collection_name}",
                    "count": 0,
                    "error": None
                }
            
            # Safety check for bulk deletions
            if len(matching_records) > 10:
                self.logger.warning(f"Attempting to delete {len(matching_records)} records from {collection_name}")
                # Could add additional confirmation logic here if needed
            
            # Store records for response before deletion
            records_to_delete = matching_records.copy()
            
            if soft_delete:
                # Soft delete: mark records as deleted
                deleted_count = self._perform_soft_delete(collection, filters)
            else:
                # Hard delete: remove records completely
                deleted_count = self._perform_hard_delete(collection, filters)
            
            self.logger.info(f"Successfully deleted {deleted_count} records from {collection_name}")
            
            return {
                "success": True,
                "data": records_to_delete,
                "message": f"Successfully deleted {deleted_count} records from {collection_name}",
                "count": deleted_count,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Failed to delete records from {collection_name}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "data": [],
                "message": "Record deletion failed",
                "count": 0,
                "error": error_msg
            }
    
    def _perform_hard_delete(self, collection: Table, filters: Dict[str, Any]) -> int:
        """
        Perform hard deletion of records matching the filters.
        
        Args:
            collection: TinyDB table to delete from
            filters: Filter criteria
            
        Returns:
            Number of records deleted
        """
        # Build query conditions
        query_conditions = []
        Query_obj = Query()
        
        for field, value in filters.items():
            if isinstance(value, dict):
                query_conditions.extend(self._parse_complex_filter(Query_obj, field, value))
            else:
                query_conditions.append(Query_obj[field] == value)
        
        # Combine conditions with AND logic
        if len(query_conditions) == 1:
            final_query = query_conditions[0]
        else:
            final_query = query_conditions[0]
            for condition in query_conditions[1:]:
                final_query = final_query & condition
        
        # Perform the deletion
        deleted_doc_ids = collection.remove(final_query)
        return len(deleted_doc_ids) if isinstance(deleted_doc_ids, list) else deleted_doc_ids
    
    def _perform_soft_delete(self, collection: Table, filters: Dict[str, Any]) -> int:
        """
        Perform soft deletion of records matching the filters.
        
        Args:
            collection: TinyDB table to update
            filters: Filter criteria
            
        Returns:
            Number of records soft-deleted
        """
        # Build query conditions
        query_conditions = []
        Query_obj = Query()
        
        for field, value in filters.items():
            if isinstance(value, dict):
                query_conditions.extend(self._parse_complex_filter(Query_obj, field, value))
            else:
                query_conditions.append(Query_obj[field] == value)
        
        # Combine conditions with AND logic
        if len(query_conditions) == 1:
            final_query = query_conditions[0]
        else:
            final_query = query_conditions[0]
            for condition in query_conditions[1:]:
                final_query = final_query & condition
        
        # Mark records as deleted
        soft_delete_data = {
            'deleted': True,
            'deleted_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        updated_doc_ids = collection.update(soft_delete_data, final_query)
        return len(updated_doc_ids) if isinstance(updated_doc_ids, list) else updated_doc_ids   
 
    def advanced_search(self, collection_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform advanced search with complex filtering capabilities.
        Supports logical operators (AND, OR, NOT) and comparison operators.
        
        Args:
            collection_name: Name of the collection ('users', 'tasks', 'products')
            query: Advanced query dictionary with logical and comparison operators
            
        Returns:
            Dictionary with operation result including matching records
            
        Raises:
            ValueError: If collection name is invalid or query syntax is invalid
            ConnectionError: If database is not connected
        """
        try:
            # Validate collection name
            collection = self.get_collection(collection_name)
            
            # Validate query syntax
            if query:
                self.query_parser.validate_query_syntax(query)
            
            # Execute the advanced search
            matching_records = self._apply_filters(collection, query)
            
            self.logger.info(f"Advanced search found {len(matching_records)} records in {collection_name}")
            
            return {
                "success": True,
                "data": matching_records,
                "message": f"Advanced search completed successfully, found {len(matching_records)} records",
                "count": len(matching_records),
                "error": None,
                "query": query
            }
            
        except Exception as e:
            error_msg = f"Advanced search failed in {collection_name}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "data": [],
                "message": "Advanced search failed",
                "count": 0,
                "error": error_msg,
                "query": query if 'query' in locals() else None
            }
    
    def get_query_capabilities(self) -> Dict[str, Any]:
        """
        Get information about supported query capabilities.
        
        Returns:
            Dictionary describing supported operators and syntax
        """
        return {
            "supported_operators": self.query_parser.get_supported_operators(),
            "syntax_examples": {
                "simple_equality": {"field": "value"},
                "comparison": {"field": {"gt": 10}},
                "logical_and": {"$and": [{"field1": "value1"}, {"field2": "value2"}]},
                "logical_or": {"$or": [{"field1": "value1"}, {"field2": "value2"}]},
                "logical_not": {"$not": {"field": "value"}},
                "complex_example": {
                    "$and": [
                        {"status": "active"},
                        {"$or": [
                            {"priority": {"in": ["high", "urgent"]}},
                            {"assigned_to": {"exists": True}}
                        ]},
                        {"created_at": {"gte": "2024-01-01"}}
                    ]
                }
            },
            "field_operators": {
                "equality": ["eq", "ne"],
                "comparison": ["gt", "gte", "lt", "lte"],
                "string": ["contains", "startswith", "endswith"],
                "list": ["in", "not_in"],
                "existence": ["exists"],
                "range": ["between"]
            }
        }   
 
    def get_tasks_by_user(self, user_id: int, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all tasks assigned to a specific user with optional status filtering.
        
        Args:
            user_id: ID of the user to get tasks for
            status_filter: Optional status to filter by ('pending', 'in_progress', 'completed', etc.)
            
        Returns:
            Dictionary with operation result including user's tasks
            
        Raises:
            ValueError: If user_id is invalid
            ConnectionError: If database is not connected
        """
        try:
            # Validate user_id
            if not isinstance(user_id, int) or user_id <= 0:
                raise ValueError("user_id must be a positive integer")
            
            # Validate user exists
            user_exists = self._validate_user_exists(user_id)
            if not user_exists:
                self.logger.warning(f"User with ID {user_id} does not exist")
                return {
                    "success": True,
                    "data": [],
                    "message": f"User with ID {user_id} does not exist",
                    "count": 0,
                    "error": None,
                    "user_id": user_id,
                    "status_filter": status_filter
                }
            
            # Build query for user's tasks
            query = {"assigned_to": user_id}
            
            # Add status filter if provided
            if status_filter:
                # Validate status
                valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'archived']
                if status_filter not in valid_statuses:
                    raise ValueError(f"Invalid status filter. Must be one of: {valid_statuses}")
                query["status"] = status_filter
            
            # Execute the query
            result = self.read_records("tasks", query)
            
            if result["success"]:
                self.logger.info(f"Found {result['count']} tasks for user {user_id}" + 
                               (f" with status '{status_filter}'" if status_filter else ""))
                
                return {
                    "success": True,
                    "data": result["data"],
                    "message": f"Successfully retrieved {result['count']} tasks for user {user_id}" + 
                              (f" with status '{status_filter}'" if status_filter else ""),
                    "count": result["count"],
                    "error": None,
                    "user_id": user_id,
                    "status_filter": status_filter
                }
            else:
                return result
                
        except Exception as e:
            error_msg = f"Failed to get tasks for user {user_id}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "data": [],
                "message": "Failed to retrieve user tasks",
                "count": 0,
                "error": error_msg,
                "user_id": user_id if 'user_id' in locals() else None,
                "status_filter": status_filter if 'status_filter' in locals() else None
            }
    
    def get_user_task_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Get a summary of tasks for a specific user grouped by status.
        
        Args:
            user_id: ID of the user to get task summary for
            
        Returns:
            Dictionary with task counts by status and detailed breakdown
        """
        try:
            # Validate user_id
            if not isinstance(user_id, int) or user_id <= 0:
                raise ValueError("user_id must be a positive integer")
            
            # Validate user exists
            user_exists = self._validate_user_exists(user_id)
            if not user_exists:
                return {
                    "success": True,
                    "data": {
                        "user_id": user_id,
                        "user_exists": False,
                        "total_tasks": 0,
                        "by_status": {},
                        "by_priority": {}
                    },
                    "message": f"User with ID {user_id} does not exist",
                    "count": 0,
                    "error": None
                }
            
            # Get all tasks for the user
            all_tasks_result = self.get_tasks_by_user(user_id)
            
            if not all_tasks_result["success"]:
                return all_tasks_result
            
            tasks = all_tasks_result["data"]
            
            # Group tasks by status
            status_counts = {}
            priority_counts = {}
            
            for task in tasks:
                # Count by status
                status = task.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Count by priority
                priority = task.get("priority", "unknown")
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            summary_data = {
                "user_id": user_id,
                "user_exists": True,
                "total_tasks": len(tasks),
                "by_status": status_counts,
                "by_priority": priority_counts
            }
            
            self.logger.info(f"Generated task summary for user {user_id}: {len(tasks)} total tasks")
            
            return {
                "success": True,
                "data": summary_data,
                "message": f"Successfully generated task summary for user {user_id}",
                "count": len(tasks),
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Failed to generate task summary for user {user_id}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "data": {},
                "message": "Failed to generate task summary",
                "count": 0,
                "error": error_msg
            }
    
    def get_tasks_by_multiple_users(self, user_ids: List[int], status_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Get tasks assigned to multiple users with optional status filtering.
        
        Args:
            user_ids: List of user IDs to get tasks for
            status_filter: Optional status to filter by
            
        Returns:
            Dictionary with tasks grouped by user
        """
        try:
            # Validate input
            if not isinstance(user_ids, list) or not user_ids:
                raise ValueError("user_ids must be a non-empty list")
            
            if not all(isinstance(uid, int) and uid > 0 for uid in user_ids):
                raise ValueError("All user_ids must be positive integers")
            
            # Build query using advanced search
            if len(user_ids) == 1:
                query = {"assigned_to": user_ids[0]}
            else:
                query = {"assigned_to": {"in": user_ids}}
            
            # Add status filter if provided
            if status_filter:
                valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'archived']
                if status_filter not in valid_statuses:
                    raise ValueError(f"Invalid status filter. Must be one of: {valid_statuses}")
                
                if len(user_ids) == 1:
                    query["status"] = status_filter
                else:
                    query = {
                        "$and": [
                            {"assigned_to": {"in": user_ids}},
                            {"status": status_filter}
                        ]
                    }
            
            # Execute advanced search
            result = self.advanced_search("tasks", query)
            
            if result["success"]:
                # Group tasks by user
                tasks_by_user = {}
                for user_id in user_ids:
                    tasks_by_user[user_id] = []
                
                for task in result["data"]:
                    assigned_to = task.get("assigned_to")
                    if assigned_to in user_ids:
                        tasks_by_user[assigned_to].append(task)
                
                return {
                    "success": True,
                    "data": {
                        "tasks_by_user": tasks_by_user,
                        "total_tasks": result["count"],
                        "user_ids": user_ids,
                        "status_filter": status_filter
                    },
                    "message": f"Successfully retrieved tasks for {len(user_ids)} users",
                    "count": result["count"],
                    "error": None
                }
            else:
                return result
                
        except Exception as e:
            error_msg = f"Failed to get tasks for multiple users: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "data": {},
                "message": "Failed to retrieve tasks for multiple users",
                "count": 0,
                "error": error_msg
            }
    
    def _validate_user_exists(self, user_id: int) -> bool:
        """
        Validate that a user exists in the database.
        
        Args:
            user_id: ID of the user to validate
            
        Returns:
            True if user exists, False otherwise
        """
        try:
            user_result = self.read_records("users", {"id": user_id})
            return user_result["success"] and user_result["count"] > 0
        except Exception as e:
            self.logger.error(f"Error validating user existence: {str(e)}")
            return False
    
    def get_unassigned_tasks(self, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all tasks that are not assigned to any user.
        
        Args:
            status_filter: Optional status to filter by
            
        Returns:
            Dictionary with unassigned tasks
        """
        try:
            # Build query for unassigned tasks
            query = {
                "$or": [
                    {"assigned_to": {"exists": False}},
                    {"assigned_to": None}
                ]
            }
            
            # Add status filter if provided
            if status_filter:
                valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'archived']
                if status_filter not in valid_statuses:
                    raise ValueError(f"Invalid status filter. Must be one of: {valid_statuses}")
                
                query = {
                    "$and": [
                        query,
                        {"status": status_filter}
                    ]
                }
            
            # Execute advanced search
            result = self.advanced_search("tasks", query)
            
            if result["success"]:
                return {
                    "success": True,
                    "data": result["data"],
                    "message": f"Successfully retrieved {result['count']} unassigned tasks" + 
                              (f" with status '{status_filter}'" if status_filter else ""),
                    "count": result["count"],
                    "error": None,
                    "status_filter": status_filter
                }
            else:
                return result
                
        except Exception as e:
            error_msg = f"Failed to get unassigned tasks: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "data": [],
                "message": "Failed to retrieve unassigned tasks",
                "count": 0,
                "error": error_msg
            }