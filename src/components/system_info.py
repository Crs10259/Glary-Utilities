from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QTabWidget, QGroupBox, QFormLayout, QScrollArea,
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                            QGridLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from src.components.base_component import BaseComponent
from src.config import Icon
import os

class SystemInfoWidget(BaseComponent):
    """System info widget, display hardware, operating system and network detailed information"""
    
    def __init__(self, parent=None):
        # Call parent class constructor
        super().__init__(parent)
        self.logger.info("Initializing system info component")
    
    def get_translation(self, key, default=None):
        """Get translation with default fallback"""
        return self.settings.get_translation("system_info", key, default)
    
    def setup_ui(self):
        # Clear old layout (if any)
        if self.layout():
            # Clear all widgets in old layout
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Title area
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)
        
        # Title
        self.title = QLabel(self.get_translation("title", "System Information"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        title_layout.addWidget(self.title)
        
        # Add title area to main layout
        self.main_layout.addWidget(title_container)
        
        # Description
        self.description = QLabel(self.get_translation("description", "View system hardware and software information"))
        self.description.setStyleSheet("font-size: 14px; color: #a0a0a0;")
        self.main_layout.addWidget(self.description)
        
        # Create or clear tab widgets
        if hasattr(self, 'tab_widget'):
            # If it exists, keep tab widgets but clear their content
            current_index = self.tab_widget.currentIndex()
            self.tab_widget.clear()
        else:
            # Create new tab widgets
            self.tab_widget = QTabWidget()
            current_index = 0
        
        # Set tab styles
        self.tab_widget.setObjectName("SystemInfoTabWidget")
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #2d2d2d;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #a0a0a0;
                border: 1px solid #3a3a3a;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background-color: #353535;
            }
        """)
        
        # Create tab content containers
        self.hardware_tab = QWidget()
        self.hardware_tab.setObjectName("HardwareTab")
        self.os_tab = QWidget()
        self.os_tab.setObjectName("OSTab")
        self.network_tab = QWidget()
        self.network_tab.setObjectName("NetworkTab")
        
        # Set tab content
        self.setup_hardware_tab()
        self.setup_os_tab()
        self.setup_network_tab()
        
        # Add tabs, ensure only added once, no overlap
        self.tab_widget.addTab(self.hardware_tab, self.get_translation("hardware_tab", "Hardware"))
        self.tab_widget.addTab(self.os_tab, self.get_translation("os_tab", "OS"))
        self.tab_widget.addTab(self.network_tab, self.get_translation("network_tab", "Network"))
        
        # Restore previous tab index (if any)
        if current_index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(current_index)
        
        self.main_layout.addWidget(self.tab_widget)
        
        # Add bottom button area
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)
        
        # Add space placeholder, push refresh button to the right
        bottom_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton(self.get_translation("refresh", "Refresh"))
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #00a8ff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0096e0;
            }
            QPushButton:pressed {
                background-color: #0085c7;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_info)
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        bottom_layout.addWidget(self.refresh_button)
        
        # Add bottom area to main layout
        self.main_layout.addWidget(bottom_container)
        
        # Set layout
        self.setLayout(self.main_layout)
        
        # Ensure styles are applied correctly
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # Log
        self.logger.info("System info UI initialized")
    
    def setup_hardware_tab(self):
        """Setup hardware information tab"""
        # Create a main scroll area, ensure scrollable in small window
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Create content area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # CPU Information
        cpu_group = QGroupBox(self.get_translation("cpu_info", "CPU Information"))
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
        cpu_layout = QGridLayout(cpu_group)
        cpu_layout.setHorizontalSpacing(20)
        cpu_layout.setVerticalSpacing(8)
        
        # Add CPU information fields
        self._cpu_value_labels = {}
        cpu_info = self.system_information.get_cpu_info()
        row = 0
        for key, value in cpu_info.items():
            # Convert CPU key name to translation key name
            # For example, cpu_brand -> cpu_brand, cpu_cores_physical -> cpu_cores_physical
            cpu_key = key
            if key.startswith("cpu_"):
                cpu_key = key[4:]  # Remove prefix "cpu_"
            
            # Get translation, if no specific translation use readable form of original key name
            readable_key = cpu_key.replace('_', ' ').title()
            translation_key = f"cpu_{cpu_key.lower()}"
            translated_text = self.get_translation(translation_key, readable_key)
            
            key_label = QLabel(translated_text + ":")
            key_label.setStyleSheet("color: #a0a0a0;")
            key_label.setWordWrap(True)  # Allow text wrapping
            key_label.setMinimumWidth(120)  # Set minimum width to ensure readability
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet("color: #e0e0e0;")
            value_label.setWordWrap(True)  # Allow text wrapping
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Allow text selection

            # Save reference for refresh
            self._cpu_value_labels[key] = value_label
            
            # Use single column layout, ensure clear display in small window
            cpu_layout.addWidget(key_label, row, 0)
            cpu_layout.addWidget(value_label, row, 1)
            row += 1
        
        cpu_layout.setColumnStretch(1, 1)
        
        layout.addWidget(cpu_group)
        
        # Memory Information
        memory_group = QGroupBox(self.get_translation("memory_info", "Memory Information"))
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
        memory_layout = QGridLayout(memory_group)
        memory_layout.setHorizontalSpacing(20)
        memory_layout.setVerticalSpacing(8)
        
        # Add memory information fields
        self._memory_value_labels = {}
        memory_info = self.system_information.get_memory_info()
        row = 0
        for key, value in memory_info.items():
            # Normalize key by replacing spaces with underscores to build translation key
            translation_key = f"memory_{key.lower().replace(' ', '_')}"
            translated_text = self.get_translation(translation_key, key)
            
            key_label = QLabel(translated_text + ":")
            key_label.setStyleSheet("color: #a0a0a0;")
            key_label.setWordWrap(True)  # Allow text wrapping
            key_label.setMinimumWidth(120)  # Set minimum width to ensure readability
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet("color: #e0e0e0;")
            value_label.setWordWrap(True)  # Allow text wrapping
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Allow text selection

            # Save reference for refresh
            self._memory_value_labels[key] = value_label
            
            # Use single column layout, ensure clear display in small window
            memory_layout.addWidget(key_label, row, 0)
            memory_layout.addWidget(value_label, row, 1)
            row += 1
        
        memory_layout.setColumnStretch(1, 1)
        
        layout.addWidget(memory_group)
        
        # GPU Information
        gpu_group = QGroupBox(self.get_translation("gpu_info", "GPU Information"))
        gpu_group.setStyleSheet("""
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
        
        # Create a scroll area to display GPU information
        gpu_scroll = QScrollArea()
        gpu_scroll.setWidgetResizable(True)
        gpu_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        gpu_content = QWidget()
        self.gpu_info_layout = QVBoxLayout(gpu_content)
        self.gpu_info_layout.setContentsMargins(10, 10, 10, 10)
        self.gpu_info_layout.setSpacing(15)
        
        gpu_scroll.setWidget(gpu_content)
        
        # Layout GPU area
        gpu_layout = QVBoxLayout(gpu_group)
        gpu_layout.addWidget(gpu_scroll)
        
        # Fill GPU information
        self.update_gpu_info()
        layout.addWidget(gpu_group)
        
        # Disk Information
        disk_group = QGroupBox(self.get_translation("disk_info", "Disk Information"))
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
            self.get_translation("total", "Total"),
            self.get_translation("used", "Used")
        ])
        self.disk_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # Adjust column width based on content
        self.disk_table.horizontalHeader().setStretchLastSection(True)  # Ensure the last column fills remaining space
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
        
        # Set minimum height, ensure table has enough space to display
        self.disk_table.setMinimumHeight(120)
        
        # Add stretch factor, ensure layout has elasticity in vertical direction
        layout.addStretch()
        
        # Set main scroll area content
        scroll_area.setWidget(content_widget)
        
        # Create main hardware tab layout
        main_layout = QVBoxLayout(self.hardware_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
    
    def setup_os_tab(self):
        """Set up the operating system information tab"""
        # Create a main scroll area, ensure scrollable in small window
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Create content area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
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
        os_layout = QGridLayout(os_group)
        os_layout.setHorizontalSpacing(20)
        os_layout.setVerticalSpacing(8)
        
        # Add OS information fields
        os_info = self.system_information.get_os_info()
        row = 0
        for key, value in os_info.items():
            readable_key = key.replace('_', ' ').title()
            translation_key = f"os_{key.lower().replace(' ', '_')}"
            translated_text = self.get_translation(translation_key, readable_key)
            
            key_label = QLabel(translated_text + ":")
            key_label.setStyleSheet("color: #a0a0a0;")
            key_label.setWordWrap(True)  # Allow text wrapping
            key_label.setMinimumWidth(150)  # Set minimum width to ensure readability
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet("color: #e0e0e0;")
            value_label.setWordWrap(True)  # Allow text wrapping
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Allow text selection
            
            os_layout.addWidget(key_label, row, 0)
            os_layout.addWidget(value_label, row, 1)
            row += 1
        
        os_layout.setColumnStretch(1, 1)
        
        layout.addWidget(os_group)
        
        # Python Information
        python_group = QGroupBox(self.get_translation("python_info", "Python Information"))
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
        python_layout = QGridLayout(python_group)
        python_layout.setHorizontalSpacing(20)
        python_layout.setVerticalSpacing(8)
        
        # Add Python information fields
        python_info = self.system_information.get_python_info()
        row = 0
        for key, value in python_info.items():
            readable_key = key.replace('_', ' ').title()
            translation_key = f"python_{key.lower().replace(' ', '_')}"
            translated_text = self.get_translation(translation_key, readable_key)
            
            key_label = QLabel(translated_text + ":")
            key_label.setStyleSheet("color: #a0a0a0;")
            key_label.setWordWrap(True)  # Allow text wrapping
            key_label.setMinimumWidth(150)  # Set minimum width to ensure readability
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet("color: #e0e0e0;")
            value_label.setWordWrap(True)  # Allow text wrapping
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Allow text selection
            
            python_layout.addWidget(key_label, row, 0)
            python_layout.addWidget(value_label, row, 1)
            row += 1
        
        python_layout.setColumnStretch(1, 1)
        
        layout.addWidget(python_group)
        
        # Add stretch factor, ensure layout has elasticity in vertical direction
        layout.addStretch()
        
        # Set main scroll area content
        scroll_area.setWidget(content_widget)
        
        # Create main OS tab layout
        main_layout = QVBoxLayout(self.os_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
    
    def setup_network_tab(self):
        """Set up the network information tab"""
        layout = QVBoxLayout(self.network_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Network Information
        network_group = QGroupBox(self.get_translation("network_info", "Network Information"))
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
        network_info = self.system_information.get_network_info()
        for key, value in network_info.items():
            translated_key = self.get_translation(f"network_{key.lower().replace(' ', '_')}", key)
            key_label = QLabel(translated_key + ":")
            key_label.setStyleSheet("color: #a0a0a0;")
            value_label = QLabel(str(value))
            value_label.setStyleSheet("color: #e0e0e0;")
            network_layout.addRow(key_label, value_label)
        
        layout.addWidget(network_group)
        
        # Network Interfaces
        interfaces_group = QGroupBox(self.get_translation("network_interfaces", "Network Interfaces"))
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
            self.get_translation("interface_name", "Interface"),
            self.get_translation("interface_address", "Address"),
            self.get_translation("interface_netmask", "Netmask"),
            self.get_translation("interface_status", "Status")
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
    
    def populate_disk_table(self):
        """Populate disk table"""
        try:
            self.disk_table.setRowCount(0)
            disk_data = self.system_information.get_disk_table_data()
            
            for disk_info in disk_data:
                row_position = self.disk_table.rowCount()
                self.disk_table.insertRow(row_position)
                
                # Set table items
                self.disk_table.setItem(row_position, 0, QTableWidgetItem(disk_info['device']))
                self.disk_table.setItem(row_position, 1, QTableWidgetItem(disk_info['mountpoint']))
                self.disk_table.setItem(row_position, 2, QTableWidgetItem(disk_info['fstype']))
                self.disk_table.setItem(row_position, 3, QTableWidgetItem(disk_info['total']))
                self.disk_table.setItem(row_position, 4, QTableWidgetItem(disk_info['used']))
                
        except Exception as e:
            self.logger.error(f"Error populating disk table: {e}")
            self.disk_table.setRowCount(1)
            self.disk_table.setItem(0, 0, QTableWidgetItem("Error"))
            self.disk_table.setItem(0, 1, QTableWidgetItem(str(e)))
            self.disk_table.setItem(0, 2, QTableWidgetItem(""))
            self.disk_table.setItem(0, 3, QTableWidgetItem(""))
            self.disk_table.setItem(0, 4, QTableWidgetItem(""))
    
    def populate_interfaces_table(self):
        """Populate network interfaces table"""
        try:
            self.interfaces_table.setRowCount(0)
            interface_data = self.system_information.get_network_interfaces_data()
            
            for interface_info in interface_data:
                row_position = self.interfaces_table.rowCount()
                self.interfaces_table.insertRow(row_position)
                
                # Set table items
                self.interfaces_table.setItem(row_position, 0, QTableWidgetItem(interface_info['name']))
                self.interfaces_table.setItem(row_position, 1, QTableWidgetItem(interface_info['address']))
                self.interfaces_table.setItem(row_position, 2, QTableWidgetItem(interface_info['netmask']))
                self.interfaces_table.setItem(row_position, 3, QTableWidgetItem(interface_info['status']))
                
        except Exception as e:
            self.logger.error(f"Error populating network interfaces table: {e}")
    
    def refresh_info(self):
        """Refresh all system information"""
        try:
            # Update CPU info labels
            if hasattr(self, '_cpu_value_labels'):
                cpu_info = self.system_information.get_cpu_info()
                for key, value in cpu_info.items():
                    if key in self._cpu_value_labels:
                        self._cpu_value_labels[key].setText(str(value))

            # Update memory info labels
            if hasattr(self, '_memory_value_labels'):
                memory_info = self.system_information.get_memory_info()
                for key, value in memory_info.items():
                    if key in self._memory_value_labels:
                        self._memory_value_labels[key].setText(str(value))

            # Only refresh data, don't recreate UI elements
            # Update disk information
            if hasattr(self, 'disk_table'):
                self.populate_disk_table()
            
            # Update network interface information
            if hasattr(self, 'interfaces_table'):
                self.populate_interfaces_table()
            
            # Update GPU information
            if hasattr(self, 'gpu_info_layout'):
                self.update_gpu_info()
            
            self.logger.info("System information refreshed")
            
            # Show success message (with application icon)
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.get_translation("refresh_success", "Refresh Successful"))
            msg_box.setText(self.get_translation("refresh_success_message", "System information has been refreshed successfully"))
            msg_box.setIcon(QMessageBox.Information)
            
            # Set application icon
            app_icon_path = Icon.Icon.Path
            if app_icon_path and os.path.exists(app_icon_path):
                msg_box.setWindowIcon(QIcon(app_icon_path))
            
            # Set message box style
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                }
                QLabel {
                    color: #e0e0e0;
                    font-size: 13px;
                }
                QPushButton {
                    background-color: #00a8ff;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #0096e0;
                }
                QPushButton:pressed {
                    background-color: #0085c7;
                }
            """)
            msg_box.exec_()
        except Exception as e:
            self.logger.error(f"Error refreshing system information: {e}")
            # Show error message (with application icon)
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.get_translation("error", "Error"))
            msg_box.setText(self.get_translation("refresh_error", "Error refreshing system information"))
            msg_box.setIcon(QMessageBox.Warning)
            
            # Set application icon
            app_icon_path = Icon.Icon.Path
            if app_icon_path and os.path.exists(app_icon_path):
                msg_box.setWindowIcon(QIcon(app_icon_path))
            
            # Set message box style
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                }
                QLabel {
                    color: #e0e0e0;
                    font-size: 13px;
                }
                QPushButton {
                    background-color: #00a8ff;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #0096e0;
                }
                QPushButton:pressed {
                    background-color: #0085c7;
                }
            """)
            msg_box.exec_()
    
    def check_all_translations(self):
        """Check if all translation keys used in this component exist"""
        # Define all translation keys used
        keys = [
            "title", "description", "refresh", "refresh_success", "refresh_success_message",
            "hardware_tab", "os_tab", "network_tab",
            "cpu_info", "memory_info", "disks_info", "gpu_info", "gpu_number", 
            "operating_system", "python_info", "network_info",
            "network_interfaces", "interface_name", "interface_address",
            "interface_netmask", "interface_status",
            # OS tab translations
            "os_system", "os_release", "os_version", "os_machine",
            "os_processor", "os_platform", "os_architecture",
            # Python tab translations
            "python_version", "python_implementation", "python_compiler",
            "python_build", "python_location",
            # Network tab translations
            "network_hostname", "network_ip_address", "network_fqdn",
            "network_mac_address",
            # Hardware tab translations
            "device", "mountpoint", "filesystem", "total", "used",
            "memory_total", "memory_available", "memory_used", "memory_usage",
            "memory_swap_total", "memory_swap_used", "memory_swap_free",
            # CPU info translations
            "cpu_model", "cpu_physical_cores", "cpu_logical_cores",
            "cpu_current_frequency", "cpu_min_frequency", "cpu_max_frequency",
            "cpu_architecture", "cpu_usage",
            # GPU info translations
            "gpu_name", "gpu_model", "gpu_id", "gpu_uuid", "gpu_memory", 
            "gpu_memory_total", "gpu_memory_used", "gpu_memory_free",
            "gpu_utilization", "gpu_temperature", "gpu_power", "gpu_power_usage",
            "gpu_driver", "gpu_fan_speed", "gpu_load", "gpu_memory_load",
            "gpu_bus_id", "gpu_compute_capability", "gpu_processor_count",
            "gpu_clock", "gpu_memory_clock", "gpu_core_clock", "gpu_vram",
            # Additional translations
            "error", "refresh_error", "ready_message", "gpu_not_detected",
            "gpu_error", "gpu_install_message", "gpu_info_error"
        ]
        
        # Check each key and return missing ones
        missing = []
        for key in keys:
            if not self.get_translation(key, None):
                missing.append(key)
        
        return missing

    def update_gpu_info(self):
        """Update GPU information display"""
        # Clear existing content
        while self.gpu_info_layout.count():
            item = self.gpu_info_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get translation text, prevent hardcoded Chinese information display
        no_gpu_message = self.get_translation("gpu_not_detected", "No GPU device detected")
        gpu_util_message = self.get_translation("gpu_install_message", "Please install GPUtil library to get GPU information:\npip install GPUtil")
        error_message = self.get_translation("gpu_info_error", "Error getting GPU information")
        
        # Get current application language
        current_language = self.settings.get_setting("language", "en")
        self.logger.info(f"Current display language: {current_language}")
        
        try:
            # Get raw GPU information directly from system information class
            raw_info = self.system_information.get_gpu_info()
            self.logger.info(f"Raw GPU information: {raw_info[:100]}...")  # Only log first 100 characters
            
            # Check if it's an error message or empty information
            if not raw_info:
                label = QLabel(error_message)
                label.setStyleSheet("color: #a0a0a0; font-size: 14px; padding: 20px;")
                label.setAlignment(Qt.AlignCenter)
                self.gpu_info_layout.addWidget(label)
                return
            
            # Handle various status messages, ensure correct text is displayed based on current language setting
            if any(x in raw_info for x in ["未检测到GPU", "No GPU", "not detected"]):
                label = QLabel(no_gpu_message)
                label.setStyleSheet("color: #a0a0a0; font-size: 14px; padding: 20px;")
                label.setAlignment(Qt.AlignCenter)
                self.gpu_info_layout.addWidget(label)
                return
            elif any(x in raw_info for x in ["GPUtil", "pip install", "安装"]):
                label = QLabel(gpu_util_message)
                label.setStyleSheet("color: #a0a0a0; font-size: 14px; padding: 20px;")
                label.setAlignment(Qt.AlignCenter)
                self.gpu_info_layout.addWidget(label)
                return
            elif any(x in raw_info for x in ["错误", "Error", "Failed", "失败"]):
                label = QLabel(f"{error_message}:\n{raw_info}")
                label.setStyleSheet("color: #a0a0a0; font-size: 14px; padding: 20px;")
                label.setAlignment(Qt.AlignCenter)
                self.gpu_info_layout.addWidget(label)
                return
            
            # Map all Chinese key names to corresponding English key names to support translation
            key_mapping = {
                # Chinese -> English mapping
                "名称": "Name",
                "显存": "Memory",
                "总内存": "Total Memory",
                "已用内存": "Used Memory",
                "可用内存": "Free Memory",
                "驱动版本": "Driver Version",
                "显存使用率": "Memory Utilization",
                "GPU使用率": "GPU Utilization",
                "温度": "Temperature",
                "处理器": "Processor",
                "驱动日期": "Driver Date",
                "内存": "Memory",
                "驱动": "Driver",
                "模块": "Module",
                "厂商": "Vendor",
                "设备ID": "Device ID",
                "Metal支持": "Metal Support"
            }
            
            # GPU property translation key mapping (applicable to all languages)
            gpu_property_map = {
                "name": "gpu_name",
                "memory": "gpu_memory",
                "total memory": "gpu_memory_total",
                "used memory": "gpu_memory_used",
                "free memory": "gpu_memory_free",
                "driver version": "gpu_driver",
                "memory utilization": "gpu_memory_utilization",
                "gpu utilization": "gpu_utilization",
                "temperature": "gpu_temperature",
                "processor": "gpu_processor",
                "driver date": "gpu_driver_date",
                "vendor": "gpu_vendor",
                "device id": "gpu_device_id", 
                "metal support": "gpu_metal_support",
                "driver": "gpu_driver",
                "module": "gpu_module"
            }
            
            # Split GPU information blocks
            gpu_blocks = raw_info.split("\n\n")
            
            for i, gpu_block in enumerate(gpu_blocks):
                if not gpu_block.strip():
                    continue
                
                # Create GPU group, numbered from 0
                gpu_title = self.get_translation("gpu_number", "GPU") + f" {i}"
                gpu_group = QGroupBox(gpu_title)
                gpu_group.setStyleSheet("""
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
                
                gpu_layout = QFormLayout(gpu_group)
                
                # Process each GPU's detailed information
                lines = gpu_block.split("\n")
                for line in lines:
                    if ":" in line:
                        # Separate key-value pairs
                        key, value = line.split(":", 1)
                        original_key = key.strip()
                        original_value = value.strip()
                        
                        # If it's a Chinese key name and current language is English, map it
                        if current_language.lower() == "en" and original_key in key_mapping:
                            key = key_mapping[original_key]
                        
                        # Normalize key name to lowercase for translation lookup
                        key_lower = key.lower()
                        
                        # Find translation key
                        translation_key = None
                        for prop_key, trans_key in gpu_property_map.items():
                            if prop_key in key_lower:
                                translation_key = trans_key
                                break
                        
                        # Use found translation key or create a reasonable fallback
                        if translation_key:
                            display_key = self.get_translation(translation_key, key)
                        else:
                            # Create possible translation key
                            fallback_key = "gpu_" + key_lower.replace(" ", "_")
                            display_key = self.get_translation(fallback_key, key)
                        
                        # Add to layout
                        key_label = QLabel(display_key + ":")
                        key_label.setStyleSheet("color: #a0a0a0;")
                        value_label = QLabel(original_value)
                        value_label.setStyleSheet("color: #e0e0e0;")
                        gpu_layout.addRow(key_label, value_label)
                
                self.gpu_info_layout.addWidget(gpu_group)
                
        except Exception as e:
            # Handle any exceptions
            self.logger.error(f"Error updating GPU information: {str(e)}")
            label = QLabel(f"{error_message}: {str(e)}")
            label.setStyleSheet("color: #a0a0a0; font-size: 14px; padding: 20px;")
            label.setAlignment(Qt.AlignCenter)
            self.gpu_info_layout.addWidget(label)
    
    def refresh_language(self):
        """Refresh interface language"""
        # Update title and description
        self.title.setText(self.get_translation("title", "System Information"))
        self.description.setText(self.get_translation("description", "View system hardware and software information"))
        
        # Save current tab index
        current_index = self.tab_widget.currentIndex()
        
        # Update tab titles
        self.tab_widget.setTabText(0, self.get_translation("hardware_tab", "Hardware"))
        self.tab_widget.setTabText(1, self.get_translation("os_tab", "OS"))
        self.tab_widget.setTabText(2, self.get_translation("network_tab", "Network"))
        
        # Update refresh button
        self.refresh_button.setText(self.get_translation("refresh", "Refresh"))
        
        # Update table titles
        if hasattr(self, 'disk_table'):
            self.disk_table.setHorizontalHeaderLabels([
                self.get_translation("device", "Device"),
                self.get_translation("mountpoint", "Mount Point"),
                self.get_translation("filesystem", "File System"),
                self.get_translation("total", "Total"),
                self.get_translation("used", "Used")
            ])
        
        if hasattr(self, 'interfaces_table'):
            self.interfaces_table.setHorizontalHeaderLabels([
                self.get_translation("interface_name", "Interface"),
                self.get_translation("interface_address", "Address"),
                self.get_translation("interface_netmask", "Netmask"),
                self.get_translation("interface_status", "Status")
            ])
        
        # Reload all areas' content, ensure using latest translations
        self.setup_hardware_tab()
        self.setup_os_tab()
        self.setup_network_tab()
        
        # Restore previous tab index
        if current_index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(current_index)
        
        # Add animation to highlight changes
        super().refresh_language() 