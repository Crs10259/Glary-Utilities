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
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont, QColor
from components.base_component import BaseComponent
from utils.platform import PlatformUtils
from utils.logger import Logger

# 获取日志记录器
logger = Logger().get_logger()

class SystemInfoWidget(BaseComponent):
    """系统信息小部件，显示硬件、操作系统和网络详细信息"""
    
    def __init__(self, parent=None):
        # 调用父类构造函数
        super().__init__(parent)
        logger.info("初始化系统信息组件")
    
    def get_translation(self, key, default=None):
        """获取翻译，带默认回退"""
        return self.settings.get_translation("system_info", key, default)
    
    def setup_ui(self):
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
            
        # 主布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # 标题
        self.title = QLabel("系统信息")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        self.main_layout.addWidget(self.title)
        
        # 描述
        self.description = QLabel("查看有关系统硬件和软件的详细信息")
        self.description.setStyleSheet("font-size: 14px; color: #a0a0a0;")
        self.main_layout.addWidget(self.description)
        
        # 选项卡小部件
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
        
        # 创建选项卡
        self.hw_tab = QWidget()
        self.os_tab = QWidget()
        self.network_tab = QWidget()
        
        # 设置选项卡
        self.setup_hardware_tab()
        self.setup_os_tab()
        self.setup_network_tab()
        
        # 将选项卡添加到小部件
        self.tab_widget.addTab(self.hw_tab, self.get_translation("hardware_tab", "硬件"))
        self.tab_widget.addTab(self.os_tab, self.get_translation("os_tab", "操作系统"))
        self.tab_widget.addTab(self.network_tab, self.get_translation("network_tab", "网络"))
        
        # 将选项卡小部件添加到主布局
        self.main_layout.addWidget(self.tab_widget)
        
        # 刷新按钮
        self.refresh_button = QPushButton(self.get_translation("refresh", "刷新信息"))
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
        
        # 按钮容器（用于右对齐）
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(self.refresh_button)
        
        self.main_layout.addWidget(button_container)
        
        # 设置布局
        self.setLayout(self.main_layout)
        
        # 确保样式正确应用
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # 记录日志
        logger.info("系统信息UI初始化完成")
    
    def setup_hardware_tab(self):
        """设置硬件信息选项卡"""
        # 创建主滚动区域
        self.hw_scroll = QScrollArea()
        self.hw_scroll.setWidgetResizable(True)
        
        # 创建内容小部件
        hw_content = QWidget()
        layout = QVBoxLayout(hw_content)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # CPU 信息
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
        
        # 添加CPU信息字段
        cpu_info = self.get_cpu_info()
        for key, value in cpu_info.items():
            key_label = QLabel(key + ":")
            key_label.setStyleSheet("color: #a0a0a0;")
            value_label = QLabel(value)
            value_label.setStyleSheet("color: #e0e0e0;")
            cpu_layout.addRow(key_label, value_label)
        
        layout.addWidget(cpu_group)
        
        # GPU 信息组
        gpu_group = QGroupBox(self.get_translation("gpu", "显卡/GPU"))
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
        
        # 创建GPU信息容器
        self.gpu_info_container = QWidget()
        self.gpu_info_layout = QVBoxLayout(self.gpu_info_container)
        self.gpu_info_layout.setContentsMargins(10, 10, 10, 10)
        self.gpu_info_layout.setSpacing(15)
        
        # 获取GPU信息
        self.update_gpu_info()
        
        # 将GPU信息容器添加到GPU组
        gpu_layout = QVBoxLayout(gpu_group)
        gpu_layout.addWidget(self.gpu_info_container)
        
        # 添加GPU组到主布局
        layout.addWidget(gpu_group)
        
        # 内存信息
        memory_group = QGroupBox(self.get_translation("memory", "内存"))
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
        
        # 添加内存信息字段
        memory_info = self.get_memory_info()
        for key, value in memory_info.items():
            key_label = QLabel(key + ":")
            key_label.setStyleSheet("color: #a0a0a0;")
            value_label = QLabel(value)
            value_label.setStyleSheet("color: #e0e0e0;")
            memory_layout.addRow(key_label, value_label)
        
        layout.addWidget(memory_group)
        
        # 磁盘信息
        disk_group = QGroupBox(self.get_translation("disk", "磁盘"))
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
        
        # 创建磁盘表
        self.disk_table = QTableWidget()
        self.disk_table.setColumnCount(5)
        self.disk_table.setHorizontalHeaderLabels([
            self.get_translation("device", "设备"),
            self.get_translation("mountpoint", "挂载点"),
            self.get_translation("filesystem", "文件系统"),
            self.get_translation("total", "总大小"),
            self.get_translation("used", "已用")
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
        
        # 填充磁盘表
        self.populate_disk_table()
        disk_layout.addWidget(self.disk_table)
        
        layout.addWidget(disk_group)
        
        # 设置内容小部件，添加到滚动区域
        self.hw_scroll.setWidget(hw_content)
        
        # 创建硬件标签的主布局并添加滚动区域
        hw_main_layout = QVBoxLayout(self.hw_tab)
        hw_main_layout.setContentsMargins(0, 0, 0, 0)
        hw_main_layout.addWidget(self.hw_scroll)
        
        # 记录日志
        logger.info("硬件信息选项卡设置完成")
    
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
        python_group = QGroupBox("Python")
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
            print(f"Error populating disk table: {e}")  # 填充磁盘表格时出错
            self.disk_table.setRowCount(1)
            self.disk_table.setItem(0, 0, QTableWidgetItem("Error"))
            self.disk_table.setItem(0, 1, QTableWidgetItem(str(e)))
            self.disk_table.setItem(0, 2, QTableWidgetItem(""))
            self.disk_table.setItem(0, 3, QTableWidgetItem(""))
            self.disk_table.setItem(0, 4, QTableWidgetItem(""))
    
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
        """刷新所有系统信息"""
        # 重新填充CPU信息
        cpu_group = self.hw_tab.findChild(QGroupBox, "")
        if cpu_group and cpu_group.title() == self.get_translation("cpu", "CPU"):
            # 清除当前CPU布局
            while cpu_group.layout().count():
                item = cpu_group.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # 添加更新的CPU信息
            cpu_info = self.get_cpu_info()
            for key, value in cpu_info.items():
                key_label = QLabel(key + ":")
                key_label.setStyleSheet("color: #a0a0a0;")
                value_label = QLabel(value)
                value_label.setStyleSheet("color: #e0e0e0;")
                cpu_group.layout().addRow(key_label, value_label)
        
        # 重新填充内存信息
        memory_group = self.hw_tab.findChild(QGroupBox, "")
        if memory_group and memory_group.title() == self.get_translation("memory", "内存"):
            # 清除当前内存布局
            while memory_group.layout().count():
                item = memory_group.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # 添加更新的内存信息
            memory_info = self.get_memory_info()
            for key, value in memory_info.items():
                key_label = QLabel(key + ":")
                key_label.setStyleSheet("color: #a0a0a0;")
                value_label = QLabel(value)
                value_label.setStyleSheet("color: #e0e0e0;")
                memory_group.layout().addRow(key_label, value_label)
        
        # 重新填充磁盘信息
        self.populate_disk_table()
        
        # 重新填充操作系统信息
        self.setup_os_tab()
        
        # 重新填充网络信息
        self.setup_network_tab()
        
        # 重新填充GPU信息
        self.update_gpu_info()
        
        # 提示用户
        QMessageBox.information(self, "信息刷新", "系统信息已成功刷新！")

    def get_gpu_info(self):
        """获取GPU信息"""
        try:
            raw_info = PlatformUtils.get_gpu_info()
            if "error" in raw_info.lower():
                return {"GPU信息": raw_info}
            
            # 解析GPU信息
            gpus = [gpu.split("\n") for gpu in raw_info.split("\n\n")]
            info = {}
            for i, gpu in enumerate(gpus, 1):
                for line in gpu:
                    if ":" in line:
                        key, val = line.split(":", 1)
                        info[f"GPU {i} {key.strip()}"] = val.strip()
            return info
        except Exception as e:
            logger.error(f"获取GPU信息时出错: {str(e)}")
            return {"GPU错误": str(e)}
    
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
            "address", "netmask", "status", "gpu"
        ]
        
        # Check each key and return missing ones
        missing = []
        for key in keys:
            try:
                self.get_translation(key, None)
            except:
                missing.append(key)
        
        return missing

    def update_gpu_info(self):
        """更新GPU信息显示"""
        # 清除现有内容
        while self.gpu_info_layout.count():
            item = self.gpu_info_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 获取GPU信息
        raw_info = PlatformUtils.get_gpu_info()
        logger.info(f"获取GPU信息: {raw_info}")
        
        if "未检测到GPU" in raw_info:
            label = QLabel("未检测到GPU设备")
            label.setStyleSheet("color: #a0a0a0; font-size: 14px; padding: 20px;")
            label.setAlignment(Qt.AlignCenter)
            self.gpu_info_layout.addWidget(label)
            return
        elif "GPUtil" in raw_info:
            label = QLabel("请安装GPUtil库以获取GPU信息:\npip install GPUtil")
            label.setStyleSheet("color: #a0a0a0; font-size: 14px; padding: 20px;")
            label.setAlignment(Qt.AlignCenter)
            self.gpu_info_layout.addWidget(label)
            return
        elif "错误" in raw_info:
            label = QLabel(f"获取GPU信息时出错:\n{raw_info}")
            label.setStyleSheet("color: #a0a0a0; font-size: 14px; padding: 20px;")
            label.setAlignment(Qt.AlignCenter)
            self.gpu_info_layout.addWidget(label)
            return
        
        # 分割多个GPU信息
        gpu_blocks = raw_info.split("\n\n")
        
        for i, gpu_block in enumerate(gpu_blocks):
            # 创建一个为每个GPU的组
            gpu_group = QGroupBox(f"GPU {i+1}")
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
            
            # 处理每个GPU的详细信息
            lines = gpu_block.split("\n")
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key_label = QLabel(key.strip() + ":")
                    key_label.setStyleSheet("color: #a0a0a0;")
                    value_label = QLabel(value.strip())
                    value_label.setStyleSheet("color: #e0e0e0;")
                    gpu_layout.addRow(key_label, value_label)
            
            self.gpu_info_layout.addWidget(gpu_group) 