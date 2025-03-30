import os
import sys
import platform
import subprocess
import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QRadioButton, QTextEdit, QButtonGroup, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from components.base_component import BaseComponent

class DismThread(QThread):
    """Worker thread for DISM operations"""
    progress_updated = pyqtSignal(str)
    operation_completed = pyqtSignal(bool, str)
    
    def __init__(self, operation):
        super().__init__()
        self.operation = operation  # One of: check_health, scan_health, restore_health, cleanup_image
    
    def run(self):
        """Run the worker thread"""
        if platform.system() != "Windows":
            self.progress_updated.emit("DISM is only available on Windows")
            self.operation_completed.emit(False, "Operation not supported on this platform")
            return
        
        try:
            if self.operation == "check_health":
                self.check_health()
            elif self.operation == "scan_health":
                self.scan_health()
            elif self.operation == "restore_health":
                self.restore_health()
            elif self.operation == "cleanup_image":
                self.cleanup_image()
            else:
                self.progress_updated.emit(f"Unknown operation: {self.operation}")
                self.operation_completed.emit(False, "Unknown operation")
        except Exception as e:
            self.progress_updated.emit(f"Error performing operation: {str(e)}")
            self.operation_completed.emit(False, str(e))
    
    def check_health(self):
        """Check health of the Windows image"""
        self.progress_updated.emit("Checking Windows image health...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/CheckHealth"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def scan_health(self):
        """Scan health of the Windows image"""
        self.progress_updated.emit("Scanning Windows image health...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/ScanHealth"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def restore_health(self):
        """Restore health of the Windows image"""
        self.progress_updated.emit("Restoring Windows image health...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/RestoreHealth"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def cleanup_image(self):
        """Clean up the Windows image"""
        self.progress_updated.emit("Cleaning up Windows image...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/StartComponentCleanup"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def _process_output(self, proc):
        """Process the output of a DISM command"""
        success = True
        last_line = ""
        
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            
            line = line.strip()
            if line:
                self.progress_updated.emit(line)
                last_line = line
        
        proc.wait()
        
        if proc.returncode != 0:
            success = False
            last_line = f"Operation failed with return code {proc.returncode}"
        
        self.operation_completed.emit(success, last_line)

class DismToolWidget(BaseComponent):
    def __init__(self, settings, parent=None):
        self.worker = None
        super().__init__(settings, parent)
    
    def get_translation(self, key, default=None):
        """Override get_translation to use the correct section name"""
        return self.settings.get_translation("dism_tool", key, default)
    
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
        
        # Warning label for non-Windows systems
        if platform.system() != "Windows":
            warning_label = QLabel("⚠️ DISM is only available on Windows systems")
            warning_label.setStyleSheet("color: #ff9900; font-weight: bold;")
            self.main_layout.addWidget(warning_label)
        
        # Operations group
        self.operations_group = QGroupBox(self.get_translation("operations"))
        self.operations_group.setStyleSheet("""
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
        operations_layout = QVBoxLayout(self.operations_group)
        
        # Radio buttons for operation selection
        self.operation_group = QButtonGroup(self)
        
        self.check_health_rb = QRadioButton(self.get_translation("check_health"))
        self.check_health_rb.setChecked(True)
        self.check_health_rb.setStyleSheet("color: #e0e0e0;")
        operations_layout.addWidget(self.check_health_rb)
        self.operation_group.addButton(self.check_health_rb)
        
        self.scan_health_rb = QRadioButton(self.get_translation("scan_health"))
        self.scan_health_rb.setStyleSheet("color: #e0e0e0;")
        operations_layout.addWidget(self.scan_health_rb)
        self.operation_group.addButton(self.scan_health_rb)
        
        self.restore_health_rb = QRadioButton(self.get_translation("restore_health"))
        self.restore_health_rb.setStyleSheet("color: #e0e0e0;")
        operations_layout.addWidget(self.restore_health_rb)
        self.operation_group.addButton(self.restore_health_rb)
        
        self.cleanup_image_rb = QRadioButton(self.get_translation("cleanup_image"))
        self.cleanup_image_rb.setStyleSheet("color: #e0e0e0;")
        operations_layout.addWidget(self.cleanup_image_rb)
        self.operation_group.addButton(self.cleanup_image_rb)
        
        self.main_layout.addWidget(self.operations_group)
        
        # Start button
        self.start_button = QPushButton(self.get_translation("start_button"))
        self.start_button.setStyleSheet("""
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
        self.start_button.clicked.connect(self.start_operation)
        self.start_button.setEnabled(platform.system() == "Windows")
        
        # Button container (for right alignment)
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(self.start_button)
        
        self.main_layout.addWidget(button_container)
        
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
    
    def start_operation(self):
        """Start the selected DISM operation"""
        operation = None
        
        if self.check_health_rb.isChecked():
            operation = "check_health"
        elif self.scan_health_rb.isChecked():
            operation = "scan_health"
        elif self.restore_health_rb.isChecked():
            operation = "restore_health"
        elif self.cleanup_image_rb.isChecked():
            operation = "cleanup_image"
        
        if not operation:
            return
        
        # Clear log and disable start button
        self.log_output.clear()
        self.start_button.setEnabled(False)
        self.log_output.append(f"Starting operation: {operation}")
        
        # Start worker thread
        self.worker = DismThread(operation)
        self.worker.progress_updated.connect(self.update_log)
        self.worker.operation_completed.connect(self.operation_completed)
        self.worker.start()
    
    def update_log(self, message):
        """Update the log output"""
        self.log_output.append(message)
        # Scroll to bottom
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def operation_completed(self, success, message):
        """Handle operation completion"""
        # Re-enable start button
        self.start_button.setEnabled(True)
        
        # Add completion message to log
        if success:
            self.log_output.append("✅ Operation completed successfully")
            self.log_output.append(message)
        else:
            self.log_output.append("❌ Operation failed")
            self.log_output.append(message)

    def refresh_language(self):
        """Update UI elements with new translations"""
        self.title.setText(self.get_translation("title"))
        self.description.setText(self.get_translation("description"))
        self.operations_group.setTitle(self.get_translation("operations"))
        self.check_health_rb.setText(self.get_translation("check_health"))
        self.scan_health_rb.setText(self.get_translation("scan_health"))
        self.restore_health_rb.setText(self.get_translation("restore_health"))
        self.cleanup_image_rb.setText(self.get_translation("cleanup_image"))
        self.start_button.setText(self.get_translation("start_button"))
        self.log_label.setText(self.get_translation("log_output"))
        
        # Add animation to highlight the change
        super().refresh_language()

    def check_all_translations(self):
        """Check if all translation keys used in this component exist
        
        Raises:
            KeyError: If any translation key is missing
        """
        # Try to get all translations used in this component
        keys = [
            "title", "description", "operations", "check_health", 
            "scan_health", "restore_health", "cleanup_image",
            "start_button", "log_output"
        ]
        
        for key in keys:
            # This will raise KeyError if the key doesn't exist
            self.get_translation(key, None)

# Create an alias for backward compatibility
DISMToolWidget = DismToolWidget 