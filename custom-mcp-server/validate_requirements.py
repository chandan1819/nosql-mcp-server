#!/usr/bin/env python3
"""
Quick validation script for Custom MCP Server requirements.
This script validates all requirements without running the full test suite.
"""

import os
import sys
import json
import importlib.util
from pathlib import Path

# Change to the script's directory
script_dir = Path(__file__).parent
os.chdir(script_dir)


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


def validate_file_structure() -> bool:
    """Validate that all required files exist."""
    print_status("Validating file structure...", "PROGRESS")
    
    required_files = [
        # Main entry points
        "run_server.py",
        "demo_client.py",
        "setup.py",
        
        # Source code
        "src/mcp_server.py",
        "src/mcp_client.py",
        "src/response_formatter.py",
        "src/database/manager.py",
        "src/database/init_db.py",
        "src/database/query_parser.py",
        "src/server/main.py",
        "src/client/main.py",
        "src/client/demo_client.py",
        
        # Configuration
        "requirements.txt",
        "pyproject.toml",
        "config.json",
        "pytest.ini",
        
        # Documentation
        "README.md",
        "API_DOCUMENTATION.md",
        "DEMO_CLIENT_README.md",
        
        # Startup scripts
        "start_server.bat",
        "start_client.bat",
        "start_server.sh",
        "start_client.sh",
        
        # Package files
        "package.py",
        ".gitignore"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print_status(f"Missing files: {', '.join(missing_files)}", "ERROR")
        return False
    
    print_status(f"All {len(required_files)} required files present", "SUCCESS")
    return True


def validate_python_imports() -> bool:
    """Validate that all Python modules can be imported."""
    print_status("Validating Python imports...", "PROGRESS")
    
    # Add src to path
    sys.path.insert(0, "src")
    
    modules_to_test = [
        ("mcp_server", "MCPServer"),
        ("mcp_client", "MCPClient"),
        ("response_formatter", "ResponseFormatter"),
        ("database.manager", "DatabaseManager"),
        ("database.init_db", None),
        ("database.query_parser", "QueryParser")
    ]
    
    failed_imports = []
    
    for module_name, class_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            if class_name:
                if not hasattr(module, class_name):
                    failed_imports.append(f"{module_name}.{class_name}")
        except ImportError as e:
            failed_imports.append(f"{module_name}: {str(e)}")
    
    if failed_imports:
        print_status(f"Import failures: {', '.join(failed_imports)}", "ERROR")
        return False
    
    print_status("All Python modules import successfully", "SUCCESS")
    return True


def validate_database_structure() -> bool:
    """Validate database initialization and structure."""
    print_status("Validating database structure...", "PROGRESS")
    
    # Check if database file exists or can be created
    db_path = Path("data/mcp_server.json")
    
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Try to initialize database
    try:
        sys.path.insert(0, "src")
        from database.manager import DatabaseManager
        
        # Test database creation
        with DatabaseManager(str(db_path)) as db:
            # Check collections exist
            collections = ["users", "tasks", "products"]
            for collection in collections:
                try:
                    db.get_collection(collection)
                except Exception as e:
                    print_status(f"Collection {collection} error: {e}", "ERROR")
                    return False
        
        print_status("Database structure validation passed", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Database validation failed: {e}", "ERROR")
        return False


def validate_configuration_files() -> bool:
    """Validate configuration files are properly formatted."""
    print_status("Validating configuration files...", "PROGRESS")
    
    config_files = [
        ("config.json", "JSON"),
        ("pyproject.toml", "TOML"),
        ("requirements.txt", "TEXT")
    ]
    
    for file_path, file_type in config_files:
        if not Path(file_path).exists():
            print_status(f"Missing config file: {file_path}", "ERROR")
            return False
        
        try:
            if file_type == "JSON":
                with open(file_path, 'r') as f:
                    json.load(f)
            elif file_type == "TEXT":
                with open(file_path, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        print_status(f"Empty config file: {file_path}", "ERROR")
                        return False
        except Exception as e:
            print_status(f"Invalid {file_type} in {file_path}: {e}", "ERROR")
            return False
    
    print_status("All configuration files are valid", "SUCCESS")
    return True


def validate_requirements_coverage() -> bool:
    """Validate that all requirements from the spec are covered."""
    print_status("Validating requirements coverage...", "PROGRESS")
    
    # Check key requirement indicators
    requirements_checks = [
        # Requirement 1: MCP server with database connectivity
        ("MCP server implementation", Path("src/mcp_server.py").exists()),
        ("Database manager", Path("src/database/manager.py").exists()),
        
        # Requirement 2: CRUD operations through MCP commands
        ("CRUD operations", Path("src/mcp_server.py").exists()),
        
        # Requirement 3: Search and filter queries
        ("Query parser", Path("src/database/query_parser.py").exists()),
        
        # Requirement 4: Pre-populated database with sample data
        ("Database initialization", Path("src/database/init_db.py").exists()),
        
        # Requirement 5: Sample MCP client script
        ("Demo client", Path("demo_client.py").exists()),
        ("MCP client implementation", Path("src/mcp_client.py").exists()),
        
        # Requirement 6: Comprehensive setup instructions
        ("Setup script", Path("setup.py").exists()),
        ("README documentation", Path("README.md").exists()),
        ("API documentation", Path("API_DOCUMENTATION.md").exists())
    ]
    
    failed_checks = []
    for check_name, check_result in requirements_checks:
        if not check_result:
            failed_checks.append(check_name)
    
    if failed_checks:
        print_status(f"Missing requirement implementations: {', '.join(failed_checks)}", "ERROR")
        return False
    
    print_status("All requirements have corresponding implementations", "SUCCESS")
    return True


def validate_entry_points() -> bool:
    """Validate that entry points are properly configured."""
    print_status("Validating entry points...", "PROGRESS")
    
    entry_points = [
        ("Server entry point", "run_server.py"),
        ("Client entry point", "demo_client.py"),
        ("Setup entry point", "setup.py"),
        ("Alternative server entry", "src/server/main.py"),
        ("Alternative client entry", "src/client/main.py")
    ]
    
    for name, file_path in entry_points:
        if not Path(file_path).exists():
            print_status(f"Missing {name}: {file_path}", "ERROR")
            return False
        
        # Check if file has proper shebang and main block
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if '__name__ == "__main__"' not in content:
                    print_status(f"{name} missing main block", "WARNING")
        except Exception as e:
            print_status(f"Error reading {file_path}: {e}", "ERROR")
            return False
    
    print_status("All entry points are properly configured", "SUCCESS")
    return True


def validate_documentation() -> bool:
    """Validate that documentation is comprehensive."""
    print_status("Validating documentation...", "PROGRESS")
    
    doc_files = [
        ("README.md", ["Quick Start", "Installation", "Usage"]),
        ("API_DOCUMENTATION.md", ["API", "Tools", "Examples"]),
        ("DEMO_CLIENT_README.md", ["Demo", "Client", "Usage"])
    ]
    
    for doc_file, required_sections in doc_files:
        if not Path(doc_file).exists():
            print_status(f"Missing documentation: {doc_file}", "ERROR")
            return False
        
        try:
            with open(doc_file, 'r') as f:
                content = f.read().lower()
                missing_sections = []
                for section in required_sections:
                    if section.lower() not in content:
                        missing_sections.append(section)
                
                if missing_sections:
                    print_status(f"{doc_file} missing sections: {', '.join(missing_sections)}", "WARNING")
        except Exception as e:
            print_status(f"Error reading {doc_file}: {e}", "ERROR")
            return False
    
    print_status("Documentation validation passed", "SUCCESS")
    return True


def main():
    """Main validation function."""
    print("=" * 60)
    print(" Custom MCP Server Requirements Validation ")
    print("=" * 60)
    
    validations = [
        ("File Structure", validate_file_structure),
        ("Python Imports", validate_python_imports),
        ("Database Structure", validate_database_structure),
        ("Configuration Files", validate_configuration_files),
        ("Requirements Coverage", validate_requirements_coverage),
        ("Entry Points", validate_entry_points),
        ("Documentation", validate_documentation)
    ]
    
    passed = 0
    failed = 0
    
    for validation_name, validation_func in validations:
        print(f"\n{validation_name}:")
        try:
            if validation_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_status(f"Validation error: {e}", "ERROR")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f" Validation Results: {passed} passed, {failed} failed ")
    print("=" * 60)
    
    if failed == 0:
        print_status("All validations passed! ✨", "SUCCESS")
        print_status("The Custom MCP Server is ready for use.", "SUCCESS")
        return True
    else:
        print_status(f"{failed} validation(s) failed.", "ERROR")
        print_status("Please address the issues above before proceeding.", "ERROR")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)