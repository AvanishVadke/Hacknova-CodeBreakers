"""
Application Configuration
Load environment variables and application settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Smart Campus Access Control System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # CV Pipeline
    FACE_RECOGNITION_THRESHOLD: float = 0.6
    ANPR_CONFIDENCE_THRESHOLD: float = 0.75
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
