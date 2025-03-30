import os
import sys
import psutil
import platform
import shutil
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QProgressBar, QGridLayout)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
from components.base_component import BaseComponent
from components.icons import Icon

class InfoTile(QFrame):
    """Custom styled info tile widget"""
    def __init__(self, title, value, icon_path=None, parent=None):
        super().__init__(parent)
        self.setObjectName("infoTile")
        self.setStyleSheet("""
            #infoTile {
                background-color: #2d2d2d;
                border-radius: 8px;
                border: none;
            }
        """)
        self.setMinimumHeight(120)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #a0a0a0; font-size: 14px;")
        
        # Value label
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #e0e0e0; font-size: 24px; font-weight: bold;")
        
        # Add to layout
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.value_label)
        
        # Add icon if provided and exists
        if icon_path and os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if not icon.isNull():
                self.icon_label = QLabel()
                self.icon_label.setPixmap(icon.pixmap(QSize(32, 32)))
                self.layout.addWidget(self.icon_label, 0, Qt.AlignRight)
    
    def update_value(self, value):
        """Update the displayed value"""
        self.value_label.setText(value)

class ActionTile(QFrame):
    """Custom styled action tile widget"""
    def __init__(self, title, description, icon_path=None, parent=None):
        super().__init__(parent)
        self.setObjectName("actionTile")
        self.setStyleSheet("""
            #actionTile {
                background-color: #2d2d2d;
                border-radius: 8px;
                border: none;
            }
            #actionTile:hover {
                background-color: #353535;
                border: none;
            }
        """)
        self.setMinimumHeight(100)
        self.setCursor(Qt.PointingHandCursor)
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Add icon if provided and exists
        if icon_path and os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.icon_label = QLabel()
                    pixmap = icon.pixmap(QSize(32, 32))
                    if not pixmap.isNull():
                        self.icon_label.setPixmap(pixmap)
                        self.layout.addWidget(self.icon_label)
                    else:
                        print(f"警告: 无法加载图标 {icon_path} 的像素图")
                else:
                    print(f"警告: 无法加载图标 {icon_path}")
            except Exception as e:
                print(f"加载图标时出错 {icon_path}: {str(e)}")
        
        # Text container
        self.text_container = QVBoxLayout()
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #e0e0e0; font-size: 16px; font-weight: bold;")
        
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        
        self.text_container.addWidget(self.title_label)
        self.text_container.addWidget(self.desc_label)
        
        self.layout.addLayout(self.text_container)
        
        if Icon.Arrow.Exist:
            try:
                arrow_icon = QIcon(Icon.Arrow.Path)
                self.arrow_label = QLabel()
                arrow_pixmap = arrow_icon.pixmap(QSize(16, 16))
                if not arrow_pixmap.isNull():
                    self.arrow_label.setPixmap(arrow_pixmap)
                    self.layout.addWidget(self.arrow_label, 0, Qt.AlignRight)

            except Exception as e:
                print(f"加载箭头图标时出错: {str(e)}")

