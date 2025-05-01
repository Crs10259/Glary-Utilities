import os
import logging
from datetime import datetime
from config import Path

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
            
            # 创建日志目录
            log_dir = Path.LOG_DIR
            os.makedirs(log_dir, exist_ok=True)
            
            # 创建日志文件名（使用当前日期）
            log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
            
            # 文件处理器
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 设置格式
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加处理器
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)
    
    def get_logger(self):
        return self._logger
    
    def debug(self, message):
        """记录调试级别日志"""
        self._logger.debug(message)
    
    def info(self, message):
        """记录信息级别日志"""
        self._logger.info(message)
    
    def warning(self, message):
        """记录警告级别日志"""
        self._logger.warning(message)
    
    def error(self, message):
        """记录错误级别日志"""
        self._logger.error(message)
    
    def critical(self, message):
        """记录严重错误级别日志"""
        self._logger.critical(message)

def setup_logger():
    """初始化并配置全局日志记录器"""
    logger_instance = Logger()
    return logger_instance.get_logger()