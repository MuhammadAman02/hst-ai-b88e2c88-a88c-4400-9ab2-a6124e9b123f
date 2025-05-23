"""Configuration settings for the Skin Tone Color Advisor application."""
from pydantic_settings import BaseSettings
from pydantic import Field
import os
from typing import Optional

class AppConfig(BaseSettings):
    """Application configuration with validation."""
    
    # Application Settings
    app_name: str = Field(default="Skin Tone Color Advisor", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Upload Settings
    upload_folder: str = Field(default="uploads", description="Folder for uploaded images")
    max_upload_size: int = Field(default=10 * 1024 * 1024, description="Maximum upload size in bytes (10MB)")
    allowed_extensions: list = Field(default=["jpg", "jpeg", "png"], description="Allowed file extensions")
    
    # Server Settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global configuration instance
settings = AppConfig()

# Ensure upload directory exists
os.makedirs(settings.upload_folder, exist_ok=True)