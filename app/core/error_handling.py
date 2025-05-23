"""Error handling utilities for the application."""
from enum import Enum
from typing import Dict, Any, Optional
import logging

class ErrorCode(Enum):
    """Application error codes."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    PROCESSING_ERROR = "PROCESSING_ERROR"
    FILE_ERROR = "FILE_ERROR"
    IMAGE_PROCESSING_ERROR = "IMAGE_PROCESSING_ERROR"

class ApplicationError(Exception):
    """Base application exception."""
    
    def __init__(self, message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class ErrorHandler:
    """Centralized error handling."""
    
    @staticmethod
    def handle_error(error: Exception) -> Dict[str, Any]:
        """Handle application errors consistently."""
        logger = logging.getLogger(__name__)
        
        if isinstance(error, ApplicationError):
            logger.error(f"Application error: {error.message}", extra=error.details)
            return {
                "error": error.error_code.value,
                "message": error.message,
                "details": error.details
            }
        else:
            logger.error(f"Unexpected error: {str(error)}")
            return {
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {}
            }

def register_exception_handlers(app):
    """Register exception handlers with the FastAPI application."""
    # This function is a placeholder for FastAPI exception handlers
    # For NiceGUI, we'll handle exceptions directly in the request handlers
    pass