"""Logging configuration for the application."""
import logging
import sys
from typing import Optional

def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: The name of the logger
        level: Optional logging level (defaults to INFO if not specified)
        
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set level from parameter or default to INFO
    log_level = getattr(logging, level or "INFO")
    logger.setLevel(log_level)
    
    # Create handler if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger