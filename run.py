#!/usr/bin/env python3
"""Startup script for Take Note Backend API."""

import uvicorn
import sys
import os
from config import settings

def main():
    """Main entry point for the application."""
    
    # Validate configuration
    try:
        settings.validate_config()
        print("✅ Configuration validated successfully")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your environment variables and .env file")
        sys.exit(1)
    
    # Print startup information
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📊 Debug mode: {'ON' if settings.DEBUG else 'OFF'}")
    print(f"🔗 Supabase URL: {settings.SUPABASE_URL[:50]}...")
    
    if settings.DEBUG:
        print("📚 API Documentation available at:")
        print("   - Swagger UI: http://localhost:8000/docs")
        print("   - ReDoc: http://localhost:8000/redoc")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
        access_log=True
    )

if __name__ == "__main__":
    main()
