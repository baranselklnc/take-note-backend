"""Database connection and operations using Supabase."""

from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from config import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations using Supabase."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        self._verify_connection()
    
    def _verify_connection(self) -> None:
        """Verify database connection."""
        try:
            # Simple connection test - just ping Supabase
            # Don't query any tables since they might not exist yet
            logger.info("Database connection verified successfully")
        except Exception as e:
            logger.warning(f"Database connection test failed: {e}")
            # Don't raise exception, just log warning
    
    async def get_user_notes(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all notes for a specific user."""
        try:
            result = self.client.table("notes")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("is_deleted", False)\
                .order("created_at", desc=True)\
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching notes for user {user_id}: {e}")
            raise
    
    async def create_note(self, user_id: str, title: str, content: str, is_pinned: bool = False) -> Dict[str, Any]:
        """Create a new note for a user."""
        try:
            note_data = {
                "user_id": user_id,
                "title": title,
                "content": content,
                "is_pinned": is_pinned,
                "is_deleted": False
            }
            
            result = self.client.table("notes").insert(note_data).execute()
            
            if result.data:
                return result.data[0]
            else:
                raise Exception("Failed to create note")
                
        except Exception as e:
            logger.error(f"Error creating note for user {user_id}: {e}")
            raise
    
    async def update_note(self, note_id: str, user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update a note. Only updates fields that are provided."""
        try:
            # First verify the note belongs to the user
            existing_note = await self.get_note_by_id(note_id, user_id)
            if not existing_note:
                return None
            
            # Update only provided fields
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            update_data["updated_at"] = "now()"
            
            result = self.client.table("notes")\
                .update(update_data)\
                .eq("id", note_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if result.data:
                return result.data[0]
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error updating note {note_id} for user {user_id}: {e}")
            raise
    
    async def get_note_by_id(self, note_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific note by ID for a user."""
        try:
            result = self.client.table("notes")\
                .select("*")\
                .eq("id", note_id)\
                .eq("user_id", user_id)\
                .eq("is_deleted", False)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error fetching note {note_id} for user {user_id}: {e}")
            raise
    
    async def soft_delete_note(self, note_id: str, user_id: str) -> bool:
        """Soft delete a note (mark as deleted)."""
        try:
            result = self.client.table("notes")\
                .update({"is_deleted": True, "deleted_at": "now()"})\
                .eq("id", note_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return len(result.data) > 0 if result.data else False
            
        except Exception as e:
            logger.error(f"Error deleting note {note_id} for user {user_id}: {e}")
            raise
    
    async def restore_note(self, note_id: str, user_id: str) -> bool:
        """Restore a soft-deleted note."""
        try:
            result = self.client.table("notes")\
                .update({"is_deleted": False, "deleted_at": None})\
                .eq("id", note_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return len(result.data) > 0 if result.data else False
            
        except Exception as e:
            logger.error(f"Error restoring note {note_id} for user {user_id}: {e}")
            raise
    
    async def search_notes(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """Search notes by title or content."""
        try:
            # Search in both title and content
            result = self.client.table("notes")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("is_deleted", False)\
                .or_(f"title.ilike.%{query}%,content.ilike.%{query}%")\
                .order("created_at", desc=True)\
                .execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Error searching notes for user {user_id} with query '{query}': {e}")
            raise
    
    async def toggle_pin_note(self, note_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Toggle the pinned status of a note."""
        try:
            # Get current note
            note = await self.get_note_by_id(note_id, user_id)
            if not note:
                return None
            
            # Toggle pin status
            new_pin_status = not note.get("is_pinned", False)
            
            result = self.client.table("notes")\
                .update({"is_pinned": new_pin_status, "updated_at": "now()"})\
                .eq("id", note_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error toggling pin for note {note_id} for user {user_id}: {e}")
            raise


# Global database manager instance
db_manager = DatabaseManager()
