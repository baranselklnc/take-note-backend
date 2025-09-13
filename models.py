"""Pydantic models for request/response validation."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class NoteBase(BaseModel):
    """Base note model with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, max_length=10000, description="Note content")
    is_pinned: bool = Field(False, description="Whether the note is pinned")


class NoteCreate(NoteBase):
    """Model for creating a new note."""
    pass


class NoteUpdate(BaseModel):
    """Model for updating a note."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Note title")
    content: Optional[str] = Field(None, min_length=1, max_length=10000, description="Note content")
    is_pinned: Optional[bool] = Field(None, description="Whether the note is pinned")


class NoteResponse(NoteBase):
    """Model for note response."""
    id: str = Field(..., description="Unique note identifier")
    user_id: str = Field(..., description="ID of the note owner")
    is_deleted: bool = Field(..., description="Whether the note is deleted")
    created_at: datetime = Field(..., description="Note creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Note last update timestamp")
    deleted_at: Optional[datetime] = Field(None, description="Note deletion timestamp")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NoteListResponse(BaseModel):
    """Model for notes list response."""
    notes: List[NoteResponse] = Field(..., description="List of notes")
    total: int = Field(..., description="Total number of notes")
    page: int = Field(1, description="Current page number")
    size: int = Field(50, description="Number of notes per page")


class NoteSearchRequest(BaseModel):
    """Model for note search request."""
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    limit: Optional[int] = Field(50, ge=1, le=100, description="Maximum number of results")


class ErrorResponse(BaseModel):
    """Model for error responses."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")


class SuccessResponse(BaseModel):
    """Model for success responses."""
    message: str = Field(..., description="Success message")
    data: Optional[dict] = Field(None, description="Response data")


class TokenResponse(BaseModel):
    """Model for authentication token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")


class UserInfo(BaseModel):
    """Model for user information."""
    id: str = Field(..., description="User ID")
    email: Optional[str] = Field(None, description="User email")
    created_at: datetime = Field(..., description="User creation timestamp")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
