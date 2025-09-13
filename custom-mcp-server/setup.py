#!/usr/bin/env python3
"""
Setup script for the Custom MCP Server.
This script helps with installation, configuration, and initial setup.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def print_banner(title: str, width: int = 60) -> None:
    """Print a formatted banner."""
    print("\n" + "=" * width)
    print(f" {title.center(width - 2)} ")
    print("=" * width + "\n")


def print_step(step: str, status: str = "INFO") -> None:
    """Print a setup step with status."""
    status_symbols = {
        "INFO": "ℹ",
        "SUCCESS": "✓",
        "WARNING": "⚠",
        "ERROR": "✗",
        "PROGRESS": "→"
    }
    symbol = status_symbols.get(status, "•")
    print(f"{symbol} {step}")


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_step(f"Python {version.major}.{version.minor} detected - requires Python 3.8+", "ERROR")
        return False
    
    print_step(f"Python {version.major}.{version.minor}.{version.micro} - compatible", "SUCCESS")
    return True


def create_virtual_environment() -> bool:
    """Create a virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print_step("Virtual environment already exists", "INFO")
        return True
    
    try:
        print_step("Creating virtual environment...", "PROGRESS")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print_step("Virtual environment created successfully", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print_step(f"Failed to create virtual environment: {e}", "ERROR")
        return False


def get_pip_command() -> str:
    """Get the appropriate pip command for the current platform."""
    if sys.platform == "win32":
        return os.path.join("venv", "Scripts", "pip")
    else:
        return os.path.join("venv", "bin", "pip")


def install_dependencies() -> bool:
    """Install required dependencies."""
    pip_cmd = get_pip_command()
    
    if not os.path.exists(pip_cmd):
        print_step("Virtual environment not found - please create it first", "ERROR")
        return False
    
    try:
        print_step("Installing dependencies...", "PROGRESS")
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print_step("Dependencies installed successfully", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print_step(f"Failed to install dependencies: {e}", "ERROR")
        return False


def setup_directories() -> bool:
    """Create necessary directories."""
    directories = ["data", "logs"]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print_step(f"Created directory: {directory}", "SUCCESS")
            except Exception as e:
                print_step(f"Failed to create directory {directory}: {e}", "ERROR")
                return False
        else:
            print_step(f"Directory already exists: {directory}", "INFO")
    
    return True


def initialize_database() -> bool:
    """Initialize the database with sample data."""
    try:
        print_step("Initializing database...", "PROGRESS")
        
        # Use the virtual environment's Python
        if sys.platform == "win32":
            python_cmd = os.path.join("venv", "Scripts", "python")
        else:
            python_cmd = os.path.join("venv", "bin", "python")
        
        subprocess.run([python_cmd, "src/database/init_db.py"], check=True)
        print_step("Database initialized successfully", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print_step(f"Failed to initialize database: {e}", "ERROR")
        return False


def create_config_file() -> bool:
    """Create a configuration file with default settings."""
    config_path = Path("config.json")
    
    if config_path.exists():
        print_step("Configuration file already exists", "INFO")
        return True
    
    config = {
        "database": {
            "path": "data/mcp_server.json",
            "auto_initialize": True
        },
        "server": {
            "log_level": "INFO",
            "max_connections": 10
        },
        "client": {
            "retry_attempts": 3,
            "retry_delay": 2.0
        }
    }
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print_step("Configuration file created", "SUCCESS")
        return True
    except Exception as e:
        print_step(f"Failed to create configuration file: {e}", "ERROR")
        return False


def create_startup_scripts() -> bool:
    """Create convenient startup scripts."""
    scripts = []
    
    if sys.platform == "win32":
        # Windows batch files
        server_script = """@echo off
echo Starting Custom MCP Server...
venv\\Scripts\\python run_server.py
pause
"""
        client_script = """@echo off
echo Starting MCP Client Demonstration...
venv\\Scripts\\python demo_client.py
pause
"""
        scripts = [
            ("start_server.bat", server_script),
            ("start_client.bat", client_script)
        ]
    else:
        # Unix shell scripts
        server_script = """#!/bin/bash
echo "Starting Custom MCP Server..."
venv/bin/python run_server.py
"""
        client_script = """#!/bin/bash
echo "Starting MCP Client Demonstration..."
venv/bin/python demo_client.py
"""
        scripts = [
            ("start_server.sh", server_script),
            ("start_client.sh", client_script)
        ]
    
    for script_name, script_content in scripts:
        script_path = Path(script_name)
        try:
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make executable on Unix systems
            if not sys.platform == "win32":
                os.chmod(script_path, 0o755)
            
            print_step(f"Created startup script: {script_name}", "SUCCESS")
        except Exception as e:
            print_step(f"Failed to create script {script_name}: {e}", "ERROR")
            return False
    
    return True


def verify_installation() -> bool:
    """Verify that the installation is working correctly."""
    print_step("Verifying installation...", "PROGRESS")
    
    # Check if key files exist
    key_files = [
        "src/mcp_server.py",
        "src/mcp_client.py",
        "src/database/manager.py",
        "data/mcp_server.json",
        "requirements.txt"
    ]
    
    for file_path in key_files:
        if not Path(file_path).exists():
            print_step(f"Missing required file: {file_path}", "ERROR")
            return False
    
    print_step("All required files present", "SUCCESS")
    
    # Test import of main modules
    try:
        if sys.platform == "win32":
            python_cmd = os.path.join("venv", "Scripts", "python")
        else:
            python_cmd = os.path.join("venv", "bin", "python")
        
        test_script = """
import sys
import os
sys.path.insert(0, 'src')
try:
    from mcp_server import MCPServer
    from mcp_client import MCPClient
    from database.manager import DatabaseManager
    print("✓ All modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
"""
        
        result = subprocess.run([python_cmd, "-c", test_script], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_step("Module imports successful", "SUCCESS")
            return True
        else:
            print_step(f"Module import failed: {result.stderr}", "ERROR")
            return False
            
    except Exception as e:
        print_step(f"Verification failed: {e}", "ERROR")
        return False


def print_next_steps():
    """Print instructions for next steps."""
    print_banner("Setup Complete!")
    
    print("Your Custom MCP Server is now ready to use!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
        print("\n2. Start the server:")
        print("   python run_server.py")
        print("   OR double-click: start_server.bat")
        print("\n3. In another terminal, run the demo client:")
        print("   python demo_client.py")
        print("   OR double-click: start_client.bat")
    else:
        print("   source venv/bin/activate")
        print("\n2. Start the server:")
        print("   python run_server.py")
        print("   OR run: ./start_server.sh")
        print("\n3. In another terminal, run the demo client:")
        print("   python demo_client.py")
        print("   OR run: ./start_client.sh")
    
    print("\nFor quick testing without interaction:")
    print("   python demo_client.py --quick")
    
    print("\nFor help and documentation:")
    print("   See README.md for detailed instructions")
    print("   See API_DOCUMENTATION.md for API details")


def main():
    """Main setup function."""
    print_banner("Custom MCP Server Setup")
    
    print("This script will set up the Custom MCP Server environment.")
    print("It will create a virtual environment, install dependencies,")
    print("initialize the database, and create startup scripts.")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Setting up directories", setup_directories),
        ("Creating configuration file", create_config_file),
        ("Initializing database", initialize_database),
        ("Creating startup scripts", create_startup_scripts),
        ("Verifying installation", verify_installation)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print_step(f"Setup failed at step: {step_name}", "ERROR")
            sys.exit(1)
    
    print_next_steps()


if __name__ == "__main__":
    main()