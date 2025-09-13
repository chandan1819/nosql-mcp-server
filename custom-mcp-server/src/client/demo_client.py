#!/usr/bin/env python3
"""
Comprehensive MCP Client Demonstration Script

This script demonstrates all CRUD operations of the custom MCP server
by connecting to the server and running through INSERT, FETCH, UPDATE,
and DELETE operations with clear output formatting and user interaction.
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Any, Dict

# Add the parent src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcp_client import MCPClient


class MCPDemonstrationClient:
    """
    Comprehensive demonstration client that showcases all MCP server capabilities
    with interactive prompts and detailed progress reporting.
    """
    
    def __init__(self):
        """Initialize the demonstration client."""
        self.server_command = [
            "python", 
            os.path.join(os.path.dirname(__file__), "..", "..", "run_server.py")
        ]
        self.client = MCPClient(self.server_command, max_retries=3, retry_delay=2.0)
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure logging for the demonstration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('demo_client.log')
            ]
        )
    
    def print_banner(self, title: str, width: int = 80) -> None:
        """Print a formatted banner for section headers."""
        print("\n" + "=" * width)
        print(f" {title.center(width - 2)} ")
        print("=" * width + "\n")
    
    def print_section(self, title: str, width: int = 60) -> None:
        """Print a formatted section header."""
        print("\n" + "-" * width)
        print(f" {title} ")
        print("-" * width)
    
    def print_progress(self, message: str, status: str = "INFO") -> None:
        """Print a progress message with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        status_symbols = {
            "INFO": "ℹ",
            "SUCCESS": "✓",
            "WARNING": "⚠",
            "ERROR": "✗",
            "PROGRESS": "→"
        }
        symbol = status_symbols.get(status, "•")
        print(f"[{timestamp}] {symbol} {message}")
    
    def wait_for_user_input(self, prompt: str = "Press Enter to continue", allow_skip: bool = True) -> bool:
        """
        Wait for user input with option to skip or continue.
        
        Args:
            prompt: The prompt message to display
            allow_skip: Whether to allow skipping with 's'
            
        Returns:
            True to continue, False to skip (if allowed)
        """
        if allow_skip:
            full_prompt = f"{prompt} (or 's' to skip): "
        else:
            full_prompt = f"{prompt}: "
        
        try:
            user_input = input(full_prompt).strip().lower()
            if allow_skip and user_input == 's':
                return False
            return True
        except KeyboardInterrupt:
            print("\n\nDemonstration interrupted by user.")
            sys.exit(0)
    
    def format_json_output(self, data: Any, max_items: int = 5) -> str:
        """Format JSON data for readable output."""
        if isinstance(data, list) and len(data) > max_items:
            # Show first few items and indicate there are more
            formatted_items = data[:max_items]
            return json.dumps(formatted_items, indent=2) + f"\n... and {len(data) - max_items} more items"
        else:
            return json.dumps(data, indent=2)
    
    def display_operation_summary(self, operation_name: str, results: Dict[str, Any]) -> None:
        """Display a summary of operation results."""
        self.print_section(f"{operation_name} Operation Summary")
        
        summary = results.get("summary", {})
        
        if operation_name == "INSERT":
            total_created = summary.get("total_created", 0)
            errors = summary.get("errors", [])
            
            self.print_progress(f"Total records created: {total_created}", "SUCCESS" if total_created > 0 else "WARNING")
            
            if errors:
                self.print_progress(f"Errors encountered: {len(errors)}", "WARNING")
                for error in errors[:3]:  # Show first 3 errors
                    print(f"    • {error}")
                if len(errors) > 3:
                    print(f"    ... and {len(errors) - 3} more errors")
        
        elif operation_name == "FETCH":
            total_records = summary.get("total_records", 0)
            errors = summary.get("errors", [])
            
            self.print_progress(f"Total records fetched: {total_records}", "SUCCESS" if total_records > 0 else "WARNING")
            
            # Show breakdown by collection
            for collection in ["users", "tasks", "products"]:
                if collection in results:
                    count = results[collection].get("count", 0)
                    self.print_progress(f"  {collection.capitalize()}: {count} records", "INFO")
            
            if errors:
                self.print_progress(f"Errors encountered: {len(errors)}", "WARNING")
        
        elif operation_name == "UPDATE":
            total_updated = summary.get("total_updated", 0)
            errors = summary.get("errors", [])
            
            self.print_progress(f"Total records updated: {total_updated}", "SUCCESS" if total_updated > 0 else "WARNING")
            
            if errors:
                self.print_progress(f"Errors encountered: {len(errors)}", "WARNING")
        
        elif operation_name == "DELETE":
            total_deleted = summary.get("total_deleted", 0)
            errors = summary.get("errors", [])
            
            self.print_progress(f"Total records deleted: {total_deleted}", "SUCCESS" if total_deleted > 0 else "WARNING")
            
            if errors:
                self.print_progress(f"Errors encountered: {len(errors)}", "WARNING")
    
    async def run_demonstration(self) -> None:
        """Run the complete CRUD demonstration."""
        self.print_banner("MCP Server CRUD Operations Demonstration")
        
        print("This demonstration will showcase all CRUD operations of the custom MCP server:")
        print("• INSERT: Create new records in all collections")
        print("• FETCH:  Retrieve and display all records")
        print("• UPDATE: Modify existing records with before/after comparison")
        print("• DELETE: Remove records with confirmation")
        print("\nEach operation can be skipped if desired.")
        
        if not self.wait_for_user_input("\nReady to start the demonstration?", allow_skip=False):
            return
        
        try:
            # Establish connection to MCP server
            self.print_section("Establishing Connection to MCP Server")
            self.print_progress("Connecting to MCP server...", "PROGRESS")
            
            async with self.client.connection():
                self.print_progress("Successfully connected to MCP server!", "SUCCESS")
                
                # Test connection
                connection_ok = await self.client.test_connection()
                if connection_ok:
                    self.print_progress("Connection test passed", "SUCCESS")
                else:
                    self.print_progress("Connection test failed", "ERROR")
                    return
                
                # Run INSERT operations
                if self.wait_for_user_input("\nProceed with INSERT operations?"):
                    self.print_section("INSERT Operations - Creating New Records")
                    self.print_progress("Starting INSERT operations...", "PROGRESS")
                    
                    insert_results = await self.client.demonstrate_insert_operations()
                    self.display_operation_summary("INSERT", insert_results)
                    
                    # Show some sample created records
                    if insert_results["summary"]["total_created"] > 0:
                        print("\nSample created records:")
                        for collection in ["users", "tasks", "products"]:
                            if insert_results[collection]:
                                for result in insert_results[collection][:2]:  # Show first 2
                                    if result.get("success") and result.get("data"):
                                        record = result["data"]
                                        record_id = record.get("id", "unknown")
                                        if collection == "users":
                                            name = record.get("name", "Unknown")
                                            print(f"  • User {record_id}: {name}")
                                        elif collection == "tasks":
                                            title = record.get("title", "Unknown")
                                            print(f"  • Task {record_id}: {title}")
                                        elif collection == "products":
                                            name = record.get("name", "Unknown")
                                            print(f"  • Product {record_id}: {name}")
                else:
                    self.print_progress("INSERT operations skipped by user", "WARNING")
                
                # Run FETCH operations
                if self.wait_for_user_input("\nProceed with FETCH operations?"):
                    self.print_section("FETCH Operations - Retrieving All Records")
                    self.print_progress("Starting FETCH operations...", "PROGRESS")
                    
                    fetch_results = await self.client.demonstrate_fetch_operations()
                    self.display_operation_summary("FETCH", fetch_results)
                    
                    # Show detailed records if requested
                    if fetch_results["summary"]["total_records"] > 0:
                        if self.wait_for_user_input("Would you like to see detailed record listings?"):
                            for collection in ["users", "tasks", "products"]:
                                if collection in fetch_results and fetch_results[collection]["records"]:
                                    print(f"\n{collection.capitalize()} Records:")
                                    records = fetch_results[collection]["records"]
                                    for i, record in enumerate(records[:5]):  # Show first 5
                                        print(f"  {i+1}. {self.format_json_output(record)}")
                                    if len(records) > 5:
                                        print(f"  ... and {len(records) - 5} more records")
                else:
                    self.print_progress("FETCH operations skipped by user", "WARNING")
                
                # Run UPDATE operations
                if self.wait_for_user_input("\nProceed with UPDATE operations?"):
                    self.print_section("UPDATE Operations - Modifying Existing Records")
                    self.print_progress("Starting UPDATE operations...", "PROGRESS")
                    
                    update_results = await self.client.demonstrate_update_operations()
                    self.display_operation_summary("UPDATE", update_results)
                    
                    # Show before/after comparisons
                    if update_results["summary"]["total_updated"] > 0:
                        if self.wait_for_user_input("Would you like to see before/after comparisons?"):
                            for update_op in update_results["updates"]:
                                if update_op["before_records"] and update_op["after_records"]:
                                    print(f"\nUpdate: {update_op['description']}")
                                    for i, (before, after) in enumerate(zip(update_op["before_records"][:2], update_op["after_records"][:2])):
                                        print(f"  Record {before.get('id', 'unknown')}:")
                                        print(f"    Before: {self.format_json_output(before)}")
                                        print(f"    After:  {self.format_json_output(after)}")
                else:
                    self.print_progress("UPDATE operations skipped by user", "WARNING")
                
                # Run DELETE operations
                if self.wait_for_user_input("\nProceed with DELETE operations? (This will remove records)"):
                    self.print_section("DELETE Operations - Removing Records")
                    self.print_progress("Starting DELETE operations...", "PROGRESS")
                    
                    delete_results = await self.client.demonstrate_delete_operations()
                    self.display_operation_summary("DELETE", delete_results)
                    
                    # Show what was deleted
                    if delete_results["summary"]["total_deleted"] > 0:
                        print("\nRecords that were deleted:")
                        for delete_op in delete_results["deletions"]:
                            if delete_op["records_before_delete"]:
                                print(f"  {delete_op['description']}:")
                                for record in delete_op["records_before_delete"][:3]:  # Show first 3
                                    record_id = record.get("id", "unknown")
                                    collection = delete_op["collection"]
                                    if collection == "users":
                                        name = record.get("name", "Unknown")
                                        print(f"    • User {record_id}: {name}")
                                    elif collection == "tasks":
                                        title = record.get("title", "Unknown")
                                        print(f"    • Task {record_id}: {title}")
                                    elif collection == "products":
                                        name = record.get("name", "Unknown")
                                        print(f"    • Product {record_id}: {name}")
                else:
                    self.print_progress("DELETE operations skipped by user", "WARNING")
                
                # Final summary
                self.print_banner("Demonstration Complete!")
                self.print_progress("All CRUD operations have been demonstrated", "SUCCESS")
                self.print_progress("Check 'demo_client.log' for detailed logs", "INFO")
                
        except Exception as e:
            self.print_progress(f"Demonstration failed: {str(e)}", "ERROR")
            self.logger.error(f"Demonstration error: {str(e)}")
            raise
    
    async def run_quick_test(self) -> bool:
        """
        Run a quick test of all operations without user interaction.
        
        Returns:
            True if all operations completed successfully, False otherwise
        """
        print("Running quick test of all CRUD operations...")
        
        try:
            async with self.client.connection():
                # Test connection
                if not await self.client.test_connection():
                    print("✗ Connection test failed")
                    return False
                print("✓ Connection test passed")
                
                # Test INSERT
                insert_results = await self.client.demonstrate_insert_operations()
                insert_success = insert_results["summary"]["total_created"] > 0
                print(f"{'✓' if insert_success else '✗'} INSERT operations: {insert_results['summary']['total_created']} records created")
                
                # Test FETCH
                fetch_results = await self.client.demonstrate_fetch_operations()
                fetch_success = fetch_results["summary"]["total_records"] > 0
                print(f"{'✓' if fetch_success else '✗'} FETCH operations: {fetch_results['summary']['total_records']} records retrieved")
                
                # Test UPDATE
                update_results = await self.client.demonstrate_update_operations()
                update_success = len(update_results["summary"]["errors"]) == 0
                print(f"{'✓' if update_success else '✗'} UPDATE operations: {update_results['summary']['total_updated']} records updated")
                
                # Test DELETE
                delete_results = await self.client.demonstrate_delete_operations()
                delete_success = len(delete_results["summary"]["errors"]) == 0
                print(f"{'✓' if delete_success else '✗'} DELETE operations: {delete_results['summary']['total_deleted']} records deleted")
                
                overall_success = insert_success and fetch_success and update_success and delete_success
                print(f"\n{'✓ All tests passed!' if overall_success else '✗ Some tests failed'}")
                return overall_success
                
        except Exception as e:
            print(f"✗ Quick test failed: {str(e)}")
            return False