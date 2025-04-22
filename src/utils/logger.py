import os
import sys
import logging
import datetime
from logging.handlers import RotatingFileHandler
from utils.platform import PlatformUtils

class Logger:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._logger = None
        return cls._instance
    
    def __init__(self):
        """初始化Logger"""
        if Logger._initialized:
            return
        
        self._logger = logging.getLogger('GlaryUtilities')
        self._logger.setLevel(logging.DEBUG)
        
        # 防止日志重复
        if self._logger.handlers:
            return
        
        try:
            # 创建日志目录
            log_dir = os.path.join(PlatformUtils.get_home_dir(), '.glary_utilities', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            # 日志文件路径 - 精确到秒
            current_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            log_file = os.path.join(log_dir, f'glary_utilities_{current_datetime}.log')
            
            # 创建文件处理器
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            
            # 创建控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # 设置日志格式
            formatter = logging.Formatter('%(asctime)s%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                                       '%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加处理器
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)
            
            Logger._initialized = True
            
        except Exception as e:
            print(f"Error initializing logger: {e}")
            sys.exit(1)
    
    def get_logger(self):
        """获取logger实例"""
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