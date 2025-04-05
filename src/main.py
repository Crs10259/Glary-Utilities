import sys
import os
from typing import List, Dict, Any, Optional, Tuple

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication, Qt

from utils.settings_manager import Settings
from main_window import MainWindow
from components.icons import Icon
from utils.platform import PlatformUtils
from utils.logger import Logger
from utils.exception_handler import ExceptionHandler


class GlaryUtilitiesApp:
    """Main application class for Glary Utilities"""
    
    def __init__(self, argv: List[str]):
        self.argv = argv
        self.logger = Logger().get_logger()
        self.exception_handler = ExceptionHandler()
        self.settings: Optional[Settings] = None
        self.app: Optional[QApplication] = None
        self.window: Optional[MainWindow] = None
        
    def parse_arguments(self) -> Dict[str, bool]:
        """Parse command line arguments"""
        return {
            "check_translations": "--check-translations" in self.argv,
            "debug_mode": "--debug" in self.argv,
            "reset_settings": "--reset-settings" in self.argv,
            "exit_after_check": "--exit-after-check" in self.argv
        }
        
    def setup_application(self) -> None:
        """Initialize QApplication with proper settings"""
        # Enable high DPI scaling
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        # Create application
        self.app = QApplication(self.argv)
        self.app.setApplicationName("Glary Utilities")
        self.app.setOrganizationName("Glarysoft")
        
        # Set application icon
        if Icon.Icon.Exist:
            app_icon = QIcon(Icon.Icon.Path)
            if not app_icon.isNull():
                self.app.setWindowIcon(app_icon)
            else:
                self.logger.warning(f"Failed to load application icon: {Icon.Icon.Path}")
                
        # Optimize startup performance
        self.app.setStartDragDistance(20)  # Reduce drag sensitivity
        self.app.setStartDragTime(500)     # Increase drag start time
        
    def initialize_settings(self, args: Dict[str, bool]) -> None:
        """Initialize and configure settings"""
        self.settings = Settings()
        
        # Reset settings if requested
        if args["reset_settings"]:
            self.settings.reset_settings()
            self.logger.info("Settings have been reset to defaults.")
            
        # Enable debug mode if requested
        if args["debug_mode"]:
            self.settings.set_setting("debug_mode", True)
            self.logger.info("Debug mode enabled")
    
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
            
            # Initialize settings
            self.initialize_settings(args)
            
            # Create main window
            self.window = MainWindow(self.settings)
            
            # Handle translations
            if not self.handle_translations(args):
                self.exception_handler.uninstall()
                return 0
                
            # Show window and start application
            self.window.show()
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