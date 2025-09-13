#!/usr/bin/env python3
"""Seed data script for development and testing."""

import asyncio
import sys
import uuid
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from config import settings
from database import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_sample_notes(user_id: str, count: int = 10):
    """Create sample notes for testing."""
    logger.info(f"📝 Creating {count} sample notes for user {user_id}")
    
    sample_notes = [
        {
            "title": "Welcome to Take Note!",
            "content": "This is your first note. You can edit, delete, or pin this note to keep it at the top.",
            "is_pinned": True
        },
        {
            "title": "Meeting Notes - Project Planning",
            "content": "Key points from today's meeting:\n1. Define project scope\n2. Set timeline\n3. Assign responsibilities\n4. Schedule follow-up",
            "is_pinned": False
        },
        {
            "title": "Shopping List",
            "content": "- Milk\n- Bread\n- Eggs\n- Apples\n- Coffee",
            "is_pinned": False
        },
        {
            "title": "Book Recommendations",
            "content": "Books to read:\n1. Clean Code by Robert Martin\n2. Design Patterns by Gang of Four\n3. The Pragmatic Programmer",
            "is_pinned": False
        },
        {
            "title": "Ideas for Weekend",
            "content": "Things to do this weekend:\n- Visit the museum\n- Try new restaurant\n- Read a book\n- Call family",
            "is_pinned": False
        }
    ]
    
    created_notes = []
    
    for i in range(count):
        note_data = sample_notes[i % len(sample_notes)]
        
        # Add some variation to titles for multiple notes
        if i >= len(sample_notes):
            note_data = note_data.copy()
            note_data["title"] = f"{note_data['title']} ({i + 1})"
        
        try:
            note = await db_manager.create_note(
                user_id=user_id,
                title=note_data["title"],
                content=note_data["content"],
                is_pinned=note_data["is_pinned"]
            )
            created_notes.append(note)
            logger.info(f"✅ Created note: {note['title']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create note: {e}")
    
    return created_notes


async def seed_data():
    """Seed the database with sample data."""
    try:
        logger.info("🌱 Seeding database with sample data...")
        
        # Create a test user ID
        test_user_id = str(uuid.uuid4())
        logger.info(f"👤 Using test user ID: {test_user_id}")
        
        # Create sample notes
        notes = await create_sample_notes(test_user_id, 20)
        
        logger.info(f"✅ Successfully created {len(notes)} sample notes")
        logger.info("🎉 Database seeding completed!")
        
        print("\n" + "=" * 50)
        print("📊 Sample Data Created:")
        print(f"👤 Test User ID: {test_user_id}")
        print(f"📝 Notes Created: {len(notes)}")
        print("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        sys.exit(1)


async def main():
    """Main function."""
    print("🌱 Take Note Backend - Data Seeding")
    print("=" * 50)
    
    # Validate configuration
    try:
        settings.validate_config()
        logger.info("✅ Configuration validated")
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    await seed_data()


if __name__ == "__main__":
    asyncio.run(main())
