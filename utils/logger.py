"""
Logging utility for the Agentic Feedback System
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from config import LOGGING_CONFIG


def setup_logger(name="agentic_feedback"):
    """Setup and configure the application logger"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(LOGGING_CONFIG["log_file"])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOGGING_CONFIG["log_level"]))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create rotating file handler
    file_handler = RotatingFileHandler(
        LOGGING_CONFIG["log_file"],
        maxBytes=LOGGING_CONFIG["max_bytes"],
        backupCount=LOGGING_CONFIG["backup_count"]
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_exception(logger, exception, context=""):
    """Log an exception with context"""
    if context:
        logger.error(f"{context}: {type(exception).__name__}: {str(exception)}", exc_info=True)
    else:
        logger.error(f"{type(exception).__name__}: {str(exception)}", exc_info=True)


# Initialize default logger
logger = setup_logger()
