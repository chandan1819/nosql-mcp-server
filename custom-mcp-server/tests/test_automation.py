"""
Test automation scripts and utilities for continuous integration.
Provides automated test execution, reporting, and validation.
"""

import pytest
import sys
import os
import subprocess
import json
import time
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tests.test_factories import TestDatabaseFactory


class TestAutomation:
    """Automated test execution and reporting."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize test automation."""
        if project_root is None:
            project_root = Path(__file__).parent.parent
        
        self.project_root = Path(project_root)
        self.tests_dir = self.project_root / "tests"
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger("test_automation")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def run_test_suite(self, test_type: str = "all") -> Dict[str, Any]:
        """Run automated test suite with specified type."""
        self.logger.info(f"Starting automated test suite: {test_type}")
        
        start_time = time.time()
        
        # Prepare test environment
        self._prepare_test_environment()
        
        # Run tests based on type
        if test_type == "unit":
            result = self._run_unit_tests()
        elif test_type == "integration":
            result = self._run_integration_tests()
        elif test_type == "performance":
            result = self._run_performance_tests()
        elif test_type == "all":
            result = self._run_all_tests()
        else:
            raise ValueError(f"Unknown test type: {test_type}")
        
        # Generate reports
        report_path = self._generate_test_report(result, test_type)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        result.update({
            "total_duration": total_duration,
            "report_path": str(report_path),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        self.logger.info(f"Test suite completed in {total_duration:.2f}s")
        self.logger.info(f"Report saved to: {report_path}")
        
        return result
    
    def _prepare_test_environment(self):
        """Prepare the test environment."""
        self.logger.info("Preparing test environment...")
        
        # Clean up any existing test databases
        temp_dir = Path(tempfile.gettempdir())
        for temp_file in temp_dir.glob("tmp*.json"):
            try:
                temp_file.unlink()
            except (PermissionError, FileNotFoundError):
                pass
        
        # Ensure test directories exist
        self.reports_dir.mkdir(exist_ok=True)
        
        # Clean up old reports (keep last 10)
        report_files = sorted(self.reports_dir.glob("test_report_*.json"))
        if len(report_files) > 10:
            for old_report in report_files[:-10]:
                try:
                    old_report.unlink()
                except (PermissionError, FileNotFoundError):
                    pass
    
    def _run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests."""
        self.logger.info("Running unit tests...")
        
        pytest_args = [
            str(self.tests_dir),
            "-v",
            "--tb=short",
            "-m", "not performance and not slow",
            "--junit-xml=" + str(self.reports_dir / "unit_tests.xml"),
            "--cov=" + str(self.project_root / "src"),
            "--cov-report=html:" + str(self.reports_dir / "coverage_html"),
            "--cov-report=json:" + str(self.reports_dir / "coverage.json")
        ]
        
        exit_code = pytest.main(pytest_args)
        
        # Parse coverage results
        coverage_data = self._parse_coverage_report()
        
        return {
            "test_type": "unit",
            "exit_code": exit_code,
            "success": exit_code == 0,
            "coverage": coverage_data
        }
    
    def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        self.logger.info("Running integration tests...")
        
        pytest_args = [
            str(self.tests_dir / "test_integration.py"),
            "-v",
            "--tb=short",
            "--junit-xml=" + str(self.reports_dir / "integration_tests.xml")
        ]
        
        exit_code = pytest.main(pytest_args)
        
        return {
            "test_type": "integration",
            "exit_code": exit_code,
            "success": exit_code == 0
        }
    
    def _run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests."""
        self.logger.info("Running performance tests...")
        
        pytest_args = [
            str(self.tests_dir / "test_performance.py"),
            "-v",
            "-s",  # Don't capture output for performance metrics
            "--tb=short",
            "-m", "performance",
            "--junit-xml=" + str(self.reports_dir / "performance_tests.xml")
        ]
        
        exit_code = pytest.main(pytest_args)
        
        return {
            "test_type": "performance",
            "exit_code": exit_code,
            "success": exit_code == 0
        }
    
    def _run_all_tests(self) -> Dict[str, Any]:
        """Run all test types."""
        self.logger.info("Running all tests...")
        
        results = {}
        
        # Run unit tests
        unit_result = self._run_unit_tests()
        results["unit"] = unit_result
        
        # Run integration tests
        integration_result = self._run_integration_tests()
        results["integration"] = integration_result
        
        # Run performance tests
        performance_result = self._run_performance_tests()
        results["performance"] = performance_result
        
        # Overall success
        overall_success = all(result["success"] for result in results.values())
        
        return {
            "test_type": "all",
            "results": results,
            "success": overall_success,
            "exit_code": 0 if overall_success else 1
        }
    
    def _parse_coverage_report(self) -> Dict[str, Any]:
        """Parse coverage report if available."""
        coverage_file = self.reports_dir / "coverage.json"
        
        if not coverage_file.exists():
            return {"available": False}
        
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            
            return {
                "available": True,
                "total_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                "files_covered": len(coverage_data.get("files", {})),
                "missing_lines": coverage_data.get("totals", {}).get("missing_lines", 0),
                "covered_lines": coverage_data.get("totals", {}).get("covered_lines", 0)
            }
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.warning(f"Failed to parse coverage report: {e}")
            return {"available": False, "error": str(e)}
    
    def _generate_test_report(self, result: Dict[str, Any], test_type: str) -> Path:
        """Generate comprehensive test report."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"test_report_{test_type}_{timestamp}.json"
        
        # Add system information
        result["system_info"] = {
            "python_version": sys.version,
            "platform": sys.platform,
            "project_root": str(self.project_root),
            "test_files_count": len(list(self.tests_dir.glob("test_*.py")))
        }
        
        # Add test file information
        result["test_files"] = []
        for test_file in self.tests_dir.glob("test_*.py"):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    test_functions = content.count('def test_')
                    test_classes = content.count('class Test')
                
                result["test_files"].append({
                    "name": test_file.name,
                    "path": str(test_file.relative_to(self.project_root)),
                    "size": test_file.stat().st_size,
                    "test_functions": test_functions,
                    "test_classes": test_classes,
                    "modified": time.ctime(test_file.stat().st_mtime)
                })
            except Exception as e:
                self.logger.warning(f"Failed to analyze {test_file}: {e}")
        
        # Save report
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        
        return report_file
    
    def validate_test_environment(self) -> Dict[str, Any]:
        """Validate that the test environment is properly set up."""
        self.logger.info("Validating test environment...")
        
        validation_results = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Check Python version
        if sys.version_info < (3, 8):
            validation_results["issues"].append(f"Python version too old: {sys.version}")
            validation_results["valid"] = False
        
        # Check required packages
        required_packages = ["pytest", "pytest-asyncio", "tinydb", "mcp"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            validation_results["issues"].append(f"Missing packages: {', '.join(missing_packages)}")
            validation_results["valid"] = False
        
        # Check test files
        test_files = list(self.tests_dir.glob("test_*.py"))
        if len(test_files) < 5:
            validation_results["warnings"].append(f"Only {len(test_files)} test files found")
        
        # Check source files
        src_dir = self.project_root / "src"
        if not src_dir.exists():
            validation_results["issues"].append("Source directory not found")
            validation_results["valid"] = False
        
        # Check write permissions
        try:
            test_file = self.reports_dir / "test_write_permission.tmp"
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            validation_results["issues"].append(f"Cannot write to reports directory: {e}")
            validation_results["valid"] = False
        
        # Check database creation
        try:
            temp_db = TestDatabaseFactory.create_temp_db()
            TestDatabaseFactory.cleanup_temp_db(temp_db)
        except Exception as e:
            validation_results["issues"].append(f"Cannot create test database: {e}")
            validation_results["valid"] = False
        
        self.logger.info(f"Environment validation: {'PASSED' if validation_results['valid'] else 'FAILED'}")
        
        return validation_results
    
    def cleanup_test_artifacts(self):
        """Clean up test artifacts and temporary files."""
        self.logger.info("Cleaning up test artifacts...")
        
        cleanup_count = 0
        
        # Clean up temporary databases
        temp_dir = Path(tempfile.gettempdir())
        for temp_file in temp_dir.glob("tmp*.json"):
            try:
                temp_file.unlink()
                cleanup_count += 1
            except (PermissionError, FileNotFoundError):
                pass
        
        # Clean up pytest cache
        pytest_cache = self.project_root / ".pytest_cache"
        if pytest_cache.exists():
            try:
                shutil.rmtree(pytest_cache)
                cleanup_count += 1
            except (PermissionError, FileNotFoundError):
                pass
        
        # Clean up __pycache__ directories
        for pycache_dir in self.project_root.rglob("__pycache__"):
            try:
                shutil.rmtree(pycache_dir)
                cleanup_count += 1
            except (PermissionError, FileNotFoundError):
                pass
        
        self.logger.info(f"Cleaned up {cleanup_count} artifacts")
    
    def generate_ci_config(self) -> Dict[str, Any]:
        """Generate configuration for continuous integration."""
        ci_config = {
            "name": "MCP Server Tests",
            "python_versions": ["3.8", "3.9", "3.10", "3.11"],
            "test_commands": [
                "python -m pytest tests/ -v --tb=short -m 'not performance'",
                "python -m pytest tests/test_integration.py -v",
                "python -m pytest tests/test_performance.py -v -m performance"
            ],
            "coverage_threshold": 80,
            "artifacts": [
                "test_reports/",
                "htmlcov/",
                "*.xml"
            ],
            "environment_setup": [
                "pip install -r requirements.txt",
                "pip install pytest pytest-asyncio pytest-cov"
            ]
        }
        
        # Save CI config
        ci_file = self.project_root / "ci_config.json"
        with open(ci_file, 'w') as f:
            json.dump(ci_config, f, indent=2)
        
        self.logger.info(f"CI configuration saved to: {ci_file}")
        
        return ci_config


class ContinuousIntegrationRunner:
    """Runner for continuous integration scenarios."""
    
    def __init__(self):
        """Initialize CI runner."""
        self.automation = TestAutomation()
        self.logger = logging.getLogger("ci_runner")
    
    def run_pre_commit_tests(self) -> bool:
        """Run tests suitable for pre-commit hooks."""
        self.logger.info("Running pre-commit tests...")
        
        # Run fast unit tests only
        result = self.automation.run_test_suite("unit")
        
        if not result["success"]:
            self.logger.error("Pre-commit tests failed!")
            return False
        
        # Check coverage threshold
        coverage = result.get("coverage", {})
        if coverage.get("available") and coverage.get("total_coverage", 0) < 70:
            self.logger.warning(f"Coverage below threshold: {coverage['total_coverage']:.1f}%")
        
        self.logger.info("Pre-commit tests passed!")
        return True
    
    def run_pull_request_tests(self) -> bool:
        """Run comprehensive tests for pull requests."""
        self.logger.info("Running pull request tests...")
        
        # Validate environment first
        validation = self.automation.validate_test_environment()
        if not validation["valid"]:
            self.logger.error(f"Environment validation failed: {validation['issues']}")
            return False
        
        # Run all tests except performance
        pytest_args = [
            str(self.automation.tests_dir),
            "-v",
            "--tb=short",
            "-m", "not performance",
            "--cov=" + str(self.automation.project_root / "src"),
            "--cov-fail-under=75"
        ]
        
        exit_code = pytest.main(pytest_args)
        
        if exit_code != 0:
            self.logger.error("Pull request tests failed!")
            return False
        
        self.logger.info("Pull request tests passed!")
        return True
    
    def run_nightly_tests(self) -> Dict[str, Any]:
        """Run comprehensive nightly test suite."""
        self.logger.info("Running nightly test suite...")
        
        # Run all tests including performance
        result = self.automation.run_test_suite("all")
        
        # Generate detailed report
        report_summary = {
            "success": result["success"],
            "duration": result["total_duration"],
            "timestamp": result["timestamp"],
            "report_path": result["report_path"]
        }
        
        if result["success"]:
            self.logger.info("Nightly tests completed successfully!")
        else:
            self.logger.error("Nightly tests failed!")
        
        return report_summary


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Automation Runner")
    parser.add_argument("--type", choices=["unit", "integration", "performance", "all"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--validate", action="store_true", help="Validate test environment")
    parser.add_argument("--cleanup", action="store_true", help="Clean up test artifacts")
    parser.add_argument("--ci-config", action="store_true", help="Generate CI configuration")
    parser.add_argument("--pre-commit", action="store_true", help="Run pre-commit tests")
    parser.add_argument("--pull-request", action="store_true", help="Run pull request tests")
    parser.add_argument("--nightly", action="store_true", help="Run nightly tests")
    
    args = parser.parse_args()
    
    automation = TestAutomation()
    ci_runner = ContinuousIntegrationRunner()
    
    try:
        if args.validate:
            result = automation.validate_test_environment()
            if result["valid"]:
                print("✅ Test environment is valid")
                return 0
            else:
                print("❌ Test environment validation failed:")
                for issue in result["issues"]:
                    print(f"  - {issue}")
                return 1
        
        if args.cleanup:
            automation.cleanup_test_artifacts()
            print("✅ Test artifacts cleaned up")
            return 0
        
        if args.ci_config:
            automation.generate_ci_config()
            print("✅ CI configuration generated")
            return 0
        
        if args.pre_commit:
            success = ci_runner.run_pre_commit_tests()
            return 0 if success else 1
        
        if args.pull_request:
            success = ci_runner.run_pull_request_tests()
            return 0 if success else 1
        
        if args.nightly:
            result = ci_runner.run_nightly_tests()
            return 0 if result["success"] else 1
        
        # Default: run specified test type
        result = automation.run_test_suite(args.type)
        return 0 if result["success"] else 1
        
    except Exception as e:
        print(f"❌ Test automation failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)