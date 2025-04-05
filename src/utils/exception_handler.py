import sys
import traceback
from utils.logger import Logger
from PyQt5.QtCore import QObject, pyqtSignal

class ResourceErrorNotifier(QObject):
    error_occurred = pyqtSignal(str, str)  # 错误类型, 错误消息
    
class SettingsError(Exception):
    """Settings related errors"""
    pass

class TranslationError(Exception):
    """Translation related errors"""
    pass

class ExceptionHandler:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExceptionHandler, cls).__new__(cls)
            cls._instance._logger = Logger().get_logger()
        return cls._instance

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        self._logger.error("Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback))

    def install(self):
        """安装全局异常处理器"""
        sys.excepthook = self.handle_exception
        self._logger.info("Global exception handler installed")

    def uninstall(self):
        """卸载全局异常处理器"""
        sys.excepthook = sys.__excepthook__
        self._logger.info("Global exception handler uninstalled")