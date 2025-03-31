import os
import sys
import platform
import psutil
import socket
import uuid
import subprocess
import shutil
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QTabWidget, QGroupBox, QFormLayout, QScrollArea,
                            QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont, QColor
from components.base_component import BaseComponent

class SystemInfoWidget(BaseComponent):
    """System Information widget that displays hardware, OS and network details"""
    
    def __init__(self, settings, parent=None):
        super().__init__(settings, parent)
    
    def get_translation(self, key, default=None):
        """Override get_translation to use the correct section name"""
        return self.settings.get_translation("system_information", key, default)
    
    def setup_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Title
        self.title = QLabel(self.get_translation("title", "System Information"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        self.main_layout.addWidget(self.title)
        
        # Description
        self.description = QLabel(self.get_translation("description", "View detailed information about your system hardware and software"))
        self.description.setStyleSheet("font-size: 14px; color: #a0a0a0;")
        self.main_layout.addWidget(self.description)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                background-color: #2a2a2a;
            }
            QTabBar::tab {
                background-color: #252525;
                color: #a0a0a0;
                border: 1px solid #3a3a3a;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 12px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2a2a2a;
                color: #e0e0e0;
            }
            QTabBar::tab:hover {
                background-color: #303030;
            }
        """)
        
        # Create tabs
        self.hw_tab = QWidget()
        self.os_tab = QWidget()
        self.network_tab = QWidget()
        
        # Set up tabs
        self.setup_hardware_tab()
        self.setup_os_tab()
        self.setup_network_tab()
        
        # Add tabs to widget
        self.tab_widget.addTab(self.hw_tab, self.get_translation("hardware_tab", "Hardware"))
        self.tab_widget.addTab(self.os_tab, self.get_translation("os_tab", "Operating System"))
        self.tab_widget.addTab(self.network_tab, self.get_translation("network_tab", "Network"))
        
        # Add tab widget to main layout
        self.main_layout.addWidget(self.tab_widget)
        
        # Refresh button
        self.refresh_button = QPushButton(self.get_translation("refresh", "Refresh Information"))
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #00a8ff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0096e0;
            }
            QPushButton:pressed {
                background-color: #0085c7;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_info)
        
        # Button container (for right alignment)
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(self.refresh_button)
        
        self.main_layout.addWidget(button_container)
    
    def setup_hardware_tab(self):
        """Set up the hardware information tab"""
        layout = QVBoxLayout(self.hw_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # CPU Information
        cpu_group = QGroupBox(self.get_translation("cpu", "CPU"))
        cpu_group.setStyleSheet("""
            QGroupBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: #2a2a2a;
                color: #e0e0e0;
            }
        """)
        cpu_layout = QFormLayout(cpu_group)
        
        # Add CPU information fields
        cpu_info = self.get_cpu_info()
        for key, value in cpu_info.items():
            key_label = QLabel(key + ":")
            key_label.setStyleSheet("color: #a0a0a0;")
            value_label = QLabel(value)
            value_label.setStyleSheet("color: #e0e0e0;")
            cpu_layout.addRow(key_label, value_label)
        
        layout.addWidget(cpu_group)
        
        # Memory Information
        memory_group = QGroupBox(self.get_translation("memory", "Memory"))
        memory_group.setStyleSheet("""
            QGroupBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: #2a2a2a;
                color: #e0e0e0;
            }
        """)
        memory_layout = QFormLayout(memory_group)
        
        # Add memory information fields
        memory_info = self.get_memory_info()
        for key, value in memory_info.items():
            key_label = QLabel(key + ":")
            key_label.setStyleSheet("color: #a0a0a0;")
            value_label = QLabel(value)
            value_label.setStyleSheet("color: #e0e0e0;")
            memory_layout.addRow(key_label, value_label)
        
        layout.addWidget(memory_group)
        
        # Disk Information
        disk_group = QGroupBox(self.get_translation("disks", "Disks"))
        disk_group.setStyleSheet("""
            QGroupBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: #2a2a2a;
                color: #e0e0e0;
            }
        """)
        disk_layout = QVBoxLayout(disk_group)
        
        # Create disk table
        self.disk_table = QTableWidget()
        self.disk_table.setColumnCount(5)
        self.disk_table.setHorizontalHeaderLabels([
            self.get_translation("device", "Device"),
            self.get_translation("mountpoint", "Mount Point"),
            self.get_translation("filesystem", "File System"),
            self.get_translation("total", "Total Size"),
            self.get_translation("used", "Used")
        ])
        self.disk_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.disk_table.setStyleSheet("""
            QTableWidget {
                background-color: #252525;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                gridline-color: #3a3a3a;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                padding: 4px;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)
        
        # Fill disk table
        self.populate_disk_table()
        disk_layout.addWidget(self.disk_table)
        
        layout.addWidget(disk_group)
        
        # Make the entire tab scrollable if needed
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.hw_tab)
        self.hw_tab = scroll_area
    
    def setup_os_tab(self):
        """Set up the operating system information tab"""
        layout = QVBoxLayout(self.os_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # OS Information
        os_group = QGroupBox(self.get_translation("operating_system", "Operating System"))
        os_group.setStyleSheet("""
            QGroupBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: #2a2a2a;
                color: #e0e0e0;
            }
        """)
        os_layout = QFormLayout(os_group)
        
        # Add OS information fields
        os_info = self.get_os_info()
        for key, value in os_info.items():
            key_label = QLabel(key + ":")
            key_label.setStyleSheet("color: #a0a0a0;")
            value_label = QLabel(value)
            value_label.setStyleSheet("color: #e0e0e0;")
            os_layout.addRow(key_label, value_label)
        
        layout.addWidget(os_group)
        
        # Python Information
        python_group = QGroupBox(self.get_translation("python", "Python"))
        python_group.setStyleSheet("""
            QGroupBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: #2a2a2a;
                color: #e0e0e0;
            }
        """)
        python_layout = QFormLayout(python_group)
        
        # Add Python information fields
        python_info = self.get_python_info()
        for key, value in python_info.items():
            key_label = QLabel(key + ":")
            key_label.setStyleSheet("color: #a0a0a0;")
            value_label = QLabel(value)
            value_label.setStyleSheet("color: #e0e0e0;")
            python_layout.addRow(key_label, value_label)
        
        layout.addWidget(python_group)
        
        layout.addStretch()
    
    def setup_network_tab(self):
        """Set up the network information tab"""
        layout = QVBoxLayout(self.network_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Network Information
        network_group = QGroupBox(self.get_translation("network", "Network"))
        network_group.setStyleSheet("""
            QGroupBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: #2a2a2a;
                color: #e0e0e0;
            }
        """)
        network_layout = QFormLayout(network_group)
        
        # Add network information fields
        network_info = self.get_network_info()
        for key, value in network_info.items():
            key_label = QLabel(key + ":")
            key_label.setStyleSheet("color: #a0a0a0;")
            value_label = QLabel(value)
            value_label.setStyleSheet("color: #e0e0e0;")
            network_layout.addRow(key_label, value_label)
        
        layout.addWidget(network_group)
        
        # Network Interfaces
        interfaces_group = QGroupBox(self.get_translation("interfaces", "Network Interfaces"))
        interfaces_group.setStyleSheet("""
            QGroupBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: #2a2a2a;
                color: #e0e0e0;
            }
        """)
        interfaces_layout = QVBoxLayout(interfaces_group)
        
        # Create interfaces table
        self.interfaces_table = QTableWidget()
        self.interfaces_table.setColumnCount(4)
        self.interfaces_table.setHorizontalHeaderLabels([
            self.get_translation("interface", "Interface"),
            self.get_translation("address", "Address"),
            self.get_translation("netmask", "Netmask"),
            self.get_translation("status", "Status")
        ])
        self.interfaces_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.interfaces_table.setStyleSheet("""
            QTableWidget {
                background-color: #252525;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                gridline-color: #3a3a3a;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                padding: 4px;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)
        
        # Fill interfaces table
        self.populate_interfaces_table()
        interfaces_layout.addWidget(self.interfaces_table)
        
        layout.addWidget(interfaces_group)
        
        layout.addStretch()
    
    def get_cpu_info(self):
        """Get CPU information"""
        cpu_info = {}
        
        try:
            # Get processor name
            cpu_info["Model"] = platform.processor()
            
            # Get CPU cores
            cpu_info["Physical Cores"] = str(psutil.cpu_count(logical=False))
            cpu_info["Logical Cores"] = str(psutil.cpu_count())
            
            # Get CPU frequency
            freq = psutil.cpu_freq()
            if freq:
                cpu_info["Current Frequency"] = f"{freq.current:.2f} MHz"
                if hasattr(freq, 'min') and freq.min:
                    cpu_info["Min Frequency"] = f"{freq.min:.2f} MHz"
                if hasattr(freq, 'max') and freq.max:
                    cpu_info["Max Frequency"] = f"{freq.max:.2f} MHz"
            
            # Get CPU architecture
            cpu_info["Architecture"] = platform.machine()
            
        except Exception as e:
            cpu_info["Error"] = str(e)
        
        return cpu_info
    
    def get_memory_info(self):
        """Get memory information"""
        memory_info = {}
        
        try:
            # Get virtual memory
            vm = psutil.virtual_memory()
            memory_info["Total"] = self._format_bytes(vm.total)
            memory_info["Available"] = self._format_bytes(vm.available)
            memory_info["Used"] = self._format_bytes(vm.used)
            memory_info["Usage"] = f"{vm.percent}%"
            
            # Get swap memory
            swap = psutil.swap_memory()
            memory_info["Swap Total"] = self._format_bytes(swap.total)
            memory_info["Swap Used"] = self._format_bytes(swap.used)
            memory_info["Swap Free"] = self._format_bytes(swap.free)
            
        except Exception as e:
            memory_info["Error"] = str(e)
        
        return memory_info
    
    def populate_disk_table(self):
        """Populate disk table with disk information"""
        try:
            self.disk_table.setRowCount(0)
            
            for partition in psutil.disk_partitions():
                row_position = self.disk_table.rowCount()
                self.disk_table.insertRow(row_position)
                
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    # Set items
                    self.disk_table.setItem(row_position, 0, QTableWidgetItem(partition.device))
                    self.disk_table.setItem(row_position, 1, QTableWidgetItem(partition.mountpoint))
                    self.disk_table.setItem(row_position, 2, QTableWidgetItem(partition.fstype))
                    self.disk_table.setItem(row_position, 3, QTableWidgetItem(self._format_bytes(usage.total)))
                    self.disk_table.setItem(row_position, 4, QTableWidgetItem(f"{usage.percent}%"))
                    
                except PermissionError:
                    self.disk_table.setItem(row_position, 0, QTableWidgetItem(partition.device))
                    self.disk_table.setItem(row_position, 1, QTableWidgetItem(partition.mountpoint))
                    self.disk_table.setItem(row_position, 2, QTableWidgetItem(partition.fstype))
                    self.disk_table.setItem(row_position, 3, QTableWidgetItem("N/A"))
                    self.disk_table.setItem(row_position, 4, QTableWidgetItem("N/A"))
                except Exception as e:
                    self.disk_table.setItem(row_position, 0, QTableWidgetItem(partition.device))
                    self.disk_table.setItem(row_position, 1, QTableWidgetItem(partition.mountpoint))
                    self.disk_table.setItem(row_position, 2, QTableWidgetItem(partition.fstype))
                    self.disk_table.setItem(row_position, 3, QTableWidgetItem("Error"))
                    self.disk_table.setItem(row_position, 4, QTableWidgetItem(str(e)))
            
        except Exception as e:
            print(f"Error populating disk table: {e}")
    
    def get_os_info(self):
        """Get operating system information"""
        os_info = {}
        
        try:
            os_info["System"] = platform.system()
            os_info["Release"] = platform.release()
            os_info["Version"] = platform.version()
            
            if platform.system() == "Windows":
                import winreg
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                        os_info["Product Name"] = winreg.QueryValueEx(key, "ProductName")[0]
                        os_info["Build Number"] = winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
                except Exception:
                    pass
            
            os_info["Platform"] = platform.platform()
            os_info["Hostname"] = platform.node()
            
            # Get boot time
            boot_time = psutil.boot_time()
            boot_time_str = self._format_timestamp(boot_time)
            os_info["Boot Time"] = boot_time_str
            
        except Exception as e:
            os_info["Error"] = str(e)
        
        return os_info
    
    def get_python_info(self):
        """Get Python information"""
        python_info = {}
        
        try:
            python_info["Version"] = platform.python_version()
            python_info["Implementation"] = platform.python_implementation()
            python_info["Compiler"] = platform.python_compiler()
            python_info["Build"] = ' '.join(platform.python_build())
            
        except Exception as e:
            python_info["Error"] = str(e)
        
        return python_info
    
    def get_network_info(self):
        """Get network information"""
        network_info = {}
        
        try:
            # Get hostname
            network_info["Hostname"] = socket.gethostname()
            
            # Get primary IP address (not localhost)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                network_info["IP Address"] = s.getsockname()[0]
                s.close()
            except:
                # Fallback method
                network_info["IP Address"] = socket.gethostbyname(socket.gethostname())
            
            # Get FQDN
            network_info["FQDN"] = socket.getfqdn()
            
            # Get MAC address
            mac_num = hex(uuid.getnode()).replace('0x', '')
            mac = ':'.join(mac_num[i:i+2] for i in range(0, len(mac_num), 2))
            network_info["MAC Address"] = mac
            
        except Exception as e:
            network_info["Error"] = str(e)
        
        return network_info
    
    def populate_interfaces_table(self):
        """Populate network interfaces table"""
        try:
            self.interfaces_table.setRowCount(0)
            
            for name, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:  # IPv4
                        row_position = self.interfaces_table.rowCount()
                        self.interfaces_table.insertRow(row_position)
                        
                        # Get interface status
                        status = "Unknown"
                        try:
                            stats = psutil.net_if_stats()
                            if name in stats:
                                status = "Up" if stats[name].isup else "Down"
                        except:
                            pass
                        
                        # Set items
                        self.interfaces_table.setItem(row_position, 0, QTableWidgetItem(name))
                        self.interfaces_table.setItem(row_position, 1, QTableWidgetItem(addr.address))
                        self.interfaces_table.setItem(row_position, 2, QTableWidgetItem(addr.netmask))
                        self.interfaces_table.setItem(row_position, 3, QTableWidgetItem(status))
            
        except Exception as e:
            print(f"Error populating interfaces table: {e}")
    
    def refresh_info(self):
        """Refresh all system information"""
        # Hardware tab
        self.populate_disk_table()
        
        # Network tab
        self.populate_interfaces_table()
        
        # Recreate all tabs to refresh data
        self.setup_hardware_tab()
        self.setup_os_tab()
        self.setup_network_tab()
        
        # Re-add tabs to widget
        self.tab_widget.clear()
        self.tab_widget.addTab(self.hw_tab, self.get_translation("hardware_tab", "Hardware"))
        self.tab_widget.addTab(self.os_tab, self.get_translation("os_tab", "Operating System"))
        self.tab_widget.addTab(self.network_tab, self.get_translation("network_tab", "Network"))
    
    def _format_bytes(self, bytes):
        """Format bytes to a human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} PB"
    
    def _format_timestamp(self, timestamp):
        """Format timestamp to a readable date/time string"""
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def check_all_translations(self):
        """Check if all translation keys used in this component exist"""
        # Define all translation keys used
        keys = [
            "title", "description", "refresh",
            "hardware_tab", "os_tab", "network_tab",
            "cpu", "memory", "disks", "device", "mountpoint", 
            "filesystem", "total", "used", "operating_system",
            "python", "network", "interfaces", "interface",
            "address", "netmask", "status"
        ]
        
        # Check each key and return missing ones
        missing = []
        for key in keys:
            try:
                self.get_translation(key, None)
            except:
                missing.append(key)
        
        return missing 