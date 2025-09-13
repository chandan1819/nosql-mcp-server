"""
Advanced query parser for complex filter expressions.
Supports logical operators (AND, OR, NOT) and comparison operators.
"""

import logging
from typing import Dict, List, Any, Union, Optional
from tinydb import Query


class QueryParser:
    """
    Advanced query parser that converts complex filter expressions into TinyDB queries.
    Supports logical operators (AND, OR, NOT) and comparison operators.
    """
    
    def __init__(self):
        """Initialize the query parser."""
        self.logger = logging.getLogger(__name__)
        self.query_obj = Query()
    
    def parse_query(self, query_dict: Dict[str, Any]) -> Optional[Any]:
        """
        Parse a complex query dictionary into a TinyDB query.
        
        Args:
            query_dict: Dictionary containing the query specification
            
        Returns:
            TinyDB Query object or None if query is empty
            
        Raises:
            ValueError: If query syntax is invalid
        """
        if not query_dict:
            return None
        
        try:
            return self._parse_expression(query_dict)
        except Exception as e:
            self.logger.error(f"Query parsing failed: {str(e)}")
            raise ValueError(f"Invalid query syntax: {str(e)}")
    
    def _parse_expression(self, expr: Dict[str, Any]) -> Any:
        """
        Parse a single expression which can be a logical operation or field condition.
        
        Args:
            expr: Expression dictionary
            
        Returns:
            TinyDB Query object
        """
        # Check for logical operators
        if '$and' in expr:
            return self._parse_and_operation(expr['$and'])
        elif '$or' in expr:
            return self._parse_or_operation(expr['$or'])
        elif '$not' in expr:
            return self._parse_not_operation(expr['$not'])
        else:
            # Parse as field conditions
            return self._parse_field_conditions(expr)
    
    def _parse_and_operation(self, conditions: List[Dict[str, Any]]) -> Any:
        """
        Parse AND logical operation.
        
        Args:
            conditions: List of condition dictionaries
            
        Returns:
            Combined Query with AND logic
        """
        if not conditions:
            raise ValueError("AND operation requires at least one condition")
        
        if len(conditions) == 1:
            return self._parse_expression(conditions[0])
        
        # Combine all conditions with AND
        result = self._parse_expression(conditions[0])
        for condition in conditions[1:]:
            result = result & self._parse_expression(condition)
        
        return result
    
    def _parse_or_operation(self, conditions: List[Dict[str, Any]]) -> Any:
        """
        Parse OR logical operation.
        
        Args:
            conditions: List of condition dictionaries
            
        Returns:
            Combined Query with OR logic
        """
        if not conditions:
            raise ValueError("OR operation requires at least one condition")
        
        if len(conditions) == 1:
            return self._parse_expression(conditions[0])
        
        # Combine all conditions with OR
        result = self._parse_expression(conditions[0])
        for condition in conditions[1:]:
            result = result | self._parse_expression(condition)
        
        return result
    
    def _parse_not_operation(self, condition: Dict[str, Any]) -> Any:
        """
        Parse NOT logical operation.
        
        Args:
            condition: Condition dictionary to negate
            
        Returns:
            Negated Query
        """
        if not condition:
            raise ValueError("NOT operation requires a condition")
        
        return ~self._parse_expression(condition)
    
    def _parse_field_conditions(self, conditions: Dict[str, Any]) -> Any:
        """
        Parse field-level conditions.
        
        Args:
            conditions: Dictionary of field conditions
            
        Returns:
            Combined Query for all field conditions
        """
        if not conditions:
            raise ValueError("Field conditions cannot be empty")
        
        query_conditions = []
        
        for field, value in conditions.items():
            if isinstance(value, dict):
                # Complex field condition with operators
                query_conditions.extend(self._parse_field_operators(field, value))
            else:
                # Simple equality condition
                query_conditions.append(self.query_obj[field] == value)
        
        # Combine all field conditions with AND
        if len(query_conditions) == 1:
            return query_conditions[0]
        
        result = query_conditions[0]
        for condition in query_conditions[1:]:
            result = result & condition
        
        return result
    
    def _parse_field_operators(self, field: str, operators: Dict[str, Any]) -> List[Any]:
        """
        Parse operators for a specific field.
        
        Args:
            field: Field name
            operators: Dictionary of operators and their values
            
        Returns:
            List of Query conditions for the field
        """
        conditions = []
        
        for operator, value in operators.items():
            condition = self._create_field_condition(field, operator, value)
            conditions.append(condition)
        
        return conditions
    
    def _create_field_condition(self, field: str, operator: str, value: Any) -> Any:
        """
        Create a single field condition based on operator and value.
        
        Args:
            field: Field name
            operator: Comparison operator
            value: Value to compare against
            
        Returns:
            Query condition
            
        Raises:
            ValueError: If operator is not supported
        """
        # Normalize operator names
        operator = operator.lower()
        
        # Equality operators
        if operator in ['eq', 'equals', '==']:
            return self.query_obj[field] == value
        elif operator in ['ne', 'not_equals', '!=']:
            return self.query_obj[field] != value
        
        # Comparison operators
        elif operator in ['gt', 'greater_than', '>']:
            return self.query_obj[field] > value
        elif operator in ['gte', 'greater_than_or_equal', '>=']:
            return self.query_obj[field] >= value
        elif operator in ['lt', 'less_than', '<']:
            return self.query_obj[field] < value
        elif operator in ['lte', 'less_than_or_equal', '<=']:
            return self.query_obj[field] <= value
        
        # String operators
        elif operator in ['contains', 'like']:
            return self.query_obj[field].search(str(value))
        elif operator in ['startswith', 'starts_with']:
            return self.query_obj[field].search(f'^{str(value)}')
        elif operator in ['endswith', 'ends_with']:
            return self.query_obj[field].search(f'{str(value)}$')
        
        # List operators
        elif operator == 'in':
            if not isinstance(value, list):
                raise ValueError(f"'in' operator requires a list value, got {type(value)}")
            if not value:
                raise ValueError("'in' operator requires a non-empty list")
            
            # Create OR condition for multiple values
            in_conditions = [self.query_obj[field] == v for v in value]
            if len(in_conditions) == 1:
                return in_conditions[0]
            
            result = in_conditions[0]
            for condition in in_conditions[1:]:
                result = result | condition
            return result
        
        elif operator == 'not_in':
            if not isinstance(value, list):
                raise ValueError(f"'not_in' operator requires a list value, got {type(value)}")
            if not value:
                raise ValueError("'not_in' operator requires a non-empty list")
            
            # Create AND condition for exclusion of all values
            not_in_conditions = [self.query_obj[field] != v for v in value]
            if len(not_in_conditions) == 1:
                return not_in_conditions[0]
            
            result = not_in_conditions[0]
            for condition in not_in_conditions[1:]:
                result = result & condition
            return result
        
        # Existence operators
        elif operator == 'exists':
            if value:
                return self.query_obj[field].exists()
            else:
                return ~self.query_obj[field].exists()
        
        # Range operators
        elif operator == 'between':
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                raise ValueError("'between' operator requires a list/tuple with exactly 2 values")
            min_val, max_val = value
            return (self.query_obj[field] >= min_val) & (self.query_obj[field] <= max_val)
        
        else:
            raise ValueError(f"Unsupported operator: {operator}")
    
    def validate_query_syntax(self, query_dict: Dict[str, Any]) -> bool:
        """
        Validate query syntax without executing it.
        
        Args:
            query_dict: Query dictionary to validate
            
        Returns:
            True if syntax is valid
            
        Raises:
            ValueError: If syntax is invalid
        """
        try:
            if query_dict:
                self.parse_query(query_dict)
            return True
        except Exception as e:
            raise ValueError(f"Invalid query syntax: {str(e)}")
    
    def get_supported_operators(self) -> Dict[str, List[str]]:
        """
        Get list of supported operators by category.
        
        Returns:
            Dictionary of operator categories and their supported operators
        """
        return {
            "equality": ["eq", "equals", "==", "ne", "not_equals", "!="],
            "comparison": ["gt", "greater_than", ">", "gte", "greater_than_or_equal", ">=",
                          "lt", "less_than", "<", "lte", "less_than_or_equal", "<="],
            "string": ["contains", "like", "startswith", "starts_with", "endswith", "ends_with"],
            "list": ["in", "not_in"],
            "existence": ["exists"],
            "range": ["between"],
            "logical": ["$and", "$or", "$not"]
        }


