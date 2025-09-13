#!/usr/bin/env python3
"""
Package creation script for the Custom MCP Server.
This script creates a complete, distributable package of the project.
"""

import os
import sys
import shutil
import zipfile
import json
from pathlib import Path
from datetime import datetime


def print_banner(title: str, width: int = 60) -> None:
    """Print a formatted banner."""
    print("\n" + "=" * width)
    print(f" {title.center(width - 2)} ")
    print("=" * width + "\n")


def print_step(step: str, status: str = "INFO") -> None:
    """Print a packaging step with status."""
    status_symbols = {
        "INFO": "ℹ",
        "SUCCESS": "✓",
        "WARNING": "⚠",
        "ERROR": "✗",
        "PROGRESS": "→"
    }
    symbol = status_symbols.get(status, "•")
    print(f"{symbol} {step}")


def create_package_info() -> dict:
    """Create package information."""
    return {
        "name": "custom-mcp-server",
        "version": "1.0.0",
        "description": "A custom Model Context Protocol server with NoSQL database integration",
        "created": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
        "components": {
            "server": "MCP server with CRUD operations",
            "client": "Demonstration client with interactive features",
            "database": "TinyDB NoSQL database with sample data",
            "tests": "Comprehensive test suite",
            "documentation": "Complete setup and API documentation"
        },
        "entry_points": {
            "server": "run_server.py",
            "client": "demo_client.py",
            "setup": "setup.py"
        }
    }


def get_files_to_package() -> list:
    """Get list of files to include in the package."""
    include_patterns = [
        # Source code
        "src/**/*.py",
        
        # Main entry points
        "run_server.py",
        "demo_client.py",
        "setup.py",
        "package.py",
        
        # Configuration files
        "requirements.txt",
        "pyproject.toml",
        "config.json",
        "pytest.ini",
        
        # Documentation
        "README.md",
        "API_DOCUMENTATION.md",
        "DEMO_CLIENT_README.md",
        
        # Tests
        "tests/**/*.py",
        
        # Startup scripts
        "start_server.bat",
        "start_client.bat",
        "start_server.sh",
        "start_client.sh",
        
        # Git and project files
        ".gitignore",
        
        # Data directory structure (but not actual data files)
        "data/.gitkeep"
    ]
    
    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.log",
        ".pytest_cache",
        "venv",
        "env",
        ".env",
        "data/*.json",  # Exclude actual database files
        "data/*.db",
        "logs",
        ".vscode",
        ".idea"
    ]
    
    files = []
    base_path = Path(".")
    
    # Add files based on include patterns
    for pattern in include_patterns:
        if "**" in pattern:
            # Recursive pattern
            parts = pattern.split("**")
            base_dir = parts[0].rstrip("/")
            file_pattern = parts[1].lstrip("/")
            
            if base_dir:
                search_path = base_path / base_dir
            else:
                search_path = base_path
            
            if search_path.exists():
                if file_pattern:
                    files.extend(search_path.rglob(file_pattern))
                else:
                    files.extend(search_path.rglob("*"))
        else:
            # Simple pattern
            matching_files = list(base_path.glob(pattern))
            files.extend(matching_files)
    
    # Filter out excluded patterns
    filtered_files = []
    for file_path in files:
        if file_path.is_file():
            relative_path = file_path.relative_to(base_path)
            should_exclude = False
            
            for exclude_pattern in exclude_patterns:
                if exclude_pattern in str(relative_path):
                    should_exclude = True
                    break
            
            if not should_exclude:
                filtered_files.append(relative_path)
    
    return sorted(set(filtered_files))


def create_package_directory(package_name: str) -> Path:
    """Create a temporary package directory."""
    package_dir = Path(f"dist/{package_name}")
    
    # Remove existing package directory
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    # Create new package directory
    package_dir.mkdir(parents=True, exist_ok=True)
    
    return package_dir


def copy_files_to_package(files: list, package_dir: Path) -> bool:
    """Copy files to the package directory."""
    try:
        for file_path in files:
            source = Path(file_path)
            destination = package_dir / file_path
            
            # Create parent directories
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source, destination)
            
        print_step(f"Copied {len(files)} files to package directory", "SUCCESS")
        return True
        
    except Exception as e:
        print_step(f"Failed to copy files: {e}", "ERROR")
        return False


def create_package_manifest(package_dir: Path, files: list, package_info: dict) -> bool:
    """Create a package manifest file."""
    try:
        manifest = {
            "package_info": package_info,
            "files": [str(f) for f in files],
            "file_count": len(files),
            "installation_instructions": [
                "1. Extract the package to your desired location",
                "2. Navigate to the extracted directory",
                "3. Run: python setup.py",
                "4. Follow the setup instructions",
                "5. Start the server: python run_server.py",
                "6. Run the demo: python demo_client.py"
            ],
            "requirements": [
                "Python 3.8 or higher",
                "pip package manager",
                "At least 100MB free disk space",
                "Internet connection for initial setup"
            ]
        }
        
        manifest_path = package_dir / "PACKAGE_MANIFEST.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print_step("Created package manifest", "SUCCESS")
        return True
        
    except Exception as e:
        print_step(f"Failed to create manifest: {e}", "ERROR")
        return False


