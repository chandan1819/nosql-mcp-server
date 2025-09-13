"""
Comprehensive test runner for the MCP server project.
Provides utilities for running all tests and generating reports.
"""

import pytest
import sys
import os
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import json


class TestRunner:
    """Test runner with comprehensive reporting and utilities."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize test runner."""
        if project_root is None:
            project_root = Path(__file__).parent.parent
        self.project_root = Path(project_root)
        self.tests_dir = self.project_root / "tests"
        self.src_dir = self.project_root / "src"
        
    def discover_test_files(self) -> List[Path]:
        """Discover all test files in the tests directory."""
        test_files = []
        for test_file in self.tests_dir.glob("test_*.py"):
            if test_file.is_file():
                test_files.append(test_file)
        return sorted(test_files)
    
    def run_unit_tests(self, verbose: bool = True, coverage: bool = True) -> Dict[str, Any]:
        """Run all unit tests with optional coverage reporting."""
        print("🧪 Running Unit Tests...")
        print("=" * 50)
        
        # Prepare pytest arguments
        pytest_args = [
            str(self.tests_dir),
            "-v" if verbose else "-q",
            "--tb=short",
            "--strict-markers",
            "--disable-warnings"
        ]
        
        if coverage:
            pytest_args.extend([
                "--cov=" + str(self.src_dir),
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-fail-under=80"
            ])
        
        # Run tests
        start_time = time.time()
        exit_code = pytest.main(pytest_args)
        end_time = time.time()
        
        # Collect results
        result = {
            "exit_code": exit_code,
            "duration": end_time - start_time,
            "success": exit_code == 0,
            "coverage_enabled": coverage
        }
        
        print(f"\n⏱️  Tests completed in {result['duration']:.2f} seconds")
        print(f"✅ Result: {'PASSED' if result['success'] else 'FAILED'}")
        
        return result
    
    def run_specific_test_file(self, test_file: str, verbose: bool = True) -> Dict[str, Any]:
        """Run a specific test file."""
        test_path = self.tests_dir / test_file
        if not test_path.exists():
            raise FileNotFoundError(f"Test file not found: {test_path}")
        
        print(f"🧪 Running {test_file}...")
        print("=" * 50)
        
        pytest_args = [
            str(test_path),
            "-v" if verbose else "-q",
            "--tb=short"
        ]
        
        start_time = time.time()
        exit_code = pytest.main(pytest_args)
        end_time = time.time()
        
        result = {
            "test_file": test_file,
            "exit_code": exit_code,
            "duration": end_time - start_time,
            "success": exit_code == 0
        }
        
        print(f"\n⏱️  {test_file} completed in {result['duration']:.2f} seconds")
        print(f"✅ Result: {'PASSED' if result['success'] else 'FAILED'}")
        
        return result
    
    def run_test_category(self, category: str, verbose: bool = True) -> Dict[str, Any]:
        """Run tests for a specific category (e.g., 'database', 'mcp', 'error')."""
        print(f"🧪 Running {category.title()} Tests...")
        print("=" * 50)
        
        # Find test files matching the category
        pattern = f"test_{category}*.py"
        test_files = list(self.tests_dir.glob(pattern))
        
        if not test_files:
            print(f"❌ No test files found matching pattern: {pattern}")
            return {"success": False, "error": "No matching test files"}
        
        pytest_args = [str(f) for f in test_files]
        pytest_args.extend([
            "-v" if verbose else "-q",
            "--tb=short"
        ])
        
        start_time = time.time()
        exit_code = pytest.main(pytest_args)
        end_time = time.time()
        
        result = {
            "category": category,
            "test_files": [f.name for f in test_files],
            "exit_code": exit_code,
            "duration": end_time - start_time,
            "success": exit_code == 0
        }
        
        print(f"\n⏱️  {category.title()} tests completed in {result['duration']:.2f} seconds")
        print(f"✅ Result: {'PASSED' if result['success'] else 'FAILED'}")
        
        return result
    
    def run_smoke_tests(self) -> Dict[str, Any]:
        """Run a quick smoke test to verify basic functionality."""
        print("🚀 Running Smoke Tests...")
        print("=" * 50)
        
        # Run only fast, essential tests
        pytest_args = [
            str(self.tests_dir),
            "-m", "not slow",  # Exclude slow tests
            "-x",  # Stop on first failure
            "--tb=line",
            "-q"
        ]
        
        start_time = time.time()
        exit_code = pytest.main(pytest_args)
        end_time = time.time()
        
        result = {
            "type": "smoke",
            "exit_code": exit_code,
            "duration": end_time - start_time,
            "success": exit_code == 0
        }
        
        print(f"\n⏱️  Smoke tests completed in {result['duration']:.2f} seconds")
        print(f"✅ Result: {'PASSED' if result['success'] else 'FAILED'}")
        
        return result
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate a comprehensive test report."""
        print("📊 Generating Test Report...")
        print("=" * 50)
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project_root": str(self.project_root),
            "test_files": [],
            "summary": {}
        }
        
        # Discover test files
        test_files = self.discover_test_files()
        report["test_files"] = [
            {
                "name": f.name,
                "path": str(f.relative_to(self.project_root)),
                "size": f.stat().st_size,
                "modified": time.ctime(f.stat().st_mtime)
            }
            for f in test_files
        ]
        
        # Count test functions
        total_test_functions = 0
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Count functions that start with 'test_'
                    test_functions = content.count('def test_')
                    total_test_functions += test_functions
                    
                    # Add to file info
                    for file_info in report["test_files"]:
                        if file_info["name"] == test_file.name:
                            file_info["test_functions"] = test_functions
                            break
            except Exception as e:
                print(f"Warning: Could not analyze {test_file}: {e}")
        
        report["summary"] = {
            "total_test_files": len(test_files),
            "total_test_functions": total_test_functions,
            "test_categories": self._identify_test_categories(test_files)
        }
        
        # Save report to file
        report_file = self.project_root / "test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Test report saved to: {report_file}")
        print(f"📈 Summary:")
        print(f"   - Test files: {report['summary']['total_test_files']}")
        print(f"   - Test functions: {report['summary']['total_test_functions']}")
        print(f"   - Categories: {', '.join(report['summary']['test_categories'])}")
        
        return report
    
    def _identify_test_categories(self, test_files: List[Path]) -> List[str]:
        """Identify test categories based on file names."""
        categories = set()
        for test_file in test_files:
            name = test_file.stem  # Remove .py extension
            if name.startswith("test_"):
                category = name[5:]  # Remove "test_" prefix
                categories.add(category)
        return sorted(list(categories))
    
    def check_test_dependencies(self) -> Dict[str, Any]:
        """Check if all test dependencies are available."""
        print("🔍 Checking Test Dependencies...")
        print("=" * 50)
        
        required_packages = [
            "pytest",
            "pytest-asyncio",
            "tinydb",
            "mcp"
        ]
        
        missing_packages = []
        available_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                available_packages.append(package)
                print(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package}")
        
        result = {
            "available": available_packages,
            "missing": missing_packages,
            "all_available": len(missing_packages) == 0
        }
        
        if missing_packages:
            print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
            print("Install with: pip install " + " ".join(missing_packages))
        else:
            print("\n✅ All test dependencies are available!")
        
        return result
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance-focused tests."""
        print("⚡ Running Performance Tests...")
        print("=" * 50)
        
        pytest_args = [
            str(self.tests_dir),
            "-m", "performance",  # Only performance tests
            "--tb=short",
            "-v"
        ]
        
        start_time = time.time()
        exit_code = pytest.main(pytest_args)
        end_time = time.time()
        
        result = {
            "type": "performance",
            "exit_code": exit_code,
            "duration": end_time - start_time,
            "success": exit_code == 0
        }
        
        print(f"\n⏱️  Performance tests completed in {result['duration']:.2f} seconds")
        print(f"✅ Result: {'PASSED' if result['success'] else 'FAILED'}")
        
        return result


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Server Test Runner")
    parser.add_argument("--category", help="Run tests for specific category")
    parser.add_argument("--file", help="Run specific test file")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    parser.add_argument("--check-deps", action="store_true", help="Check test dependencies")
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")
    parser.add_argument("--quiet", action="store_true", help="Quiet output")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Check dependencies first if requested
    if args.check_deps:
        deps_result = runner.check_test_dependencies()
        if not deps_result["all_available"]:
            print("\n❌ Cannot run tests due to missing dependencies")
            return 1
    
    # Generate report if requested
    if args.report:
        runner.generate_test_report()
        return 0
    
    # Run specific test category
    if args.category:
        result = runner.run_test_category(args.category, verbose=not args.quiet)
        return 0 if result["success"] else 1
    
    # Run specific test file
    if args.file:
        result = runner.run_specific_test_file(args.file, verbose=not args.quiet)
        return 0 if result["success"] else 1
    
    # Run smoke tests
    if args.smoke:
        result = runner.run_smoke_tests()
        return 0 if result["success"] else 1
    
    # Run performance tests
    if args.performance:
        result = runner.run_performance_tests()
        return 0 if result["success"] else 1
    
    # Run all unit tests (default)
    result = runner.run_unit_tests(
        verbose=not args.quiet,
        coverage=not args.no_coverage
    )
    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)