class QueryBuilder:
    """
    Helper class for building complex queries programmatically.
    """
    
    def __init__(self):
        """Initialize the query builder."""
        self.conditions = []
    
    def field(self, field_name: str) -> 'FieldBuilder':
        """
        Start building a condition for a specific field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            FieldBuilder instance for chaining
        """
        return FieldBuilder(self, field_name)
    
    def and_conditions(self, *conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine multiple conditions with AND logic.
        
        Args:
            conditions: Condition dictionaries to combine
            
        Returns:
            Combined query dictionary
        """
        if not conditions:
            return {}
        if len(conditions) == 1:
            return conditions[0]
        
        return {"$and": list(conditions)}
    
    def or_conditions(self, *conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine multiple conditions with OR logic.
        
        Args:
            conditions: Condition dictionaries to combine
            
        Returns:
            Combined query dictionary
        """
        if not conditions:
            return {}
        if len(conditions) == 1:
            return conditions[0]
        
        return {"$or": list(conditions)}
    
    def not_condition(self, condition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Negate a condition.
        
        Args:
            condition: Condition dictionary to negate
            
        Returns:
            Negated query dictionary
        """
        return {"$not": condition}


class FieldBuilder:
    """
    Helper class for building field-specific conditions.
    """
    
    def __init__(self, query_builder: QueryBuilder, field_name: str):
        """
        Initialize the field builder.
        
        Args:
            query_builder: Parent QueryBuilder instance
            field_name: Name of the field
        """
        self.query_builder = query_builder
        self.field_name = field_name
    
    def equals(self, value: Any) -> Dict[str, Any]:
        """Create equality condition."""
        return {self.field_name: {"eq": value}}
    
    def not_equals(self, value: Any) -> Dict[str, Any]:
        """Create not equals condition."""
        return {self.field_name: {"ne": value}}
    
    def greater_than(self, value: Any) -> Dict[str, Any]:
        """Create greater than condition."""
        return {self.field_name: {"gt": value}}
    
    def greater_than_or_equal(self, value: Any) -> Dict[str, Any]:
        """Create greater than or equal condition."""
        return {self.field_name: {"gte": value}}
    
    def less_than(self, value: Any) -> Dict[str, Any]:
        """Create less than condition."""
        return {self.field_name: {"lt": value}}
    
    def less_than_or_equal(self, value: Any) -> Dict[str, Any]:
        """Create less than or equal condition."""
        return {self.field_name: {"lte": value}}
    
    def contains(self, value: str) -> Dict[str, Any]:
        """Create contains condition."""
        return {self.field_name: {"contains": value}}
    
    def starts_with(self, value: str) -> Dict[str, Any]:
        """Create starts with condition."""
        return {self.field_name: {"startswith": value}}
    
    def ends_with(self, value: str) -> Dict[str, Any]:
        """Create ends with condition."""
        return {self.field_name: {"endswith": value}}
    
    def in_list(self, values: List[Any]) -> Dict[str, Any]:
        """Create in list condition."""
        return {self.field_name: {"in": values}}
    
    def not_in_list(self, values: List[Any]) -> Dict[str, Any]:
        """Create not in list condition."""
        return {self.field_name: {"not_in": values}}
    
    def exists(self, should_exist: bool = True) -> Dict[str, Any]:
        """Create exists condition."""
        return {self.field_name: {"exists": should_exist}}
    
    def between(self, min_val: Any, max_val: Any) -> Dict[str, Any]:
        """Create between condition."""
        return {self.field_name: {"between": [min_val, max_val]}}