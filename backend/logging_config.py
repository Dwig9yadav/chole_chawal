"""Logging configuration"""
import logging
import json
from logging.handlers import RotatingFileHandler
from pathlib import Path
from backend.config import get_settings
from pythonjsonlogger import jsonlogger


settings = get_settings()
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)


def setup_logging():
    """Configure logging with JSON format for structured logging"""
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Remove default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # JSON Formatter
    json_formatter = jsonlogger.JsonFormatter()
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_dir / "voxai.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=10485760,
        backupCount=5
    )
    error_handler.setFormatter(json_formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)
    
    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # Suppress verbose loggers
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
