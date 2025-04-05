import os
import sys
import platform
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QCheckBox, QTextEdit, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from components.base_component import BaseComponent

class NetworkResetThread(QThread):
    """Worker thread for network reset operations"""
    progress_updated = pyqtSignal(str)
    operation_completed = pyqtSignal(bool)
    
    def __init__(self, operations):
        super().__init__()
        self.operations = operations  # Dictionary of operations to perform
    
    def run(self):
        """Run the worker thread"""
        success = True
        
        if platform.system() != "Windows":
            self.progress_updated.emit("Network reset is only supported on Windows")
            self.operation_completed.emit(False)
            return
        
        try:
            # Flush DNS
            if self.operations.get("flush_dns", False):
                self.progress_updated.emit("Flushing DNS cache...")
                success = success and self.flush_dns()
            
            # Reset Winsock
            if self.operations.get("reset_winsock", False):
                self.progress_updated.emit("Resetting Winsock...")
                success = success and self.reset_winsock()
            
            # Reset TCP/IP
            if self.operations.get("reset_tcp_ip", False):
                self.progress_updated.emit("Resetting TCP/IP stack...")
                success = success and self.reset_tcp_ip()
            
            # Reset Firewall
            if self.operations.get("reset_firewall", False):
                self.progress_updated.emit("Resetting firewall settings...")
                success = success and self.reset_firewall()
            
            self.progress_updated.emit("Network reset operations completed")
            self.operation_completed.emit(success)
        except Exception as e:
            self.progress_updated.emit(f"Error performing network reset: {str(e)}")
            self.operation_completed.emit(False)
    
    def flush_dns(self):
        """Flush DNS cache"""
        try:
            # Run ipconfig /flushdns
            proc = subprocess.run(["ipconfig", "/flushdns"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 check=True)
            
            self.progress_updated.emit(proc.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.progress_updated.emit(f"Error flushing DNS: {e.stderr}")
            return False
    
    def reset_winsock(self):
        """Reset Winsock catalog"""
        try:
            # Run netsh winsock reset
            proc = subprocess.run(["netsh", "winsock", "reset"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 check=True)
            
            self.progress_updated.emit(proc.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.progress_updated.emit(f"Error resetting Winsock: {e.stderr}")
            return False
    
    def reset_tcp_ip(self):
        """Reset TCP/IP stack"""
        try:
            # Run netsh int ip reset
            proc = subprocess.run(["netsh", "int", "ip", "reset"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 check=True)
            
            self.progress_updated.emit(proc.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.progress_updated.emit(f"Error resetting TCP/IP: {e.stderr}")
            return False
    
    def reset_firewall(self):
        """Reset Windows Firewall settings"""
        try:
            # Run netsh advfirewall reset
            proc = subprocess.run(["netsh", "advfirewall", "reset"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 check=True)
            
            self.progress_updated.emit(proc.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.progress_updated.emit(f"Error resetting firewall: {e.stderr}")
            return False

class NetworkResetWidget(BaseComponent):
    def __init__(self, parent=None):
        # 初始化属性
        self.reset_worker = None
        
        # 调用父类构造函数
        super().__init__(parent)
    
    def setup_ui(self):
        """设置UI"""
        # 清除旧布局（如果有）
        if self.layout():
            # 清除旧布局中的所有部件
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # 删除旧布局
            old_layout = self.layout()
            QWidget().setLayout(old_layout)  # 将旧布局设置给一个临时部件以便删除
        
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
        warning_label = QLabel(self.get_translation("warning"))
        warning_label.setStyleSheet("color: #ff9900; font-weight: bold; background-color: transparent;")
        main_layout.addWidget(warning_label)
        
        # Operations group
        operations_group = QGroupBox(self.get_translation("operations"))
        operations_group.setStyleSheet("""
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
        operations_layout = QVBoxLayout(operations_group)
        
        # Checkboxes for operation selection
        self.flush_dns_cb = QCheckBox(self.get_translation("flush_dns"))
        self.flush_dns_cb.setChecked(True)
        self.flush_dns_cb.setStyleSheet("color: #e0e0e0; background-color: transparent;")
        operations_layout.addWidget(self.flush_dns_cb)
        
        self.reset_winsock_cb = QCheckBox(self.get_translation("reset_winsock"))
        self.reset_winsock_cb.setChecked(True)
        self.reset_winsock_cb.setStyleSheet("color: #e0e0e0; background-color: transparent;")
        operations_layout.addWidget(self.reset_winsock_cb)
        
        self.reset_tcp_ip_cb = QCheckBox(self.get_translation("reset_tcp_ip"))
        self.reset_tcp_ip_cb.setChecked(True)
        self.reset_tcp_ip_cb.setStyleSheet("color: #e0e0e0; background-color: transparent;")
        operations_layout.addWidget(self.reset_tcp_ip_cb)
        
        self.reset_firewall_cb = QCheckBox(self.get_translation("reset_firewall"))
        self.reset_firewall_cb.setChecked(False)
        self.reset_firewall_cb.setStyleSheet("color: #e0e0e0; background-color: transparent;")
        operations_layout.addWidget(self.reset_firewall_cb)
        
        main_layout.addWidget(operations_group)
        
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
        log_label = QLabel(self.get_translation("log_output"))
        log_label.setStyleSheet("color: #a0a0a0; margin-top: 10px; background-color: transparent;")
        main_layout.addWidget(log_label)
        
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
        
        # 确保样式正确应用
        self.setAttribute(Qt.WA_StyledBackground, True)
    
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