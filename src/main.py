#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from typing import List, Dict

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QCoreApplication, Qt, QLibraryInfo

from src.utils.settings import Settings
from src.main_window import MainWindow
from src.config import Icon
from src.tools.base_tools import PlatformManager
from src.utils.logger import Logger, setup_logger
from src.splash_screen import SplashScreen
from src.config import ResourceManager
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
        
        # Set better looking global font
        self.setup_fonts()
        
        # Initialize resource manager
        ResourceManager.initialize()
        
        # Set up logger
        setup_logger()

    def setup_fonts(self) -> None:
        """Set global font"""
        # Create font
        if self.platform_manager.is_windows():
            # On Windows, prioritize Microsoft YaHei or Segoe UI
            font_name = "Microsoft YaHei" if "zh" in self.settings.get_setting("language", "en") else "Segoe UI"
            font = QFont(font_name, 9)
        elif self.platform_manager.is_mac():
            # On macOS, use SF Pro
            font = QFont("SF Pro", 13)
        else:
            # On Linux, use Ubuntu or Noto Sans
            font = QFont("Ubuntu", 10)
        
        # Set font properties
        font.setStyleStrategy(QFont.PreferAntialias | QFont.PreferQuality)
        
        # Apply globally
        self.app.setFont(font)

    def show_splash_screen(self) -> None:
        """Show splash screen"""
        self.splash = SplashScreen()
        self.splash.show()
        # Process events immediately to ensure splash screen and fade animation display right away
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
            
            # Show splash screen
            if not args["no_splash"]:
                self.show_splash_screen()
            
            # Create main window (but don't show yet)
            self.window = MainWindow(self.settings)
            
            # Handle translations
            if not self.handle_translations(args):
                return 0
            
            # Show window, start application
            if args["no_splash"]:
                # If not using splash screen, show main window directly
                self.window.show()
            else:
                # Wait for splash screen to complete, then show main window
                self.app.processEvents()  # Process events to ensure splash screen displays
                # Show main window when splash screen ends; if thread already ended, show immediately
                def _show_main_window():
                    if self.window is not None and not self.window.isVisible():
                        self.window.show()

                # Connect thread finished signal
                self.splash.loading_thread.finished.connect(_show_main_window)

                # If thread already ended (extreme case), call once immediately
                if not self.splash.loading_thread.isRunning():
                    _show_main_window()
                
            self.logger.info("Application started successfully")
            
            # Execute application
            result = self.app.exec_()
            return result
            
        except Exception as e:
            self.logger.exception(f"An error occurred during program execution: {e}")
            return 1
            

def main():
    """Application entry point"""
    app = GlaryUtilitiesApp(sys.argv)
    return app.run()


if __name__ == "__main__":
    sys.exit(main()) 