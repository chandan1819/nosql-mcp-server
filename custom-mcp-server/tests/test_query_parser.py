"""
Unit tests for the QueryParser class.
Tests advanced query parsing with logical and comparison operators.
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from database.query_parser import QueryParser, QueryBuilder, FieldBuilder
from database.manager import DatabaseManager
from tinydb import Query


class TestQueryParser:
    """Test cases for QueryParser class."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.parser = QueryParser()
    
    def test_simple_equality_query(self):
        """Test parsing simple equality queries."""
        query = {"name": "Alice"}
        parsed = self.parser.parse_query(query)
        
        assert parsed is not None
        # The parsed query should be a TinyDB QueryPath object
        assert hasattr(parsed, '__call__')
    
    def test_multiple_field_equality(self):
        """Test parsing multiple field equality (implicit AND)."""
        query = {"name": "Alice", "role": "Admin"}
        parsed = self.parser.parse_query(query)
        
        assert parsed is not None
        assert hasattr(parsed, '__call__')
    
    def test_comparison_operators(self):
        """Test parsing comparison operators."""
        test_cases = [
            {"age": {"gt": 25}},
            {"age": {"gte": 25}},
            {"age": {"lt": 65}},
            {"age": {"lte": 65}},
            {"price": {">": 100.0}},
            {"price": {">=": 100.0}},
            {"price": {"<": 500.0}},
            {"price": {"<=": 500.0}}
        ]
        
        for query in test_cases:
            parsed = self.parser.parse_query(query)
            assert parsed is not None
            assert hasattr(parsed, '__call__')
    
    def test_equality_operators(self):
        """Test parsing equality and inequality operators."""
        test_cases = [
            {"status": {"eq": "active"}},
            {"status": {"equals": "active"}},
            {"status": {"==": "active"}},
            {"status": {"ne": "inactive"}},
            {"status": {"not_equals": "inactive"}},
            {"status": {"!=": "inactive"}}
        ]
        
        for query in test_cases:
            parsed = self.parser.parse_query(query)
            assert parsed is not None
            assert hasattr(parsed, '__call__')
    
    def test_string_operators(self):
        """Test parsing string-specific operators."""
        test_cases = [
            {"title": {"contains": "test"}},
            {"title": {"like": "test"}},
            {"name": {"startswith": "John"}},
            {"name": {"starts_with": "John"}},
            {"email": {"endswith": "@example.com"}},
            {"email": {"ends_with": "@example.com"}}
        ]
        
        for query in test_cases:
            parsed = self.parser.parse_query(query)
            assert parsed is not None
            assert hasattr(parsed, '__call__')
    
    def test_list_operators(self):
        """Test parsing list-based operators."""
        test_cases = [
            {"status": {"in": ["active", "pending"]}},
            {"priority": {"not_in": ["low", "medium"]}},
            {"category": {"in": ["electronics", "books"]}}
        ]
        
        for query in test_cases:
            parsed = self.parser.parse_query(query)
            assert parsed is not None
            assert hasattr(parsed, '__call__')
    
    def test_existence_operators(self):
        """Test parsing existence operators."""
        test_cases = [
            {"assigned_to": {"exists": True}},
            {"assigned_to": {"exists": False}},
            {"optional_field": {"exists": True}}
        ]
        
        for query in test_cases:
            parsed = self.parser.parse_query(query)
            assert parsed is not None
            assert hasattr(parsed, '__call__')
    
    def test_range_operators(self):
        """Test parsing range operators."""
        test_cases = [
            {"age": {"between": [18, 65]}},
            {"price": {"between": [10.0, 100.0]}},
            {"score": {"between": [0, 100]}}
        ]
        
        for query in test_cases:
            parsed = self.parser.parse_query(query)
            assert parsed is not None
            assert hasattr(parsed, '__call__')
    
    def test_logical_and_operator(self):
        """Test parsing AND logical operator."""
        query = {
            "$and": [
                {"status": "active"},
                {"priority": "high"}
            ]
        }
        parsed = self.parser.parse_query(query)
        
        assert parsed is not None
        assert hasattr(parsed, '__call__')
    
    def test_logical_or_operator(self):
        """Test parsing OR logical operator."""
        query = {
            "$or": [
                {"status": "urgent"},
                {"priority": "high"}
            ]
        }
        parsed = self.parser.parse_query(query)
        
        assert parsed is not None
        assert hasattr(parsed, '__call__')
    
    def test_logical_not_operator(self):
        """Test parsing NOT logical operator."""
        query = {
            "$not": {"status": "inactive"}
        }
        parsed = self.parser.parse_query(query)
        
        assert parsed is not None
        assert hasattr(parsed, '__call__')
    
    def test_nested_logical_operators(self):
        """Test parsing nested logical operators."""
        query = {
            "$and": [
                {"status": "active"},
                {
                    "$or": [
                        {"priority": "high"},
                        {"assigned_to": {"exists": True}}
                    ]
                }
            ]
        }
        parsed = self.parser.parse_query(query)
        
        assert parsed is not None
        assert hasattr(parsed, '__call__')
    
    def test_complex_query_example(self):
        """Test parsing a complex real-world query."""
        query = {
            "$and": [
                {"status": {"in": ["active", "pending"]}},
                {
                    "$or": [
                        {"priority": "urgent"},
                        {
                            "$and": [
                                {"assigned_to": {"exists": True}},
                                {"due_date": {"lt": "2024-12-31"}}
                            ]
                        }
                    ]
                },
                {"$not": {"category": "archived"}}
            ]
        }
        parsed = self.parser.parse_query(query)
        
        assert parsed is not None
        assert hasattr(parsed, '__call__')
    
    def test_empty_query(self):
        """Test parsing empty query."""
        query = {}
        parsed = self.parser.parse_query(query)
        
        assert parsed is None
    
    def test_none_query(self):
        """Test parsing None query."""
        parsed = self.parser.parse_query(None)
        assert parsed is None
    
    def test_invalid_operator(self):
        """Test parsing with invalid operator raises ValueError."""
        query = {"field": {"invalid_operator": "value"}}
        
        with pytest.raises(ValueError, match="Unsupported operator"):
            self.parser.parse_query(query)
    
    def test_invalid_in_operator_value(self):
        """Test 'in' operator with invalid value type."""
        query = {"field": {"in": "not_a_list"}}
        
        with pytest.raises(ValueError, match="'in' operator requires a list"):
            self.parser.parse_query(query)
    
    def test_invalid_between_operator_value(self):
        """Test 'between' operator with invalid value."""
        query = {"field": {"between": [1, 2, 3]}}  # Too many values
        
        with pytest.raises(ValueError, match="'between' operator requires a list/tuple with exactly 2 values"):
            self.parser.parse_query(query)
    
    def test_empty_and_condition(self):
        """Test AND operator with empty conditions."""
        query = {"$and": []}
        
        with pytest.raises(ValueError, match="AND operation requires at least one condition"):
            self.parser.parse_query(query)
    
    def test_empty_or_condition(self):
        """Test OR operator with empty conditions."""
        query = {"$or": []}
        
        with pytest.raises(ValueError, match="OR operation requires at least one condition"):
            self.parser.parse_query(query)
    
    def test_empty_not_condition(self):
        """Test NOT operator with empty condition."""
        query = {"$not": {}}
        
        with pytest.raises(ValueError, match="NOT operation requires a condition"):
            self.parser.parse_query(query)
    
    def test_validate_query_syntax_valid(self):
        """Test query syntax validation with valid queries."""
        valid_queries = [
            {"name": "Alice"},
            {"age": {"gt": 25}},
            {"$and": [{"status": "active"}, {"priority": "high"}]},
            {"$or": [{"role": "admin"}, {"role": "manager"}]}
        ]
        
        for query in valid_queries:
            assert self.parser.validate_query_syntax(query) is True
    
    def test_validate_query_syntax_invalid(self):
        """Test query syntax validation with invalid queries."""
        invalid_queries = [
            {"field": {"invalid_op": "value"}},
            {"$and": []},
            {"field": {"in": "not_a_list"}}
        ]
        
        for query in invalid_queries:
            with pytest.raises(ValueError):
                self.parser.validate_query_syntax(query)
    
    def test_get_supported_operators(self):
        """Test getting supported operators."""
        operators = self.parser.get_supported_operators()
        
        assert isinstance(operators, dict)
        assert "equality" in operators
        assert "comparison" in operators
        assert "string" in operators
        assert "list" in operators
        assert "existence" in operators
        assert "range" in operators
        assert "logical" in operators
        
        # Check some specific operators
        assert "eq" in operators["equality"]
        assert "gt" in operators["comparison"]
        assert "contains" in operators["string"]
        assert "in" in operators["list"]
        assert "$and" in operators["logical"]


