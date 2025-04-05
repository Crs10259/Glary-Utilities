import os
import sys
import platform
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QProgressBar, QMessageBox,
                             QGroupBox, QRadioButton, QCheckBox, QTabWidget,
                             QTableWidget, QTableWidgetItem, QFrame, QSizePolicy,
                             QSpacerItem, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from components.base_component import BaseComponent
from PyQt5.QtGui import QBrush, QColor

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
        # 创建布局但不直接设置为self的布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题
        self.title = QLabel(self.get_translation("title", "启动修复工具"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(self.title)
        
        # 描述
        self.description = QLabel(self.get_translation("description", "此工具可以修复常见的Windows启动问题。"))
        self.description.setStyleSheet("font-size: 14px;")
        self.description.setWordWrap(True)
        main_layout.addWidget(self.description)
        
        # 选项卡
        self.tabs = QTabWidget()
        
        # 创建主修复选项卡
        self.repair_tab = QWidget()
        repair_layout = QVBoxLayout(self.repair_tab)
        
        # 修复选项组
        self.options_group = QGroupBox(self.get_translation("repair_options", "修复选项"))
        options_layout = QVBoxLayout(self.options_group)
        
        # 修复选项单选按钮
        self.repair_mbr_rb = QRadioButton(self.get_translation("repair_mbr", "修复主引导记录 (MBR)"))
        self.repair_mbr_rb.setChecked(True)
        options_layout.addWidget(self.repair_mbr_rb)
        
        self.repair_bcd_rb = QRadioButton(self.get_translation("repair_bcd", "修复启动配置数据 (BCD)"))
        options_layout.addWidget(self.repair_bcd_rb)
        
        self.repair_bootmgr_rb = QRadioButton(self.get_translation("repair_bootmgr", "修复 bootmgr"))
        options_layout.addWidget(self.repair_bootmgr_rb)
        
        self.repair_winload_rb = QRadioButton(self.get_translation("repair_winload", "修复 winload.exe"))
        options_layout.addWidget(self.repair_winload_rb)
        
        self.full_repair_rb = QRadioButton(self.get_translation("full_repair", "完整启动修复"))
        options_layout.addWidget(self.full_repair_rb)
        
        # 将选项组添加到修复选项卡
        repair_layout.addWidget(self.options_group)
        
        # 修复按钮
        self.repair_button = QPushButton(self.get_translation("start_repair", "开始修复"))
        self.repair_button.clicked.connect(self.start_repair)
        
        # 停止按钮
        self.stop_button = QPushButton(self.get_translation("stop_repair", "停止修复"))
        self.stop_button.clicked.connect(self.stop_repair)
        self.stop_button.setEnabled(False)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.repair_button)
        button_layout.addWidget(self.stop_button)
        
        repair_layout.addLayout(button_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        repair_layout.addWidget(self.progress)
        
        # 日志输出
        self.log_label = QLabel(self.get_translation("log_output", "日志输出"))
        repair_layout.addWidget(self.log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        repair_layout.addWidget(self.log_output)
        
        # 创建启动管理选项卡
        self.startup_tab = QWidget()
        self.setup_startup_manager_tab(self.startup_tab)
        
        # 将选项卡添加到选项卡控件
        self.tabs.addTab(self.repair_tab, self.get_translation("repair_tab", "启动修复"))
        self.tabs.addTab(self.startup_tab, self.get_translation("startup_tab", "启动项管理"))
        
        # 将选项卡控件添加到主布局
        main_layout.addWidget(self.tabs)
        
        # 最后设置布局
        self.setLayout(main_layout)
        
        # 添加初始消息
        self.log_output.append(self.get_translation("ready_message", "准备执行启动修复操作。选择选项并点击开始修复。"))
    
    def setup_startup_manager_tab(self, tab):
        """设置启动项管理选项卡"""
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 描述
        description = QLabel(self.get_translation("startup_desc", "管理Windows启动项，启用或禁用自启动程序。"))
        description.setStyleSheet("font-size: 14px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # 启动项表格
        self.startup_table = QTableWidget()
        self.startup_table.setColumnCount(4)
        self.startup_table.setHorizontalHeaderLabels([
            self.get_translation("startup_name", "名称"),
            self.get_translation("startup_path", "路径"),
            self.get_translation("startup_status", "状态"),
            self.get_translation("startup_type", "类型")
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
        self.refresh_button = QPushButton(self.get_translation("refresh", "刷新列表"))
        self.refresh_button.clicked.connect(self.refresh_startup_items)
        button_layout.addWidget(self.refresh_button)
        
        # 启用/禁用按钮
        self.enable_button = QPushButton(self.get_translation("enable", "启用"))
        self.enable_button.clicked.connect(self.enable_startup_item)
        button_layout.addWidget(self.enable_button)
        
        self.disable_button = QPushButton(self.get_translation("disable", "禁用"))
        self.disable_button.clicked.connect(self.disable_startup_item)
        button_layout.addWidget(self.disable_button)
        
        # 删除按钮
        self.delete_button = QPushButton(self.get_translation("delete", "删除"))
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
        if self.repair_mbr_rb.isChecked():
            repair_type = "mbr"
        elif self.repair_bcd_rb.isChecked():
            repair_type = "bcd"
        elif self.repair_bootmgr_rb.isChecked():
            repair_type = "bootmgr"
        elif self.repair_winload_rb.isChecked():
            repair_type = "winload"
        elif self.full_repair_rb.isChecked():
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
            self.progress.setValue(0)
            
            # Create and start thread
            self.boot_worker = BootRepairThread(repair_type)
            self.boot_worker.update_progress.connect(self.update_progress)
            self.boot_worker.update_log.connect(self.update_log)
            self.boot_worker.finished_operation.connect(self.repair_finished)
            self.boot_worker.start()
            
            # Update UI
            self.repair_button.setEnabled(False)
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
        self.progress.setValue(value)
    
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
        self.repair_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Set progress to 100%
        self.progress.setValue(100)
        
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
        """Refresh all UI elements with current language translations"""
        # 查找标题和描述标签
        title_label = self.findChild(QLabel, "title_label")
        if title_label:
            title_label.setText(self.get_translation("title"))
            
        desc_label = self.findChild(QLabel, "desc_label")
        if desc_label:
            desc_label.setText(self.get_translation("description"))

        # 查找和更新选项卡小部件
        tabs = self.findChild(QTabWidget)
        if tabs:
            # 更新选项卡标题
            tabs.setTabText(0, self.get_translation("title", "Boot Repair"))
            tabs.setTabText(1, self.get_translation("startup_manager", "Startup Manager"))
        
        # 更新警告标签
        warning_label = self.findChild(QLabel, "warning_label")
        if warning_label:
            warning_label.setText(self.get_translation("warning"))
        
        # 更新修复选项组
        repair_group = self.findChild(QGroupBox, "repair_group")
        if repair_group:
            repair_group.setTitle(self.get_translation("operations", "Repair Options"))
        
        # 更新单选按钮
        self.repair_mbr_rb.setText(self.get_translation("fix_mbr", "Repair Master Boot Record (MBR)"))
        self.repair_bcd_rb.setText(self.get_translation("rebuild_bcd", "Repair Boot Configuration Data (BCD)"))
        self.repair_bootmgr_rb.setText(self.get_translation("fix_boot", "Repair Boot Manager"))
        
        # 更新按钮
        self.repair_button.setText(self.get_translation("repair_button", "Start Repair"))
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
            