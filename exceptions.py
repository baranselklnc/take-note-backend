"""Custom exceptions and error handlers for the API."""

from typing import Union
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class APIException(Exception):
    """Base API exception class."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class NoteNotFoundError(APIException):
    """Raised when a note is not found."""
    
    def __init__(self, note_id: str):
        super().__init__(
            message=f"Note with ID {note_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The requested note with ID {note_id} does not exist or you don't have permission to access it."
        )


class NoteAccessDeniedError(APIException):
    """Raised when user doesn't have access to a note."""
    
    def __init__(self, note_id: str):
        super().__init__(
            message=f"Access denied to note {note_id}",
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this note."
        )


class DatabaseError(APIException):
    """Raised when database operations fail."""
    
    def __init__(self, operation: str, detail: str = None):
        super().__init__(
            message=f"Database operation failed: {operation}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail or "An error occurred while accessing the database."
        )


class AuthenticationError(APIException):
    """Raised when authentication fails."""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            message="Authentication failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class ValidationError(APIException):
    """Raised when request validation fails."""
    
    def __init__(self, detail: str):
        super().__init__(
            message="Validation error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions."""
    logger.error(f"API Exception: {exc.message} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "detail": exc.detail,
            "path": str(request.url.path)
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.error(f"HTTP Exception: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "detail": getattr(exc, 'detail', None),
            "path": str(request.url.path)
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors."""
    logger.error(f"Validation Error: {exc.errors()}")
    
    # Format validation errors for better readability
    formatted_errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "detail": "Request validation failed",
            "errors": formatted_errors,
            "path": str(request.url.path)
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later.",
            "path": str(request.url.path)
        }
    )


def handle_database_error(func):
    """Decorator to handle database errors."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise DatabaseError(
                operation=func.__name__,
                detail=str(e)
            )
    return wrapper


def validate_note_access(note_user_id: str, current_user_id: str) -> None:
    """Validate that current user has access to the note."""
    if note_user_id != current_user_id:
        raise NoteAccessDeniedError("access_denied")


def validate_note_exists(note: Union[dict, None], note_id: str) -> None:
    """Validate that note exists."""
    if not note:
        raise NoteNotFoundError(note_id)
