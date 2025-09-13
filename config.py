"""Configuration settings for the Take Note Backend API."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # App Configuration
    APP_NAME: str = os.getenv("APP_NAME", "Take Note Backend API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 gün
    
    # Database Configuration
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    def validate_config(self) -> None:
        """Validate that required configuration is present."""
        required_vars = [
            ("SUPABASE_URL", self.SUPABASE_URL),
            ("SUPABASE_KEY", self.SUPABASE_KEY),
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


# Global settings instance
settings = Settings()

# Validate configuration on import
try:
    settings.validate_config()
except ValueError as e:
    if settings.DEBUG:
        print(f"Configuration warning: {e}")
    else:
        raise