def create_quick_start_guide(package_dir: Path) -> bool:
    """Create a quick start guide for the package."""
    try:
        quick_start = """# Custom MCP Server - Quick Start Guide

## What's Included

This package contains a complete Custom MCP Server implementation with:
- MCP server with CRUD operations
- Demonstration client with interactive features
- NoSQL database with sample data
- Comprehensive test suite
- Complete documentation

## Quick Setup (5 minutes)

1. **Extract the Package**
   - Extract all files to your desired location
   - Open a terminal/command prompt in the extracted directory

2. **Run Setup**
   ```bash
   python setup.py
   ```
   This will:
   - Create a virtual environment
   - Install all dependencies
   - Initialize the database
   - Create startup scripts

3. **Start the Server**
   ```bash
   python run_server.py
   ```
   Or use the startup scripts:
   - Windows: Double-click `start_server.bat`
   - Linux/Mac: Run `./start_server.sh`

4. **Run the Demo (in another terminal)**
   ```bash
   python demo_client.py
   ```
   Or use the startup scripts:
   - Windows: Double-click `start_client.bat`
   - Linux/Mac: Run `./start_client.sh`

## What the Demo Shows

The demonstration client will show you:
- **INSERT**: Creating new records in all collections
- **FETCH**: Retrieving and displaying all records
- **UPDATE**: Modifying existing records with before/after comparison
- **DELETE**: Removing records with confirmation

## Quick Test

For automated testing without interaction:
```bash
python demo_client.py --quick
```

## Documentation

- `README.md` - Complete setup and usage instructions
- `API_DOCUMENTATION.md` - Detailed API reference
- `DEMO_CLIENT_README.md` - Client demonstration guide

## Support

If you encounter any issues:
1. Check the README.md for troubleshooting
2. Verify Python 3.8+ is installed
3. Ensure all setup steps were completed
4. Check log files for error details

## Next Steps

After the demo works:
1. Explore the source code in the `src/` directory
2. Run the test suite: `pytest`
3. Modify the database schema or add new tools
4. Integrate with your own MCP clients

Enjoy exploring the Custom MCP Server!
"""
        
        quick_start_path = package_dir / "QUICK_START.md"
        with open(quick_start_path, 'w') as f:
            f.write(quick_start)
        
        print_step("Created quick start guide", "SUCCESS")
        return True
        
    except Exception as e:
        print_step(f"Failed to create quick start guide: {e}", "ERROR")
        return False


def create_zip_package(package_dir: Path, package_name: str) -> bool:
    """Create a ZIP file of the package."""
    try:
        zip_path = Path(f"dist/{package_name}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(package_dir.parent)
                    zipf.write(file_path, arcname)
        
        file_size = zip_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        
        print_step(f"Created ZIP package: {zip_path} ({size_mb:.1f} MB)", "SUCCESS")
        return True
        
    except Exception as e:
        print_step(f"Failed to create ZIP package: {e}", "ERROR")
        return False


def create_tar_package(package_dir: Path, package_name: str) -> bool:
    """Create a TAR.GZ file of the package."""
    try:
        import tarfile
        
        tar_path = Path(f"dist/{package_name}.tar.gz")
        
        with tarfile.open(tar_path, 'w:gz') as tarf:
            tarf.add(package_dir, arcname=package_name)
        
        file_size = tar_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        
        print_step(f"Created TAR.GZ package: {tar_path} ({size_mb:.1f} MB)", "SUCCESS")
        return True
        
    except Exception as e:
        print_step(f"Failed to create TAR.GZ package: {e}", "ERROR")
        return False


def main():
    """Main packaging function."""
    print_banner("Custom MCP Server Packaging")
    
    package_info = create_package_info()
    package_name = f"{package_info['name']}-v{package_info['version']}"
    
    print(f"Creating package: {package_name}")
    print(f"Python version: {package_info['python_version']}")
    print(f"Platform: {package_info['platform']}")
    
    # Get files to package
    print_step("Scanning files to package...", "PROGRESS")
    files = get_files_to_package()
    print_step(f"Found {len(files)} files to package", "SUCCESS")
    
    # Create package directory
    print_step("Creating package directory...", "PROGRESS")
    package_dir = create_package_directory(package_name)
    
    # Copy files
    print_step("Copying files to package...", "PROGRESS")
    if not copy_files_to_package(files, package_dir):
        sys.exit(1)
    
    # Create manifest
    print_step("Creating package manifest...", "PROGRESS")
    if not create_package_manifest(package_dir, files, package_info):
        sys.exit(1)
    
    # Create quick start guide
    print_step("Creating quick start guide...", "PROGRESS")
    if not create_quick_start_guide(package_dir):
        sys.exit(1)
    
    # Create ZIP package
    print_step("Creating ZIP package...", "PROGRESS")
    if not create_zip_package(package_dir, package_name):
        sys.exit(1)
    
    # Create TAR.GZ package (if not on Windows)
    if sys.platform != "win32":
        print_step("Creating TAR.GZ package...", "PROGRESS")
        if not create_tar_package(package_dir, package_name):
            print_step("TAR.GZ creation failed, but ZIP is available", "WARNING")
    
    print_banner("Packaging Complete!")
    print(f"Package created successfully: {package_name}")
    print(f"Location: dist/{package_name}.zip")
    if sys.platform != "win32":
        print(f"Also available: dist/{package_name}.tar.gz")
    
    print("\nPackage contents:")
    print(f"- {len(files)} source files")
    print("- Complete documentation")
    print("- Setup and startup scripts")
    print("- Test suite")
    print("- Quick start guide")
    
    print("\nTo distribute:")
    print("1. Share the ZIP file with users")
    print("2. Users should extract and run: python setup.py")
    print("3. Then follow the QUICK_START.md guide")


if __name__ == "__main__":
    main()