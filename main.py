"""Main FastAPI application for Take Note Backend API."""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import List, Optional

from config import settings
from database import db_manager
from models import (
    NoteCreate, NoteUpdate, NoteResponse, NoteListResponse,
    NoteSearchRequest, ErrorResponse, SuccessResponse
)
from auth import get_current_user, require_auth
from exceptions import (
    NoteNotFoundError, NoteAccessDeniedError, DatabaseError,
    api_exception_handler, http_exception_handler,
    validation_exception_handler, general_exception_handler,
    validate_note_access, validate_note_exists
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Take Note Backend API...")
    try:
        # Verify database connection
        await db_manager.get_user_notes("test")
        logger.info("Database connection verified")
    except Exception as e:
        logger.warning(f"Database connection test failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Take Note Backend API...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Take Note mobile application",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(NoteNotFoundError, api_exception_handler)
app.add_exception_handler(NoteAccessDeniedError, api_exception_handler)
app.add_exception_handler(DatabaseError, api_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.get("/", response_model=SuccessResponse)
async def root():
    """Root endpoint with API information."""
    return SuccessResponse(
        message="Take Note Backend API is running",
        data={
            "version": settings.APP_VERSION,
            "docs_url": "/docs" if settings.DEBUG else None
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        await db_manager.get_user_notes("health_check_test")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)}
        )


@app.get("/notes", response_model=NoteListResponse)
async def get_notes(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Number of notes per page"),
    search: Optional[str] = Query(None, min_length=1, max_length=100, description="Search query"),
    user_id: str = Depends(require_auth)
):
    """
    Get all notes for the authenticated user.
    
    Args:
        page: Page number (default: 1)
        size: Number of notes per page (default: 50, max: 100)
        search: Optional search query for title or content
        user_id: Authenticated user ID
        
    Returns:
        List of notes with pagination info
    """
    try:
        if search:
            # Search notes
            notes_data = await db_manager.search_notes(user_id, search)
        else:
            # Get all notes
            notes_data = await db_manager.get_user_notes(user_id)
        
        # Apply pagination
        total = len(notes_data)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_notes = notes_data[start_idx:end_idx]
        
        # Convert to response models
        notes = [NoteResponse(**note) for note in paginated_notes]
        
        return NoteListResponse(
            notes=notes,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error(f"Error fetching notes for user {user_id}: {e}")
        raise DatabaseError("fetch_notes", str(e))


@app.post("/notes", response_model=NoteResponse, status_code=201)
async def create_note(
    note_data: NoteCreate,
    user_id: str = Depends(require_auth)
):
    """
    Create a new note.
    
    Args:
        note_data: Note creation data
        user_id: Authenticated user ID
        
    Returns:
        Created note
    """
    try:
        created_note = await db_manager.create_note(
            user_id=user_id,
            title=note_data.title,
            content=note_data.content,
            is_pinned=note_data.is_pinned
        )
        
        return NoteResponse(**created_note)
        
    except Exception as e:
        logger.error(f"Error creating note for user {user_id}: {e}")
        raise DatabaseError("create_note", str(e))


@app.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    user_id: str = Depends(require_auth)
):
    """
    Get a specific note by ID.
    
    Args:
        note_id: Note ID
        user_id: Authenticated user ID
        
    Returns:
        Note data
    """
    try:
        note = await db_manager.get_note_by_id(note_id, user_id)
        validate_note_exists(note, note_id)
        
        return NoteResponse(**note)
        
    except Exception as e:
        if isinstance(e, NoteNotFoundError):
            raise
        logger.error(f"Error fetching note {note_id} for user {user_id}: {e}")
        raise DatabaseError("get_note", str(e))


@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    note_data: NoteUpdate,
    user_id: str = Depends(require_auth)
):
    """
    Update a note.
    
    Args:
        note_id: Note ID
        note_data: Note update data
        user_id: Authenticated user ID
        
    Returns:
        Updated note
    """
    try:
        # Check if note exists and user has access
        existing_note = await db_manager.get_note_by_id(note_id, user_id)
        validate_note_exists(existing_note, note_id)
        
        # Prepare update data (only include non-None values)
        update_data = {}
        if note_data.title is not None:
            update_data["title"] = note_data.title
        if note_data.content is not None:
            update_data["content"] = note_data.content
        if note_data.is_pinned is not None:
            update_data["is_pinned"] = note_data.is_pinned
        
        if not update_data:
            # No fields to update, return existing note
            return NoteResponse(**existing_note)
        
        # Update the note
        updated_note = await db_manager.update_note(note_id, user_id, **update_data)
        
        if not updated_note:
            raise NoteNotFoundError(note_id)
        
        return NoteResponse(**updated_note)
        
    except Exception as e:
        if isinstance(e, NoteNotFoundError):
            raise
        logger.error(f"Error updating note {note_id} for user {user_id}: {e}")
        raise DatabaseError("update_note", str(e))


@app.delete("/notes/{note_id}", response_model=SuccessResponse)
async def delete_note(
    note_id: str,
    user_id: str = Depends(require_auth)
):
    """
    Delete a note (soft delete).
    
    Args:
        note_id: Note ID
        user_id: Authenticated user ID
        
    Returns:
        Success message
    """
    try:
        # Check if note exists and user has access
        existing_note = await db_manager.get_note_by_id(note_id, user_id)
        validate_note_exists(existing_note, note_id)
        
        # Soft delete the note
        success = await db_manager.soft_delete_note(note_id, user_id)
        
        if not success:
            raise NoteNotFoundError(note_id)
        
        return SuccessResponse(
            message=f"Note {note_id} deleted successfully",
            data={"note_id": note_id}
        )
        
    except Exception as e:
        if isinstance(e, NoteNotFoundError):
            raise
        logger.error(f"Error deleting note {note_id} for user {user_id}: {e}")
        raise DatabaseError("delete_note", str(e))


@app.post("/notes/{note_id}/restore", response_model=SuccessResponse)
async def restore_note(
    note_id: str,
    user_id: str = Depends(require_auth)
):
    """
    Restore a soft-deleted note (undo delete).
    
    Args:
        note_id: Note ID
        user_id: Authenticated user ID
        
    Returns:
        Success message
    """
    try:
        success = await db_manager.restore_note(note_id, user_id)
        
        if not success:
            raise NoteNotFoundError(note_id)
        
        return SuccessResponse(
            message=f"Note {note_id} restored successfully",
            data={"note_id": note_id}
        )
        
    except Exception as e:
        if isinstance(e, NoteNotFoundError):
            raise
        logger.error(f"Error restoring note {note_id} for user {user_id}: {e}")
        raise DatabaseError("restore_note", str(e))


@app.patch("/notes/{note_id}/pin", response_model=NoteResponse)
async def toggle_pin_note(
    note_id: str,
    user_id: str = Depends(require_auth)
):
    """
    Toggle the pinned status of a note.
    
    Args:
        note_id: Note ID
        user_id: Authenticated user ID
        
    Returns:
        Updated note with new pin status
    """
    try:
        updated_note = await db_manager.toggle_pin_note(note_id, user_id)
        
        if not updated_note:
            raise NoteNotFoundError(note_id)
        
        return NoteResponse(**updated_note)
        
    except Exception as e:
        if isinstance(e, NoteNotFoundError):
            raise
        logger.error(f"Error toggling pin for note {note_id} for user {user_id}: {e}")
        raise DatabaseError("toggle_pin_note", str(e))


@app.post("/notes/search", response_model=NoteListResponse)
async def search_notes(
    search_request: NoteSearchRequest,
    user_id: str = Depends(require_auth)
):
    """
    Search notes by title or content.
    
    Args:
        search_request: Search request data
        user_id: Authenticated user ID
        
    Returns:
        List of matching notes
    """
    try:
        notes_data = await db_manager.search_notes(user_id, search_request.query)
        
        # Apply limit
        limited_notes = notes_data[:search_request.limit]
        
        # Convert to response models
        notes = [NoteResponse(**note) for note in limited_notes]
        
        return NoteListResponse(
            notes=notes,
            total=len(limited_notes),
            page=1,
            size=len(limited_notes)
        )
        
    except Exception as e:
        logger.error(f"Error searching notes for user {user_id}: {e}")
        raise DatabaseError("search_notes", str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
