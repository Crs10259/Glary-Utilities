import os
import sys
import platform
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QProgressBar, QMessageBox,
                             QGroupBox, QRadioButton, QCheckBox, QTabWidget,
                             QTableWidget, QTableWidgetItem, QFrame, QSizePolicy,
                             QSpacerItem, QHeaderView, QButtonGroup)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from components.base_component import BaseComponent
from PyQt5.QtGui import QBrush, QColor
from config import Icon

class BootRepairThread(QThread):
    """Thread for running boot repair operations in the background"""
    update_progress = pyqtSignal(int)
    update_log = pyqtSignal(str)
    finished_operation = pyqtSignal(bool, str)
    
    def __init__(self, repair_type, parent=None):
        super().__init__(parent)
        self.repair_type = repair_type
        self.is_running = False
        
    def run(self):
        self.is_running = True
        
        try:
            if self.repair_type == "mbr":
                self.repair_mbr()
            elif self.repair_type == "bcd":
                self.repair_bcd()
            elif self.repair_type == "bootmgr":
                self.repair_bootmgr()
            elif self.repair_type == "winload":
                self.repair_winload()
            elif self.repair_type == "full":
                self.full_repair()
                
            self.finished_operation.emit(True, "Boot repair completed successfully!")
        except Exception as e:
            self.update_log.emit(f"Error: {str(e)}")
            self.finished_operation.emit(False, f"Boot repair failed: {str(e)}")
        
        self.is_running = False
    
    def repair_mbr(self):
        """Repair the Master Boot Record"""
        self.update_log.emit("Starting MBR repair...")
        self.update_progress.emit(10)
        
        # For safety, this is a simulation
        if platform.system() == "Windows":
            self.update_log.emit("Checking disk status...")
            self.update_progress.emit(30)
            
            # Simulate disk check
            for i in range(30, 60, 5):
                QThread.sleep(1)
                self.update_progress.emit(i)
                self.update_log.emit(f"Analyzing MBR structures... ({i}%)")
            
            self.update_log.emit("MBR repair would run the following command:")
            self.update_log.emit("bootrec /fixmbr")
            
            QThread.sleep(2)
            self.update_progress.emit(100)
            self.update_log.emit("MBR repair completed (simulated)")
        else:
            self.update_log.emit("MBR repair is only available on Windows.")
            self.update_progress.emit(100)
    
    def repair_bcd(self):
        """Repair the Boot Configuration Data"""
        self.update_log.emit("Starting BCD repair...")
        self.update_progress.emit(10)
        
        # For safety, this is a simulation
        if platform.system() == "Windows":
            self.update_log.emit("Backing up existing BCD...")
            self.update_progress.emit(20)
            
            # Simulate repair process
            for i in range(20, 70, 5):
                QThread.sleep(1)
                self.update_progress.emit(i)
                self.update_log.emit(f"Rebuilding boot configuration data... ({i}%)")
            
            self.update_log.emit("BCD repair would run the following commands:")
            self.update_log.emit("bootrec /rebuildbcd")
            
            QThread.sleep(2)
            self.update_progress.emit(100)
            self.update_log.emit("BCD repair completed (simulated)")
        else:
            self.update_log.emit("BCD repair is only available on Windows.")
            self.update_progress.emit(100)
    
    def repair_bootmgr(self):
        """Repair the Boot Manager"""
        self.update_log.emit("Starting Boot Manager repair...")
        self.update_progress.emit(10)
        
        # For safety, this is a simulation
        if platform.system() == "Windows":
            self.update_log.emit("Checking Boot Manager...")
            self.update_progress.emit(30)
            
            # Simulate repair process
            for i in range(30, 80, 5):
                QThread.sleep(1)
                self.update_progress.emit(i)
                self.update_log.emit(f"Repairing boot manager files... ({i}%)")
            
            self.update_log.emit("Boot Manager repair would run the following command:")
            self.update_log.emit("bootrec /fixboot")
            
            QThread.sleep(2)
            self.update_progress.emit(100)
            self.update_log.emit("Boot Manager repair completed (simulated)")
        else:
            self.update_log.emit("Boot Manager repair is only available on Windows.")
            self.update_progress.emit(100)
    
    def repair_winload(self):
        """Repair the Windows Loader"""
        self.update_log.emit("Starting Windows Loader repair...")
        self.update_progress.emit(10)
        
        # For safety, this is a simulation
        if platform.system() == "Windows":
            self.update_log.emit("Checking Windows boot files...")
            self.update_progress.emit(20)
            
            # Simulate repair process
            for i in range(20, 90, 7):
                QThread.sleep(1)
                self.update_progress.emit(i)
                self.update_log.emit(f"Restoring Windows Loader files... ({i}%)")
            
            self.update_log.emit("Windows Loader repair would use SFC to repair system files:")
            self.update_log.emit("sfc /scannow")
            
            QThread.sleep(2)
            self.update_progress.emit(100)
            self.update_log.emit("Windows Loader repair completed (simulated)")
        else:
            self.update_log.emit("Windows Loader repair is only available on Windows.")
            self.update_progress.emit(100)
    
    def full_repair(self):
        """Perform a full boot repair sequence"""
        self.update_log.emit("Starting full boot repair sequence...")
        self.update_progress.emit(5)
        
        # For safety, this is a simulation
        if platform.system() == "Windows":
            # Simulate full repair
            self.update_log.emit("Step 1: Fixing MBR...")
            self.update_progress.emit(10)
            QThread.sleep(2)
            
            self.update_log.emit("Step 2: Fixing boot sector...")
            self.update_progress.emit(25)
            QThread.sleep(2)
            
            self.update_log.emit("Step 3: Rebuilding BCD...")
            self.update_progress.emit(40)
            QThread.sleep(2)
            
            self.update_log.emit("Step 4: Repairing Windows boot files...")
            self.update_progress.emit(60)
            QThread.sleep(2)
            
            self.update_log.emit("Step 5: Scanning system files...")
            self.update_progress.emit(80)
            QThread.sleep(2)
            
            self.update_log.emit("Full boot repair would run the following commands:")
            self.update_log.emit("1. bootrec /fixmbr")
            self.update_log.emit("2. bootrec /fixboot")
            self.update_log.emit("3. bootrec /rebuildbcd")
            self.update_log.emit("4. sfc /scannow")
            
            self.update_progress.emit(100)
            self.update_log.emit("Full boot repair completed (simulated)")
        else:
            self.update_log.emit("Boot repair is only available on Windows.")
            self.update_progress.emit(100)