class TestQueryBuilder:
    """Test cases for QueryBuilder helper class."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.builder = QueryBuilder()
    
    def test_and_conditions(self):
        """Test building AND conditions."""
        condition1 = {"status": "active"}
        condition2 = {"priority": "high"}
        
        result = self.builder.and_conditions(condition1, condition2)
        
        expected = {"$and": [condition1, condition2]}
        assert result == expected
    
    def test_or_conditions(self):
        """Test building OR conditions."""
        condition1 = {"role": "admin"}
        condition2 = {"role": "manager"}
        
        result = self.builder.or_conditions(condition1, condition2)
        
        expected = {"$or": [condition1, condition2]}
        assert result == expected
    
    def test_not_condition(self):
        """Test building NOT condition."""
        condition = {"status": "inactive"}
        
        result = self.builder.not_condition(condition)
        
        expected = {"$not": condition}
        assert result == expected
    
    def test_single_condition_and(self):
        """Test AND with single condition."""
        condition = {"status": "active"}
        
        result = self.builder.and_conditions(condition)
        
        assert result == condition
    
    def test_empty_conditions_and(self):
        """Test AND with no conditions."""
        result = self.builder.and_conditions()
        
        assert result == {}
    
    def test_field_builder(self):
        """Test field builder creation."""
        field_builder = self.builder.field("name")
        
        assert isinstance(field_builder, FieldBuilder)
        assert field_builder.field_name == "name"


class TestFieldBuilder:
    """Test cases for FieldBuilder helper class."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.builder = QueryBuilder()
        self.field_builder = self.builder.field("test_field")
    
    def test_equals(self):
        """Test equals condition builder."""
        result = self.field_builder.equals("value")
        expected = {"test_field": {"eq": "value"}}
        assert result == expected
    
    def test_not_equals(self):
        """Test not equals condition builder."""
        result = self.field_builder.not_equals("value")
        expected = {"test_field": {"ne": "value"}}
        assert result == expected
    
    def test_greater_than(self):
        """Test greater than condition builder."""
        result = self.field_builder.greater_than(10)
        expected = {"test_field": {"gt": 10}}
        assert result == expected
    
    def test_less_than_or_equal(self):
        """Test less than or equal condition builder."""
        result = self.field_builder.less_than_or_equal(100)
        expected = {"test_field": {"lte": 100}}
        assert result == expected
    
    def test_contains(self):
        """Test contains condition builder."""
        result = self.field_builder.contains("substring")
        expected = {"test_field": {"contains": "substring"}}
        assert result == expected
    
    def test_in_list(self):
        """Test in list condition builder."""
        result = self.field_builder.in_list(["a", "b", "c"])
        expected = {"test_field": {"in": ["a", "b", "c"]}}
        assert result == expected
    
    def test_exists(self):
        """Test exists condition builder."""
        result = self.field_builder.exists(True)
        expected = {"test_field": {"exists": True}}
        assert result == expected
    
    def test_between(self):
        """Test between condition builder."""
        result = self.field_builder.between(10, 20)
        expected = {"test_field": {"between": [10, 20]}}
        assert result == expected


