import os
import sys
import platform
import subprocess
import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QCheckBox, QTextEdit, QGroupBox, QComboBox,
                            QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from components.base_component import BaseComponent
from utils.platform import PlatformUtils

class DiskCheckThread(QThread):
    """Worker thread for disk check operations"""
    progress_updated = pyqtSignal(str)
    operation_completed = pyqtSignal(bool)
    
    def __init__(self, drive, check_file_system, check_bad_sectors, read_only=True, operation="check"):
        super().__init__()
        self.drive = drive  # Drive letter to check
        self.check_file_system = check_file_system  # Whether to check file system
        self.check_bad_sectors = check_bad_sectors  # Whether to check for bad sectors
        self.read_only = read_only  # Whether to run in read-only mode
        self.operation = operation  # "check" or "repair"
    
    def run(self):
        """Run the worker thread"""
        if not PlatformUtils.is_windows():
            self.progress_updated.emit("磁盘检查当前仅在Windows系统上支持")
            self.operation_completed.emit(False)
            return
        
        try:
            if self.operation == "check":
                self.check_disk()
            elif self.operation == "repair":
                if self.read_only:
                    self.progress_updated.emit("只读模式已启用。仅在检查模式下运行...")
                    self.check_disk()
                else:
                    self.repair_disk()
            else:
                self.progress_updated.emit(f"未知操作: {self.operation}")
                self.operation_completed.emit(False)
        except Exception as e:
            self.progress_updated.emit(f"执行操作时出错: {str(e)}")
            self.operation_completed.emit(False)
    
    def check_disk(self):
        """检查磁盘错误而不修复它们"""
        # 验证驱动器
        if not os.path.exists(self.drive):
            self.progress_updated.emit(f"驱动器 {self.drive} 不存在或不可访问")
            self.operation_completed.emit(False)
            return
        
        self.progress_updated.emit(f"正在检查驱动器 {self.drive}...")
        
        # 构建命令参数
        cmd = ["chkdsk", self.drive]
        
        # 添加必要的选项
        if self.check_file_system:
            # 文件系统检查不需要额外参数
            pass
        
        if self.check_bad_sectors:
            cmd.append("/B")  # 检查坏扇区
        
        self.progress_updated.emit(f"运行命令: {' '.join(cmd)}")
        
        try:
            # 使用PlatformUtils运行chkdsk
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # 处理输出
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                
                line = line.strip()
                if line:
                    self.progress_updated.emit(line)
            
            proc.wait()
            
            if proc.returncode == 0:
                self.progress_updated.emit("磁盘检查成功完成")
                self.operation_completed.emit(True)
            else:
                self.progress_updated.emit(f"磁盘检查失败，返回代码 {proc.returncode}")
                self.operation_completed.emit(False)
        except FileNotFoundError:
            self.progress_updated.emit("错误: 找不到chkdsk命令。请确保您在Windows系统上运行此程序。")
            self.operation_completed.emit(False)
        except PermissionError:
            self.progress_updated.emit("错误: 权限被拒绝。请尝试以管理员身份运行程序。")
            self.operation_completed.emit(False)
        except Exception as e:
            self.progress_updated.emit(f"运行磁盘检查时出错: {str(e)}")
            self.operation_completed.emit(False)
    
    def repair_disk(self):
        """Check and repair disk errors"""
        self.progress_updated.emit(f"正在检查并修复驱动器 {self.drive}...")
        
        # Build command arguments
        cmd = ["chkdsk", self.drive, "/F"]  # /F to fix errors
        
        if self.check_bad_sectors:
            cmd.append("/R")  # Repair bad sectors
        
        self.progress_updated.emit(f"运行命令: {' '.join(cmd)}")
        self.progress_updated.emit("注意: 此操作可能需要系统重新启动")
        
        try:
            # 使用PlatformUtils运行chkdsk修复命令
            result = PlatformUtils.run_command(cmd)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.progress_updated.emit(line.strip())
                
                self.progress_updated.emit("磁盘修复已成功安排")
                self.operation_completed.emit(True)
            else:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.progress_updated.emit(line.strip())
                
                if result.stderr:
                    self.progress_updated.emit(f"错误: {result.stderr}")
                
                self.progress_updated.emit(f"磁盘修复失败，返回代码 {result.returncode}")
                self.operation_completed.emit(False)
        except Exception as e:
            self.progress_updated.emit(f"运行磁盘修复时出错: {str(e)}")
            self.operation_completed.emit(False)

