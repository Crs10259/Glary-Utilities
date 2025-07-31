import os
import sys
import platform
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QCheckBox, QTextEdit, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from components.base_component import BaseComponent
from tools.network_reset import NetworkResetThread

class NetworkResetWidget(BaseComponent):
    def __init__(self, parent=None):
        # Initialize attributes
        self.reset_worker = None
        
        # Call parent class constructor
        super().__init__(parent)
    
    def setup_ui(self):
        """Setup UI"""
        # Create layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        self.title = QLabel(self.get_translation("title"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0; background-color: transparent;")
        main_layout.addWidget(self.title)
        
        # Description
        self.description = QLabel(self.get_translation("description"))
        self.description.setStyleSheet("font-size: 14px; color: #a0a0a0; background-color: transparent;")
        main_layout.addWidget(self.description)
        
        # Warning for non-Windows systems
        if platform.system() != "Windows":
            warning_label = QLabel("⚠️ Network reset is only available on Windows systems")
            warning_label.setStyleSheet("color: #ff9900; font-weight: bold; background-color: transparent;")
            main_layout.addWidget(warning_label)
        
        # Warning label
        self.warning_label = QLabel(self.get_translation("warning"))
        self.warning_label.setObjectName("warning_label")
        self.warning_label.setStyleSheet("color: #ff9900; font-weight: bold; background-color: transparent;")
        main_layout.addWidget(self.warning_label)
        
        # Operations group
        self.operations_group = QGroupBox(self.get_translation("operations"))
        self.operations_group.setObjectName("operations_group")
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
        self.flush_dns_cb = QCheckBox(self.get_translation("flush_dns"))
        self.flush_dns_cb.setObjectName("network_flush_dns")
        self.flush_dns_cb.setChecked(True)
        operations_layout.addWidget(self.flush_dns_cb)
        
        self.reset_winsock_cb = QCheckBox(self.get_translation("reset_winsock"))
        self.reset_winsock_cb.setObjectName("network_reset_winsock")
        self.reset_winsock_cb.setChecked(True)
        operations_layout.addWidget(self.reset_winsock_cb)
        
        self.reset_tcp_ip_cb = QCheckBox(self.get_translation("reset_tcp_ip"))
        self.reset_tcp_ip_cb.setObjectName("network_reset_tcp_ip")
        self.reset_tcp_ip_cb.setChecked(False)
        operations_layout.addWidget(self.reset_tcp_ip_cb)
        
        self.reset_firewall_cb = QCheckBox(self.get_translation("reset_firewall"))
        self.reset_firewall_cb.setObjectName("network_reset_firewall")
        self.reset_firewall_cb.setChecked(False)
        operations_layout.addWidget(self.reset_firewall_cb)
        
        main_layout.addWidget(self.operations_group)
        
        # Add some spacing
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))
        
        # Reset button
        self.reset_button = QPushButton(self.get_translation("reset_button"))
        self.reset_button.setStyleSheet("""
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
        self.reset_button.clicked.connect(self.reset_network)
        self.reset_button.setEnabled(platform.system() == "Windows")
        
        # Button container (for right alignment)
        button_container = QWidget()
        button_container.setStyleSheet("background-color: transparent;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(self.reset_button)
        
        main_layout.addWidget(button_container)
        
        # Log output
        self.log_label = QLabel(self.get_translation("log_output"))
        self.log_label.setObjectName("log_label")
        self.log_label.setStyleSheet("color: #a0a0a0; margin-top: 10px; background-color: transparent;")
        main_layout.addWidget(self.log_label)
        
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
        main_layout.addWidget(self.log_output)
        
        # Set a minimum size for the log
        self.log_output.setMinimumHeight(200)
        
        # Set the layout
        self.setLayout(main_layout)
        
        # Ensure styles are applied correctly
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # Apply theme styles
        self.apply_theme()
    
    def reset_network(self):
        """Reset network settings based on selected operations"""
        # Get selected operations
        operations = {
            "flush_dns": self.flush_dns_cb.isChecked(),
            "reset_winsock": self.reset_winsock_cb.isChecked(),
            "reset_tcp_ip": self.reset_tcp_ip_cb.isChecked(),
            "reset_firewall": self.reset_firewall_cb.isChecked()
        }
        
        # Check if any operation is selected
        if not any(operations.values()):
            self.log_output.append("Please select at least one operation")
            return
        
        # Clear log and disable reset button
        self.log_output.clear()
        self.reset_button.setEnabled(False)
        self.log_output.append("Starting network reset operations...")
        
        # Start worker thread
        self.reset_worker = NetworkResetThread(operations)
        self.reset_worker.progress_updated.connect(self.update_log)
        self.reset_worker.operation_completed.connect(self.operation_completed)
        self.reset_worker.start()
    
    def update_log(self, message):
        """Update the log output"""
        self.log_output.append(message)
        # Scroll to bottom
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def operation_completed(self, success):
        """Handle operation completion"""
        # Re-enable reset button
        self.reset_button.setEnabled(True)
        
        # Add completion message to log
        if success:
            self.log_output.append("✅ Network reset operations completed successfully")
            self.log_output.append("Note: Some changes may require a system restart to take effect")
        else:
            self.log_output.append("❌ Some network reset operations failed")
            self.log_output.append("Please check the log for details")

    def get_translation(self, key, default=None):
        """Override get_translation to use the correct section name"""
        return self.settings.get_translation("network_reset", key, default) 

    def apply_theme(self):
        """Apply theme styles to component"""
        # First call parent class apply theme method
        super().apply_theme()
        
        # Get current theme colors
        theme_name = self.settings.get_setting("theme", "dark")
        theme_data = self.settings.load_theme(theme_name)
        
        if theme_data and "colors" in theme_data:
            bg_color = theme_data["colors"].get("bg_color", "#2d2d2d")
            text_color = theme_data["colors"].get("text_color", "#dcdcdc")
            accent_color = theme_data["colors"].get("accent_color", "#007acc")
            
            # Create checkbox styles
            checkbox_style = f"""
                QCheckBox {{ 
                    color: {text_color}; 
                    background-color: transparent; 
                    spacing: 5px; 
                    padding: 5px; 
                    font-size: 13px; 
                    min-height: 20px; 
                    margin: 2px 0; 
                }}
                
                QCheckBox::indicator {{ 
                    width: 16px; 
                    height: 16px; 
                    border: 2px solid {accent_color}; 
                    border-radius: 3px; 
                    background-color: {bg_color}; 
                }}
                
                QCheckBox::indicator:unchecked {{ 
                    background-color: {bg_color}; 
                }}
                
                QCheckBox::indicator:checked {{ 
                    background-color: {accent_color}; 
                }}
                
                QCheckBox::indicator:unchecked:hover {{ 
                    border-color: {self._lighten_color(accent_color, 20)}; 
                    background-color: {self._lighten_color(bg_color, 10)}; 
                }}
                
                QCheckBox::indicator:checked:hover {{ 
                    background-color: {self._lighten_color(accent_color, 10)}; 
                }}
            """
            
            # Apply to various checkboxes
            if hasattr(self, 'flush_dns_cb'):
                self.flush_dns_cb.setStyleSheet(checkbox_style)
            if hasattr(self, 'reset_winsock_cb'):
                self.reset_winsock_cb.setStyleSheet(checkbox_style)
            if hasattr(self, 'reset_tcp_ip_cb'):
                self.reset_tcp_ip_cb.setStyleSheet(checkbox_style)
            if hasattr(self, 'reset_firewall_cb'):
                self.reset_firewall_cb.setStyleSheet(checkbox_style)

    def refresh_language(self):
        """Update UI texts when language changes"""
        # Main headings
        self.title.setText(self.get_translation("title"))
        self.description.setText(self.get_translation("description"))
        # Warning and group titles
        self.warning_label.setText(self.get_translation("warning"))
        self.operations_group.setTitle(self.get_translation("operations"))
        self.log_label.setText(self.get_translation("log_output"))

        # Checkbox texts
        self.flush_dns_cb.setText(self.get_translation("flush_dns"))
        self.reset_winsock_cb.setText(self.get_translation("reset_winsock"))
        self.reset_tcp_ip_cb.setText(self.get_translation("reset_tcp_ip"))
        self.reset_firewall_cb.setText(self.get_translation("reset_firewall"))

        # Buttons
        self.reset_button.setText(self.get_translation("reset_button"))

        # Simple visual cue
        self._animate_refresh()
