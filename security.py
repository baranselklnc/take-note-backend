"""Security utilities and middleware for the API."""

import time
import hashlib
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse."""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, Dict[str, Any]] = {}
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean up old entries
        self._cleanup_old_entries(current_time)
        
        # Check rate limit
        if not self._check_rate_limit(client_ip, current_time):
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": str(self.period)}
            )
        
        # Record the request
        self._record_request(client_ip, current_time)
        
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded IP (for reverse proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str, current_time: float) -> bool:
        """Check if client is within rate limit."""
        if client_ip not in self.clients:
            return True
        
        client_data = self.clients[client_ip]
        request_times = client_data["requests"]
        
        # Count requests in the current period
        recent_requests = [
            req_time for req_time in request_times
            if current_time - req_time < self.period
        ]
        
        return len(recent_requests) < self.calls
    
    def _record_request(self, client_ip: str, current_time: float) -> None:
        """Record a request for rate limiting."""
        if client_ip not in self.clients:
            self.clients[client_ip] = {"requests": []}
        
        self.clients[client_ip]["requests"].append(current_time)
    
    def _cleanup_old_entries(self, current_time: float) -> None:
        """Clean up old rate limiting entries."""
        for client_ip in list(self.clients.keys()):
            client_data = self.clients[client_ip]
            request_times = client_data["requests"]
            
            # Remove requests older than the period
            recent_requests = [
                req_time for req_time in request_times
                if current_time - req_time < self.period
            ]
            
            if recent_requests:
                self.clients[client_ip]["requests"] = recent_requests
            else:
                # Remove client if no recent requests
                del self.clients[client_ip]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response."""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Add HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for monitoring and debugging."""
    
    async def dispatch(self, request: Request, call_next):
        """Log request details."""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {self._get_client_ip(request)}"
        )
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} for {request.method} {request.url.path} "
            f"in {process_time:.3f}s"
        )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Validate and sanitize input data."""
    
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB
        super().__init__(app)
        self.max_request_size = max_request_size
    
    async def dispatch(self, request: Request, call_next):
        """Validate request size and content."""
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request entity too large"
            )
        
        # Check for suspicious content
        if self._is_suspicious_request(request):
            logger.warning(f"Suspicious request detected: {request.method} {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request"
            )
        
        response = await call_next(request)
        return response
    
    def _is_suspicious_request(self, request: Request) -> bool:
        """Check if request appears suspicious."""
        # Check for SQL injection patterns
        suspicious_patterns = [
            "union select", "drop table", "delete from",
            "insert into", "update set", "script>",
            "<script", "javascript:", "vbscript:"
        ]
        
        # Check URL path
        path = request.url.path.lower()
        for pattern in suspicious_patterns:
            if pattern in path:
                return True
        
        # Check query parameters
        for param_name, param_value in request.query_params.items():
            param_value_lower = param_value.lower()
            for pattern in suspicious_patterns:
                if pattern in param_value_lower:
                    return True
        
        return False


def generate_request_id() -> str:
    """Generate a unique request ID for tracking."""
    import uuid
    return str(uuid.uuid4())


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == hashed_password


class APIKeyAuth:
    """API Key authentication for service-to-service communication."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def __call__(self, credentials: HTTPAuthorizationCredentials = HTTPBearer()) -> str:
        """Validate API key."""
        if not credentials or credentials.credentials != self.api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return credentials.credentials


# Content Security Policy
CSP_HEADER = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "font-src 'self' data:; "
    "connect-src 'self' https:; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)


def add_security_headers(response: Response) -> None:
    """Add comprehensive security headers to response."""
    response.headers["Content-Security-Policy"] = CSP_HEADER
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