class DashboardWidget(BaseComponent):
    def __init__(self, settings, parent=None):
        # Initialize properties
        self.update_timer = None
        
        # Call parent constructor
        super().__init__(settings, parent)
        
        # Check for missing translations (development mode only)
        missing_keys = self.check_all_translations()
        if missing_keys:
            print(f"Warning: Missing translations in DashboardWidget:")
            for language, keys in missing_keys.items():
                print(f"  Language: {language}, Missing keys: {', '.join(keys)}")
        
        # Setup timer for stats update
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_system_info)
        self.update_timer.start(2000) 
    
    def get_translation(self, key, default=None):
        """Override get_translation to use the correct section name"""
        return self.settings.get_translation("dashboard", key, default)
    
    def setup_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Dashboard title
        self.title = QLabel(self.get_translation("system_status"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        self.main_layout.addWidget(self.title)
        
        # System stats section
        self.create_system_stats_section()
        
        # Quick access section
        self.create_quick_access_section()
        
        # Add spacer
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
    
    def create_system_stats_section(self):
        # Stats container
        self.stats_frame = QFrame()
        self.stats_layout = QGridLayout(self.stats_frame)
        self.stats_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_layout.setSpacing(15)
        
        # CPU usage tile
        self.cpu_tile = InfoTile(
            self.get_translation("cpu_usage"), 
            "0%", 
            Icon.CPU.Path
        )
        self.stats_layout.addWidget(self.cpu_tile, 0, 0)
        
        # Memory usage tile
        self.memory_tile = InfoTile(
            self.get_translation("memory_usage"), 
            "0%", 
            Icon.Memory.Path
        )
        self.stats_layout.addWidget(self.memory_tile, 0, 1)
        
        # Disk usage tile
        self.disk_tile = InfoTile(
            self.get_translation("disk_usage"), 
            "0%", 
            Icon.Disk.Path
        )
        self.stats_layout.addWidget(self.disk_tile, 1, 0)
        
        # Temperature tile
        self.temp_tile = InfoTile(
            self.get_translation("system_temperature"), 
            "N/A", 
            Icon.Temperature.Path
        )
        self.stats_layout.addWidget(self.temp_tile, 1, 1)
        
        # Add stats frame to main layout
        self.main_layout.addWidget(self.stats_frame)
    
    def create_quick_access_section(self):
        # Quick access title
        self.quick_title = QLabel(self.get_translation("quick_access"))
        self.quick_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e0e0e0;")
        self.main_layout.addWidget(self.quick_title)
        
        # Quick access container
        self.quick_frame = QFrame()
        self.quick_layout = QGridLayout(self.quick_frame)
        self.quick_layout.setContentsMargins(0, 0, 0, 0)
        self.quick_layout.setSpacing(15)
        
        # 检查图片是否存在，不存在则使用默认图标
        if Icon.Optimize.Exist:
            optimize_icon = Icon.Optimize.Path
        else:
            optimize_icon = None
            print(f"警告: 找不到图标 {optimize_icon}")
        
        # Optimize system tile
        self.optimize_tile = ActionTile(
            self.get_translation("optimize_system"),
            "Speed up your system by fixing issues",
            optimize_icon
        )
        self.quick_layout.addWidget(self.optimize_tile, 0, 0)
        
        # 检查图片是否存在
        if Icon.Clean.Exist:
            clean_icon = Icon.Clean.Path
        else:
            clean_icon = None
            print(f"警告: 找不到图标 {clean_icon}")
        
        # Clean junk tile
        self.clean_tile = ActionTile(
            self.get_translation("clean_junk"),
            "Free up disk space by removing unnecessary files",
            clean_icon
        )
        self.quick_layout.addWidget(self.clean_tile, 0, 1)
        
        # 检查图片是否存在
        if Icon.Virus.Exist:
            virus_icon = Icon.Virus.Path
        else:
            virus_icon = None
            print(f"警告: 找不到图标 {virus_icon}")
        
        # Virus scan tile
        self.virus_tile = ActionTile(
            self.get_translation("scan_system"),
            "Scan your system for viruses and malware",
            virus_icon
        )
        self.quick_layout.addWidget(self.virus_tile, 1, 0)
        
        # 检查图片是否存在
        if Icon.Info.Exist:
            info_icon = Icon.Info.Path
        else:
            info_icon = None
            print(f"警告: 找不到图标 {info_icon}")
        
        # Get System info tile
        self.info_tile = ActionTile(
            self.get_translation("get_system_info"),
            "Get system information",
            info_icon
        )
        self.quick_layout.addWidget(self.info_tile, 1, 1)
        
        # Add quick access frame to main layout
        self.main_layout.addWidget(self.quick_frame)
        
        # Connect action tiles to their respective functions
        self.optimize_tile.mousePressEvent = lambda event: self.navigate_to_page(3)  # System Repair
        self.clean_tile.mousePressEvent = lambda event: self.navigate_to_page(1)     # System Cleaner
        self.virus_tile.mousePressEvent = lambda event: self.navigate_to_page(8)     # Virus Scan
        self.info_tile.mousePressEvent = lambda event: self.navigate_to_page(0)     # Dashboard
    
    def update_system_info(self):
        """Update system statistics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent()
        self.cpu_tile.update_value(f"{cpu_percent}%")
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        self.memory_tile.update_value(f"{memory_percent}%")
        
        # Disk usage (system drive)
        try:
            if platform.system() == 'Windows':
                # On Windows, get usage of C: drive using shutil
                total, used, free = shutil.disk_usage('C:')
                disk_percent = (used / total) * 100
            else:
                # On Unix/Linux/Mac, get usage of root directory
                total, used, free = shutil.disk_usage('/')
                disk_percent = (used / total) * 100
            
            self.disk_tile.update_value(f"{disk_percent:.1f}%")
        except Exception as e:
            self.disk_tile.update_value("Error")
            print(f"Error getting disk usage: {e}")
        
        # Temperature (if available)
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current > 0:
                                self.temp_tile.update_value(f"{entry.current}°C")
                                return
            self.temp_tile.update_value("N/A")
        except:
            self.temp_tile.update_value("N/A")
    
    def navigate_to_page(self, page_index):
        """Navigate to a specific page in the main window"""
        # Map page indices to page names
        page_names = {
            0: "Dashboard",
            1: "System Cleaner",
            2: "GPU Information",
            3: "System Repair",
            4: "DISM Tool",
            5: "Network Reset",
            6: "Disk Check",
            7: "Boot Repair",
            8: "Virus Scan",
            9: "Settings"
        }
        
        # Find the main window to change the page
        main_window = self.window()
        if main_window and page_index in page_names:
            main_window.set_active_page(page_names[page_index])


    def refresh_language(self):
        # Update UI text elements
        self.title.setText(self.get_translation("system_status"))
        self.quick_title.setText(self.get_translation("quick_access"))
        
        # Update tiles
        self.cpu_tile.title_label.setText(self.get_translation("cpu_usage"))
        self.memory_tile.title_label.setText(self.get_translation("memory_usage"))
        self.disk_tile.title_label.setText(self.get_translation("disk_usage"))
        self.temp_tile.title_label.setText(self.get_translation("system_temperature"))
        
        # Update action tiles
        self.optimize_tile.title_label.setText(self.get_translation("optimize_system"))
        self.clean_tile.title_label.setText(self.get_translation("clean_junk"))
        self.virus_tile.title_label.setText(self.get_translation("scan_system"))
        self.info_tile.title_label.setText(self.get_translation("get_system_info"))
        
        # Add animation to highlight the change
        super().refresh_language()

    def check_all_translations(self):
        """Check if all translation keys used in this component exist
        
        Raises:
            KeyError: If any translation key is missing
        """
        # Try to get all translations used in this component
        keys = [
            "system_status", "cpu_usage", "memory_usage", "disk_usage",
            "system_temperature", "quick_access", "optimize_system", 
            "clean_junk", "scan_system", "get_system_info"
        ]
        
        for key in keys:
            # This will raise KeyError if the key doesn't exist
            self.get_translation(key, None) 