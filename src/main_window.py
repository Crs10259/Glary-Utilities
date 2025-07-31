import os
import sys
import platform
import subprocess
import time
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                          QLabel, QToolButton, QPushButton, QAction, QMenu, 
                          QSplitter, QToolBar, QStatusBar, QFrame, QSizePolicy, 
                          QStackedWidget, QLineEdit, QDialog, QDialogButtonBox, 
                          QTabWidget, QGridLayout, QSpacerItem, QScrollArea, 
                          QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
                          QGraphicsDropShadowEffect, QMenuBar, QApplication, QColorDialog,
                          QTextBrowser)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPainter, QPainterPath
from PyQt5.QtCore import (Qt, QSize, QPoint, QPropertyAnimation, 
                        QParallelAnimationGroup, QSequentialAnimationGroup,
                        QEasingCurve, pyqtSignal, QTimer, QAbstractAnimation, QThread,
                        QRect, QEvent, QObject)
from utils.logger import Logger
from tools.base_tools import PlatformManager

from components.base_component import BaseComponent
from components.dashboard import DashboardWidget
from components.system_cleaner import SystemCleanerWidget
from components.disk_check import DiskCheckWidget
from components.boot_repair import BootToolsWidget
from components.virus_scan import VirusScanWidget
from components.system_repair import SystemRepairWidget
from components.dism_tool import DismToolWidget
from components.network_reset import NetworkResetWidget
from components.system_info import SystemInfoWidget
from components.settings import SettingsWidget
from config import Icon
from config import App