class BootRepairWidget(BaseComponent):
    """Widget for boot repair operations"""
    def __init__(self, parent=None):
        # 初始化属性
        self.boot_worker = None
        
        # 调用父类构造函数
        super().__init__(parent)
        
    def setup_ui(self):
        """设置UI元素"""
        # 设置主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # 启用样式表背景
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # 标题
        self.title = QLabel(self.get_translation("title", "Boot Repair & Startup Manager"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.main_layout.addWidget(self.title)
        
        # 描述
        self.description = QLabel(self.get_translation("description", "Repair Windows boot issues and manage startup programs."))
        self.description.setStyleSheet("font-size: 14px;")
        self.description.setWordWrap(True)
        self.main_layout.addWidget(self.description)
        
        # 非Windows系统的警告标签
        if platform.system() != "Windows":
            warning_label = QLabel("⚠️ Boot repair features are only available on Windows")
            warning_label.setStyleSheet("color: #ff9900; font-weight: bold;")
            self.main_layout.addWidget(warning_label)
        
        # 创建标签页
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        # 修复标签页
        self.repair_tab = QWidget()
        
        # 启动项管理标签页
        self.startup_tab = QWidget()
        
        # 设置标签页的内容
        self.setup_repair_tab(self.repair_tab)
        self.setup_startup_manager_tab(self.startup_tab)
        
        # 添加标签页
        self.tabs.addTab(self.repair_tab, self.get_translation("repair_tab", "Boot Repair"))
        self.tabs.addTab(self.startup_tab, self.get_translation("startup_tab", "Startup Manager"))
        
        # 添加到主布局
        self.main_layout.addWidget(self.tabs)
        
        # 应用当前主题
        self.apply_theme()
        
    def apply_theme(self):
        """应用主题样式到组件"""
        try:
            # 首先调用基类的应用主题方法
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

                # 更新标题和描述的颜色（如果它们存在）
                if hasattr(self, 'title') and self.title is not None:
                    self.title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {text_color};")
                
                if hasattr(self, 'description') and self.description is not None:
                    self.description.setStyleSheet(f"font-size: 14px; color: {text_color};")
                
                # 获取check图标路径
                check_icon_path = ""
                try:
                    if hasattr(Icon, "Check") and hasattr(Icon.Check, "Path"):
                        check_icon_path = Icon.Check.Path
                    else:
                        check_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons", "check.svg")
                        print(f"Using fallback check icon path: {check_icon_path}")
                except Exception as e:
                    print(f"Error getting check icon path: {e}")
                    check_icon_path = ""
                
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
                    
                    QCheckBox, QRadioButton {{ color: {text_color}; background-color: transparent; spacing: 5px; }}
                    
                    QCheckBox::indicator {{ width: 16px; height: 16px; border: 2px solid {accent_color}; border-radius: 3px; background-color: {bg_color}; }}
                    QCheckBox::indicator:unchecked {{ background-color: {bg_color}; }}
                    QCheckBox::indicator:checked {{ background-color: {accent_color}; image: url({check_icon_path}); }}
                    QCheckBox::indicator:unchecked:hover {{ border-color: {self.lighten_color(accent_color, 20)}; background-color: {self.lighten_color(bg_color, 10)}; }}
                    QCheckBox::indicator:checked:hover {{ background-color: {self.lighten_color(accent_color, 10)}; }}
                    
                    QRadioButton::indicator {{ width: 16px; height: 16px; border: 2px solid {accent_color}; border-radius: 9px; background-color: {bg_color}; }}
                    QRadioButton::indicator:unchecked {{ background-color: {bg_color}; }}
                    QRadioButton::indicator:checked {{ background-color: {bg_color}; border: 4px solid {accent_color}; }}
                    QRadioButton::indicator:unchecked:hover {{ border-color: {self.lighten_color(accent_color, 20)}; background-color: {self.lighten_color(bg_color, 10)}; }}
                    QRadioButton::indicator:checked:hover {{ border-color: {self.lighten_color(accent_color, 10)}; }}
                    
                    QLabel {{ color: {text_color}; background-color: transparent; }}
                """)
                 # Apply alternating row colors specifically for the table
                try:
                    if hasattr(self, 'startup_table') and self.startup_table is not None:
                        self.startup_table.setAlternatingRowColors(True)
                        self.startup_table.setStyleSheet(f"QTableWidget {{ alternate-background-color: {self.lighten_color(table_bg_color, 5)}; background-color: {table_bg_color}; color: {text_color}; border: 1px solid {border_color}; gridline-color: {border_color};}} QTableWidget::item {{ padding: 4px; color: {text_color}; }} QTableWidget::item:selected {{ background-color: {accent_color}80; color: #ffffff; }}")
                except AttributeError:
                    pass
                
                # 修复单选按钮连接
                self.fix_radiobutton_connections()
        except Exception as e:
            print(f"Error applying theme in BootRepairWidget: {e}")
            
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
            print(f"计算颜色变化出错: {str(e)}")
            return color
            
    def setup_repair_tab(self, tab):
        """设置修复选项卡"""
        # 创建标签页布局
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(10, 10, 10, 10)
        
        # 选项组
        options_group = QGroupBox(self.get_translation("repair_options", "Repair Options"))
        options_layout = QVBoxLayout(options_group)
        
        # 创建按钮组，确保单选按钮互斥
        self.repair_button_group = QButtonGroup(self)
        self.repair_button_group.setObjectName("boot_repair_button_group")
        
        # 修复选项
        self.repair_mbr_radio = QRadioButton(self.get_translation("fix_mbr", "Fix Boot Sector"))
        self.repair_mbr_radio.setObjectName("repair_mbr_radio")
        self.repair_mbr_radio.setChecked(True)
        self.repair_button_group.addButton(self.repair_mbr_radio)
        
        self.repair_bcd_radio = QRadioButton(self.get_translation("rebuild_bcd", "Repair Boot Configuration Data (BCD)"))
        self.repair_bcd_radio.setObjectName("repair_bcd_radio")
        self.repair_button_group.addButton(self.repair_bcd_radio)
        
        self.repair_bootmgr_radio = QRadioButton(self.get_translation("fix_boot", "Repair Boot Manager"))
        self.repair_bootmgr_radio.setObjectName("repair_bootmgr_radio")
        self.repair_button_group.addButton(self.repair_bootmgr_radio)
        
        self.repair_winload_radio = QRadioButton(self.get_translation("repair_winload", "Repair Windows Loader"))
        self.repair_winload_radio.setObjectName("repair_winload_radio")
        self.repair_button_group.addButton(self.repair_winload_radio)
        
        self.repair_full_radio = QRadioButton(self.get_translation("full_repair", "Full Repair"))
        self.repair_full_radio.setObjectName("repair_full_radio")
        self.repair_button_group.addButton(self.repair_full_radio)
        
        # 连接按钮组信号
        self.repair_button_group.buttonClicked.connect(self.on_repair_type_changed)
        
        options_layout.addWidget(self.repair_mbr_radio)
        options_layout.addWidget(self.repair_bcd_radio)
        options_layout.addWidget(self.repair_bootmgr_radio)
        options_layout.addWidget(self.repair_winload_radio)
        options_layout.addWidget(self.repair_full_radio)
        
        # 添加选项组到标签页
        tab_layout.addWidget(options_group)
        
        # 日志输出区域
        log_group = QGroupBox(self.get_translation("operation_log", "Operation Log"))
        log_layout = QVBoxLayout(log_group)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setText(self.get_translation("boot_repair_ready", "Boot repair tool is ready, please select a repair option and click the \"Start Repair\" button."))
        
        log_layout.addWidget(self.log_output)
        
        # 添加日志组到标签页
        tab_layout.addWidget(log_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        tab_layout.addWidget(self.progress_bar)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton(self.get_translation("repair_button", "Start Repair"))
        self.start_button.clicked.connect(self.start_repair)
        
        self.stop_button = QPushButton(self.get_translation("stop_button", "Stop"))
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_repair)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        
        # 添加按钮区域到标签页
        tab_layout.addLayout(buttons_layout)
    
    def setup_startup_manager_tab(self, tab):
        """设置启动项管理选项卡"""
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 描述
        description = QLabel(self.get_translation("startup_desc", "Manage Windows startup items, enable or disable self-starting programs."))
        description.setStyleSheet("font-size: 14px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # 启动项表格
        self.startup_table = QTableWidget()
        self.startup_table.setColumnCount(4)
        self.startup_table.setHorizontalHeaderLabels([
            self.get_translation("startup_name", "Name"),
            self.get_translation("startup_path", "Path"),
            self.get_translation("startup_status", "Status"),
            self.get_translation("startup_type", "Type")
        ])
        
        # 设置表格属性
        self.startup_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.startup_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.startup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.startup_table.setAlternatingRowColors(True)
        layout.addWidget(self.startup_table)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 刷新按钮
        self.refresh_button = QPushButton(self.get_translation("refresh", "Refresh List"))
        self.refresh_button.clicked.connect(self.refresh_startup_items)
        button_layout.addWidget(self.refresh_button)
        
        # 启用/禁用按钮
        self.enable_button = QPushButton(self.get_translation("enable", "Enable Selected"))
        self.enable_button.clicked.connect(self.enable_startup_item)
        button_layout.addWidget(self.enable_button)
        
        self.disable_button = QPushButton(self.get_translation("disable", "Disable Selected"))
        self.disable_button.clicked.connect(self.disable_startup_item)
        button_layout.addWidget(self.disable_button)
        
        # 删除按钮
        self.delete_button = QPushButton(self.get_translation("delete", "Delete Selected"))
        self.delete_button.clicked.connect(self.delete_startup_item)
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
        
        # 加载示例数据
        self.load_demo_startup_items()
        
        # 连接选择信号
        self.startup_table.itemSelectionChanged.connect(self.update_button_states)
        
        # 初始化按钮状态
        self.update_button_states()

    def load_demo_startup_items(self):
        """加载演示用的启动项数据"""
        self.startup_table.setRowCount(0)  # 清除现有行
        
        demo_items = [
            ["Microsoft Edge", "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe", "已启用", "注册表"],
            ["Spotify", "C:\\Users\\AppData\\Roaming\\Spotify\\Spotify.exe", "已启用", "启动文件夹"],
            ["Steam", "C:\\Program Files\\Steam\\steam.exe", "已禁用", "注册表"],
            ["Discord", "C:\\Users\\AppData\\Local\\Discord\\app-1.0.9002\\Discord.exe", "已启用", "任务计划程序"],
            ["OneDrive", "C:\\Program Files\\Microsoft OneDrive\\OneDrive.exe", "已禁用", "注册表"],
        ]
        
        for item in demo_items:
            row = self.startup_table.rowCount()
            self.startup_table.insertRow(row)
            
            for col, text in enumerate(item):
                self.startup_table.setItem(row, col, QTableWidgetItem(text))
                
            # 为已禁用项设置不同的颜色
            if item[2] == "已禁用":
                for col in range(4):
                    self.startup_table.item(row, col).setForeground(QBrush(QColor("#888888")))

    def refresh_startup_items(self):
        """刷新启动项列表"""
        self.log_output.append(self.get_translation("refreshing", "正在刷新启动项列表..."))
        # 在实际应用中，这里应该查询系统中的启动项
        # 现在我们只是重新加载示例数据
        self.load_demo_startup_items()
        self.log_output.append(self.get_translation("refresh_complete", "刷新完成"))
    
    def enable_startup_item(self):
        """启用选中的启动项"""
        selected_rows = self.get_selected_rows()
        if not selected_rows:
                return
            
        for row in selected_rows:
            item = self.startup_table.item(row, 0)
            name = item.text()
            self.log_output.append(self.get_translation("enabling", f"正在启用 {name}..."))
            
            # 更新状态
            status_item = self.startup_table.item(row, 2)
            status_item.setText("已启用")
            
            # 恢复正常颜色
            for col in range(4):
                self.startup_table.item(row, col).setForeground(QBrush(QColor("#000000")))
                
        self.update_button_states()
    
    def disable_startup_item(self):
        """禁用选中的启动项"""
        selected_rows = self.get_selected_rows()
        if not selected_rows:
                return
            
        for row in selected_rows:
            item = self.startup_table.item(row, 0)
            name = item.text()
            self.log_output.append(self.get_translation("disabling", f"正在禁用 {name}..."))
            
            # 更新状态
            status_item = self.startup_table.item(row, 2)
            status_item.setText("已禁用")
            
            # 设置灰色
            for col in range(4):
                self.startup_table.item(row, col).setForeground(QBrush(QColor("#888888")))
                
        self.update_button_states()
    
    def delete_startup_item(self):
        """删除选中的启动项"""
        selected_rows = self.get_selected_rows()
        if not selected_rows:
            return
        
        # 从底部开始删除，避免索引变化问题
        for row in sorted(selected_rows, reverse=True):
            item = self.startup_table.item(row, 0)
            name = item.text()
            self.log_output.append(self.get_translation("deleting", f"正在删除 {name}..."))
            self.startup_table.removeRow(row)
            
        self.update_button_states()

    def get_selected_rows(self):
        """获取选中的行索引"""
        selected_indexes = self.startup_table.selectedIndexes()
        if not selected_indexes:
            return []
            
        # 提取不重复的行索引
        rows = set()
        for index in selected_indexes:
            rows.add(index.row())
            
        return list(rows)

    def update_button_states(self):
        """更新按钮的启用/禁用状态"""
        has_selection = bool(self.get_selected_rows())
        self.enable_button.setEnabled(has_selection)
        self.disable_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
    
    def start_repair(self):
        """Start the boot repair process"""
        # Determine which repair option is selected
        if self.repair_mbr_radio.isChecked():
            repair_type = "mbr"
        elif self.repair_bcd_radio.isChecked():
            repair_type = "bcd"
        elif self.repair_bootmgr_radio.isChecked():
            repair_type = "bootmgr"
        elif self.repair_winload_radio.isChecked():
            repair_type = "winload"
        elif self.repair_full_radio.isChecked():
            repair_type = "full"
        
        # Check if we're on Windows
        if platform.system() != "Windows":
            QMessageBox.warning(self, "Compatibility Error", 
                                "Boot repair features are only available on Windows systems.")
            return
            
        # Confirmation dialog
        reply = QMessageBox.question(self, 'Confirm Boot Repair', 
                                    f"Are you sure you want to perform {repair_type.upper()} boot repair?\n\n"
                                    "Note: This is a simulated operation for safety.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Clear previous log
            self.log_output.clear()
            self.log_output.append(f"Starting {repair_type.upper()} boot repair...")
            
            # Reset progress bar
            self.progress_bar.setValue(0)
            
            # Create and start thread
            self.boot_worker = BootRepairThread(repair_type)
            self.boot_worker.update_progress.connect(self.update_progress)
            self.boot_worker.update_log.connect(self.update_log)
            self.boot_worker.finished_operation.connect(self.repair_finished)
            self.boot_worker.start()
            
            # Update UI
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
    
    def stop_repair(self):
        """Stop the boot repair process"""
        if self.boot_worker and self.boot_worker.is_running:
            reply = QMessageBox.question(self, 'Confirm Stop', 
                                        "Are you sure you want to stop the repair process?\n"
                                        "This may leave your system in an inconsistent state.",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.boot_worker.terminate()
                self.boot_worker.wait()
                
                self.update_log("Repair process stopped by user.")
                self.repair_finished(False, "Operation cancelled")
    
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_bar.setValue(value)
    
    def update_log(self, message):
        """Update the log output"""
        self.log_output.append(message)
        # Scroll to bottom
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )
    
    def repair_finished(self, success, message):
        """Handle repair completion"""
        # Re-enable the start button
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Set progress to 100%
        self.progress_bar.setValue(100)
        
        # Show message
        if success:
            QMessageBox.information(self, "Boot Repair Complete", message)
        else:
            QMessageBox.warning(self, "Boot Repair Failed", message)
        
        # Add final log message
        self.update_log(f"Boot repair process completed. Result: {'Success' if success else 'Failed'}")

    def get_translation(self, key, default=None):
        """Override get_translation to use the correct section name"""
        return self.settings.get_translation("boot_repair", key, default)

    def refresh_language(self):
        """Refresh all UI text elements with current language translations"""
        # 标签页标题
        self.tabs.setTabText(0, self.get_translation("repair_tab", "Boot Repair"))
        self.tabs.setTabText(1, self.get_translation("startup_tab", "Startup Manager"))
        
        # 更新单选按钮
        self.repair_mbr_radio.setText(self.get_translation("fix_mbr", "Fix Boot Sector"))
        self.repair_bcd_radio.setText(self.get_translation("rebuild_bcd", "Repair Boot Configuration Data (BCD)"))
        self.repair_bootmgr_radio.setText(self.get_translation("fix_boot", "Repair Boot Manager"))
        self.repair_winload_radio.setText(self.get_translation("repair_winload", "Repair Windows Loader"))
        self.repair_full_radio.setText(self.get_translation("full_repair", "Full Repair"))
        
        # 更新按钮
        self.start_button.setText(self.get_translation("repair_button", "Start Repair"))
        self.stop_button.setText(self.get_translation("stop_button", "Stop"))
        
        # 更新日志组
        log_group = self.findChild(QGroupBox, "log_group")
        if log_group:
            log_group.setTitle(self.get_translation("log_output", "Log Output"))
        
        # 更新启动管理器选项卡
        if hasattr(self, "enable_button"):
            self.enable_button.setText(self.get_translation("enable", "Enable Selected"))
        if hasattr(self, "disable_button"):
            self.disable_button.setText(self.get_translation("disable", "Disable Selected"))
        if hasattr(self, "delete_button"):
            self.delete_button.setText(self.get_translation("delete", "Delete Selected"))
        if hasattr(self, "refresh_button"):
            self.refresh_button.setText(self.get_translation("refresh", "Refresh List"))
            
        # 更新启动项表格
        startup_list = self.findChild(QTableWidget, "startup_list")
        if startup_list:
            startup_list.setHorizontalHeaderLabels([
                self.get_translation("name", "Name"),
                self.get_translation("publisher", "Publisher"),
                self.get_translation("status", "Status"),
                self.get_translation("impact", "Impact")
            ]) 
            
    def on_repair_type_changed(self, button):
        """处理修复类型选择改变"""
        button_id = button.objectName()
        button_text = button.text()
        print(f"启动修复类型更改为: {button_text}")
        
        # 保存设置
        self.settings.set_setting("boot_repair_type", button_id)
        self.settings.set_setting("boot_repair_text", button_text)
        self.settings.sync()
        
        # 更新UI文本
        self.log_output.setText(self.get_translation("boot_repair_ready", "Boot repair tool is ready, please select a repair option and click the \"Start Repair\" button."))
        
        # 您可以根据不同的修复类型添加特定逻辑
        if button_id == "repair_full_radio":
            self.log_output.append(self.get_translation("full_repair_warning", "警告: 完整修复将重建所有启动组件，请确保您有足够的权限和备份。"))
            
    def toggle_startup_item(self, state):
        """处理启动项复选框状态改变"""
        if state == Qt.Checked:
            self.enable_startup_cb.setText(self.get_translation("enable_startup_checked"))
        else:
            self.enable_startup_cb.setText(self.get_translation("enable_startup"))
        
    def toggle_service(self, state):
        """处理服务复选框状态改变"""
        if state == Qt.Checked:
            self.disable_service_cb.setText(self.get_translation("disable_service_checked"))
        else:
            self.disable_service_cb.setText(self.get_translation("disable_service"))
            