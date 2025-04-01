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
                             QHeaderView, QTableWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QDir

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


class VirusScanWidget(QWidget):
    """Widget for virus scanning operations"""
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.scan_thread = None
        self.custom_scan_targets = []
        self.detected_threats = []
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the virus scan UI components"""
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title and description
        title_label = QLabel(self.get_translation("title"))
        title_label.setObjectName("title_label")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        desc_label = QLabel(self.get_translation("description"))
        desc_label.setObjectName("desc_label")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Scan options
        scan_options_group = QGroupBox(self.get_translation("scan_types"))
        scan_options_group.setObjectName("scan_options_group")
        scan_options_layout = QVBoxLayout(scan_options_group)
        
        # Radio buttons for scan type
        self.radio_quick = QRadioButton(self.get_translation("quick_scan"))
        self.radio_quick.setObjectName("radio_quick")
        self.radio_quick.setChecked(True)
        scan_options_layout.addWidget(self.radio_quick)
        
        self.radio_full = QRadioButton(self.get_translation("full_scan"))
        self.radio_full.setObjectName("radio_full")
        scan_options_layout.addWidget(self.radio_full)
        
        self.radio_custom = QRadioButton(self.get_translation("custom_scan"))
        self.radio_custom.setObjectName("radio_custom")
        scan_options_layout.addWidget(self.radio_custom)
        
        # Custom scan targets
        self.custom_targets_widget = QWidget()
        self.custom_targets_widget.setObjectName("custom_targets_widget")
        self.custom_targets_layout = QVBoxLayout(self.custom_targets_widget)
        self.custom_targets_layout.setContentsMargins(20, 10, 0, 0)
        
        # Targets list
        self.targets_list = QListWidget()
        self.targets_list.setObjectName("targets_list")
        self.targets_list.setMaximumHeight(100)
        self.custom_targets_layout.addWidget(self.targets_list)
        
        # Targets buttons
        targets_buttons_layout = QHBoxLayout()
        self.add_target_button = QPushButton(self.get_translation("select_folder"))
        self.add_target_button.setObjectName("add_target_button")
        targets_buttons_layout.addWidget(self.add_target_button)
        
        self.remove_target_button = QPushButton(self.get_translation("remove", "Remove Selected"))
        self.remove_target_button.setObjectName("remove_target_button")
        targets_buttons_layout.addWidget(self.remove_target_button)
        
        targets_buttons_layout.addStretch()
        self.custom_targets_layout.addLayout(targets_buttons_layout)
        
        # Initially hide custom targets
        self.custom_targets_widget.setVisible(False)
        scan_options_layout.addWidget(self.custom_targets_widget)
        
        # Additional scan options
        options_layout = QVBoxLayout()
        self.option_archive = QCheckBox(self.get_translation("scan_archives", "Scan inside archives (zip, rar, etc.)"))
        self.option_archive.setObjectName("option_archive")
        options_layout.addWidget(self.option_archive)
        
        self.option_rootkits = QCheckBox(self.get_translation("scan_rootkits", "Scan for rootkits and bootkits"))
        self.option_rootkits.setObjectName("option_rootkits")
        options_layout.addWidget(self.option_rootkits)
        
        self.option_autofix = QCheckBox(self.get_translation("autofix", "Automatically attempt to fix detected issues"))
        self.option_autofix.setObjectName("option_autofix")
        options_layout.addWidget(self.option_autofix)
        
        scan_options_layout.addLayout(options_layout)
        layout.addWidget(scan_options_group)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                text-align: center;
                height: 20px;
                margin: 5px 0;
            }
            QProgressBar::chunk {
                background-color: #00a8ff;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Threats found
        threats_group = QGroupBox(self.get_translation("threats_found", "Detected Threats"))
        threats_group.setObjectName("threats_group")
        threats_layout = QVBoxLayout(threats_group)
        
        self.threats_table = QTableWidget(0, 3)
        self.threats_table.setObjectName("threats_table")
        self.threats_table.setHorizontalHeaderLabels([
            self.get_translation("file", "File"),
            self.get_translation("threat_type", "Threat Type"),
            self.get_translation("status", "Status")
        ])
        self.threats_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.threats_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.threats_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.threats_table.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
            }
            QTableWidget::item {
                color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #333333;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                padding: 4px;
            }
        """)
        threats_layout.addWidget(self.threats_table)
        layout.addWidget(threats_group)
        
        # Log output
        log_group = QGroupBox(self.get_translation("log_output", "Scan Log"))
        log_group.setObjectName("log_group")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setObjectName("log_text")
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.start_button = QPushButton(self.get_translation("scan_button"))
        self.start_button.setObjectName("start_button")
        self.start_button.setMinimumWidth(120)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #00a8ff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
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
                color: #aaaaaa;
            }
        """)
        buttons_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton(self.get_translation("stop_button"))
        self.stop_button.setObjectName("stop_button")
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumWidth(120)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
            QPushButton:pressed {
                background-color: #ac2925;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
            }
        """)
        buttons_layout.addWidget(self.stop_button)
        
        self.fix_button = QPushButton(self.get_translation("clean_threats"))
        self.fix_button.setObjectName("fix_button")
        self.fix_button.setEnabled(False)
        self.fix_button.setMinimumWidth(120)
        self.fix_button.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
            QPushButton:pressed {
                background-color: #3e8f3e;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
            }
        """)
        buttons_layout.addWidget(self.fix_button)
        
        layout.addLayout(buttons_layout)
        
        # Connect signals
        self.radio_custom.toggled.connect(self.custom_targets_widget.setVisible)
        self.add_target_button.clicked.connect(self.add_scan_target)
        self.remove_target_button.clicked.connect(self.remove_scan_target)
        self.start_button.clicked.connect(self.start_scan)
        self.stop_button.clicked.connect(self.stop_scan)
        self.fix_button.clicked.connect(self.fix_threats)
        
        # Initial setup
        self.custom_targets_widget.setVisible(False)
        self.log_text.append("Virus Scanner ready. Select scan type and click 'Start Scan'.")
        
    def add_scan_target(self):
        """Add file or folder to custom scan targets"""
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        
        # Allow selecting files or directories
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        for view in dialog.findChildren(QListWidget):
            view.setSelectionMode(QListWidget.ExtendedSelection)
        
        if dialog.exec_():
            selected = dialog.selectedFiles()
            for item in selected:
                if item not in self.custom_scan_targets:
                    self.custom_scan_targets.append(item)
                    self.targets_list.addItem(item)
    
    def remove_scan_target(self):
        """Remove selected target from custom scan list"""
        selected_items = self.targets_list.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            row = self.targets_list.row(item)
            item_text = item.text()
            
            self.targets_list.takeItem(row)
            if item_text in self.custom_scan_targets:
                self.custom_scan_targets.remove(item_text)
    
    def start_scan(self):
        """Start the virus scan process"""
        # Determine scan type
        if self.radio_quick.isChecked():
            scan_type = "quick"
        elif self.radio_full.isChecked():
            scan_type = "full"
        elif self.radio_custom.isChecked():
            scan_type = "custom"
            if not self.custom_scan_targets:
                QMessageBox.warning(self, "No Targets", 
                                  "Please select at least one file or folder to scan.")
                return
        
        # Collect scan options
        scan_options = {
            'scan_type': scan_type,
            'scan_targets': self.custom_scan_targets.copy() if scan_type == "custom" else [],
            'options': {
                'archives': self.option_archive.isChecked(),
                'rootkits': self.option_rootkits.isChecked(),
                'autofix': self.option_autofix.isChecked()
            }
        }
        
        # Confirmation dialog
        reply = QMessageBox.question(self, 'Start Virus Scan', 
                                   f"Start {scan_type} scan now?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:
            # Clear previous results
            self.log_text.clear()
            self.threats_table.setRowCount(0)
            self.detected_threats = []
            self.fix_button.setEnabled(False)
            
            # Reset progress bar
            self.progress_bar.setValue(0)
            
            # Create and start thread
            self.scan_thread = VirusScanThread(scan_options)
            self.scan_thread.update_progress.connect(self.update_progress)
            self.scan_thread.update_log.connect(self.update_log)
            self.scan_thread.found_threat.connect(self.add_threat)
            self.scan_thread.finished_scan.connect(self.scan_finished)
            self.scan_thread.start()
            
            # Update UI
            self.start_button.setEnabled(False)
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
        self.progress_bar.setValue(value)
    
    def update_log(self, message):
        """Update the log output"""
        self.log_text.append(message)
        # Scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def add_threat(self, file_path, threat_type):
        """Add a detected threat to the list"""
        row = self.threats_table.rowCount()
        self.threats_table.insertRow(row)
        
        # Create items with proper text
        file_item = QTableWidgetItem(os.path.basename(file_path))
        threat_item = QTableWidgetItem(threat_type)
        status_item = QTableWidgetItem("Detected")
        
        # Set tooltips
        file_item.setToolTip(file_path)
        
        # Set items in the table
        self.threats_table.setItem(row, 0, file_item)
        self.threats_table.setItem(row, 1, threat_item)
        self.threats_table.setItem(row, 2, status_item)
        
        # Store the full threat information for later use
        self.detected_threats.append((file_path, threat_type))
        
        # Enable the fix button if there are threats
        self.fix_button.setEnabled(True)
    
    def fix_threats(self):
        """Attempt to fix selected threats"""
        selected_items = self.threats_table.selectedIndexes()
        if not selected_items:
            # If nothing selected, ask if user wants to fix all
            reply = QMessageBox.question(self, 'Fix All Threats', 
                                       f"No threats selected. Do you want to fix all {self.threats_table.rowCount()} detected threats?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.No:
                return
                
            # Use all items
            selected_items = [self.threats_table.item(i.row(), i.column()) for i in selected_items]
        
        # Confirm action
        reply = QMessageBox.question(self, 'Confirm Action', 
                                   f"Attempt to fix {len(selected_items)} selected threats?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            for item in selected_items:
                file_path = item.text()
                
                # Simulate fixing the threat
                self.update_log(f"Attempting to fix: {file_path}")
                time.sleep(0.5)  # Simulate work
                
                # For demo purposes, randomly succeed or fail
                if random.random() < 0.8:  # 80% success rate
                    self.update_log(f"✓ Successfully fixed: {file_path}")
                    # Remove the fixed item
                    row = self.threats_table.index(self.threats_table.row(item), 0).row()
                    self.threats_table.removeRow(row)
                else:
                    self.update_log(f"✗ Failed to fix: {file_path}")
                    # Mark the item with a different color or icon to indicate failed fix attempt
                    item.setForeground(Qt.red)
                
            # Update the fix button state
            self.fix_button.setEnabled(self.threats_table.rowCount() > 0)
            
            # Show summary
            QMessageBox.information(self, "Fix Complete", 
                                   f"Fix attempt completed.\n\n"
                                   f"Remaining threats: {self.threats_table.rowCount()}")
    
    def scan_finished(self, success, message, threats_found):
        """Handle scan completion"""
        # Re-enable the start button
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Set progress to 100%
        self.progress_bar.setValue(100)
        
        # Show message
        if success:
            if threats_found > 0:
                QMessageBox.warning(self, "Scan Complete", 
                                   f"{message}\n\n"
                                   f"Found {threats_found} potential threats.")
            else:
                QMessageBox.information(self, "Scan Complete", 
                                      f"{message}\n\n"
                                      "No threats were detected.")
        else:
            QMessageBox.warning(self, "Scan Incomplete", message)
        
        # Add final log message
        self.update_log(f"Scan process completed. Result: {'Success' if success else 'Incomplete'}")
        self.update_log(f"Total threats found: {threats_found}")
        
        # Enable fix button if threats found
        self.fix_button.setEnabled(threats_found > 0)

    def get_translation(self, key, default=None):
        """Override get_translation to use the correct section name"""
        return self.settings.get_translation("virus_scan", key, default)
    
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