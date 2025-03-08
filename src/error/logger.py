# src/error/logger.py content
import logging
import os
from datetime import datetime
from typing import Optional

def get_logger(name: str, level: int = logging.INFO, 
               log_dir: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: The name of the logger
        level: The logging level
        log_dir: The directory for log files
        
    Returns:
        A configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Add file handler if log_dir is specified
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file name with timestamp
        timestamp = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(log_dir, f'{name}_{timestamp}.log')
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
    
    return logger