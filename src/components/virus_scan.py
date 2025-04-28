import os
import sys
import platform
import subprocess
import time
import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QProgressBar, QMessageBox,
                             QGroupBox, QCheckBox, QFileDialog, QListWidget,
                             QListWidgetItem, QRadioButton, QComboBox, QTableWidget,
                             QHeaderView, QTableWidgetItem, QTextBrowser, QTabWidget,
                             QLineEdit, QButtonGroup)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QDir, QDateTime
from PyQt5.QtWidgets import QApplication
from components.base_component import BaseComponent

class VirusScanThread(QThread):
    """Thread for running virus scan operations in the background"""
    update_progress = pyqtSignal(int)
    update_log = pyqtSignal(str)
    found_threat = pyqtSignal(str, str)
    finished_scan = pyqtSignal(bool, str, int)
    
    def __init__(self, scan_options, parent=None):
        super().__init__(parent)
        self.scan_options = scan_options
        self.is_running = False
        self.should_stop = False
        self.threats_found = 0
        
    def run(self):
        self.is_running = True
        self.should_stop = False
        self.threats_found = 0
        
        try:
            scan_type = self.scan_options.get('scan_type', 'quick')
            scan_targets = self.scan_options.get('scan_targets', [])
            scan_options = self.scan_options.get('options', {})
            
            self.update_log.emit(f"Starting {scan_type} scan...")
            self.update_progress.emit(0)
            
            if scan_type == "quick":
                self.quick_scan()
            elif scan_type == "full":
                self.full_scan()
            elif scan_type == "custom":
                self.custom_scan(scan_targets)
            
            if self.should_stop:
                self.update_log.emit("Scan was stopped by user.")
                self.finished_scan.emit(False, "Scan cancelled", self.threats_found)
            else:
                self.update_log.emit("Scan completed successfully.")
                self.finished_scan.emit(True, "Scan completed", self.threats_found)
                
        except Exception as e:
            self.update_log.emit(f"Error during scan: {str(e)}")
            self.finished_scan.emit(False, f"Scan failed: {str(e)}", self.threats_found)
        
        self.is_running = False
    
    def stop(self):
        """Signal the scan to stop"""
        self.should_stop = True
    
    def quick_scan(self):
        """Perform a quick scan of common locations"""
        self.update_log.emit("Performing quick scan of common locations...")
        
        # Common locations to scan
        locations = [
            os.path.join(os.environ.get('TEMP', 'C:\\Windows\\Temp')),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop'),
            os.path.join(os.environ.get('ProgramData', 'C:\\ProgramData'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
        ]
        
        total_items = len(locations)
        scanned_items = 0
        
        for location in locations:
            if self.should_stop:
                return
                
            # Update progress
            progress = int((scanned_items / total_items) * 100)
            self.update_progress.emit(progress)
            
            self.update_log.emit(f"Scanning: {location}")
            
            try:
                # Simulate scanning files in this location
                self.simulate_directory_scan(location)
            except Exception as e:
                self.update_log.emit(f"Error scanning {location}: {str(e)}")
            
            scanned_items += 1
        
        self.update_progress.emit(100)
        self.update_log.emit(f"Quick scan complete. Found {self.threats_found} potential threats.")
    
    def full_scan(self):
        """Perform a full system scan"""
        self.update_log.emit("Performing full system scan. This may take a while...")
        
        # Get drives to scan
        drives = []
        for drive_letter in range(ord('C'), ord('Z') + 1):
            drive = chr(drive_letter) + ":\\"
            if os.path.exists(drive):
                drives.append(drive)
        
        total_drives = len(drives)
        scanned_drives = 0
        
        for drive in drives:
            if self.should_stop:
                return
                
            # Update progress - we'll allocate 95% of the progress to the scanning
            progress = int((scanned_drives / total_drives) * 95)
            self.update_progress.emit(progress)
            
            self.update_log.emit(f"Scanning drive: {drive}")
            
            try:
                # Simulate scanning this drive (just first level for simulation)
                self.simulate_directory_scan(drive, depth=0)
            except Exception as e:
                self.update_log.emit(f"Error scanning {drive}: {str(e)}")
            
            scanned_drives += 1
            
            # Simulate deeper scan by sleeping
            time.sleep(2)
        
        self.update_progress.emit(100)
        self.update_log.emit(f"Full scan complete. Found {self.threats_found} potential threats.")
    
    def custom_scan(self, targets):
        """Scan specific targets selected by user"""
        if not targets:
            self.update_log.emit("No targets specified for custom scan.")
            self.update_progress.emit(100)
            return
            
        self.update_log.emit(f"Starting custom scan of {len(targets)} locations...")
        
        total_targets = len(targets)
        scanned_targets = 0
        
        for target in targets:
            if self.should_stop:
                return
                
            # Update progress
            progress = int((scanned_targets / total_targets) * 100)
            self.update_progress.emit(progress)
            
            self.update_log.emit(f"Scanning: {target}")
            
            try:
                # Check if target exists
                if os.path.exists(target):
                    # Simulate scanning
                    if os.path.isdir(target):
                        self.simulate_directory_scan(target)
                    else:
                        self.simulate_file_scan(target)
                else:
                    self.update_log.emit(f"Warning: Target does not exist: {target}")
            except Exception as e:
                self.update_log.emit(f"Error scanning {target}: {str(e)}")
            
            scanned_targets += 1
        
        self.update_progress.emit(100)
        self.update_log.emit(f"Custom scan complete. Found {self.threats_found} potential threats.")
    
    def simulate_directory_scan(self, directory, depth=1):
        """Simulate scanning a directory for threats"""
        try:
            # Check if we have permission to access the directory
            items = os.listdir(directory)
            
            # Simulate finding some files with issues (for demo purposes)
            for item in items[:10]:  # Limit to first 10 items for simulation
                if self.should_stop:
                    return
                    
                item_path = os.path.join(directory, item)
                
                # Simulate scanning the file
                if os.path.isfile(item_path):
                    self.simulate_file_scan(item_path)
                
                # If this is a directory and we're recursing, scan it too
                if os.path.isdir(item_path) and depth > 0:
                    # Only recurse for a few folders (for simulation)
                    if random.random() < 0.1:  # 10% chance to recurse for demo
                        self.simulate_directory_scan(item_path, depth - 1)
                
                # Pause briefly to simulate work
                time.sleep(0.05)
                
        except PermissionError:
            self.update_log.emit(f"Permission denied for: {directory}")
        except Exception as e:
            self.update_log.emit(f"Error scanning directory {directory}: {str(e)}")
    
    def simulate_file_scan(self, file_path):
        """Simulate scanning a single file for threats"""
        try:
            # Log that we're scanning this file
            self.update_log.emit(f"Scanning file: {os.path.basename(file_path)}")
            
            # Simulate the scan by sleeping a bit
            time.sleep(0.1)
            
            # Randomly decide if this file has a threat (for demo)
            if random.random() < 0.02:  # 2% chance to find a "threat"
                threat_type = random.choice([
                    "Potential malware", 
                    "Suspicious script", 
                    "Unwanted adware",
                    "PUP (Potentially Unwanted Program)",
                    "Suspicious behavior detected"
                ])
                
                self.threats_found += 1
                self.update_log.emit(f"⚠️ Found potential threat: {os.path.basename(file_path)}")
                self.found_threat.emit(file_path, threat_type)
        
        except PermissionError:
            self.update_log.emit(f"Permission denied for: {file_path}")
        except Exception as e:
            self.update_log.emit(f"Error scanning file {file_path}: {str(e)}")


class VirusScanWidget(BaseComponent):
    """Widget for virus scanning operations"""
    def __init__(self, parent=None):
        # 初始化属性
        self.scanner_worker = None
        self.scan_thread = None
        self.custom_scan_targets = []
        self.detected_threats = []
        self.main_window = parent
        
        # Call parent constructor
        super().__init__(parent)
        
        # Set up the UI (called by parent but we need to ensure it exists)
        if not hasattr(self, 'quick_scan_rb'):
            self.setup_ui()
        
    def get_translation(self, key, default=None):
        """获取当前组件的翻译
        
        Args:
            key: 翻译键
            default: 如果翻译不存在时的默认值
            
        Returns:
            翻译文本
        """
        try:
            # 使用BaseComponent中定义的get_translation方法
            return super().get_translation(key, default)
        except (KeyError, AttributeError) as e:
            self.logger.error(f"Translation missing in VirusScanWidget: {key}")
            
            # 返回默认值或键名
            return default if default is not None else key

    def setup_ui(self):
        """设置UI元素"""
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # 创建选项卡部件
        self.tabs = QTabWidget()
        
        # 扫描选项卡
        self.scan_tab = QWidget()
        self.setup_scan_tab(self.scan_tab)
        self.tabs.addTab(self.scan_tab, self.get_translation("scan_tab", "Scan"))
        
        # 隔离区选项卡
        self.quarantine_tab = QWidget()
        self.setup_quarantine_tab(self.quarantine_tab)
        self.tabs.addTab(self.quarantine_tab, self.get_translation("quarantine_tab", "Quarantine"))
        
        # 添加到主布局
        self.main_layout.addWidget(self.tabs)
        
        # 在初始化后特别处理单选按钮的大小和样式
        self.update_radio_buttons_size()
    
    def apply_theme(self):
        """应用主题样式到组件"""
        # 调用父类的应用主题方法，使用统一样式
        super().apply_theme()
        
        # 获取当前主题
        theme_name = self.settings.get_setting("theme", "dark")
        theme_data = self.settings.load_theme(theme_name)
        
        if theme_data and "colors" in theme_data:
            bg_color = theme_data["colors"].get("bg_color", "#2d2d2d")
            text_color = theme_data["colors"].get("text_color", "#dcdcdc")
            accent_color = theme_data["colors"].get("accent_color", "#007acc")
            border_color = theme_data["colors"].get("border_color", "#444444")
            table_bg_color = theme_data["colors"].get("table_bg_color", self.lighten_color(bg_color, -5))
            header_bg_color = theme_data["colors"].get("header_bg_color", self.lighten_color(bg_color, 10))
            disabled_bg_color = theme_data["colors"].get("disabled_bg_color", self.lighten_color(bg_color, -10))
            disabled_text_color = theme_data["colors"].get("disabled_text_color", self.lighten_color(text_color, -30))
            button_bg_color = theme_data["colors"].get("button_bg_color", self.lighten_color(bg_color, 10))
            button_hover_bg_color = theme_data["colors"].get("button_hover_bg_color", self.lighten_color(bg_color, 15))
            button_pressed_bg_color = theme_data["colors"].get("button_pressed_bg_color", self.lighten_color(bg_color, 5))
            input_bg_color = theme_data["colors"].get("input_bg_color", self.lighten_color(bg_color, -5))

            # 更新组件样式 - 更全面的样式覆盖
            self.setStyleSheet(f"""
                QWidget {{ background-color: transparent; color: {text_color}; }}
                QTabWidget::pane {{ border: 1px solid {border_color}; border-radius: 4px; background-color: {bg_color}; }}
                QTabBar::tab {{ background-color: {header_bg_color}; color: {text_color}; padding: 8px 16px; border-top-left-radius: 4px; border-top-right-radius: 4px; }}
                QTabBar::tab:selected {{ background-color: {bg_color}; border-bottom: none; }}
                QGroupBox {{ background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 4px; margin-top: 1em; padding-top: 10px; }}
                QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {text_color}; }}
                QTextEdit, QTextBrowser {{ background-color: {table_bg_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 4px; }}
                QTableWidget {{ background-color: {table_bg_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 4px; gridline-color: {border_color}; selection-background-color: {accent_color}40; }}
                QTableWidget::item {{ padding: 4px; color: {text_color}; }}
                QTableWidget::item:selected {{ background-color: {accent_color}80; color: #ffffff; }}
                QHeaderView::section {{ background-color: {header_bg_color}; color: {text_color}; padding: 4px; border: 1px solid {border_color}; }}
                QProgressBar {{ border: 1px solid {border_color}; border-radius: 4px; background-color: {table_bg_color}; text-align: center; color: {text_color}; }}
                QProgressBar::chunk {{ background-color: {accent_color}; width: 10px; border-radius: 3px; margin: 1px; }}
                QPushButton {{ background-color: {button_bg_color}; color: {text_color}; border: 1px solid #555; border-radius: 4px; padding: 6px 12px; }}
                QPushButton:hover {{ background-color: {button_hover_bg_color}; }}
                QPushButton:pressed {{ background-color: {button_pressed_bg_color}; }}
                QPushButton:disabled {{ background-color: {disabled_bg_color}; color: {disabled_text_color}; }}
                QComboBox, QLineEdit {{ background-color: {input_bg_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 4px; padding: 4px; }}
                
                QCheckBox, QRadioButton {{ color: {text_color}; background-color: transparent; spacing: 5px; }}
                
                QCheckBox::indicator {{ width: 16px; height: 16px; border: 2px solid {accent_color}; border-radius: 3px; background-color: {bg_color}; }}
                QCheckBox::indicator:unchecked {{ background-color: {bg_color}; }}
                QCheckBox::indicator:unchecked:hover {{ border-color: {self.lighten_color(accent_color, 20)}; background-color: {self.lighten_color(bg_color, 10)}; }}
                QCheckBox::indicator:checked:hover {{ background-color: {self.lighten_color(accent_color, 10)}; }}
                
                QRadioButton::indicator {{ width: 16px; height: 16px; border: 2px solid {accent_color}; border-radius: 9px; background-color: {bg_color}; }}
                QRadioButton::indicator:unchecked {{ background-color: {bg_color}; }}
                QRadioButton::indicator:checked {{ background-color: {bg_color}; border: 4px solid {accent_color}; }}
                QRadioButton::indicator:unchecked:hover {{ border-color: {self.lighten_color(accent_color, 20)}; background-color: {self.lighten_color(bg_color, 10)}; }}
                QRadioButton::indicator:checked:hover {{ border-color: {self.lighten_color(accent_color, 10)}; }}
                
                QLabel {{ color: {text_color}; background-color: transparent; }}
                
                QComboBox::drop-down {{ 
                    subcontrol-origin: padding; 
                    subcontrol-position: center right; 
                    width: 20px; 
                    border-left: 1px solid {border_color}; 
                }}
            """)
        
            if hasattr(self, 'clean_button'):
                self.clean_button.setStyleSheet(f"""
                    QPushButton {{ 
                        background-color: {button_bg_color}; 
                        color: {text_color}; 
                        border: 1px solid #555; 
                        border-radius: 4px; 
                        padding: 6px 12px; 
                        padding-left: 30px; 
                        text-align: left;
                    }}
                    QPushButton:hover {{ background-color: {button_hover_bg_color}; }}
                    QPushButton:pressed {{ background-color: {button_pressed_bg_color}; }}
                    QPushButton:disabled {{ background-color: {disabled_bg_color}; color: {disabled_text_color}; }}
                """)
            
            if hasattr(self, 'scan_button'):
                self.scan_button.setStyleSheet(f"""
                    QPushButton {{ 
                        background-color: {accent_color}; 
                        color: white; 
                        border: 1px solid {self.lighten_color(accent_color, -10)}; 
                        border-radius: 4px; 
                        padding: 6px 12px; 
                        padding-left: 30px;
                        text-align: left;
                    }}
                    QPushButton:hover {{ background-color: {self.lighten_color(accent_color, 10)}; }}
                    QPushButton:pressed {{ background-color: {self.lighten_color(accent_color, -10)}; }}
                    QPushButton:disabled {{ background-color: {disabled_bg_color}; color: {disabled_text_color}; }}
                """)
                
            # Apply alternating row colors specifically for the table
            try:
                if self.result_table:
                    self.result_table.setAlternatingRowColors(True)
                    self.result_table.setStyleSheet(f"QTableWidget {{ alternate-background-color: {self.lighten_color(table_bg_color, 5)}; background-color: {table_bg_color}; color: {text_color}; border: 1px solid {border_color}; gridline-color: {border_color};}} QTableWidget::item {{ padding: 4px; color: {text_color}; }} QTableWidget::item:selected {{ background-color: {accent_color}80; color: #ffffff; }}")
            except AttributeError:
                pass
                
            try:
                if self.quarantined_list:
                    self.quarantined_list.setAlternatingRowColors(True)
                    self.quarantined_list.setStyleSheet(f"QTableWidget {{ alternate-background-color: {self.lighten_color(table_bg_color, 5)}; background-color: {table_bg_color}; color: {text_color}; border: 1px solid {border_color}; gridline-color: {border_color};}} QTableWidget::item {{ padding: 4px; color: {text_color}; }} QTableWidget::item:selected {{ background-color: {accent_color}80; color: #ffffff; }}")
            except AttributeError:
                pass
        
    def apply_current_theme(self):
        """应用当前主题的颜色 - 此方法由MainWindow的refresh_component_theme调用"""
        try:
            # 调用具体的主题应用方法
            self.apply_theme()
        except Exception as e:
            self.logger.error(f"Error applying current theme in VirusScanWidget: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
    def lighten_color(self, color, amount=0):
        """使颜色变亮或变暗
        
        Args:
            color: 十六进制颜色代码
            amount: 变化量，正数变亮，负数变暗
            
        Returns:
            新的十六进制颜色代码
        """
        try:
            c = color.lstrip('#')
            c = tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
            
            r, g, b = c
            
            r = min(255, max(0, r + amount * 2.55))
            g = min(255, max(0, g + amount * 2.55))
            b = min(255, max(0, b + amount * 2.55))
            
            return '#{:02x}{:02x}{:02x}'.format(int(r), int(g), int(b))
        except Exception as e:
            self.logger.error(f"计算颜色变化出错: {str(e)}")
            return color
        
    def setup_scan_tab(self, tab):
        """设置扫描选项卡的UI"""
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 描述
        description = QLabel(self.get_translation("scan_description", "Scan your system for malware and viruses"))
        description.setStyleSheet("font-size: 14px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # 扫描选项组
        scan_options_group = QGroupBox(self.get_translation("scan_options", "Scan Options"))
        options_layout = QVBoxLayout(scan_options_group)
        
        # 创建扫描类型按钮组
        self.scan_type_group = QButtonGroup()
        self.scan_type_group.setObjectName("virus_scan_type_group")
        
        # 快速扫描选项
        self.quick_scan_rb = QRadioButton(self.get_translation("quick_scan", "Quick Scan"))
        self.quick_scan_rb.setChecked(True)
        self.quick_scan_rb.setObjectName("virus_scan_quick")
        options_layout.addWidget(self.quick_scan_rb)
        self.scan_type_group.addButton(self.quick_scan_rb)
        
        # 完整扫描选项
        self.full_scan_rb = QRadioButton(self.get_translation("full_scan", "Full Scan"))
        self.full_scan_rb.setObjectName("virus_scan_full")
        options_layout.addWidget(self.full_scan_rb)
        self.scan_type_group.addButton(self.full_scan_rb)
        
        # 自定义扫描选项
        self.custom_scan_rb = QRadioButton(self.get_translation("custom_scan", "Custom Scan"))
        self.custom_scan_rb.setObjectName("virus_scan_custom")
        options_layout.addWidget(self.custom_scan_rb)
        self.scan_type_group.addButton(self.custom_scan_rb)
        
        # 自定义扫描路径选择
        custom_scan_layout = QHBoxLayout()
        self.custom_path_edit = QLineEdit()
        self.custom_path_edit.setPlaceholderText(self.get_translation("select_path", "Select directory or file to scan"))
        self.custom_path_edit.setEnabled(False)
        custom_scan_layout.addWidget(self.custom_path_edit)
        
        self.browse_button = QPushButton(self.get_translation("browse", "Browse..."))
        self.browse_button.setEnabled(False)
        self.browse_button.clicked.connect(self.browse_path)
        custom_scan_layout.addWidget(self.browse_button)
        
        options_layout.addLayout(custom_scan_layout)
        layout.addWidget(scan_options_group)
        
        # 扫描按钮和停止按钮
        button_layout = QHBoxLayout()
        
        self.scan_button = QPushButton(self.get_translation("start_scan", "Start Scan"))
        self.scan_button.clicked.connect(self.start_scan)
        button_layout.addWidget(self.scan_button)
        
        self.stop_button = QPushButton(self.get_translation("stop_scan", "Stop Scan"))
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        # 结果列表
        result_group = QGroupBox(self.get_translation("scan_results", "Scan Results"))
        result_layout = QVBoxLayout(result_group)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels([
            self.get_translation("file", "File"),
            self.get_translation("location", "Location"),
            self.get_translation("threat", "Threat"),
            self.get_translation("status", "Status")
        ])
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setAlternatingRowColors(True)
        result_layout.addWidget(self.result_table)
        
        # 操作按钮
        action_layout = QHBoxLayout()
        
        self.clean_button = QPushButton(self.get_translation("clean_all", "Clean All"))
        self.clean_button.clicked.connect(self.clean_threats)
        self.clean_button.setEnabled(False)
        action_layout.addWidget(self.clean_button)
        
        self.quarantine_button = QPushButton(self.get_translation("quarantine", "Quarantine Selected"))
        self.quarantine_button.clicked.connect(self.quarantine_selected)
        self.quarantine_button.setEnabled(False)
        action_layout.addWidget(self.quarantine_button)
        
        result_layout.addLayout(action_layout)
        layout.addWidget(result_group)
        
        # 统计信息
        self.stats_label = QLabel(self.get_translation("scan_stats", "Scan Statistics: Scanned 0 files, Found 0 threats"))
        layout.addWidget(self.stats_label)
        
    def setup_quarantine_tab(self, tab):
        """设置隔离区选项卡"""
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 隔离区说明
        description = QLabel(self.get_translation("quarantine_description", 
            "Files in quarantine have been detected as potential threats and isolated. You can delete these files or choose to restore them."))
        description.setWordWrap(True)
        description.setStyleSheet("color: #a0a0a0;")
        layout.addWidget(description)
        
        # 隔离文件列表
        self.quarantined_list = QTableWidget()
        self.quarantined_list.setColumnCount(3)
        self.quarantined_list.setHorizontalHeaderLabels([
            self.get_translation("file_name", "File Name"),
            self.get_translation("threat_type", "Threat Type"),
            self.get_translation("date", "Date")
        ])
        self.quarantined_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.quarantined_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.quarantined_list.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout.addWidget(self.quarantined_list)
        
        # 按钮容器
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 恢复按钮
        self.restore_button = QPushButton(self.get_translation("restore", "恢复"))
        self.restore_button.setEnabled(False)
        button_layout.addWidget(self.restore_button)
        
        # 删除按钮
        self.delete_button = QPushButton(self.get_translation("delete", "删除"))
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        layout.addWidget(button_container)

    def refresh_language(self):
        """Refresh all UI elements with current language translations"""
        # 查找标题和描述标签
        title_label = self.findChild(QLabel, "title_label")
        if title_label:
            title_label.setText(self.get_translation("title"))
            
        desc_label = self.findChild(QLabel, "desc_label")
        if desc_label:
            desc_label.setText(self.get_translation("description"))
        
        # 更新扫描选项
        scan_options_group = self.findChild(QGroupBox, "scan_options_group")
        if scan_options_group:
            scan_options_group.setTitle(self.get_translation("scan_types"))
        
        # 更新进度组
        progress_group = self.findChild(QGroupBox, "progress_group")
        if progress_group:
            progress_group.setTitle(self.get_translation("progress", "Scan Progress"))
        
        # 更新单选按钮
        if hasattr(self, "radio_quick"):
            self.radio_quick.setText(self.get_translation("quick_scan"))
        if hasattr(self, "radio_full"):
            self.radio_full.setText(self.get_translation("full_scan"))
        if hasattr(self, "radio_custom"):
            self.radio_custom.setText(self.get_translation("custom_scan"))
        
        # 更新自定义扫描控件
        if hasattr(self, "add_target_button"):
            self.add_target_button.setText(self.get_translation("select_folder"))
        if hasattr(self, "remove_target_button"):
            self.remove_target_button.setText(self.get_translation("remove", "Remove Selected"))
        
        # 更新扫描选项复选框
        if hasattr(self, "option_archive"):
            self.option_archive.setText(self.get_translation("scan_archives", "Scan inside archives (zip, rar, etc.)"))
        if hasattr(self, "option_rootkits"):
            self.option_rootkits.setText(self.get_translation("scan_rootkits", "Scan for rootkits and bootkits"))
        if hasattr(self, "option_autofix"):
            self.option_autofix.setText(self.get_translation("autofix", "Automatically attempt to fix detected issues"))
        
        # 更新威胁组
        threats_group = self.findChild(QGroupBox, "threats_group")
        if threats_group:
            threats_group.setTitle(self.get_translation("threats_found", "Detected Threats"))
        
        # 更新日志组
        log_group = self.findChild(QGroupBox, "log_group")
        if log_group:
            log_group.setTitle(self.get_translation("log_output", "Scan Log"))
        
        # 更新按钮
        if hasattr(self, "start_button"):
            self.start_button.setText(self.get_translation("scan_button"))
        if hasattr(self, "stop_button"):
            self.stop_button.setText(self.get_translation("stop_button"))
        if hasattr(self, "fix_button"):
            self.fix_button.setText(self.get_translation("clean_threats"))
        if hasattr(self, "clear_log_button"):
            self.clear_log_button.setText(self.get_translation("clear_log", "Clear Log"))

    def clear_log(self):
        """清除日志输出"""
        self.log_text.clear()
        self.log_text.append(self.get_translation("ready_message", "病毒扫描就绪。选择扫描类型并点击'开始扫描'。"))
        
    def start_scan(self):
        """Start the virus scan process"""
        # Determine scan type
        if self.quick_scan_rb.isChecked():
            scan_type = "quick"
        elif self.full_scan_rb.isChecked():
            scan_type = "full"
        elif self.custom_scan_rb.isChecked():
            scan_type = "custom"
            if not self.custom_scan_targets:
                QMessageBox.warning(self, 
                                  self.get_translation("no_targets", "未选择目标"), 
                                  self.get_translation("select_targets_msg", "请至少选择一个要扫描的文件或文件夹。"))
                return
        
        # Collect scan options
        scan_options = {
            'scan_type': scan_type,
            'scan_targets': self.custom_scan_targets.copy() if scan_type == "custom" else [],
            'options': {
                'archives': False,
                'rootkits': False,
                'autofix': False
            }
        }
        
        # Confirmation dialog
        reply = QMessageBox.question(self, 
                                   self.get_translation("start_scan_confirm", "Start Virus Scan"), 
                                   self.get_translation("start_scan_msg", "Start {scan_type} scan now?"),
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:
            # Clear previous results
            self.result_table.setRowCount(0)
            self.detected_threats = []
            self.clean_button.setEnabled(False)
            self.quarantine_button.setEnabled(False)
            
            # Reset progress bar
            self.progress.setValue(0)
            
            # 检查是否启用动画
            if self.settings.get_setting("enable_animations", True):
                # 添加扫描动画效果
                self.progress.setStyleSheet("QProgressBar {border: 1px solid grey; border-radius: 2px; text-align: center;} "
                                          "QProgressBar::chunk {background-color: #4CAF50; width: 20px;}")
            else:
                # 不使用动画特效，使用简单样式
                self.progress.setStyleSheet("QProgressBar {border: 1px solid grey; border-radius: 2px; text-align: center;} "
                                          "QProgressBar::chunk {background-color: #4CAF50;}")
            
            # Create and start thread
            self.scan_thread = VirusScanThread(scan_options)
            self.scan_thread.update_progress.connect(self.update_progress)
            self.scan_thread.update_log.connect(self.add_log)
            self.scan_thread.found_threat.connect(self.add_threat)
            self.scan_thread.finished_scan.connect(self.scan_finished)
            self.scan_thread.start()
            
            # Update UI
            self.scan_button.setEnabled(False)
            self.stop_button.setEnabled(True)

    def stop_scan(self):
        """Stop the virus scan process"""
        if self.scan_thread and self.scan_thread.is_running:
            reply = QMessageBox.question(self, 'Stop Scan', 
                                       "Are you sure you want to stop the scan?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.scan_thread.stop()
                self.update_log("Stopping scan, please wait...")
    
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress.setValue(value)
        
    def update_log(self, message):
        """更新日志输出"""
        # 格式化日志消息，添加时间戳
        timestamp = QDateTime.currentDateTime().toString('hh:mm:ss')
        formatted_message = f"[{timestamp}] {message}"
        
        # 根据消息类型设置不同的颜色
        if "完成" in message or "成功" in message or "✓" in message:
            # 成功消息使用绿色
            formatted_message = f"<span style='color:#4CAF50;'>{formatted_message}</span>"
        elif "警告" in message or "注意" in message:
            # 警告消息使用黄色
            formatted_message = f"<span style='color:#FFC107;'>{formatted_message}</span>"
        elif "错误" in message or "失败" in message or "✗" in message or "威胁" in message:
            # 错误或威胁消息使用红色
            formatted_message = f"<span style='color:#F44336;'>{formatted_message}</span>"
        elif "扫描" in message and "文件" in message:
            # 扫描文件消息使用灰色，减少视觉干扰
            formatted_message = f"<span style='color:#9E9E9E;'>{formatted_message}</span>"
        
        self.log_text.append(formatted_message)
        
        # 滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        
        # 即时更新UI，避免在长时间操作中界面冻结
        QApplication.processEvents() 
    
    def add_log(self, message):
        """添加日志消息"""
        # 临时的实现，将消息显示在状态标签上
        self.stats_label.setText(message)
        self.logger.info(f"[Virus Scan] {message}")

    def add_threat(self, file_path: str, threat_type: str) -> None:
        """将检测到的威胁添加到结果表格"""
        row = self.result_table.rowCount()
        self.result_table.insertRow(row)
        
        # 文件名
        filename = os.path.basename(file_path)
        self.result_table.setItem(row, 0, QTableWidgetItem(filename))
        
        # 文件位置（目录）
        location = os.path.dirname(file_path)
        self.result_table.setItem(row, 1, QTableWidgetItem(location))
        
        # 威胁类型
        self.result_table.setItem(row, 2, QTableWidgetItem(threat_type))
        
        # 状态
        self.result_table.setItem(row, 3, QTableWidgetItem(self.get_translation("detected", "已检测")))
        
        # 存储完整的威胁信息
        self.detected_threats.append({
            'path': file_path,
            'type': threat_type
        })
        
        # 启用清除和隔离按钮
        self.clean_button.setEnabled(True)
        self.quarantine_button.setEnabled(True)
        
        # 更新统计信息
        self.update_stats()
    
    def update_stats(self):
        """更新扫描统计信息"""
        files_scanned = random.randint(100, 1000)  # 模拟文件扫描数量
        threats_found = len(self.detected_threats)
        
        stats_text = self.get_translation(
            "scan_stats", 
            "Scan Statistics: Scanned {files} files, Found {threats} threats"
        ).format(files=files_scanned, threats=threats_found)
        
        self.stats_label.setText(stats_text)
    
    def scan_finished(self, success, message, threats_found):
        """处理扫描完成事件"""
        # 重新启用扫描按钮
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # 设置进度为100%
        self.progress.setValue(100)
        
        # 显示完成消息
        if success:
            if threats_found > 0:
                QMessageBox.warning(
                    self, 
                    self.get_translation("scan_complete", "扫描完成"), 
                    self.get_translation("threats_found_msg", f"{message}\n\n发现 {threats_found} 个潜在威胁。")
                )
            else:
                QMessageBox.information(
                    self, 
                    self.get_translation("scan_complete", "扫描完成"), 
                    self.get_translation("no_threats_msg", f"{message}\n\n未检测到威胁。")
                )
        else:
            QMessageBox.warning(
                self, 
                self.get_translation("scan_incomplete", "扫描未完成"), 
                message
            )
        
        # 添加最终日志消息
        result = self.get_translation("success", "成功") if success else self.get_translation("incomplete", "未完成")
        self.add_log(f"{self.get_translation('scan_completed', '扫描过程已完成')}. {self.get_translation('result', '结果')}: {result}")
        self.add_log(f"{self.get_translation('total_threats', '发现威胁总数')}: {threats_found}")
        
        # 如果发现威胁，启用清除按钮
        self.clean_button.setEnabled(threats_found > 0)
        self.quarantine_button.setEnabled(threats_found > 0)

    def browse_path(self):
        """浏览并选择要扫描的文件或目录"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        
        if file_dialog.exec_():
            selected_paths = file_dialog.selectedFiles()
            if selected_paths:
                # 设置自定义路径到编辑框
                self.custom_path_edit.setText(selected_paths[0])
                # 添加到扫描目标列表
                if selected_paths[0] not in self.custom_scan_targets:
                    self.custom_scan_targets.append(selected_paths[0])

    def toggle_custom_scan(self, checked):
        """根据自定义扫描选项的选中状态切换相关控件的可用性"""
        self.custom_path_edit.setEnabled(checked)
        self.browse_button.setEnabled(checked)
        
        # 如果取消选中，清空自定义扫描目标
        if not checked:
            self.custom_scan_targets = []
            self.custom_path_edit.clear()

    def clean_threats(self):
        """清除检测到的威胁"""
        reply = QMessageBox.question(self, 
                                    self.get_translation("confirm_clean", "确认清除"), 
                                    self.get_translation("confirm_clean_msg", "确定要清除所有检测到的威胁吗？"), 
                                    QMessageBox.Yes | QMessageBox.No, 
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            row_count = self.result_table.rowCount()
            for row in range(row_count):
                self.result_table.item(row, 2).setText(self.get_translation("cleaned", "已清除"))
            
            QMessageBox.information(self, 
                                   self.get_translation("clean_complete", "清除完成"), 
                                   self.get_translation("clean_success", "所有威胁已成功清除！"))
            
            self.clean_button.setEnabled(False)
            self.quarantine_button.setEnabled(False)

    def quarantine_selected(self):
        """隔离选中的威胁"""
        # 获取选中的行
        selected_items = self.result_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 
                              self.get_translation("no_selection", "未选择"), 
                              self.get_translation("select_threats", "请选择要隔离的威胁。"))
            return
        
        # 获取不重复的行索引
        rows = set()
        for item in selected_items:
            rows.add(item.row())
        
        if not rows:
            return
        
        reply = QMessageBox.question(self, 
                                    self.get_translation("confirm_quarantine", "确认隔离"), 
                                    self.get_translation("confirm_quarantine_msg", "确定要隔离选中的威胁吗？"), 
                                    QMessageBox.Yes | QMessageBox.No, 
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            for row in rows:
                self.result_table.item(row, 2).setText(self.get_translation("quarantined", "已隔离"))
            
            QMessageBox.information(self, 
                                   self.get_translation("quarantine_complete", "隔离完成"), 
                                   self.get_translation("quarantine_success", "选中的威胁已成功隔离！")) 

    def on_scan_type_changed(self, button):
        """处理扫描类型选择改变"""
        button_id = button.objectName()
        self.logger.info(f"病毒扫描类型更改为: {button.text()}")
        
        # 保存设置
        self.settings.set_setting("virus_scan_type", button_id)
        self.settings.sync()
        
        # 更新UI状态
        if button_id == "virus_scan_custom":
            self.custom_path_edit.setEnabled(True)
            self.browse_button.setEnabled(True)
        else:
            self.custom_path_edit.setEnabled(False)
            self.browse_button.setEnabled(False)
        
        # 在初始化后特别处理单选按钮的大小和样式
        self.update_radio_buttons_size()

    def update_radio_buttons_size(self):
        """更新单选按钮的大小和样式，适配当前主题"""
        # 获取当前主题颜色
        theme_name = self.settings.get_setting("theme", "dark")
        theme_data = self.settings.load_theme(theme_name)
        
        # 设置默认颜色
        text_color = "#dcdcdc"
        accent_color = "#007acc"
        
        # 更新颜色值（如果有主题数据）
        if theme_data and "colors" in theme_data:
            text_color = theme_data["colors"].get("text_color", text_color)
            accent_color = theme_data["colors"].get("accent_color", accent_color)

        # 生成通用的样式
        radio_style = f"""
            QRadioButton {{
                min-height: 30px;
                font-size: 13px;
                padding: 4px;
                color: {text_color};
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {accent_color};
                border-radius: 10px;
            }}
            QRadioButton::indicator:checked {{
                background-color: {accent_color};
                border: 4px solid {accent_color};
                width: 10px;
                height: 10px;
            }}
            QRadioButton:checked {{
                font-weight: bold;
            }}
        """

    def apply_settings(self, settings=None):
        """应用设置更改到此组件
        
        Args:
            settings: 可选的设置对象。如果为None，则使用父对象的设置。
        """
        try:
            # 获取设置对象
            if settings is None:
                if hasattr(self, 'settings'):
                    settings = self.settings
                elif hasattr(self, 'main_window') and self.main_window:
                    settings = self.main_window.settings
            
            if settings:
                # 应用主题
                self.apply_theme()
                
                # 刷新语言
                self.refresh_language()
                
                # 更新单选按钮大小和样式
                self.update_radio_buttons_size()
                
                # 应用任何组件特定设置
                if hasattr(settings, 'get_setting'):
                    # 动画设置
                    enable_animations = settings.get_setting('enable_animations', True)
                    # 应用动画设置（如果需要）
                    
                    # 应用扫描特定设置
                    auto_quarantine = settings.get_setting('auto_quarantine', False)
                    if hasattr(self, 'auto_quarantine_check') and self.auto_quarantine_check:
                        self.auto_quarantine_check.setChecked(auto_quarantine)
                    
                    # 应用保存的扫描类型
                    scan_type = settings.get_setting('virus_scan_type', 'virus_scan_quick')
                    self._apply_saved_scan_type(scan_type)

        except Exception as e:
            self.logger.error(f"在 VirusScanWidget 中应用设置时发生错误: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def _apply_saved_scan_type(self, scan_type):
        """应用保存的扫描类型设置
        
        Args:
            scan_type: 要应用的扫描类型ID
        """
        try:
            # 设置相应的单选按钮为选中状态
            if scan_type == 'virus_scan_quick' and hasattr(self, 'quick_scan_rb'):
                self.quick_scan_rb.setChecked(True)
                self.toggle_custom_scan(False)
            elif scan_type == 'virus_scan_full' and hasattr(self, 'full_scan_rb'):
                self.full_scan_rb.setChecked(True)
                self.toggle_custom_scan(False)
            elif scan_type == 'virus_scan_custom' and hasattr(self, 'custom_scan_rb'):
                self.custom_scan_rb.setChecked(True)
                self.toggle_custom_scan(True)
        except Exception as e:
            self.logger.error(f"应用扫描类型时出错: {str(e)}") 