class DiskCheckWidget(BaseComponent):
    def __init__(self, parent=None):
        # 初始化属性
        self.disk_worker = None
        
        # 调用父类构造函数
        super().__init__(parent)
    
    def get_translation(self, key, default=None):
        """Override get_translation to use the correct section name"""
        return self.settings.get_translation("disk_check", key, default)
    
    def setup_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Title
        self.title = QLabel(self.get_translation("title"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        self.main_layout.addWidget(self.title)
        
        # Description
        self.description = QLabel(self.get_translation("description"))
        self.description.setStyleSheet("font-size: 14px; color: #a0a0a0;")
        self.main_layout.addWidget(self.description)
        
        # Warning for non-Windows systems
        if not PlatformUtils.is_windows():
            warning_label = QLabel("⚠️ " + self.get_translation("windows_only", "磁盘检查功能仅在Windows系统上可用"))
            warning_label.setStyleSheet("color: #ff9900; font-weight: bold;")
            self.main_layout.addWidget(warning_label)
        
        # Drive selection
        self.drive_group = QGroupBox(self.get_translation("select_drive"))
        self.drive_group.setStyleSheet("""
            QGroupBox {
                color: #c0c0c0;
                font-weight: bold;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        drive_layout = QVBoxLayout(self.drive_group)
        
        # Drive dropdown
        self.drive_combo = QComboBox()
        self.drive_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: none;
                selection-background-color: #3a3a3a;
            }
        """)
        drive_layout.addWidget(self.drive_combo)
        
        self.main_layout.addWidget(self.drive_group)
        
        # Check types
        self.check_group = QGroupBox(self.get_translation("check_types"))
        self.check_group.setStyleSheet("""
            QGroupBox {
                color: #c0c0c0;
                font-weight: bold;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        check_layout = QVBoxLayout(self.check_group)
        
        # Checkboxes for check types
        self.file_system_cb = QCheckBox(self.get_translation("file_system"))
        self.file_system_cb.setChecked(True)
        self.file_system_cb.setStyleSheet("color: #e0e0e0;")
        check_layout.addWidget(self.file_system_cb)
        
        self.bad_sectors_cb = QCheckBox(self.get_translation("bad_sectors"))
        self.bad_sectors_cb.setChecked(False)
        self.bad_sectors_cb.setStyleSheet("color: #e0e0e0;")
        check_layout.addWidget(self.bad_sectors_cb)
        
        # Read-only mode checkbox
        self.read_only_cb = QCheckBox(self.get_translation("read_only"))
        self.read_only_cb.setChecked(self.settings.get_setting("disk_check_readonly", True))
        self.read_only_cb.setStyleSheet("color: #e0e0e0;")
        check_layout.addWidget(self.read_only_cb)
        
        self.main_layout.addWidget(self.check_group)
        
        # Warning label
        self.warning_label = QLabel(self.get_translation("warning"))
        self.warning_label.setStyleSheet("color: #ff9900; font-weight: bold;")
        self.main_layout.addWidget(self.warning_label)
        
        # Buttons
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        # Check button
        self.check_button = QPushButton(self.get_translation("check_button"))
        self.check_button.setStyleSheet("""
            QPushButton {
                background-color: #00a8ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0096e0;
            }
            QPushButton:pressed {
                background-color: #0085c7;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.check_button.clicked.connect(self.check_disk)
        self.check_button.setEnabled(PlatformUtils.is_windows())
        buttons_layout.addWidget(self.check_button)
        
        # Repair button
        self.repair_button = QPushButton(self.get_translation("repair_button"))
        self.repair_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5555;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff3333;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.repair_button.clicked.connect(self.repair_disk)
        self.repair_button.setEnabled(PlatformUtils.is_windows())
        buttons_layout.addWidget(self.repair_button)
        
        self.main_layout.addWidget(buttons_container)
        
        # Log output
        self.log_label = QLabel(self.get_translation("log_output"))
        self.log_label.setStyleSheet("color: #a0a0a0; margin-top: 10px;")
        self.main_layout.addWidget(self.log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        self.main_layout.addWidget(self.log_output)
        
        # Set a minimum size for the log
        self.log_output.setMinimumHeight(200)
        
        # 初始状态信息
        self.log_output.append(self.get_translation("ready_message", "磁盘检查工具准备就绪。请选择一个驱动器和检查选项，然后点击检查按钮。"))
        
        # 在初始化完所有UI元素后再填充驱动器列表
        if PlatformUtils.is_windows():
            self.populate_drives()
    
    def populate_drives(self):
        """填充驱动器下拉列表"""
        # 确保log_output已初始化
        if not hasattr(self, 'log_output') or self.log_output is None:
            print("警告: log_output 尚未初始化")
            return
        
        try:
            # 获取可用驱动器
            drives = PlatformUtils.get_drives()
            
            if drives:
                for drive in drives:
                    if drive.get("accessible", False):
                        # 添加可访问的驱动器
                        display_name = drive.get("display_name")
                        name = drive.get("name")
                        self.drive_combo.addItem(display_name, name)
                        
                        # 记录日志
                        drive_type = drive.get("type", "未知")
                        self.log_output.append(f"发现驱动器: {name} - 类型: {drive_type}")
                    else:
                        # 记录不可访问的驱动器
                        self.log_output.append(f"跳过不可访问的驱动器: {drive.get('name')}")
                
                # 默认选择第一个驱动器
                if self.drive_combo.count() > 0:
                    self.drive_combo.setCurrentIndex(0)
                    
                # 在Windows上，尝试选择C盘作为默认驱动器（如果可用）
                if PlatformUtils.is_windows():
                    c_drive_index = -1
                    for i in range(self.drive_combo.count()):
                        if self.drive_combo.itemData(i) == "C:":
                            c_drive_index = i
                            break
                            
                    if c_drive_index >= 0:
                        self.drive_combo.setCurrentIndex(c_drive_index)
            else:
                self.log_output.append("未找到可用驱动器")
                # 禁用检查按钮
                self.check_button.setEnabled(False)
                self.repair_button.setEnabled(False)
                
        except Exception as e:
            self.log_output.append(f"填充驱动器列表时出错: {str(e)}")
            print(f"填充驱动器列表时出错: {str(e)}")
    
    def check_disk(self):
        """检查磁盘错误"""
        # 获取选中的驱动器
        drive = self.drive_combo.currentText()
        
        # 验证驱动器
        if not drive:
            self.log_output.append("请选择一个驱动器")
            return
        
        # 额外验证：确保驱动器存在且可访问
        if not os.path.exists(drive):
            self.log_output.append(f"驱动器 {drive} 不存在或不可访问")
            return
        
        # 检查驱动器类型（仅适用于Windows）
        if platform.system() == "Windows":
            from ctypes import windll
            drive_type = windll.kernel32.GetDriveTypeW(f"{drive}\\")
            # 类型2是可移动驱动器，类型5是CD-ROM
            if drive_type in [2, 5]:
                self.log_output.append(f"警告: {drive} 是可移动驱动器或光驱，可能无法正确检查")
            # 类型0或1是未知或无效驱动器
            elif drive_type in [0, 1]:
                self.log_output.append(f"错误: {drive} 是无效驱动器")
                return
        
        # 获取检查类型
        check_file_system = self.file_system_cb.isChecked()
        check_bad_sectors = self.bad_sectors_cb.isChecked()
        read_only = self.read_only_cb.isChecked()
        
        if not check_file_system and not check_bad_sectors:
            self.log_output.append("请至少选择一种检查类型")
            return
        
        # 清除日志并禁用按钮
        self.log_output.clear()
        self.check_button.setEnabled(False)
        self.repair_button.setEnabled(False)
        
        self.log_output.append(f"开始对驱动器 {drive} 进行磁盘检查...")
        
        # 启动工作线程
        self.disk_worker = DiskCheckThread(drive, check_file_system, check_bad_sectors, read_only, "check")
        self.disk_worker.progress_updated.connect(self.update_log)
        self.disk_worker.operation_completed.connect(self.operation_completed)
        self.disk_worker.start()
    
    def repair_disk(self):
        """Repair disk errors"""
        # Get selected drive
        drive = self.drive_combo.currentText()
        
        if not drive:
            self.log_output.append("Please select a drive")
            return
        
        # Get check types
        check_file_system = self.file_system_cb.isChecked()
        check_bad_sectors = self.bad_sectors_cb.isChecked()
        read_only = self.read_only_cb.isChecked()
        
        if not check_file_system and not check_bad_sectors:
            self.log_output.append("Please select at least one check type")
            return
        
        # Clear log and disable buttons
        self.log_output.clear()
        self.check_button.setEnabled(False)
        self.repair_button.setEnabled(False)
        
        if read_only:
            self.log_output.append(f"Read-only mode is enabled. Running in check-only mode for drive {drive}...")
        else:
            self.log_output.append(f"Starting disk repair for drive {drive}...")
        
        # Start worker thread
        self.disk_worker = DiskCheckThread(drive, check_file_system, check_bad_sectors, read_only, "repair")
        self.disk_worker.progress_updated.connect(self.update_log)
        self.disk_worker.operation_completed.connect(self.operation_completed)
        self.disk_worker.start()
    
    def update_log(self, message):
        """Update the log output"""
        self.log_output.append(message)
        # Scroll to bottom
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def operation_completed(self, success):
        """Handle operation completion"""
        # Re-enable buttons
        self.check_button.setEnabled(True)
        self.repair_button.setEnabled(True)
        
        # Add completion message to log
        if success:
            self.log_output.append("✅ Operation completed")
        else:
            self.log_output.append("❌ Operation failed")
    
    def refresh_language(self):
        """Update all UI elements with new translations when language changes"""
        # Update all text elements
        self.title.setText(self.get_translation("title"))
        self.description.setText(self.get_translation("description"))
        self.drive_group.setTitle(self.get_translation("select_drive"))
        self.check_group.setTitle(self.get_translation("check_types"))
        self.file_system_cb.setText(self.get_translation("file_system"))
        self.bad_sectors_cb.setText(self.get_translation("bad_sectors"))
        self.read_only_cb.setText(self.get_translation("read_only"))
        self.warning_label.setText(self.get_translation("warning"))
        self.check_button.setText(self.get_translation("check_button"))
        self.repair_button.setText(self.get_translation("repair_button"))
        self.log_label.setText(self.get_translation("log_output"))
        
        # Animate to show that language has changed
        self._animate_refresh()
    
    def check_all_translations(self):
        """Check if all translation keys used in this component exist
        
        Raises:
            KeyError: If any translation key is missing
        """
        # Try to get all translations used in this component
        keys = [
            "title", "description", "select_drive", "check_types",
            "file_system", "bad_sectors", "read_only", "warning",
            "check_button", "repair_button", "log_output", "windows_only", "ready_message"
        ]
        
        for key in keys:
            # This will raise KeyError if the key doesn't exist
            self.get_translation(key, None) 