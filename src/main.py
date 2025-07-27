#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from typing import List, Dict

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QCoreApplication, Qt, QLibraryInfo

from utils.settings import Settings
from main_window import MainWindow
from config import Icon
from tools.base_tools import PlatformManager
from utils.logger import Logger, setup_logger
from splash_screen import SplashScreen
from config import ResourceManager
import logging

class GlaryUtilitiesApp:
    """Main application class for Glary Utilities"""
    
    def __init__(self, argv: List[str]):
        self.argv = argv
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("GlaryUtilities")
        self.platform_manager = PlatformManager()
        self.settings = None
        self.app = None
        self.window = None
        self.splash = None
        
    def parse_arguments(self) -> Dict[str, bool]:
        """Parse command line arguments"""
        return {
            "check_translations": "--check-translations" in self.argv,
            "debug_mode": "--debug" in self.argv,
            "reset_settings": "--reset-settings" in self.argv,
            "exit_after_check": "--exit-after-check" in self.argv,
            "no_splash": "--no-splash" in self.argv
        }
        
    def setup_application(self) -> None:
        """Initialize QApplication with proper settings"""
        # Enable high DPI scaling
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Create application
        self.app = QApplication(self.argv)
        self.app.setApplicationName("Glary Utilities")
        self.app.setOrganizationName("Glarysoft")
        
        # Initialize settings
        self.settings = Settings()
        
        # 设置更好看的全局字体
        self.setup_fonts()
        
        # Initialize resource manager
        ResourceManager.initialize()
        
        # Set up logger
        setup_logger()

    def setup_fonts(self) -> None:
        """设置全局字体"""
        # 创建字体
        if self.platform_manager.is_windows():
            # Windows系统上优先使用微软雅黑或Segoe UI
            font_name = "Microsoft YaHei" if "zh" in self.settings.get_setting("language", "en") else "Segoe UI"
            font = QFont(font_name, 9)
        elif self.platform_manager.is_mac():
            # macOS上使用SF Pro
            font = QFont("SF Pro", 13)
        else:
            # Linux上使用Ubuntu或Noto Sans
            font = QFont("Ubuntu", 10)
        
        # 设置字体特性
        font.setStyleStrategy(QFont.PreferAntialias | QFont.PreferQuality)
        
        # 应用到全局
        self.app.setFont(font)

    def show_splash_screen(self) -> None:
        """显示启动画面"""
        self.splash = SplashScreen()
        self.splash.show()
        # 立即处理一次事件循环，确保启动画面和渐变动画立刻显示
        self.app.processEvents()
        
    def handle_translations(self, args: Dict[str, bool]) -> bool:
        """Handle translation checking
        
        Returns:
            bool: True if application should continue, False if it should exit
        """
        if not args["check_translations"]:
            return True
            
        self.logger.info("Checking for missing translations...")
        self.window.check_all_translations()
        self.logger.info("Translation check completed")
        
        # Exit if only checking translations
        if args["exit_after_check"]:
            self.logger.info("Exiting after check")
            return False
            
        return True
    
    def run(self) -> int:
        """Run the application
        
        Returns:
            int: Exit code
        """
        
        try:
            # Parse command line arguments
            args = self.parse_arguments()
            
            # Setup application
            self.setup_application()
            
            # 显示启动画面
            if not args["no_splash"]:
                self.show_splash_screen()
            
            # 创建主窗口（但暂不显示）
            self.window = MainWindow(self.settings)
            
            # Handle translations
            if not self.handle_translations(args):
                return 0
            
            # 显示窗口，启动应用程序
            if args["no_splash"]:
                # 如果不使用启动画面，直接显示主窗口
                self.window.show()
            else:
                # 等待启动画面完成后，再显示主窗口
                self.app.processEvents()  # 处理事件以确保启动画面显示
                # 当启动画面结束后显示主窗口；若线程早已结束则立即显示
                def _show_main_window():
                    if self.window is not None and not self.window.isVisible():
                        self.window.show()

                # 连接线程结束信号
                self.splash.loading_thread.finished.connect(_show_main_window)

                # 如果线程已经提前结束（极端情况下），立即调用一次
                if not self.splash.loading_thread.isRunning():
                    _show_main_window()
                
            self.logger.info("Application started successfully")
            
            # Execute application
            result = self.app.exec_()
            return result
            
        except Exception as e:
            self.logger.exception(f"An error occurred during program execution: {e}")
            return 1
            

def main() -> int:
    """Application entry point"""
    app = GlaryUtilitiesApp(sys.argv)
    return app.run()


if __name__ == "__main__":
    sys.exit(main()) 