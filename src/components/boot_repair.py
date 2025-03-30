import os
import sys
import platform
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QProgressBar, QMessageBox,
                             QGroupBox, QRadioButton, QCheckBox, QTabWidget,
                             QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

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

class BootRepairWidget(QWidget):
    """Widget for boot repair operations"""
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.repair_thread = None
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(self.get_translation("title"))
        title_label.setObjectName("title_label")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(self.get_translation("description"))
        desc_label.setObjectName("desc_label")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("margin-bottom: 20px;")
        main_layout.addWidget(desc_label)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Boot Repair tab
        boot_repair_tab = QWidget()
        self.setup_boot_repair_tab(boot_repair_tab)
        tabs.addTab(boot_repair_tab, self.get_translation("title"))
        
        # Startup Manager tab
        startup_manager_tab = QWidget()
        self.setup_startup_manager_tab(startup_manager_tab)
        tabs.addTab(startup_manager_tab, self.get_translation("startup_manager"))
        
        main_layout.addWidget(tabs)
    
    def setup_boot_repair_tab(self, tab):
        # Tab layout
        layout = QVBoxLayout(tab)
        
        # Warning label
        warning_label = QLabel(self.get_translation("warning"))
        warning_label.setObjectName("warning_label")
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("color: #ff9900; margin-bottom: 20px;")
        layout.addWidget(warning_label)
        
        # Repair options group
        repair_group = QGroupBox(self.get_translation("repair_options"))
        repair_group.setObjectName("repair_group")
        repair_layout = QVBoxLayout(repair_group)
        
        # Radio buttons for repair options
        self.radio_mbr = QRadioButton(self.get_translation("mbr"))
        self.radio_mbr.setChecked(True)
        repair_layout.addWidget(self.radio_mbr)
        
        self.radio_bcd = QRadioButton(self.get_translation("bcd"))
        repair_layout.addWidget(self.radio_bcd)
        
        self.radio_bootmgr = QRadioButton(self.get_translation("bootmgr"))
        repair_layout.addWidget(self.radio_bootmgr)
        
        self.radio_winload = QRadioButton(self.get_translation("winload"))
        repair_layout.addWidget(self.radio_winload)
        
        self.radio_full = QRadioButton(self.get_translation("full"))
        repair_layout.addWidget(self.radio_full)
        
        layout.addWidget(repair_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat(f"%p% {self.get_translation('complete')}")
        layout.addWidget(self.progress_bar)
        
        # Log output
        log_group = QGroupBox(self.get_translation("log_output"))
        log_group.setObjectName("log_group")
        log_layout = QVBoxLayout(log_group)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(200)
        log_layout.addWidget(self.log_output)
        
        layout.addWidget(log_group)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        # Start repair button
        self.start_button = QPushButton(self.get_translation("start_repair"))
        self.start_button.setMinimumHeight(40)
        self.start_button.setStyleSheet("background-color: #00a8ff; color: white;")
        self.start_button.clicked.connect(self.start_repair)
        button_layout.addWidget(self.start_button)
        
        # Stop button
        self.stop_button = QPushButton(self.get_translation("stop"))
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_repair)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # Initial log message
        self.log_output.append("Boot repair tool ready. Select a repair option and click 'Start Repair'.")
    
    def setup_startup_manager_tab(self, tab):
        # Tab layout
        layout = QVBoxLayout(tab)
        
        # Description
        desc_label = QLabel(self.get_translation("startup_description"))
        desc_label.setObjectName("startup_desc_label")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("margin-bottom: 20px;")
        layout.addWidget(desc_label)
        
        # Startup items list
        list_group = QGroupBox(self.get_translation("startup_items"))
        list_group.setObjectName("startup_items_group")
        list_layout = QVBoxLayout(list_group)
        
        self.startup_list = QTableWidget()
        self.startup_list.setObjectName("startup_list")
        self.startup_list.setColumnCount(4)
        self.startup_list.setHorizontalHeaderLabels(["Name", "Publisher", "Status", "Impact"])
        self.startup_list.horizontalHeader().setStretchLastSection(True)
        self.startup_list.verticalHeader().setVisible(False)
        self.startup_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.startup_list.setSelectionMode(QTableWidget.SingleSelection)
        self.startup_list.setEditTriggers(QTableWidget.NoEditTriggers)
        list_layout.addWidget(self.startup_list)
        
        # Refresh button
        self.refresh_button = QPushButton(self.get_translation("refresh_list"))
        self.refresh_button.setObjectName("refresh_button")
        self.refresh_button.clicked.connect(self.refresh_startup_items)
        list_layout.addWidget(self.refresh_button)
        
        layout.addWidget(list_group)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.enable_button = QPushButton(self.get_translation("enable"))
        self.enable_button.setObjectName("enable_button")
        self.enable_button.clicked.connect(self.enable_startup_item)
        buttons_layout.addWidget(self.enable_button)
        
        self.disable_button = QPushButton(self.get_translation("disable"))
        self.disable_button.setObjectName("disable_button")
        self.disable_button.clicked.connect(self.disable_startup_item)
        buttons_layout.addWidget(self.disable_button)
        
        self.delete_button = QPushButton(self.get_translation("delete"))
        self.delete_button.setObjectName("delete_button")
        self.delete_button.clicked.connect(self.delete_startup_item)
        buttons_layout.addWidget(self.delete_button)
        
        layout.addLayout(buttons_layout)
        
        # Load startup items
        self.refresh_startup_items()
        
    def refresh_startup_items(self):
        """Refresh the list of startup items"""
        try:
            self.startup_list.setRowCount(0)
            
            if platform.system() != "Windows":
                # Add a note for non-Windows systems
                self.startup_list.setRowCount(1)
                self.startup_list.setItem(0, 0, QTableWidgetItem("Startup Manager is only available on Windows"))
                self.startup_list.setSpan(0, 0, 1, 4)
                return
            
            # Get startup items from registry
            import winreg
            
            # Registry keys for startup items
            reg_keys = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce")
            ]
            
            row = 0
            
            # Get startup items from registry
            for hkey, key_path in reg_keys:
                try:
                    with winreg.OpenKey(hkey, key_path) as key:
                        # Get number of values in the key
                        num_values = winreg.QueryInfoKey(key)[1]
                        
                        for i in range(num_values):
                            try:
                                # Get name and value of each entry
                                name, value, _ = winreg.EnumValue(key, i)
                                
                                # Add to table
                                self.startup_list.insertRow(row)
                                self.startup_list.setItem(row, 0, QTableWidgetItem(name))
                                self.startup_list.setItem(row, 1, QTableWidgetItem("N/A"))
                                self.startup_list.setItem(row, 2, QTableWidgetItem("Enabled"))
                                self.startup_list.setItem(row, 3, QTableWidgetItem("Low"))
                                
                                row += 1
                            except Exception as e:
                                print(f"Error getting startup item: {e}")
                except Exception as e:
                    print(f"Error opening registry key: {e}")
            
            # Get startup items from start menu
            startup_dir = os.path.join(
                os.environ.get('APPDATA', ''),
                r"Microsoft\Windows\Start Menu\Programs\Startup"
            )
            
            if os.path.exists(startup_dir):
                for item in os.listdir(startup_dir):
                    item_path = os.path.join(startup_dir, item)
                    if os.path.isfile(item_path) and item.endswith('.lnk'):
                        # Add to table
                        self.startup_list.insertRow(row)
                        self.startup_list.setItem(row, 0, QTableWidgetItem(item))
                        self.startup_list.setItem(row, 1, QTableWidgetItem("N/A"))
                        self.startup_list.setItem(row, 2, QTableWidgetItem("Enabled"))
                        self.startup_list.setItem(row, 3, QTableWidgetItem("Low"))
                        
                        row += 1
            
            if row == 0:
                # No startup items found
                self.startup_list.setRowCount(1)
                self.startup_list.setItem(0, 0, QTableWidgetItem("No startup items found"))
                self.startup_list.setSpan(0, 0, 1, 4)
        except Exception as e:
            print(f"Error refreshing startup items: {e}")
    
    def enable_startup_item(self):
        """Enable selected startup item"""
        if platform.system() != "Windows":
            QMessageBox.warning(self, "Not Supported", "Startup Manager is only available on Windows")
            return
        
        try:
            # Get selected row
            selected_row = self.startup_list.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "No Selection", "Please select a startup item to enable")
                return
            
            item_name = self.startup_list.item(selected_row, 0).text()
            
            # Simple simulation for now
            QMessageBox.information(self, "Startup Item Enabled", f"The startup item '{item_name}' has been enabled.")
            
            # Update status in table
            self.startup_list.item(selected_row, 2).setText("Enabled")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error enabling startup item: {str(e)}")
    
    def disable_startup_item(self):
        """Disable selected startup item"""
        if platform.system() != "Windows":
            QMessageBox.warning(self, "Not Supported", "Startup Manager is only available on Windows")
            return
        
        try:
            # Get selected row
            selected_row = self.startup_list.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "No Selection", "Please select a startup item to disable")
                return
            
            item_name = self.startup_list.item(selected_row, 0).text()
            
            # Simple simulation for now
            QMessageBox.information(self, "Startup Item Disabled", f"The startup item '{item_name}' has been disabled.")
            
            # Update status in table
            self.startup_list.item(selected_row, 2).setText("Disabled")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error disabling startup item: {str(e)}")
    
    def delete_startup_item(self):
        """Delete selected startup item"""
        if platform.system() != "Windows":
            QMessageBox.warning(self, "Not Supported", "Startup Manager is only available on Windows")
            return
        
        try:
            # Get selected row
            selected_row = self.startup_list.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "No Selection", "Please select a startup item to delete")
                return
            
            item_name = self.startup_list.item(selected_row, 0).text()
            
            # Confirm deletion
            reply = QMessageBox.question(self, "Confirm Deletion", 
                                       f"Are you sure you want to delete the startup item '{item_name}'?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Simple simulation for now
                QMessageBox.information(self, "Startup Item Deleted", f"The startup item '{item_name}' has been deleted.")
                
                # Remove from table
                self.startup_list.removeRow(selected_row)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error deleting startup item: {str(e)}")
    
    def start_repair(self):
        """Start the boot repair process"""
        # Determine which repair option is selected
        if self.radio_mbr.isChecked():
            repair_type = "mbr"
        elif self.radio_bcd.isChecked():
            repair_type = "bcd"
        elif self.radio_bootmgr.isChecked():
            repair_type = "bootmgr"
        elif self.radio_winload.isChecked():
            repair_type = "winload"
        elif self.radio_full.isChecked():
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
            self.repair_thread = BootRepairThread(repair_type)
            self.repair_thread.update_progress.connect(self.update_progress)
            self.repair_thread.update_log.connect(self.update_log)
            self.repair_thread.finished_operation.connect(self.repair_finished)
            self.repair_thread.start()
            
            # Update UI
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
    
    def stop_repair(self):
        """Stop the boot repair process"""
        if self.repair_thread and self.repair_thread.is_running:
            reply = QMessageBox.question(self, 'Confirm Stop', 
                                        "Are you sure you want to stop the repair process?\n"
                                        "This may leave your system in an inconsistent state.",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.repair_thread.terminate()
                self.repair_thread.wait()
                
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
        self.radio_mbr.setText(self.get_translation("fix_mbr", "Repair Master Boot Record (MBR)"))
        self.radio_bcd.setText(self.get_translation("rebuild_bcd", "Repair Boot Configuration Data (BCD)"))
        self.radio_bootmgr.setText(self.get_translation("fix_boot", "Repair Boot Manager"))
        
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
            