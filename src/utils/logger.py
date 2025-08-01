import os
import logging
from datetime import datetime
from src.config import Path

class Logger:
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        if self._logger is None:
            self._logger = logging.getLogger('GlaryUtilities')
            self._logger.setLevel(logging.DEBUG)
            
            # Create log directory
            log_dir = Path.LOG_DIR
            os.makedirs(log_dir, exist_ok=True)
            
            # Create log filename (using current date)
            log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
            
            # File handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Set format
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)
    
    def get_logger(self):
        return self._logger
    
    def debug(self, message):
        """Log debug level message"""
        self._logger.debug(message)
    
    def info(self, message):
        """Log info level message"""
        self._logger.info(message)
    
    def warning(self, message):
        """Log warning level message"""
        self._logger.warning(message)
    
    def error(self, message):
        """Log error level message"""
        self._logger.error(message)
    
    def critical(self, message):
        """Log critical error level message"""
        self._logger.critical(message)

def setup_logger():
    """Initialize and configure global logger"""
    logger_instance = Logger()
    return logger_instance.get_logger()