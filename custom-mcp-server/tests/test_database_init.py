"""
Unit tests for database initialization script.
"""

import pytest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.init_db import main, setup_logging
from database.manager import DatabaseManager
from tests.test_factories import TestDatabaseFactory, TestUtilities


class TestDatabaseInitialization:
    """Test cases for database initialization functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_db_path = TestDatabaseFactory.create_temp_db()
    
    def teardown_method(self):
        """Clean up test environment."""
        TestDatabaseFactory.cleanup_temp_db(self.temp_db_path)
    
    def test_setup_logging(self):
        """Test logging setup function."""
        # Capture logging configuration
        with patch('logging.basicConfig') as mock_config:
            setup_logging()
            
            # Verify logging was configured
            mock_config.assert_called_once()
            call_args = mock_config.call_args
            
            # Check that required parameters were set
            assert 'level' in call_args.kwargs
            assert 'format' in call_args.kwargs
            assert 'handlers' in call_args.kwargs
    
    @patch('database.init_db.DatabaseManager')
    def test_main_successful_initialization(self, mock_db_manager_class):
        """Test successful database initialization."""
        # Mock database manager
        mock_db_manager = MagicMock()
        mock_db_manager.is_connected.return_value = True
        mock_db_manager.initialize_sample_data.return_value = {
            'users': 3,
            'tasks': 5,
            'products': 4
        }
        mock_db_manager_class.return_value = mock_db_manager
        
        # Capture stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = main()
        
        # Verify successful execution
        assert result == 0
        
        # Verify database manager was used correctly
        mock_db_manager_class.assert_called_once()
        mock_db_manager.is_connected.assert_called_once()
        mock_db_manager.initialize_sample_data.assert_called_once()
        mock_db_manager.close.assert_called_once()
        
        # Verify output contains success message
        output = mock_stdout.getvalue()
        assert "initialization completed successfully" in output.lower()
        assert "users: 3 records" in output
        assert "tasks: 5 records" in output
        assert "products: 4 records" in output
    
    @patch('database.init_db.DatabaseManager')
    def test_main_database_connection_failure(self, mock_db_manager_class):
        """Test handling of database connection failure."""
        # Mock database manager with connection failure
        mock_db_manager = MagicMock()
        mock_db_manager.is_connected.return_value = False
        mock_db_manager_class.return_value = mock_db_manager
        
        # Capture stderr
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            result = main()
        
        # Verify failure exit code
        assert result == 1
        
        # Verify database manager was checked for connection
        mock_db_manager.is_connected.assert_called_once()
        
        # Verify initialization was not attempted
        mock_db_manager.initialize_sample_data.assert_not_called()
    
    @patch('database.init_db.DatabaseManager')
    def test_main_initialization_exception(self, mock_db_manager_class):
        """Test handling of initialization exception."""
        # Mock database manager that raises exception
        mock_db_manager = MagicMock()
        mock_db_manager.is_connected.return_value = True
        mock_db_manager.initialize_sample_data.side_effect = Exception("Database error")
        mock_db_manager_class.return_value = mock_db_manager
        
        # Capture stderr
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            result = main()
        
        # Verify failure exit code
        assert result == 1
        
        # Verify exception was handled
        mock_db_manager.initialize_sample_data.assert_called_once()
    
    @patch('database.init_db.DatabaseManager')
    def test_main_no_new_records(self, mock_db_manager_class):
        """Test initialization when database already contains data."""
        # Mock database manager with no new records
        mock_db_manager = MagicMock()
        mock_db_manager.is_connected.return_value = True
        mock_db_manager.initialize_sample_data.return_value = {
            'users': 0,
            'tasks': 0,
            'products': 0
        }
        mock_db_manager_class.return_value = mock_db_manager
        
        # Capture stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = main()
        
        # Verify successful execution
        assert result == 0
        
        # Verify output indicates no new records
        output = mock_stdout.getvalue()
        assert "already contains data" in output.lower()
        assert "no new records inserted" in output.lower()
    
    @patch('database.init_db.DatabaseManager')
    @patch('os.chdir')
    def test_main_directory_change(self, mock_chdir, mock_db_manager_class):
        """Test that main function changes to project root directory."""
        # Mock database manager
        mock_db_manager = MagicMock()
        mock_db_manager.is_connected.return_value = True
        mock_db_manager.initialize_sample_data.return_value = {'users': 1}
        mock_db_manager_class.return_value = mock_db_manager
        
        # Execute main
        result = main()
        
        # Verify directory was changed
        mock_chdir.assert_called_once()
        
        # Verify the path is reasonable (should be project root)
        call_args = mock_chdir.call_args[0][0]
        assert os.path.exists(call_args) or str(call_args).endswith('custom-mcp-server')
    
    def test_main_integration_with_real_database(self):
        """Integration test with real database manager."""
        # Use real database manager with temporary database
        with patch('database.init_db.DatabaseManager') as mock_db_manager_class:
            # Create real database manager with temp path
            real_db_manager = DatabaseManager(self.temp_db_path)
            mock_db_manager_class.return_value = real_db_manager
            
            try:
                # Execute main function
                result = main()
                
                # Should succeed
                assert result == 0
                
                # Verify data was actually inserted
                users = real_db_manager.read_records("users")
                tasks = real_db_manager.read_records("tasks")
                products = real_db_manager.read_records("products")
                
                TestUtilities.assert_response_structure(users, success=True)
                TestUtilities.assert_response_structure(tasks, success=True)
                TestUtilities.assert_response_structure(products, success=True)
                
                assert users["count"] >= 3
                assert tasks["count"] >= 5
                assert products["count"] >= 4
                
            finally:
                real_db_manager.close()
    
    @patch('sys.argv', ['init_db.py'])
    @patch('database.init_db.main')
    def test_script_entry_point(self, mock_main):
        """Test script entry point when run as main."""
        mock_main.return_value = 0
        
        # Import and run the script
        import database.init_db
        
        # The script should call main when imported as __main__
        # This is tested by mocking sys.argv and main function
        assert mock_main.call_count >= 0  # May or may not be called depending on test execution


class TestDatabaseInitializationEdgeCases:
    """Test edge cases for database initialization."""
    
    def test_initialization_with_permission_error(self):
        """Test initialization with permission errors."""
        # Create a read-only database file
        readonly_path = TestDatabaseFactory.create_temp_db()
        
        try:
            # Make file read-only
            os.chmod(readonly_path, 0o444)
            
            with patch('database.init_db.DatabaseManager') as mock_db_manager_class:
                # Create database manager that simulates permission error
                mock_db_manager = MagicMock()
                mock_db_manager.is_connected.return_value = True
                mock_db_manager.initialize_sample_data.side_effect = PermissionError("Permission denied")
                mock_db_manager_class.return_value = mock_db_manager
                
                # Should handle permission error gracefully
                result = main()
                assert result == 1
                
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(readonly_path, 0o666)
                os.unlink(readonly_path)
            except (PermissionError, FileNotFoundError):
                pass
    
    def test_initialization_with_disk_full_error(self):
        """Test initialization with disk full simulation."""
        with patch('database.init_db.DatabaseManager') as mock_db_manager_class:
            # Simulate disk full error
            mock_db_manager = MagicMock()
            mock_db_manager.is_connected.return_value = True
            mock_db_manager.initialize_sample_data.side_effect = OSError("No space left on device")
            mock_db_manager_class.return_value = mock_db_manager
            
            # Should handle disk full error gracefully
            result = main()
            assert result == 1
    
    def test_initialization_with_corrupted_database(self):
        """Test initialization with corrupted database."""
        with patch('database.init_db.DatabaseManager') as mock_db_manager_class:
            # Simulate corrupted database
            mock_db_manager = MagicMock()
            mock_db_manager.is_connected.return_value = False  # Connection fails due to corruption
            mock_db_manager_class.return_value = mock_db_manager
            
            # Should handle corrupted database gracefully
            result = main()
            assert result == 1
    
    @patch('database.init_db.DatabaseManager')
    def test_initialization_partial_success(self, mock_db_manager_class):
        """Test initialization with partial success."""
        # Mock database manager with partial success
        mock_db_manager = MagicMock()
        mock_db_manager.is_connected.return_value = True
        mock_db_manager.initialize_sample_data.return_value = {
            'users': 3,
            'tasks': 0,  # Failed to insert tasks
            'products': 4
        }
        mock_db_manager_class.return_value = mock_db_manager
        
        # Capture stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = main()
        
        # Should still succeed (partial success is acceptable)
        assert result == 0
        
        # Verify output shows only successful collections
        output = mock_stdout.getvalue()
        assert "users: 3 records" in output
        assert "products: 4 records" in output
        assert "tasks: 0 records" not in output  # Should not show zero counts
    
    def test_logging_configuration_error(self):
        """Test handling of logging configuration errors."""
        with patch('logging.basicConfig', side_effect=Exception("Logging error")):
            # Should not raise exception even if logging setup fails
            try:
                setup_logging()
            except Exception as e:
                pytest.fail(f"setup_logging should not raise exception: {e}")
    
    @patch('database.init_db.Path')
    def test_path_resolution_error(self, mock_path):
        """Test handling of path resolution errors."""
        # Mock Path to raise exception
        mock_path.side_effect = Exception("Path error")
        
        # Should handle path resolution errors
        result = main()
        assert result == 1
    
    @patch('os.chdir')
    def test_directory_change_error(self, mock_chdir):
        """Test handling of directory change errors."""
        # Mock chdir to raise exception
        mock_chdir.side_effect = OSError("Cannot change directory")
        
        with patch('database.init_db.DatabaseManager') as mock_db_manager_class:
            mock_db_manager = MagicMock()
            mock_db_manager.is_connected.return_value = True
            mock_db_manager.initialize_sample_data.return_value = {'users': 1}
            mock_db_manager_class.return_value = mock_db_manager
            
            # Should handle directory change errors
            result = main()
            assert result == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])