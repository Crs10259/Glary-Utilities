import os
import sys
import platform
import subprocess
import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QRadioButton, QTextEdit, QCheckBox, QButtonGroup, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from components.base_component import BaseComponent
from tools.dism_tools import DismThread

class DismToolWidget(BaseComponent):
    def __init__(self, parent=None):
        # Call parent class constructor
        super().__init__(parent)
        
        # Initialize attributes
        self.dism_worker = None
    
    def get_translation(self, key, default=None):
        """Override get_translation to use correct section name"""
        return self.settings.get_translation("dism_tool", key, default)
    
    def apply_theme(self):
        """Apply theme styles to component"""
        # Call parent class apply theme method, use unified style
        super().apply_theme()
        
    def setup_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Title
        self.title = QLabel(self.get_translation("title"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0; background-color: transparent;")
        self.main_layout.addWidget(self.title)
        
        # Description
        self.description = QLabel(self.get_translation("description"))
        self.description.setStyleSheet("font-size: 14px; color: #a0a0a0; background-color: transparent;")
        self.main_layout.addWidget(self.description)
        
        # Warning label for non-Windows systems (only show on non-Windows systems)
        if platform.system() != "Windows":
            warning_label = QLabel("⚠️ DISM is only available on Windows systems")
            warning_label.setStyleSheet("color: #ff9900; font-weight: bold; background-color: transparent;")
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
                background-color: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: transparent;
            }
        """)
        operations_layout = QVBoxLayout(self.operations_group)
        
        # Checkboxes for operation selection
        self.operation_group = QButtonGroup(self)
        self.operation_group.setObjectName("dism_operation_group")
       
        self.check_health_rb = QCheckBox(self.get_translation("check_health"))
        self.check_health_rb.setChecked(True)
        self.check_health_rb.setObjectName("dism_check_health")
        
        operations_layout.addWidget(self.check_health_rb)
        self.operation_group.addButton(self.check_health_rb)
        
        self.scan_health_rb = QCheckBox(self.get_translation("scan_health"))
        self.scan_health_rb.setObjectName("dism_scan_health")
        operations_layout.addWidget(self.scan_health_rb)
        self.operation_group.addButton(self.scan_health_rb)
        
        self.restore_health_rb = QCheckBox(self.get_translation("restore_health"))
        self.restore_health_rb.setObjectName("dism_restore_health")
        operations_layout.addWidget(self.restore_health_rb)
        self.operation_group.addButton(self.restore_health_rb)
        
        self.cleanup_image_rb = QCheckBox(self.get_translation("cleanup_image"))
        self.cleanup_image_rb.setObjectName("dism_cleanup_image")
        operations_layout.addWidget(self.cleanup_image_rb)
        self.operation_group.addButton(self.cleanup_image_rb)
        
        # Connect button group to handler
        self.operation_group.buttonClicked.connect(self.on_operation_changed)
        
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
        button_container.setStyleSheet("background-color: transparent;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(self.start_button)
        
        self.main_layout.addWidget(button_container)
        
        # Log output
        self.log_label = QLabel(self.get_translation("log_output"))
        self.log_label.setStyleSheet("color: #a0a0a0; margin-top: 10px; background-color: transparent;")
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
        
        # Set minimum height for log output
        self.log_output.setMinimumHeight(200)
        
        # Set layout
        self.setLayout(self.main_layout)
        
        # Ensure styles are applied correctly
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # Apply theme styles to radio buttons
        self.apply_theme()
    
    def start_operation(self):
        """Start selected DISM operation"""
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
        self.dism_worker = DismThread(operation)
        self.dism_worker.progress_updated.connect(self.update_log)
        self.dism_worker.operation_completed.connect(self.operation_completed)
        self.dism_worker.start()
    
    def update_log(self, message):
        """Update log output"""
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
            self.log_output.append("❌ 操作失败")
            self.log_output.append(message)

    def refresh_language(self):
        """使用新翻译更新UI元素"""
        self.title.setText(self.get_translation("title"))
        self.description.setText(self.get_translation("description"))
        self.operations_group.setTitle(self.get_translation("operations"))
        self.check_health_rb.setText(self.get_translation("check_health"))
        self.scan_health_rb.setText(self.get_translation("scan_health"))
        self.restore_health_rb.setText(self.get_translation("restore_health"))
        self.cleanup_image_rb.setText(self.get_translation("cleanup_image"))
        self.start_button.setText(self.get_translation("start_button"))
        self.log_label.setText(self.get_translation("log_output"))
        
        # Add animation to highlight changes
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
            # If key does not exist, raise KeyError
            self.get_translation(key, None)

    def on_operation_changed(self, button):
        """Handle operation selection change"""
        # Get current selected button
        selected_button = None
        
        if self.check_health_rb.isChecked():
            selected_button = self.check_health_rb
        elif self.scan_health_rb.isChecked():
            selected_button = self.scan_health_rb
        elif self.restore_health_rb.isChecked():
            selected_button = self.restore_health_rb
        elif self.cleanup_image_rb.isChecked():
            selected_button = self.cleanup_image_rb
            
        if selected_button:
            # Save user's choice to settings
            operation_key = selected_button.objectName()
            self.settings.set_setting("dism_operation", operation_key)
            self.settings.sync()  # Ensure settings are saved
