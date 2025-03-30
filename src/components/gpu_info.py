import os
import platform
import subprocess
import re
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QGridLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from components.base_component import BaseComponent

class GPUInfoWorker(QThread):
    """Worker thread to fetch GPU information without blocking UI"""
    info_ready = pyqtSignal(dict)
    
    def run(self):
        """Run the worker thread to collect GPU info"""
        gpu_info = self.get_gpu_info()
        self.info_ready.emit(gpu_info)
    
    def get_gpu_info(self):
        """Get GPU information based on operating system"""
        system = platform.system()
        gpu_info = {
            "name": "Unknown",
            "driver_version": "Unknown",
            "memory_total": "Unknown",
            "memory_used": "Unknown",
            "temperature": "Unknown"
        }
        
        if system == "Windows":
            # Try to get GPU info using PowerShell commands
            try:
                # Get GPU name
                name_cmd = ['powershell', 'Get-WmiObject Win32_VideoController | Select-Object -ExpandProperty Name']
                name_result = subprocess.run(name_cmd, stdout=subprocess.PIPE, text=True)
                if name_result.returncode == 0 and name_result.stdout.strip():
                    gpu_info["name"] = name_result.stdout.strip()
                
                # Get driver version
                driver_cmd = ['powershell', 'Get-WmiObject Win32_VideoController | Select-Object -ExpandProperty DriverVersion']
                driver_result = subprocess.run(driver_cmd, stdout=subprocess.PIPE, text=True)
                if driver_result.returncode == 0 and driver_result.stdout.strip():
                    gpu_info["driver_version"] = driver_result.stdout.strip()
                
                # Try getting NVIDIA-specific info if available
                try:
                    # Check if nvidia-smi is available
                    nvidia_cmd = ['nvidia-smi', '--query-gpu=memory.total,memory.used,temperature.gpu', '--format=csv,noheader,nounits']
                    nvidia_result = subprocess.run(nvidia_cmd, stdout=subprocess.PIPE, text=True)
                    
                    if nvidia_result.returncode == 0 and nvidia_result.stdout.strip():
                        parts = nvidia_result.stdout.strip().split(',')
                        if len(parts) >= 3:
                            gpu_info["memory_total"] = f"{parts[0].strip()} MB"
                            gpu_info["memory_used"] = f"{parts[1].strip()} MB"
                            gpu_info["temperature"] = f"{parts[2].strip()}°C"
                except:
                    pass  # NVIDIA tools not available
            except Exception as e:
                print(f"Error getting GPU info: {e}")
        
        elif system == "Linux":
            # Try using lspci on Linux
            try:
                # Get GPU info using lspci
                lspci_cmd = ['lspci', '-v']
                lspci_result = subprocess.run(lspci_cmd, stdout=subprocess.PIPE, text=True)
                
                if lspci_result.returncode == 0:
                    # Look for VGA compatible controller
                    output = lspci_result.stdout
                    vga_pattern = r"VGA compatible controller: (.*)"
                    vga_match = re.search(vga_pattern, output)
                    
                    if vga_match:
                        gpu_info["name"] = vga_match.group(1).strip()
                
                # Try getting NVIDIA-specific info if available
                try:
                    # Check if nvidia-smi is available
                    nvidia_cmd = ['nvidia-smi', '--query-gpu=driver_version,memory.total,memory.used,temperature.gpu', '--format=csv,noheader,nounits']
                    nvidia_result = subprocess.run(nvidia_cmd, stdout=subprocess.PIPE, text=True)
                    
                    if nvidia_result.returncode == 0 and nvidia_result.stdout.strip():
                        parts = nvidia_result.stdout.strip().split(',')
                        if len(parts) >= 4:
                            gpu_info["driver_version"] = parts[0].strip()
                            gpu_info["memory_total"] = f"{parts[1].strip()} MB"
                            gpu_info["memory_used"] = f"{parts[2].strip()} MB"
                            gpu_info["temperature"] = f"{parts[3].strip()}°C"
                except:
                    pass  # NVIDIA tools not available
            except Exception as e:
                print(f"Error getting GPU info: {e}")
        
        elif system == "Darwin":  # macOS
            try:
                # Get GPU info using system_profiler
                cmd = ['system_profiler', 'SPDisplaysDataType', '-json']
                result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    if "SPDisplaysDataType" in data and len(data["SPDisplaysDataType"]) > 0:
                        gpu_data = data["SPDisplaysDataType"][0]
                        
                        if "spdisplays_device-name" in gpu_data:
                            gpu_info["name"] = gpu_data["spdisplays_device-name"]
                        
                        if "spdisplays_version" in gpu_data:
                            gpu_info["driver_version"] = gpu_data["spdisplays_version"]
                        
                        if "spdisplays_vram" in gpu_data:
                            gpu_info["memory_total"] = gpu_data["spdisplays_vram"]
            except Exception as e:
                print(f"Error getting GPU info: {e}")
        
        return gpu_info