class MainWindow(QMainWindow):
    """Main application window"""
    
    # Language change signal
    language_changed = pyqtSignal(str)
    page_changed = pyqtSignal(str)
    
    def __init__(self, settings):
        """Initialize main window
        
        Args:
            settings: Settings manager instance
        """
        super().__init__()
        
        # Configure logging
        self.logger = Logger().get_logger()

        # Save settings instance
        self.settings = settings
        
        # Platform manager
        self.platform_manager = PlatformManager()
        
        # Set properties
        self.dragging = False
        self.drag_position = None
        self.current_page = "Dashboard"
        
        # Initialize dictionary
        self.page_buttons = {}
        
        # Set window basic properties
        self.setWindowTitle("Glary Utilities")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)
        
        # Set window properties based on platform
        if self.platform_manager.is_linux():
            # Linux: Use system native title bar
            self.setWindowFlags(Qt.Window)
            self.setAttribute(Qt.WA_TranslucentBackground, False)
            self.setFocusPolicy(Qt.StrongFocus)
        else:
            # Windows/macOS: Use custom borderless window
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setFocusPolicy(Qt.StrongFocus)
        
        # Initialize UI
        self.initUI()
        
        # Apply theme
        self.apply_theme()
        
        # Set window icon
        self.apply_window_icon()
        
        # Initialize page to Dashboard
        self.set_active_page("Dashboard")
        
        # Global event filter
        self.installEventFilter(self)
        
        # Language change signal
        self.language_changed.connect(self.change_language)
        
        # Validate translations - find missing keys
        missing_translations = self.settings.validate_translations(raise_error=False)
        if missing_translations:
            self.logger.warning("Found missing translations!")
            for language, sections in missing_translations.items():
                self.logger.warning(f"\nLanguage: {language}")
                for section, keys in sections.items():
                    self.logger.warning(f"  Section: {section}")
                    for key in keys:
                        self.logger.warning(f"    Missing: {key}")

    def initUI(self):
        """Initialize user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Only set custom title bar on non-Linux platforms
        if not self.platform_manager.is_linux():
            self.setup_title_bar()
            main_layout.addWidget(self.title_bar)
        
        # Create content area
        self.setup_content_area()
        main_layout.addWidget(self.content_widget)
        
        # Set status bar
        self.setup_status_bar()
        
        # Set tooltips
        self.setup_tooltips()
        
    def setup_title_bar(self):
        """Set custom title bar"""
        # Create title bar
        self.title_bar = QFrame(self)
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(0)
        
        # Set title bar style
        self.title_bar.setStyleSheet("""
            #titleBar {
                background-color: #2b2b2b;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            
            QLabel {
                background-color: transparent;
                color: #ffffff;
                font-weight: bold;
            }
            
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
            
            #closeButton:hover {
                background-color: #e81123;
                color: white;
            }
        """)
        
        # Add application icon
        app_icon = QLabel()
        app_icon.setPixmap(QPixmap(Icon.Icon.Path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        app_icon.setStyleSheet("background-color: transparent;")
        app_icon.setToolTip(self.get_translation("click_for_about", "Click for About"))
        # Make the icon clickable
        app_icon.mousePressEvent = lambda event: self.show_about_dialog()
        title_layout.addWidget(app_icon)
        
        # Add title text
        self.title_label = QLabel("Glary Utilities")
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white; background-color: transparent; margin-left: 5px;")
        title_layout.addWidget(self.title_label)
        
        # Add stretch item to push control buttons to the right
        title_layout.addStretch(1)
        
        # Window control buttons (minimize, maximize, close)
        # Minimize button
        self.minimize_button = QPushButton()
        self.minimize_button.setIcon(QIcon(Icon.Minimize.Path))
        self.minimize_button.setIconSize(QSize(16, 16))
        self.minimize_button.setFixedSize(34, 34)
        self.minimize_button.setToolTip("最小化")
        self.minimize_button.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.minimize_button)
        
        # Maximize/restore button
        self.maximize_button = QPushButton()
        self.maximize_button.setIcon(QIcon(Icon.Maximize.Path))
        self.maximize_button.setIconSize(QSize(16, 16))
        self.maximize_button.setFixedSize(34, 34)
        self.maximize_button.setToolTip("最大化")
        self.maximize_button.clicked.connect(self.toggle_maximize)
        title_layout.addWidget(self.maximize_button)
        
        # Close button
        self.close_button = QPushButton()
        self.close_button.setObjectName("closeButton")
        self.close_button.setIcon(QIcon(Icon.Close.Path))
        self.close_button.setIconSize(QSize(16, 16))
        self.close_button.setFixedSize(34, 34)
        self.close_button.setToolTip("Close")
        self.close_button.clicked.connect(self.close)
        title_layout.addWidget(self.close_button)
        
        # Allow dragging window through title bar
        self.draggable = True
        
        # Set mouse event handling for title bar
        self.title_bar.mousePressEvent = self.title_bar_mouse_press_event
        self.title_bar.mouseMoveEvent = self.title_bar_mouse_move_event
        self.title_bar.mouseReleaseEvent = self.title_bar_mouse_release_event
        
        # Linux specific optimization: ensure title bar can receive mouse events
        if self.platform_manager.is_linux():
            # Only set these properties in non-Wayland environments
            if 'WAYLAND_DISPLAY' not in os.environ:
                self.title_bar.setAttribute(Qt.WA_TransparentForMouseEvents, False)
                self.title_bar.setFocusPolicy(Qt.NoFocus)
                # Set title bar as draggable area
                self.title_bar.setProperty("draggable", True)
        
        return self.title_bar

    def toggle_maximize(self):
        """Toggle window maximize/restore state"""
        if self.isMaximized():
            self.showNormal()
            self.maximize_button.setToolTip("Maximize")
            self.maximize_button.setIcon(QIcon(Icon.Maximize.Path))
        else:
            self.showMaximized()
            self.maximize_button.setToolTip("Restore")
            self.maximize_button.setIcon(QIcon(Icon.Restore.Path))
    
    def title_bar_mouse_press_event(self, event):
        """Title bar mouse press event"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            # Only activate window in non-Wayland environments
            if 'WAYLAND_DISPLAY' not in os.environ:
                self.activateWindow()
                self.raise_()
    
    def title_bar_mouse_move_event(self, event):
        """Title bar mouse move event"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            # Get screen geometry information
            screen_geometry = self.screen().availableGeometry()
            new_pos = event.globalPos() - self.drag_position
            
            # Limit window to screen range
            new_pos.setX(max(0, min(new_pos.x(), screen_geometry.width() - self.width())))
            new_pos.setY(max(0, min(new_pos.y(), screen_geometry.height() - self.height())))
            self.move(new_pos)
            event.accept()
        else:
            # If not dragging, check if dragging should start
            if event.buttons() == Qt.LeftButton and not self.dragging:
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
    
    def title_bar_mouse_release_event(self, event):
        """Title bar mouse release event"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    
    # Event handling for window dragging and resizing - optimize Linux compatibility
    def mousePressEvent(self, event):
        """Handle mouse press event - only handle window dragging on non-Linux platforms"""
        if not self.platform_manager.is_linux():
            if event.button() == Qt.LeftButton:
                # Check if clicked on title bar
                if hasattr(self, 'title_bar') and self.title_bar.geometry().contains(event.pos()):
                    self.dragging = True
                    self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                    # Only activate window in non-Wayland environments
                    if 'WAYLAND_DISPLAY' not in os.environ:
                        self.activateWindow()
                        self.raise_()
                    event.accept()
                # Allow dragging through window edges (works on all platforms)
                else:
                    edge_margin = 5
                    if (event.pos().x() <= edge_margin or
                        event.pos().x() >= self.width() - edge_margin or
                        event.pos().y() <= edge_margin or
                        event.pos().y() >= self.height() - edge_margin):
                        self.dragging = True
                        self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                        # Only activate window in non-Wayland environments
                        if 'WAYLAND_DISPLAY' not in os.environ:
                            self.activateWindow()
                            self.raise_()
                        event.accept()
                    else:
                        super().mousePressEvent(event)
            else:
                super().mousePressEvent(event)
        else:
            # Use system title bar on Linux, no custom drag handling needed
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move event - only handle window dragging on non-Linux platforms"""
        if not self.platform_manager.is_linux():
            if self.dragging and event.buttons() == Qt.LeftButton:
                new_pos = event.globalPos() - self.drag_position
                self.move(new_pos)
                event.accept()
            else:
                super().mouseMoveEvent(event)
        else:
            # Use system title bar on Linux, no custom drag handling needed
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release event - only handle window dragging on non-Linux platforms"""
        if not self.platform_manager.is_linux():
            if event.button() == Qt.LeftButton:
                self.dragging = False
                event.accept()
            else:
                super().mouseReleaseEvent(event)
        else:
            # Use system title bar on Linux, no custom drag handling needed
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handle mouse double click event - only handle maximize on non-Linux platforms"""
        if not self.platform_manager.is_linux():
            if hasattr(self, 'title_bar') and self.title_bar.geometry().contains(event.pos()):
                self.toggle_maximize()
                event.accept()
            else:
                super().mouseDoubleClickEvent(event)
        else:
            # Use system title bar on Linux, no custom double click handling needed
            super().mouseDoubleClickEvent(event)
    
    def create_animated_action(self, icon, text, callback):
        """Create toolbar action with animation effect"""
        action = QAction(icon, text, self)
        action.triggered.connect(callback)
        
        # Get the QToolButton corresponding to this action
        action.button = None
        
        # Find the button in the next event loop
        QTimer.singleShot(0, lambda: self.find_action_button(action))
        
        return action
    
    def setup_sidebar(self):
        """Set sidebar"""
        # Create sidebar container
        sidebar_container = QWidget()
        sidebar_container.setObjectName("sidebar_container")
        sidebar_container.setMaximumWidth(220)
        sidebar_container.setMinimumWidth(220)
        sidebar_container.setStyleSheet("""
            QWidget#sidebar_container {
                background-color: #1e1e1e;
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
                border-right: 1px solid #333333;
            }
        """)
        
        # Create sidebar vertical layout
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(12, 20, 12, 15)
        sidebar_layout.setSpacing(8)
        
        # Add application logo and title
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(5, 0, 0, 15)
        
        # Add logo layout to sidebar
        sidebar_layout.addLayout(logo_layout)

        # Add category title: Common
        common_title = QLabel(self.get_translation("common_section", "Common"))
        common_title.setStyleSheet("color: #999999; font-size: 13px; margin-top: 5px; background-color: transparent; font-weight: bold; padding-left: 2px;")
        sidebar_layout.addWidget(common_title)

        # Add main function buttons
        self.dashboard_btn = self.create_sidebar_button(self.get_translation("dashboard", "Dashboard"), Icon.Dashboard.Path, "Dashboard", self.get_translation("dashboard_tooltip", "仪表盘"))
        sidebar_layout.addWidget(self.dashboard_btn)
        self.page_buttons["Dashboard"] = self.dashboard_btn
        
        self.system_cleaner_btn = self.create_sidebar_button(self.get_translation("system_cleaner", "System Cleaner"), Icon.Cleaner.Path, "System Cleaner", self.get_translation("system_cleaner_tooltip", "系统清理"))
        sidebar_layout.addWidget(self.system_cleaner_btn)
        self.page_buttons["System Cleaner"] = self.system_cleaner_btn
        
        # System Tools (previously System Repair)
        self.registry_btn = self.create_sidebar_button(self.get_translation("system_repair", "System Tools"), Icon.Repair.Path, "System Tools", self.get_translation("system_repair_tooltip", "系统工具"))
        sidebar_layout.addWidget(self.registry_btn)
        self.page_buttons["System Tools"] = self.registry_btn
        
        # Disk Tools (previously Disk Check)
        self.disk_tools_btn = self.create_sidebar_button(self.get_translation("disk_check", "Disk Tools"), Icon.Disk.Path, "Disk Tools", self.get_translation("disk_check_tooltip", "磁盘工具"))
        sidebar_layout.addWidget(self.disk_tools_btn)
        self.page_buttons["Disk Tools"] = self.disk_tools_btn
        
        # Boot Tools (previously Boot Repair)
        self.startup_btn = self.create_sidebar_button(self.get_translation("boot_repair", "Boot Tools"), Icon.Boot.Path, "Boot Tools", self.get_translation("boot_repair_tooltip", "启动工具"))
        sidebar_layout.addWidget(self.startup_btn)
        self.page_buttons["Boot Tools"] = self.startup_btn
        
        # Security Tools (previously Virus Scan)
        self.uninstaller_btn = self.create_sidebar_button(self.get_translation("virus_scan", "Security Tools"), Icon.Virus.Path, "Security Tools", self.get_translation("virus_scan_tooltip", "安全工具"))
        sidebar_layout.addWidget(self.uninstaller_btn)
        self.page_buttons["Security Tools"] = self.uninstaller_btn
        
        # Add category title: Security
        security_title = QLabel(self.get_translation("security_section", "Security"))
        security_title.setStyleSheet("color: #999999; font-size: 13px; margin-top: 15px; background-color: transparent; font-weight: bold; padding-left: 12px;")
        sidebar_layout.addWidget(security_title)
        
        # Network Tools (previously Network Reset)
        self.privacy_btn = self.create_sidebar_button(self.get_translation("network_reset", "Network Tools"), Icon.Privacy.Path, "Network Tools", self.get_translation("network_reset_tooltip", "网络工具"))
        sidebar_layout.addWidget(self.privacy_btn)
        self.page_buttons["Network Tools"] = self.privacy_btn
        
        # Add category title: Advanced
        advanced_title = QLabel(self.get_translation("advanced_section", "Advanced"))
        advanced_title.setStyleSheet("color: #999999; font-size: 13px; margin-top: 15px; background-color: transparent; font-weight: bold; padding-left: 12px;")
        sidebar_layout.addWidget(advanced_title)
        
        # Use Icon.Dism.Path for DISM Tool
        self.driver_btn = self.create_sidebar_button(self.get_translation("dism_tool", "DISM Tool"), Icon.Dism.Path, "DISM Tool", self.get_translation("dism_tool_tooltip", "DISM工具"))
        sidebar_layout.addWidget(self.driver_btn)
        self.page_buttons["DISM Tool"] = self.driver_btn
        
        # Use Icon.SystemInfo.Path for System Information
        self.optimizer_btn = self.create_sidebar_button(self.get_translation("system_information", "System Information"), Icon.SystemInfo.Path, "System Information", self.get_translation("system_information_tooltip", "系统信息"))
        sidebar_layout.addWidget(self.optimizer_btn)
        self.page_buttons["System Information"] = self.optimizer_btn
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #333333; max-height: 1px;")
        sidebar_layout.addWidget(separator)
        sidebar_layout.addSpacing(8)

        # Add settings button
        self.settings_btn = self.create_sidebar_button(self.get_translation("settings", "Settings"), Icon.Settings.Path, "Settings", self.get_translation("settings_tooltip", "设置"))
        sidebar_layout.addWidget(self.settings_btn)
        self.page_buttons["Settings"] = self.settings_btn

        # Add stretch space
        sidebar_layout.addStretch()

        # Add version information
        version_label = QLabel(f"{self.get_translation('version', 'Version')} {App.version}")
        version_label.setStyleSheet("color: #666666; font-size: 11px; margin-top: 8px; background-color: transparent; text-align: center;")
        version_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(version_label)
        
        # Return sidebar container
        return sidebar_container

    def create_sidebar_button(self, name, icon, page_name, tooltip=None):
        """Create sidebar button"""
        try:
            # Get theme color
            accent_color = self.settings.get_setting("accent_color", "#3498db")
        
            # Create button
            button = QPushButton(name)
            button.setCheckable(True)
            button.setObjectName(f"sidebar_btn_{page_name}")
            button.setProperty("page", page_name)  # Use custom property to mark associated page
        
            # Set icon
            if icon:
                button.setIcon(QIcon(icon))
        
            # Set tooltip
            if tooltip:
                button.setToolTip(tooltip)
            
            # Set icon size - increase to 28x28
            icon_size = QSize(28, 28)
            button.setIconSize(icon_size)
            
            # Save original icon size
            button._original_icon_size = icon_size
        
        except Exception as e:
            self.logger.error(f"Error creating sidebar button: {e}")
            # Create button without icon
            button = QPushButton(name)
            button.setCheckable(True)
            button.setObjectName(f"sidebar_btn_{page_name}")
            button.setProperty("page", page_name)
            if tooltip:
                button.setToolTip(tooltip)
        
        # Set basic style, add transition animation and left colored indicator bar
        base_style = f"""
            QPushButton {{
                text-align: left;
                padding-left: 15px;
                border: none;
                border-radius: 10px;
                color: #cccccc;
                font-size: 14px;
                background-color: transparent;
                margin: 6px 5px;
                border-left: 3px solid transparent;
                font-weight: normal;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.15);
                color: #ffffff;
                border-left: 3px solid {accent_color}80;
            }}
            QPushButton:checked {{
                background-color: rgba(52, 152, 219, 0.25);
                color: #ffffff;
                font-weight: bold;
                border-left: 3px solid {accent_color};
            }}
            QPushButton:pressed {{
                background-color: rgba(52, 152, 219, 0.15);
            }}
        """
        button.setStyleSheet(base_style)
        
        # Set button height and minimum width, adjust height to 52px
        button.setMinimumHeight(52)
        button.setMaximumHeight(52)
        button.setMinimumWidth(170)
        
        # Check if animations are enabled
        enable_animations = self.settings.get_setting("enable_animations", True)
        if isinstance(enable_animations, str):
            enable_animations = enable_animations.lower() in ('true', 'yes', '1', 'on')
        elif isinstance(enable_animations, int):
            enable_animations = enable_animations != 0
        else:
            enable_animations = bool(enable_animations)
        
        # If animations are enabled, set hover and press icon size change effect
        if enable_animations:
            # Create animation group
            self.hover_animation = QParallelAnimationGroup()
            self.press_animation = QParallelAnimationGroup()
            
            # When mouse hovers, increase icon size
            # Check Linux performance optimization settings
            optimize_linux = self.settings.get_setting("optimize_linux_performance", True)
            if isinstance(optimize_linux, str):
                optimize_linux = optimize_linux.lower() in ('true', 'yes', '1', 'on')
            elif isinstance(optimize_linux, int):
                optimize_linux = optimize_linux != 0
            else:
                optimize_linux = bool(optimize_linux)
                
            # Disable complex icon animations on Linux to improve performance
            if not (self.platform_manager.is_linux() and optimize_linux):
                def on_hover(hovered):
                    if hovered:
                        target_size = QSize(32, 32)  # Hover icon size increase
                        anim = QPropertyAnimation(button, b"iconSize")
                        anim.setDuration(150)
                        anim.setStartValue(button.iconSize())
                        anim.setEndValue(target_size)
                        anim.start()
                    else:
                        # Restore original size
                        anim = QPropertyAnimation(button, b"iconSize")
                        anim.setDuration(150)
                        anim.setStartValue(button.iconSize())
                        anim.setEndValue(button._original_icon_size)
                        anim.start()
                
                # When pressed, shrink icon
                def on_press(pressed):
                    if pressed:
                        target_size = QSize(26, 26)  # Pressed icon size decrease
                        anim = QPropertyAnimation(button, b"iconSize")
                        anim.setDuration(100)
                        anim.setStartValue(button.iconSize())
                        anim.setEndValue(target_size)
                        anim.start()
                
                # Connect events
                button.installEventFilter(self)
                button.enterEvent = lambda e: on_hover(True)
                button.leaveEvent = lambda e: on_hover(False)
                button.pressed.connect(lambda: on_press(True))
                button.released.connect(lambda: on_hover(True))  # Release to hover state
        
        # Connect button click event
        button.clicked.connect(lambda: self.set_active_page(page_name))
        
        return button

    def setup_content_area(self):
        """Set content area"""
        # Create content widget
        self.content_widget = QWidget()
        self.content_widget.setObjectName("content_widget")
        
        # Create content layout
        content_layout = QHBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Add sidebar
        self.sidebar = self.setup_sidebar()
        content_layout.addWidget(self.sidebar)
        
        # Add content area
        self.setup_content_area_internal()
        content_layout.addWidget(self.content_area)
        
        # Set content widget style
        if not self.platform_manager.is_linux():
            # Set rounded corners and shadow on non-Linux platforms
            self.content_widget.setStyleSheet("""
                QWidget#content_widget {
                    background-color: #252525;
                    border-radius: 10px;
                }
            """)
            
            # Set shadow effect for window
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 180))
            shadow.setOffset(0, 0)
            self.content_widget.setGraphicsEffect(shadow)
        else:
            # Use simple background color on Linux
            self.content_widget.setStyleSheet("""
                QWidget#content_widget {
                    background-color: #252525;
                }
            """)

    def setup_content_area_internal(self):
        """Set internal content area"""
        # Create stacked widget for page switching
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("content_area")
        
        # Create each page component
        self.dashboard_widget = DashboardWidget()
        self.system_cleaner_widget = SystemCleanerWidget()
        self.disk_check_widget = DiskCheckWidget()
        self.boot_tools_widget = BootToolsWidget()
        self.virus_scan_widget = VirusScanWidget()
        self.system_repair_widget = SystemRepairWidget()
        self.dism_tool_widget = DismToolWidget()
        self.network_reset_widget = NetworkResetWidget()
        self.system_info_widget = SystemInfoWidget()
        self.settings_widget = SettingsWidget(self.settings)
        
        # Add pages to stacked widget
        self.content_area.addWidget(self.dashboard_widget)
        self.content_area.addWidget(self.system_cleaner_widget)
        self.content_area.addWidget(self.disk_check_widget)
        self.content_area.addWidget(self.boot_tools_widget)
        self.content_area.addWidget(self.virus_scan_widget)
        self.content_area.addWidget(self.system_repair_widget)
        self.content_area.addWidget(self.dism_tool_widget)
        self.content_area.addWidget(self.network_reset_widget)
        self.content_area.addWidget(self.system_info_widget)
        self.content_area.addWidget(self.settings_widget)
        
        # Set content area style
        self.content_area.setStyleSheet("""
            QStackedWidget#content_area {
                background-color: transparent;
                border: none;
            }
        """)
    
    def apply_theme(self):
        """Apply current theme"""
        theme_name = self.settings.get_setting("theme", "dark")
        
        # Load theme data
        theme_data = self.settings.load_theme(theme_name)
        
        if theme_data and "colors" in theme_data:
            bg_color = theme_data["colors"].get("bg_color", "#2d2d2d")
            text_color = theme_data["colors"].get("text_color", "#dcdcdc")
            accent_color = theme_data["colors"].get("accent_color", "#007acc")
            border_color = theme_data["colors"].get("border_color", "#444444")
            
            # Update checkbox style
            checkbox_style = f"""
                QCheckBox {{
                    color: {text_color};
                    background-color: transparent;
                    spacing: 5px;
                    padding: 5px;
                    font-size: 13px;
                    min-height: 20px;
                    margin: 2px 0;
                }}
                
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 2px solid {accent_color};
                    border-radius: 3px;
                    background-color: {bg_color};
                }}
                
                QCheckBox::indicator:unchecked {{
                    background-color: {bg_color};
                }}
                
                QCheckBox::indicator:checked {{
                    background-color: {accent_color};
                    border: 2px solid {accent_color};
                    image: url(resources/icons/check.png);  /* 可选：添加勾选图标 */
                }}
                
                QCheckBox::indicator:unchecked:hover {{
                    border-color: {self.lighten_color(accent_color, 20)};
                    background-color: {self.lighten_color(bg_color, 10)};
                }}
                
                QCheckBox::indicator:checked:hover {{
                    background-color: {self.lighten_color(accent_color, 10)};
                    border-color: {self.lighten_color(accent_color, 10)};
                }}
                
                QCheckBox:disabled {{
                    color: {self.lighten_color(text_color, -30)};
                }}
                
                QCheckBox::indicator:disabled {{
                    border-color: {self.lighten_color(accent_color, -30)};
                    background-color: {self.lighten_color(bg_color, -10)};
                }}
            """
            
            # Add checkbox style to main style sheet
            self.setStyleSheet(self.styleSheet() + checkbox_style)
            
        # Update component theme
        self.update_component_themes()
            
    def update_component_themes(self):
        """Update the theme for all components"""
        # Check if content_area exists
        try:
            # Find all BaseComponent widgets and refresh their themes
            for i in range(self.content_area.count()):
                widget = self.content_area.widget(i)
                if widget:
                    # Recursively update all child components
                    self.refresh_component_theme(widget)
        except AttributeError:
            pass
                
    def refresh_component_theme(self, widget):
        """Recursively refresh theme for a widget and its children"""
        # Check if it is a special component type, which needs to call the specific theme method
        component_name = widget.__class__.__name__
        
        # Use the apply_current_theme method of the specific component first
        if component_name in ["BootRepairWidget", "VirusScanWidget"]:
            try:
                if hasattr(widget, 'apply_current_theme') and callable(widget.apply_current_theme):
                    widget.apply_current_theme()
                    return  # The theme method of the specific component has been applied, no need to continue
            except Exception as e:
                self.logger.error(f"Error applying custom theme to {component_name}: {str(e)}")
        
        # For other standard components, apply the generic apply_theme method
        try:
            if hasattr(widget, 'apply_theme') and callable(widget.apply_theme):
                widget.apply_theme()
        except Exception as e:
            self.logger.error(f"Error applying theme to widget: {str(e)}")
            
        # Process children
        for child in widget.findChildren(QWidget):
            self.refresh_component_theme(child)

    def apply_window_icon(self):
        """Set window icon"""
        try:
            # Use icon file in root directory
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons", "icon.png")
            if not os.path.exists(icon_path):
                self.logger.warning(f"Warning: Window icon file does not exist: {icon_path}")
                return
                
            self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            self.logger.error(f"Error setting window icon: {str(e)}")
    
    def set_active_page(self, page_name):
        """Set active page
        
        Args:
            page_name (str): Page name
        """
        # Page name to index mapping
        page_indices = {
            "Dashboard": 0,
            "System Cleaner": 1,
            "Disk Tools": 2,
            "Boot Tools": 3,
            "Security Tools": 4,
            "System Tools": 5,
            "Network Tools": 6,
            "DISM Tool": 7,
            "System Information": 8,
            "Settings": 9
        }
        
        if page_name in page_indices:
            index = page_indices[page_name]
            self.content_area.setCurrentIndex(index)
            self.current_page = page_name
            
            # Update active button state
            self._update_active_button(page_name)
            
            # Update window title
            self.setWindowTitle(f"Glary Utilities - {page_name}")
            
            # Log page switch
            self.logger.debug(f"Switched to page: {page_name}")
        else:
            self.logger.warning(f"Unknown page: {page_name}")
    
    def _update_page_content(self, page_name):
        """Update content area based on page name"""
        self.logger.info(f"Switched to page: {page_name}")
        
        # Get localized display name for the page
        page_display_name = self.settings.get_translation("general", page_name.lower().replace(' ', '_'))
        
        # Update window title and toolbar title
        self.setWindowTitle(f"Glary Utilities - {page_display_name}")
        if hasattr(self, 'title_label'):
            self.title_label.setText(f"Glary Utilities - {page_display_name}")
        
        # Update active button state
        self._update_active_button(page_name)
        
        # Clear search if search box exists
        if hasattr(self, 'search_box'):
            self.search_box.clear()
            
        try:
            # If page index exists, directly switch to that page
            if page_name in self.page_indices:
                self.content_area.setCurrentIndex(self.page_indices[page_name])
                
                # Get current page widget
                current_widget = self.content_area.currentWidget()
                
                # After switching to this page, let the page widget automatically update data
                if hasattr(current_widget, 'update_data') and callable(getattr(current_widget, 'update_data')):
                    current_widget.update_data()
                    
                # Save current page name
                self.current_page = page_name
                
                # Emit page change signal
                self.page_changed.emit(page_name)
            else:
                # If page doesn't exist, show an error message
                self.logger.warning(f"Index not found for page '{page_name}'")
                self.show_status_message(f"Page '{page_name}' does not exist", 3000)
                
        except Exception as e:
            # Handle exception cases
            self.logger.error(f"Error switching to page '{page_name}': {e}")
            error_widget = QLabel(f"Error loading page: {e}")
            error_widget.setStyleSheet("color: red;")
            error_widget.setAlignment(Qt.AlignCenter)
            
            # Create a temporary page to display error
            temp_page = QWidget()
            temp_layout = QVBoxLayout(temp_page)
            temp_layout.addWidget(error_widget)
            
            # Add error page to content area
            error_index = self.content_area.addWidget(temp_page)
            self.content_area.setCurrentIndex(error_index)
    
    def change_language(self, language):
        """Change application language
        
        Args:
            language: Language code or name to set
        """
        try:
            # Close current opened help dialog (if any)
            for dialog in self.findChildren(QDialog):
                if dialog.objectName() == "HelpDialog":
                    dialog.reject()
                    
            # Update language setting and refresh translation cache
            self.settings.set_language(language)
            self.settings.sync()
            
            # Directly update UI text, instead of triggering signal
            self._update_ui_texts_directly(language)
            
            # Show a message indicating language was changed
            language_display = "English" if language == "en" else "中文"
            self.show_status_message(f"Language changed to {language_display}")
            
        except Exception as e:
            self.logger.error(f"Error changing language: {str(e)}")

    def _update_ui_texts_directly(self, language):
        """Directly update UI text, avoid recursion
        
        Args:
            language: Current language code
        """
        try:
            # Get current active page
            active_page = self.current_page
            
            # Directly get translation from translation dictionary
            translations = self.settings.translations.get(language, {})
            main_window_translations = translations.get("main_window", {})
            general_translations = translations.get("general", {})
            
            # Update button text
            for button_name, button in self.page_buttons.items():
                translation_key = button_name.lower().replace(' ', '_')
                translated_name = main_window_translations.get(translation_key) or general_translations.get(translation_key) or button_name
                button.setText(translated_name)
            
            # Update title
            page_translation_key = active_page.lower().replace(' ', '_')
            page_display_name = main_window_translations.get(page_translation_key) or general_translations.get(page_translation_key) or active_page
            
            window_title = f"Glary Utilities - {page_display_name}"
            self.setWindowTitle(window_title)
            if hasattr(self, 'title_label'):
                self.title_label.setText(window_title)
            
            # Update language for all components
            for i in range(self.content_area.count()):
                widget = self.content_area.widget(i)
                if hasattr(widget, 'refresh_language') and callable(widget.refresh_language):
                    widget.refresh_language()
            
            # Update status bar
            if hasattr(self, 'status_label'):
                ready_text = general_translations.get("ready", "Ready")
                self.status_label.setText(ready_text)
                
        except Exception as e:
            self.logger.error(f"Error updating UI texts: {str(e)}")
    
    def update_ui_texts(self):
        """Update all UI text elements with current language translations"""
        # Loop through all defined page buttons and update their text
        for button_name, button in self.page_buttons.items():
            translated_name = self.settings.get_translation("general", button_name.lower().replace(' ', '_'))
            button.setText(translated_name)
    
    def update_ui_language(self):
        """Update UI language"""
        # Get current active page and update related UI
        active_page = self.current_page
        page_display_name = self.settings.get_translation("general", active_page.lower().replace(' ', '_'))
        
        # Update button text
        for button_name, button in self.page_buttons.items():
            translated_name = self.settings.get_translation("general", button_name.lower().replace(' ', '_'))
            button.setText(translated_name)
        
        # Update title
        self.setWindowTitle(f"Glary Utilities - {page_display_name}")
        if hasattr(self, 'title_label'):
            self.title_label.setText(f"Glary Utilities - {page_display_name}")
        
        # Refresh all components that support language updates
        for widget_name in dir(self):
            widget = getattr(self, widget_name)
            if hasattr(widget, 'update_language') and callable(getattr(widget, 'update_language')):
                widget.update_language()
    
    def refresh_all_components(self):
        """Refresh all components"""
        # Loop through all content pages and update them
        for i in range(self.content_area.count()):
            widget = self.content_area.widget(i)
            # (Fix infinite recursion problem) If the component has a refresh_language method, call it
            if hasattr(widget, 'refresh_language') and callable(getattr(widget, 'refresh_language')):
                QTimer.singleShot(i * 10, lambda w=widget: w.refresh_language())  # Delay execution to avoid UI freeze
                
        # (Fix infinite recursion problem) Update all sidebar buttons - avoid using get_translation
        for button in self.findChildren(QPushButton):
            if hasattr(button, 'property') and button.property("page"):
                page_name = button.property("page")
                # Directly get translation from main_window section, not from general section
                translation_key = page_name.lower().replace(' ', '_')
                try:
                    # Try to get translation text from main_window section
                    lang = self.settings.get_setting("language", "en")
                    translated_text = None
                    
                    # Get language code
                    language_map = {
                        "en": "en", "english": "en", "English": "en",
                        "zh": "zh", "中文": "zh", "chinese": "zh", "Chinese": "zh"
                    }
                    lang_code = language_map.get(lang.lower(), lang)
                    
                    # Directly get translation text from translation dictionary
                    if lang_code in self.settings.translations:
                        translations = self.settings.translations[lang_code]
                        if "main_window" in translations and translation_key in translations["main_window"]:
                            translated_text = translations["main_window"][translation_key]
                        elif "en" in self.settings.translations and "main_window" in self.settings.translations["en"] and translation_key in self.settings.translations["en"]["main_window"]:
                            translated_text = self.settings.translations["en"]["main_window"][translation_key]
                    
                    # If translation is found, set button text
                    if translated_text:
                        button.setText(translated_text)
                except Exception as e:
                    # If error occurs, use original page name
                    self.logger.error(f"Error updating button text: {e}")
                    # Keep original text, do not change
                
        # Update toolbar
        self.update_ui_texts()
                
        # Force redraw of entire UI
        self.update()
        
        # Process any waiting events, ensure UI is updated immediately
        QApplication.processEvents()
    
    def check_all_translations(self):
        """Check if all necessary translations exist"""
        # Fix recursion problem: use the new settings.validate_translations method
        # instead of manually calling get_translation to check each key
        try:
            missing = self.settings.validate_translations()
            
            if missing:
                current_lang = self.settings.get_setting("language", "en")
                if current_lang in missing:
                    missing_in_current = missing[current_lang]
                    # Record missing translations in current language
                    for section, keys in missing_in_current.items():
                        for key in keys:
                            self.logger.warning(f"Missing translation for '{section}.{key}' in language '{current_lang}'")
            return True
        except Exception as e:
            self.logger.error(f"Error checking translations: {e}")
            return False

    def apply_transparency(self):
        """Apply window transparency from settings"""
        try:
            # Get transparency value from settings (100 means fully opaque)
            transparency = int(self.settings.get_setting("window_transparency", 100))
            
            # Ensure value is within valid range
            transparency = max(70, min(100, transparency))
            
            # Only apply transparency if less than 100%
            if transparency < 100:
                try:
                    # Set window transparency
                    self.setWindowOpacity(transparency / 100.0)
                    self.logger.info(f"Applied window transparency: {transparency}%")
                except Exception as e:
                    # Log the error but continue
                    self.logger.error(f"Error applying window transparency: {str(e)}")
                    # Reset to fully opaque
                    self.settings.set_setting("window_transparency", 100)
            else:
                # Fully opaque
                self.setWindowOpacity(1.0)
        except Exception as e:
            self.logger.error(f"Error in apply_transparency: {str(e)}")
            # Reset to default
            self.setWindowOpacity(1.0)
    
    def show_status_message(self, message, timeout=2000):
        """Show status bar message"""
        # Record message in console
        self.logger.debug(f"Status message: {message}")
        
        # Update status bar label
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)
            
            # Set temporary style to highlight
            self.status_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
            
            # Use timer to restore normal style
            QTimer.singleShot(timeout, lambda: self.status_label.setStyleSheet("color: #bbbbbb; font-size: 12px;"))

    def setup_status_bar(self):
        """Create bottom status bar"""
        status_bar = QFrame()
        status_bar.setObjectName("status_bar")
        status_bar.setFixedHeight(30)
        status_bar.setStyleSheet("""
            QFrame#status_bar {
                background-color: #2d2d2d;
                border-top: 1px solid #444444;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        
        # Status bar layout
        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        
        # Status information label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #bbbbbb; font-size: 12px; background-color: transparent;")
        layout.addWidget(self.status_label)
        
        # Add stretch space
        layout.addStretch(1)
        
        return status_bar
        

    def _update_active_button(self, page_name):
        """Update the status of the active page button in the sidebar
        
        Args:
            page_name: Name of the active page
        """
        # Loop through all sidebar buttons and update their status
        for button in self.findChildren(QPushButton):
            if hasattr(button, 'property') and button.property("page"):
                # Check if the button corresponds to the current active page
                is_active = button.property("page") == page_name
                
                # Set selected state
                button.setChecked(is_active)
                
                # Update style to reflect selected state
                if is_active:
                    button.setProperty("active", "true")
                else:
                    button.setProperty("active", "false")
                
                # Force re-apply style sheet
                button.style().unpolish(button)
                button.style().polish(button)
                button.update()

    def clear_layout(self, layout):
        """Clear all widgets in the layout
        
        Args:
            layout: Layout object to clear
        """
        if layout is None:
            return
            
        # Remove all items in the layout
        while layout.count():
            item = layout.takeAt(0)
            
            # If item is a widget, delete it
            if item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()
            # If item is a layout, recursively clear it
            elif item.layout():
                self.clear_layout(item.layout())

    def get_translation(self, key, default=None):
        """Get translation for UI text using the main window section
        
        Args:
            key: Translation key
            default: Default text if translation not found
            
        Returns:
            Translated text
        """
        return self.settings.get_translation("main_window", key, default)

    def show_about_dialog(self):
        """Show about dialog (as a page within the main window, not a popup dialog)"""
        
        # Create inline about page (if it doesn't exist)
        if not hasattr(self, 'about_page'):
            # Create about page
            self.about_page = QWidget()
            self.about_page.setObjectName("About")
            
            # Create page layout
            about_layout = QVBoxLayout(self.about_page)
            about_layout.setContentsMargins(20, 20, 20, 20)
            about_layout.setSpacing(20)
            
            # Title
            title = QLabel(self.get_translation("about_title", "About"))
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
            about_layout.addWidget(title)
            
            # Application icon and title
            icon_title_layout = QHBoxLayout()
            
            # Add application icon
            app_icon_label = QLabel()
            app_icon_label.setFixedSize(80, 80)
            if os.path.exists(Icon.Icon.Path):
                app_icon = QPixmap(Icon.Icon.Path)
                app_icon_label.setPixmap(app_icon.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            app_icon_label.setStyleSheet("background-color: transparent;")
            
            # Add title and version layout
            title_version_layout = QVBoxLayout()
            title_version_layout.setSpacing(10)
            
            app_title = QLabel("Glary Utilities")
            app_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
            
            version_label = QLabel(f"{self.get_translation('version', 'Version')}: {App.version}")
            version_label.setStyleSheet("font-size: 16px; color: #cccccc;")
            
            title_version_layout.addWidget(app_title)
            title_version_layout.addWidget(version_label)
            title_version_layout.addStretch()
            
            icon_title_layout.addWidget(app_icon_label)
            icon_title_layout.addLayout(title_version_layout)
            icon_title_layout.addStretch()
            
            about_layout.addLayout(icon_title_layout)
            
            # Add separator
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setStyleSheet("background-color: #444444; max-height: 1px;")
            about_layout.addWidget(line)
            
            # Add content area
            content_widget = QWidget()
            content_widget.setStyleSheet("background-color: #2a2a2a; border-radius: 8px;")
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(20, 20, 20, 20)
            content_layout.setSpacing(15)
            
            # Apply description
            description_label = QLabel(self.get_translation("app_description", "A powerful system optimization tool."))
            description_label.setWordWrap(True)
            description_label.setStyleSheet("font-size: 16px; color: #e0e0e0;")
            content_layout.addWidget(description_label)
            
            # Add main features
            features_label = QLabel(self.get_translation("features", "Main Features"))
            features_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; margin-top: 10px;")
            content_layout.addWidget(features_label)
            
            # Feature list
            features_layout = QVBoxLayout()
            features_layout.setContentsMargins(15, 0, 0, 0)
            features_layout.setSpacing(8)
            
            feature_items = [
                self.get_translation("feature_clean", "System cleaning"),
                self.get_translation("feature_repair", "System repair"),
                self.get_translation("feature_security", "Security protection"),
                self.get_translation("feature_disk", "Disk optimization")
            ]
            
            for feature in feature_items:
                feature_label = QLabel(f"• {feature}")
                feature_label.setStyleSheet("font-size: 15px; color: #e0e0e0;")
                features_layout.addWidget(feature_label)
            
            content_layout.addLayout(features_layout)
            
            # Add system requirements
            sys_req_label = QLabel(self.get_translation("system_requirements", "System Requirements"))
            sys_req_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; margin-top: 15px;")
            content_layout.addWidget(sys_req_label)
            
            sys_req_details = QLabel(self.get_translation("requirements_details", "Windows 10/11, 4GB RAM, 200MB disk space"))
            sys_req_details.setWordWrap(True)
            sys_req_details.setStyleSheet("font-size: 15px; color: #e0e0e0; margin-left: 15px;")
            content_layout.addWidget(sys_req_details)
            
            # Add separator
            inner_line = QFrame()
            inner_line.setFrameShape(QFrame.HLine)
            inner_line.setStyleSheet("background-color: #444444; max-height: 1px; margin-top: 10px;")
            content_layout.addWidget(inner_line)
            
            # Add copyright information
            copyright_label = QLabel(f"© 2025 Glarysoft Ltd. All rights reserved.")
            copyright_label.setStyleSheet("font-size: 14px; color: #999999; margin-top: 10px;")
            content_layout.addWidget(copyright_label)
            
            # Add developer information
            dev_label = QLabel(self.get_translation("developed_by", "Developed by Chen Runsen"))
            dev_label.setStyleSheet("font-size: 14px; color: #999999;")
            content_layout.addWidget(dev_label)
            
            # Add website link
            website_label = QLabel("<a href='https://www.chenrunsen.com' style='color: #5b9bd5;'>www.chenrunsen.com</a>")
            website_label.setOpenExternalLinks(True)
            website_label.setStyleSheet("font-size: 14px; color: #5b9bd5;")
            content_layout.addWidget(website_label)
            
            # Add content area to main layout
            about_layout.addWidget(content_widget)
            
            # Button layout
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            # Add help button
            help_button = QPushButton(self.get_translation("help_button", "Help"))
            help_button.setFixedSize(120, 36)
            help_button.setStyleSheet("""
                QPushButton {
                    background-color: #555555;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 5px 15px;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
                QPushButton:pressed {
                    background-color: #444444;
                }
            """)
            help_button.clicked.connect(self.show_help_dialog)
            button_layout.addWidget(help_button)
            
            # Add button layout to main layout
            about_layout.addLayout(button_layout)
            
            # Add stretch space
            about_layout.addStretch()
            
            # Add about page to content area
            self.content_area.addWidget(self.about_page)
            
            # Update page index dictionary
            self.page_indices["About"] = self.content_area.count() - 1
            
            # Create sidebar button (if needed)
            if "About" not in self.page_buttons:
                # Add about button to sidebar
                about_btn = self.create_sidebar_button(
                    self.get_translation("about_title", "About"),
                    Icon.About.Path, 
                    "About",
                    self.get_translation("about_tooltip", "About Glary Utilities")
                )
                # Hide in sidebar for now, only show when needed
                about_btn.hide()
                self.page_buttons["About"] = about_btn
        
        # Switch to about page
        self.set_active_page("About")

    def lighten_color(self, color, amount=0):
        """Lighten or darken color
        
        Args:
            color: Hex color code
            amount: Change amount, positive number lightens, negative number darkens (range: -100 to 100)
                
        Returns:
            New hex color code
        """
        try:
            # Remove hash and convert to RGB
            c = color.lstrip('#')
            c = tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
            
            # Adjust each color channel
            r = int(max(0, min(255, c[0] + (amount * 2.55))))
            g = int(max(0, min(255, c[1] + (amount * 2.55))))
            b = int(max(0, min(255, c[2] + (amount * 2.55))))
            
            # Convert back to hex format
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception as e:
            self.logger.error(f"Color adjustment error: {str(e)}")
            return color  # Return original color if error occurs

    def show_help_dialog(self):
        """Show help content (as a page within the main window, not a popup dialog)"""
        
        # Create inline help page (if it doesn't exist)
        if not hasattr(self, 'help_page'):
            # Create help page
            self.help_page = QWidget()
            self.help_page.setObjectName("Help")
            
            # Create page layout
            help_layout = QVBoxLayout(self.help_page)
            help_layout.setContentsMargins(20, 20, 20, 20)
            help_layout.setSpacing(15)
            
            # Title
            title = QLabel(self.get_translation("help_title", "Help Documentation"))
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
            help_layout.addWidget(title)
            
            # Description
            description = QLabel(self.get_translation("help_description", "Find answers and learn how to use Glary Utilities effectively"))
            description.setStyleSheet("font-size: 14px; color: #a0a0a0;")
            help_layout.addWidget(description)
            
            # Help content
            help_text = QTextBrowser()
            help_text.setOpenExternalLinks(True)
            help_text.setStyleSheet("""
                QTextBrowser {
                    background-color: #252525;
                    color: #e0e0e0;
                    border: 1px solid #3a3a3a;
                    border-radius: 5px;
                    padding: 15px;
                    font-size: 14px;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #2d2d2d;
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #555555;
                    min-height: 20px;
                    border-radius: 5px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)
            
            # Use translation items to build help content HTML
            t = lambda key, default="": self.get_translation(key, default)
            
            help_html = f"""
            <h2>{t('help_content_title', 'Glary Utilities Help Documentation')}</h2>
            <p>{t('help_content_welcome', 'Welcome to Glary Utilities')}</p>
            
            <h3>{t('help_dashboard_title', 'Dashboard')}</h3>
            <p>{t('help_dashboard_desc', 'The Dashboard provides an overview of your system status and quick access to common tasks.')}</p>
            
            <h3>{t('help_cleaner_title', 'System Cleaner')}</h3>
            <p>{t('help_cleaner_desc', 'The System Cleaner tool helps you:')}</p>
            <ul>
                <li>{t('help_cleaner_item1', 'Clean temporary files')}</li>
                <li>{t('help_cleaner_item2', 'Free up disk space')}</li>
                <li>{t('help_cleaner_item3', 'Improve system performance')}</li>
            </ul>
            <p>{t('help_cleaner_usage', 'How to use: Click Scan to analyze your system, then select items to clean and click Clean button.')}</p>
            
            <h3>{t('help_repair_title', 'System Repair')}</h3>
            <p>{t('help_repair_desc', 'System Repair can fix common Windows issues:')}</p>
            <ul>
                <li>{t('help_repair_item1', 'Registry errors')}</li>
                <li>{t('help_repair_item2', 'System settings problems')}</li>
                <li>{t('help_repair_item3', 'Windows service issues')}</li>
            </ul>
            <p>{t('help_repair_usage', 'How to use: Select issues to scan for, review results, then apply repairs.')}</p>
            
            <h3>{t('help_disk_title', 'Disk Check')}</h3>
            <p>{t('help_disk_desc', 'The Disk Check tool can:')}</p>
            <ul>
                <li>{t('help_disk_item1', 'Detect disk errors')}</li>
                <li>{t('help_disk_item2', 'Find bad sectors')}</li>
                <li>{t('help_disk_item3', 'Optimize disk performance')}</li>
            </ul>
            <p>{t('help_disk_usage', 'How to use: Select a disk, choose check options, and click Check Disk button.')}</p>
            
            <h3>{t('help_boot_title', 'Boot Repair')}</h3>
            <p>{t('help_boot_desc', 'The Boot Repair tool can:')}</p>
            <ul>
                <li>{t('help_boot_item1', 'Fix startup problems')}</li>
                <li>{t('help_boot_item2', 'Restore boot records')}</li>
                <li>{t('help_boot_item3', 'Repair boot configuration')}</li>
            </ul>
            <p>{t('help_boot_note', 'Note: Administrator privileges are required for this tool.')}</p>
            
            <h3>{t('help_virus_title', 'Virus Scan')}</h3>
            <p>{t('help_virus_desc', 'The Virus Scan tool helps you:')}</p>
            <ul>
                <li>{t('help_virus_item1', 'Detect malware')}</li>
                <li>{t('help_virus_item2', 'Remove harmful files')}</li>
                <li>{t('help_virus_item3', 'Protect your system')}</li>
            </ul>
            <p>{t('help_virus_usage', 'How to use: Select areas to scan, click Scan button, and review results.')}</p>
            
            <h3>{t('help_network_title', 'Network Reset')}</h3>
            <p>{t('help_network_desc', 'Network Reset helps with connection issues:')}</p>
            <ul>
                <li>{t('help_network_item1', 'Reset DNS cache')}</li>
                <li>{t('help_network_item2', 'Reset Winsock catalog')}</li>
                <li>{t('help_network_item3', 'Reset TCP/IP stack')}</li>
                <li>{t('help_network_item4', 'Fix network adapters')}</li>
            </ul>
            <p>{t('help_network_usage', 'How to use: Select operations to perform and click Reset button.')}</p>
            
            <h3>{t('help_dism_title', 'DISM Tool')}</h3>
            <p>{t('help_dism_desc', 'The DISM tool can:')}</p>
            <ul>
                <li>{t('help_dism_item1', 'Repair Windows system image')}</li>
                <li>{t('help_dism_item2', 'Scan system health')}</li>
                <li>{t('help_dism_item3', 'Clean up component store')}</li>
            </ul>
            <p>{t('help_dism_usage', 'How to use: Select DISM operation and click Execute button.')}</p>
            
            <h3>{t('help_sysinfo_title', 'System Information')}</h3>
            <p>{t('help_sysinfo_desc', 'System Information provides details about:')}</p>
            <ul>
                <li>{t('help_sysinfo_item1', 'CPU and memory specifications')}</li>
                <li>{t('help_sysinfo_item2', 'Operating system details')}</li>
                <li>{t('help_sysinfo_item3', 'Network configuration')}</li>
                <li>{t('help_sysinfo_item4', 'Graphics hardware')}</li>
            </ul>
            <p>{t('help_sysinfo_usage', 'How to use: Switch between tabs to view different categories of information.')}</p>
            
            <h3>{t('help_settings_title', 'Settings')}</h3>
            <p>{t('help_settings_desc', 'In Settings you can:')}</p>
            <ul>
                <li>{t('help_settings_item1', 'Change language')}</li>
                <li>{t('help_settings_item2', 'Adjust theme and appearance')}</li>
                <li>{t('help_settings_item3', 'Configure cleaning options')}</li>
                <li>{t('help_settings_item4', 'Set application preferences')}</li>
            </ul>
            
            <h3>{t('help_contact_title', 'Contact & Support')}</h3>
            <p>{t('help_contact_desc', 'For additional help, visit our website or contact support.')}</p>
            """
            
            help_text.setHtml(help_html)
            help_layout.addWidget(help_text)
            
            # Add help page to content area
            self.content_area.addWidget(self.help_page)
            
            # Update page index dictionary
            self.page_indices["Help"] = self.content_area.count() - 1
            
            # Create sidebar button (if needed)
            if "Help" not in self.page_buttons:
                # Add help button to sidebar
                help_btn = self.create_sidebar_button(
                    self.get_translation("help_title", "Help"),
                    Icon.Help.Path, 
                    "Help",
                    self.get_translation("help_tooltip", "View help documentation")
                )
                # Hide in sidebar for now, only show when needed
                help_btn.hide()
                self.page_buttons["Help"] = help_btn
        
        # Switch to help page
        self.set_active_page("Help")
        
    def setup_tooltips(self):
        """Set tooltips for all main components, providing inline help"""
        # Dashboard
        if hasattr(self, 'dashboard_btn'):
            self.dashboard_btn.setToolTip(self.get_translation("dashboard_tooltip", "View system overview and quick access to common tasks"))
            
        # System Cleaner
        if hasattr(self, 'system_cleaner_btn'):
            self.system_cleaner_btn.setToolTip(self.get_translation("system_cleaner_tooltip", "Clean temporary files and free up disk space"))
            
        # System Repair
        if hasattr(self, 'registry_btn'):
            self.registry_btn.setToolTip(self.get_translation("system_repair_tooltip", "Fix common Windows issues and optimize system settings"))
            
        # Disk Check
        if hasattr(self, 'disk_tools_btn'):
            self.disk_tools_btn.setToolTip(self.get_translation("disk_check_tooltip", "Check disk for errors and optimize performance"))
            
        # Boot Repair
        if hasattr(self, 'startup_btn'):
            self.startup_btn.setToolTip(self.get_translation("boot_repair_tooltip", "Fix startup issues and repair boot configuration"))
            
        # Virus Scan
        if hasattr(self, 'uninstaller_btn'):
            self.uninstaller_btn.setToolTip(self.get_translation("virus_scan_tooltip", "Scan for malware and protect your system"))
            
        # Network Reset
        if hasattr(self, 'privacy_btn'):
            self.privacy_btn.setToolTip(self.get_translation("network_reset_tooltip", "Fix network issues and reset connections"))
            
        # DISM Tool
        if hasattr(self, 'driver_btn'):
            self.driver_btn.setToolTip(self.get_translation("dism_tool_tooltip", "Repair Windows system image and check system health"))
            
        # System Information
        if hasattr(self, 'optimizer_btn'):
            self.optimizer_btn.setToolTip(self.get_translation("system_information_tooltip", "View detailed information about your hardware and software"))
            
        # Settings
        if hasattr(self, 'settings_btn'):
            self.settings_btn.setToolTip(self.get_translation("settings_tooltip", "Configure application settings and preferences"))

    def closeEvent(self, event):
        """Ensure all background threads/timers are terminated when closing window to prevent process hanging"""
        try:
            # Stop all QTimer
            for timer in self.findChildren(QTimer):
                try:
                    timer.stop()
                except Exception:
                    pass

            # Terminate all QThread
            for thread in self.findChildren(QThread):
                try:
                    thread.requestInterruption()
                    thread.quit()
                    thread.wait(1000)
                except Exception:
                    pass
        except Exception as e:
            self.logger.error(f"Error while shutting down threads: {e}")

        # Continue with default handling, finally exit application
        super().closeEvent(event)
 