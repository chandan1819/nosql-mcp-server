#!/usr/bin/env python3
"""
Database initialization script for the MCP server.
This script populates the database with sample data for testing and demonstration.
"""

import sys
import os
import logging
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

from database.manager import DatabaseManager


def setup_logging():
    """Configure logging for the initialization script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main function to initialize the database with sample data."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Change to the project root directory
        project_root = Path(__file__).parent.parent.parent
        os.chdir(project_root)
        
        logger.info("Starting database initialization...")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Check if database is connected
        if not db_manager.is_connected():
            logger.error("Failed to connect to database")
            return 1
        
        # Initialize sample data
        result = db_manager.initialize_sample_data()
        
        # Report results
        total_records = sum(result.values())
        if total_records > 0:
            logger.info("Database initialization completed successfully!")
            logger.info(f"Records inserted:")
            for collection, count in result.items():
                if count > 0:
                    logger.info(f"  - {collection}: {count} records")
        else:
            logger.info("Database already contains data. No new records inserted.")
        
        # Close database connection
        db_manager.close()
        
        return 0
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)