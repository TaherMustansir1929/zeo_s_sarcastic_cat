import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(file_path: str):
    """Initialize and configure the logger."""
    logger = logging.getLogger(file_path[:-4])
    logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure rotating file handler
    log_file = os.path.join(log_dir, file_path)
    handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )

    # Set formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add handler to logger if it doesn't already have one
    if not logger.handlers:
        logger.addHandler(handler)

    return logger

def log_entry(message, level='info', file_path="sarcasm.log"):
    """Log a message with the specified level.

    Args:
        message (str): The message to log
        level (str): The log level ('debug', 'info', 'warning', 'error', 'critical')
    """
    logger = setup_logger(file_path)
    
    log_levels = {
        'debug': logger.debug,
        'info': logger.info,
        'warning': logger.warning,
        'error': logger.error,
        'critical': logger.critical
    }
    
    log_func = log_levels.get(level.lower(), logger.info)
    log_func(message)