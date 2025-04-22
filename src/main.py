#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from typing import List, Dict, Any, Optional, Tuple
import logging

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication, Qt, QLibraryInfo

from utils.settings_manager import Settings
from main_window import MainWindow
from components.icons import Icon
from utils.platform import PlatformUtils
from utils.logger import Logger, setup_logger
from utils.exception_handler import ExceptionHandler
from splash_screen import SplashScreen
from utils.resource_manager import ResourceManager


class GlaryUtilitiesApp:
    """Main application class for Glary Utilities"""
    
    def __init__(self, argv: List[str]):
        self.argv = argv
        self.logger = Logger().get_logger()
        self.exception_handler = ExceptionHandler()
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
        
        # Initialize resource manager
        ResourceManager.initialize()
        
        # Set up logger
        setup_logger()

    def show_splash_screen(self) -> None:
        """显示启动画面"""
        self.splash = SplashScreen()
        self.splash.show()
        
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
        # Install global exception handler
        self.exception_handler.install()
        
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
                self.exception_handler.uninstall()
                return 0
            
            # 显示窗口，启动应用程序
            if args["no_splash"]:
                # 如果不使用启动画面，直接显示主窗口
                self.window.show()
            else:
                # 等待启动画面完成后，再显示主窗口
                self.app.processEvents()  # 处理事件以确保启动画面显示
                # 当启动画面结束后，显示主窗口
                self.splash.loading_thread.finished.connect(lambda: self.window.show())
                
            self.logger.info("Application started successfully")
            
            # Execute application
            result = self.app.exec_()
            return result
            
        except Exception as e:
            self.logger.exception(f"An error occurred during program execution: {e}")
            return 1
            
        finally:
            # Uninstall global exception handler
            self.exception_handler.uninstall()


def main() -> int:
    """Application entry point"""
    app = GlaryUtilitiesApp(sys.argv)
    return app.run()


if __name__ == "__main__":
    sys.exit(main()) 