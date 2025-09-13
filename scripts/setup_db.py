#!/usr/bin/env python3
"""Database setup script for Take Note Backend."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from config import settings
from database import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_database():
    """Setup database tables and initial data."""
    try:
        logger.info("🔧 Setting up database...")
        
        # Test database connection
        logger.info("📡 Testing database connection...")
        await db_manager.get_user_notes("test_connection")
        logger.info("✅ Database connection successful")
        
        logger.info("🎉 Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        sys.exit(1)


async def main():
    """Main function."""
    print("🚀 Take Note Backend - Database Setup")
    print("=" * 50)
    
    # Validate configuration
    try:
        settings.validate_config()
        logger.info("✅ Configuration validated")
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    await setup_database()


if __name__ == "__main__":
    asyncio.run(main())