class InfoRow(QFrame):
    """Row for displaying a single GPU information item"""
    def __init__(self, title, value="", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(50)
        self.setObjectName("infoRow")
        self.setStyleSheet("""
            #infoRow {
                background-color: #2d2d2d;
                border-radius: 6px;
                border: none;
                margin-bottom: 5px;
            }
        """)
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 10)
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #a0a0a0; font-size: 14px;")
        self.title_label.setMinimumWidth(200)
        
        # Value label
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #e0e0e0; font-size: 14px;")
        
        # Add to layout
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.value_label, 1)
    
    def update_value(self, value):
        """Update the displayed value"""
        self.value_label.setText(value)

class GpuInfoWidget(BaseComponent):
    def __init__(self, settings, parent=None):
        super().__init__(settings, parent)
        
        # Start worker thread to fetch GPU info
        self.fetch_gpu_info()
    
    def get_translation(self, key, default=None):
        """Override get_translation to use the correct section name"""
        return self.settings.get_translation("gpu_info", key, default)
    
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
        
        # Info container
        self.info_container = QFrame()
        self.info_container.setObjectName("infoContainer")
        self.info_container.setStyleSheet("""
            #infoContainer {
                background-color: #252525;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        self.info_layout = QVBoxLayout(self.info_container)
        self.info_layout.setContentsMargins(10, 10, 10, 10)
        self.info_layout.setSpacing(10)
        
        # Add GPU info rows
        self.gpu_name_row = InfoRow(self.get_translation("gpu_name"), "Loading...")
        self.info_layout.addWidget(self.gpu_name_row)
        
        self.driver_version_row = InfoRow(self.get_translation("driver_version"), "Loading...")
        self.info_layout.addWidget(self.driver_version_row)
        
        self.memory_total_row = InfoRow(self.get_translation("memory_total"), "Loading...")
        self.info_layout.addWidget(self.memory_total_row)
        
        self.memory_used_row = InfoRow(self.get_translation("memory_used"), "Loading...")
        self.info_layout.addWidget(self.memory_used_row)
        
        self.temperature_row = InfoRow(self.get_translation("temperature"), "Loading...")
        self.info_layout.addWidget(self.temperature_row)
        
        # Add container to main layout
        self.main_layout.addWidget(self.info_container)
        
        # Refresh button
        self.refresh_button = QPushButton(self.get_translation("refresh"))
        self.refresh_button.setStyleSheet("""
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
        """)
        self.refresh_button.clicked.connect(self.fetch_gpu_info)
        
        # Button container (for right alignment)
        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.button_layout.addWidget(self.refresh_button)
        
        self.main_layout.addWidget(self.button_container)
        
        # Add spacer
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
    
    def fetch_gpu_info(self):
        """Start worker thread to fetch GPU info"""
        # Update UI to show loading state
        self.gpu_name_row.update_value("Loading...")
        self.driver_version_row.update_value("Loading...")
        self.memory_total_row.update_value("Loading...")
        self.memory_used_row.update_value("Loading...")
        self.temperature_row.update_value("Loading...")
        
        # Disable refresh button during loading
        self.refresh_button.setEnabled(False)
        
        # Start worker thread
        self.worker = GPUInfoWorker()
        self.worker.info_ready.connect(self.update_gpu_info)
        self.worker.start()
    
    def update_gpu_info(self, gpu_info):
        """Update the GPU information in the UI"""
        self.gpu_name_row.update_value(gpu_info["name"])
        self.driver_version_row.update_value(gpu_info["driver_version"])
        self.memory_total_row.update_value(gpu_info["memory_total"])
        self.memory_used_row.update_value(gpu_info["memory_used"])
        self.temperature_row.update_value(gpu_info["temperature"])
        
        # Re-enable refresh button
        self.refresh_button.setEnabled(True)

    def refresh_language(self):
        # Update text elements with new translations
        self.title.setText(self.get_translation("title"))
        self.description.setText(self.get_translation("description"))
        self.gpu_name_row.label.setText(self.get_translation("gpu_name"))
        self.driver_version_row.label.setText(self.get_translation("driver_version"))
        self.memory_total_row.label.setText(self.get_translation("memory_total"))
        self.memory_used_row.label.setText(self.get_translation("memory_used"))
        self.temperature_row.label.setText(self.get_translation("temperature"))
        self.refresh_button.setText(self.get_translation("refresh"))
        
        # Add animation to highlight the change
        super().refresh_language()

    def check_all_translations(self):
        """Check if all translation keys used in this component exist
        
        Raises:
            KeyError: If any translation key is missing
        """
        # Try to get all translations used in this component
        keys = [
            "title", "description", "gpu_name", "driver_version", 
            "memory_total", "memory_used", "temperature", "refresh"
        ]
        
        for key in keys:
            # This will raise KeyError if the key doesn't exist
            self.get_translation(key, None)

# Create an alias for compatibility
GPUInfoWidget = GpuInfoWidget 