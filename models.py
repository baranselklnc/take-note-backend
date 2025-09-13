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


# AI Models
class NoteSummary(BaseModel):
    """Model for note summarization response."""
    summary: str = Field(..., description="AI-generated summary")
    original_length: int = Field(..., description="Original content length")
    summary_length: int = Field(..., description="Summary length")
    compression_ratio: float = Field(..., description="Compression ratio")
    model: str = Field(..., description="AI model used")


class NoteCategory(BaseModel):
    """Model for note categorization response."""
    category: str = Field(..., description="AI-generated category")
    confidence: float = Field(..., description="Confidence score (0-1)")
    model: str = Field(..., description="AI model used")


class AutoTags(BaseModel):
    """Model for auto-generated tags response."""
    tags: List[str] = Field(..., description="AI-generated tags")
    confidence_scores: List[float] = Field(..., description="Confidence scores for each tag")
    model: str = Field(..., description="AI model used")


class AISearchResult(BaseModel):
    """Model for AI search results."""
    note: NoteResponse = Field(..., description="Note data")
    relevance_score: float = Field(..., description="Relevance score (0-1)")


class AISearchResponse(BaseModel):
    """Model for AI search response."""
    results: List[AISearchResult] = Field(..., description="Search results")
    query: str = Field(..., description="Original search query")
    total_results: int = Field(..., description="Total number of results")


class AIProcessRequest(BaseModel):
    """Model for AI processing request."""
    content: str = Field(..., min_length=1, max_length=10000, description="Content to process")


class AIProcessResponse(BaseModel):
    """Model for comprehensive AI processing response."""
    summary: NoteSummary = Field(..., description="Summary result")
    category: NoteCategory = Field(..., description="Category result")
    tags: AutoTags = Field(..., description="Tags result")
    processed_at: datetime = Field(..., description="Processing timestamp")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