class TestQueryParserIntegration:
    """Integration tests with DatabaseManager."""
    
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
        """Create test data for integration tests."""
        # Create test users
        users = [
            {"name": "Alice Johnson", "email": "alice@example.com", "role": "Admin", "age": 30},
            {"name": "Bob Smith", "email": "bob@example.com", "role": "User", "age": 25},
            {"name": "Carol Davis", "email": "carol@example.com", "role": "Manager", "age": 35},
            {"name": "David Wilson", "email": "david@example.com", "role": "User", "age": 28}
        ]
        
        for user in users:
            self.db_manager.create_record("users", user)
        
        # Create test tasks
        tasks = [
            {"title": "High Priority Task", "status": "in_progress", "priority": "high", "assigned_to": 1},
            {"title": "Medium Priority Task", "status": "pending", "priority": "medium", "assigned_to": 2},
            {"title": "Low Priority Task", "status": "completed", "priority": "low", "assigned_to": 3},
            {"title": "Urgent Task", "status": "in_progress", "priority": "urgent", "assigned_to": 1},
            {"title": "Unassigned Task", "status": "pending", "priority": "medium"}
        ]
        
        for task in tasks:
            self.db_manager.create_record("tasks", task)
    
    def test_advanced_search_simple_query(self):
        """Test advanced search with simple query."""
        query = {"role": "Admin"}
        result = self.db_manager.advanced_search("users", query)
        
        assert result["success"] is True
        assert result["count"] == 1
        assert result["data"][0]["name"] == "Alice Johnson"
    
    def test_advanced_search_comparison_query(self):
        """Test advanced search with comparison operators."""
        query = {"age": {"gt": 30}}
        result = self.db_manager.advanced_search("users", query)
        
        assert result["success"] is True
        assert result["count"] == 1
        assert result["data"][0]["name"] == "Carol Davis"
    
    def test_advanced_search_logical_and(self):
        """Test advanced search with AND logic."""
        query = {
            "$and": [
                {"status": "in_progress"},
                {"priority": "high"}
            ]
        }
        result = self.db_manager.advanced_search("tasks", query)
        
        assert result["success"] is True
        assert result["count"] == 1
        assert result["data"][0]["title"] == "High Priority Task"
    
    def test_advanced_search_logical_or(self):
        """Test advanced search with OR logic."""
        query = {
            "$or": [
                {"priority": "urgent"},
                {"priority": "high"}
            ]
        }
        result = self.db_manager.advanced_search("tasks", query)
        
        assert result["success"] is True
        assert result["count"] == 2
        priorities = [task["priority"] for task in result["data"]]
        assert "urgent" in priorities
        assert "high" in priorities
    
    def test_advanced_search_complex_query(self):
        """Test advanced search with complex nested query."""
        query = {
            "$and": [
                {"status": {"in": ["in_progress", "pending"]}},
                {
                    "$or": [
                        {"priority": "urgent"},
                        {"assigned_to": {"exists": True}}
                    ]
                }
            ]
        }
        result = self.db_manager.advanced_search("tasks", query)
        
        assert result["success"] is True
        assert result["count"] >= 3  # Should match multiple tasks
    
    def test_advanced_search_no_matches(self):
        """Test advanced search with no matching results."""
        query = {"role": "NonExistentRole"}
        result = self.db_manager.advanced_search("users", query)
        
        assert result["success"] is True
        assert result["count"] == 0
        assert result["data"] == []
    
    def test_advanced_search_invalid_syntax(self):
        """Test advanced search with invalid query syntax."""
        query = {"field": {"invalid_operator": "value"}}
        result = self.db_manager.advanced_search("users", query)
        
        assert result["success"] is False
        assert "Invalid query syntax" in result["error"]
    
    def test_get_query_capabilities(self):
        """Test getting query capabilities information."""
        capabilities = self.db_manager.get_query_capabilities()
        
        assert isinstance(capabilities, dict)
        assert "supported_operators" in capabilities
        assert "syntax_examples" in capabilities
        assert "field_operators" in capabilities
        
        # Check that examples are provided
        examples = capabilities["syntax_examples"]
        assert "simple_equality" in examples
        assert "logical_and" in examples
        assert "complex_example" in examples