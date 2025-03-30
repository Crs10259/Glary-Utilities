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
        if platform.system() != "Windows":
            self.progress_updated.emit("Disk check is only supported on Windows")
            self.operation_completed.emit(False)
            return
        
        try:
            if self.operation == "check":
                self.check_disk()
            elif self.operation == "repair":
                if self.read_only:
                    self.progress_updated.emit("Read-only mode is enabled. Running in check-only mode...")
                    self.check_disk()
                else:
                    self.repair_disk()
            else:
                self.progress_updated.emit(f"Unknown operation: {self.operation}")
                self.operation_completed.emit(False)
        except Exception as e:
            self.progress_updated.emit(f"Error performing operation: {str(e)}")
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
            # 运行chkdsk
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
        self.progress_updated.emit(f"Checking and repairing drive {self.drive}...")
        
        # Build command arguments
        cmd = ["chkdsk", self.drive, "/F"]  # /F to fix errors
        
        if self.check_bad_sectors:
            cmd.append("/R")  # Repair bad sectors
        
        self.progress_updated.emit(f"Running command: {' '.join(cmd)}")
        self.progress_updated.emit("Note: This operation may require a system restart")
        
        try:
            # Run chkdsk with repair options
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            # Process output
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                
                line = line.strip()
                if line:
                    self.progress_updated.emit(line)
            
            proc.wait()
            
            if proc.returncode == 0:
                self.progress_updated.emit("Disk repair scheduled successfully")
                self.operation_completed.emit(True)
            else:
                self.progress_updated.emit(f"Disk repair failed with return code {proc.returncode}")
                self.operation_completed.emit(False)
        except Exception as e:
            self.progress_updated.emit(f"Error running disk repair: {str(e)}")
            self.operation_completed.emit(False)

class DiskCheckWidget(BaseComponent):
    def __init__(self, settings, parent=None):
        self.worker = None
        # 创建 log_output 属性
        self.log_output = None
        super().__init__(settings, parent)
    
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
        if platform.system() != "Windows":
            warning_label = QLabel("⚠️ Disk check is only available on Windows systems")
            warning_label.setStyleSheet("color: #ff9900; font-weight: bold;")
            self.main_layout.addWidget(warning_label)
        
        # Drive selection
        self.drive_group = QGroupBox(self.get_translation("select_drive"))
        self.drive_group.setStyleSheet("""
            QGroupBox {
                color: #c0c0c0;
                font-weight: bold;
                border: none;
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
                border: none;
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
            QComboBox::down-arrow {
                image: url(assets/images/down-arrow.png);
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
                border: none;
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
        self.check_button.setEnabled(platform.system() == "Windows")
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
        self.repair_button.setEnabled(platform.system() == "Windows")
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
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        self.main_layout.addWidget(self.log_output)
        
        # Set a minimum size for the log
        self.log_output.setMinimumHeight(200)
        
        # 在初始化完所有UI元素后再填充驱动器列表
        if platform.system() == "Windows":
            self.populate_drives()
    
    def populate_drives(self):
        """填充驱动器下拉列表"""
        # 确保log_output已初始化
        if not hasattr(self, 'log_output') or self.log_output is None:
            print("警告: log_output 尚未初始化")
            return
        
        try:
            # 获取可用驱动器
            available_drives = []
            
            # 对于Windows，获取驱动器字母
            if platform.system() == "Windows":
                from ctypes import windll
                import string
                
                # 获取驱动器位掩码
                bitmask = windll.kernel32.GetLogicalDrives()
                
                # 将位掩码转换为驱动器字母并验证每个驱动器
                for letter in string.ascii_uppercase:  # A到Z
                    drive = f"{letter}:"
                    if bitmask & (1 << (ord(letter) - ord('A'))):
                        # 额外检查：确保驱动器真的存在且可访问
                        try:
                            drive_path = f"{drive}\\"
                            drive_type = windll.kernel32.GetDriveTypeW(drive_path)
                            
                            # 添加所有类型的驱动器，但标记类型
                            drive_type_name = "未知"
                            if drive_type == 2:
                                drive_type_name = "可移动"
                            elif drive_type == 3:
                                drive_type_name = "固定"
                            elif drive_type == 4:
                                drive_type_name = "网络"
                            elif drive_type == 5:
                                drive_type_name = "光盘"
                            
                            # 检查磁盘是否可访问
                            accessible = False
                            try:
                                if os.path.exists(drive):
                                    # 尝试读取磁盘根目录
                                    os.listdir(drive)
                                    accessible = True
                            except Exception:
                                pass
                            
                            if accessible:
                                # 只添加可访问的驱动器
                                available_drives.append((drive, f"{drive} ({drive_type_name})"))
                                self.log_output.append(f"发现驱动器: {drive} - 类型: {drive_type_name}")
                            else:
                                self.log_output.append(f"跳过不可访问的驱动器: {drive}")
                        except Exception as e:
                            self.log_output.append(f"检查驱动器 {drive} 时出错: {str(e)}")
            
            # 填充下拉列表
            if available_drives:
                for drive, display_text in available_drives:
                    self.drive_combo.addItem(display_text, drive)
                
                # 默认选择C盘（如果可用）
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
        self.worker = DiskCheckThread(drive, check_file_system, check_bad_sectors, read_only, "check")
        self.worker.progress_updated.connect(self.update_log)
        self.worker.operation_completed.connect(self.operation_completed)
        self.worker.start()
    
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
        self.worker = DiskCheckThread(drive, check_file_system, check_bad_sectors, read_only, "repair")
        self.worker.progress_updated.connect(self.update_log)
        self.worker.operation_completed.connect(self.operation_completed)
        self.worker.start()
    
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
            "check_button", "repair_button", "log_output"
        ]
        
        for key in keys:
            # This will raise KeyError if the key doesn't exist
            self.get_translation(key, None) 