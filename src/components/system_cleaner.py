import os
import sys
import shutil
import tempfile
import platform
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QCheckBox, QLineEdit, QListWidget, QFileDialog,
                            QProgressBar, QTabWidget, QGroupBox, QFormLayout,
                            QListWidgetItem, QTableWidget, QHeaderView, QTextEdit,
                            QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont
from components.base_component import BaseComponent

class CleanerWorker(QThread):
    """扫描和清理文件的工作线程"""
    progress_updated = pyqtSignal(int, str)
    scan_completed = pyqtSignal(dict)
    clean_completed = pyqtSignal(dict)
    
    def __init__(self, options, exclusions, extensions, operation="scan"):
        super().__init__()
        self.options = options  # 要扫描的选项字典
        self.exclusions = exclusions  # 排除的目录/文件列表
        self.extensions = extensions  # 要清理的文件扩展名列表
        self.operation = operation  # "scan" 或 "clean"
        self.stop_requested = False
    
    def run(self):
        """运行工作线程"""
        if self.operation == "scan":
            self.scan_files()
        elif self.operation == "clean":
            self.clean_files()
    
    def stop(self):
        """请求工作线程停止"""
        self.stop_requested = True
    
    def scan_files(self):
        """扫描不必要的文件"""
        results = {
            "files": [],
            "total_size": 0,
            "count": 0
        }
        
        # 获取临时目录
        temp_dir = tempfile.gettempdir()
        
        # 获取用户主目录
        home_dir = os.path.expanduser("~")
        
        progress = 0
        self.progress_updated.emit(progress, "开始扫描...")
        
        # 扫描临时文件
        if self.options.get("temp_files", False):
            self.progress_updated.emit(progress, "扫描临时文件...")
            temp_files = self.scan_directory(temp_dir)
            results["files"].extend(temp_files)
            progress += 20
            self.progress_updated.emit(progress, f"找到 {len(temp_files)} 个临时文件")
        
        # 扫描回收站
        if self.options.get("recycle_bin", False):
            self.progress_updated.emit(progress, "扫描回收站...")
            recycle_files = self.scan_recycle_bin()
            results["files"].extend(recycle_files)
            progress += 20
            self.progress_updated.emit(progress, f"找到 {len(recycle_files)} 个回收站文件")
        
        # 扫描缓存文件（浏览器）
        if self.options.get("cache_files", False):
            self.progress_updated.emit(progress, "扫描缓存文件...")
            cache_files = self.scan_browser_caches(home_dir)
            results["files"].extend(cache_files)
            progress += 20
            self.progress_updated.emit(progress, f"找到 {len(cache_files)} 个缓存文件")
        
        # 扫描日志文件
        if self.options.get("log_files", False):
            self.progress_updated.emit(progress, "扫描日志文件...")
            log_files = self.scan_log_files()
            results["files"].extend(log_files)
            progress += 20
            self.progress_updated.emit(progress, f"找到 {len(log_files)} 个日志文件")
        
        # 计算总数
        results["count"] = len(results["files"])
        results["total_size"] = sum(file["size"] for file in results["files"])
        
        self.progress_updated.emit(100, f"扫描完成。找到 {results['count']} 个文件 ({self.format_size(results['total_size'])})")
        self.scan_completed.emit(results)
    
    def clean_files(self):
        """清理选定的文件"""
        results = {
            "cleaned_count": 0,
            "cleaned_size": 0,
            "failed_count": 0
        }
        
        total_files = len(self.options.get("files", []))
        if total_files == 0:
            self.progress_updated.emit(100, "没有文件可清理")
            self.clean_completed.emit(results)
            return
        
        self.progress_updated.emit(0, f"清理 {total_files} 个文件...")
        
        for i, file_info in enumerate(self.options.get("files", [])):
            if self.stop_requested:
                break
                
            file_path = file_info["path"]
            try:
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    
                    results["cleaned_count"] += 1
                    results["cleaned_size"] += file_info["size"]
                    
                    progress = int((i + 1) / total_files * 100)
                    self.progress_updated.emit(progress, f"清理了 {results['cleaned_count']} 个文件 ({self.format_size(results['cleaned_size'])})")
                else:
                    results["failed_count"] += 1
            except Exception as e:
                print(f"清理 {file_path} 时出错: {e}")
                results["failed_count"] += 1
        
        self.progress_updated.emit(100, f"清理完成。清理了 {results['cleaned_count']} 个文件 ({self.format_size(results['cleaned_size'])})")
        self.clean_completed.emit(results)
    
    def scan_directory(self, directory):
        """扫描目录以查找要清理的文件"""
        files = []
        
        try:
            for root, dirs, filenames in os.walk(directory):
                if self.stop_requested:
                    break
                    
                # 跳过排除的目录
                dirs[:] = [d for d in dirs if os.path.join(root, d) not in self.exclusions]
                
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    
                    # 跳过排除的文件
                    if file_path in self.exclusions:
                        continue
                    
                    # 仅包括具有指定扩展名的文件（如果提供了扩展名）
                    if self.extensions and not any(filename.endswith(ext) for ext in self.extensions):
                        continue
                    
                    try:
                        file_size = os.path.getsize(file_path)
                        files.append({
                            "path": file_path,
                            "name": filename,
                            "size": file_size
                        })
                    except Exception as e:
                        print(f"获取文件信息时出错 {file_path}: {e}")
        except Exception as e:
            print(f"扫描目录 {directory} 时出错: {e}")
        
        return files
    
    def scan_recycle_bin(self):
        """扫描回收站中的文件"""
        files = []
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows回收站位于C:\\$Recycle.Bin
                recycle_bin = "C:\\$Recycle.Bin"
                if os.path.exists(recycle_bin):
                    files = self.scan_directory(recycle_bin)
            elif system == "Darwin":  # macOS
                # macOS垃圾箱位于~/.Trash
                trash_path = os.path.expanduser("~/.Trash")
                if os.path.exists(trash_path):
                    files = self.scan_directory(trash_path)
            elif system == "Linux":
                # Linux垃圾箱位于~/.local/share/Trash
                trash_path = os.path.expanduser("~/.local/share/Trash")
                if os.path.exists(trash_path):
                    files = self.scan_directory(trash_path)
        except Exception as e:
            print(f"扫描回收站时出错: {e}")
        
        return files
    
    def scan_browser_caches(self, home_dir):
        """扫描浏览器缓存目录"""
        files = []
        
        try:
            system = platform.system()
            
            # Chrome缓存
            chrome_cache = None
            if system == "Windows":
                chrome_cache = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Cache")
            elif system == "Darwin":
                chrome_cache = os.path.join(home_dir, "Library", "Caches", "Google", "Chrome")
            elif system == "Linux":
                chrome_cache = os.path.join(home_dir, ".cache", "google-chrome")
            
            if chrome_cache and os.path.exists(chrome_cache):
                files.extend(self.scan_directory(chrome_cache))
            
            # Firefox缓存
            firefox_cache = None
            if system == "Windows":
                firefox_cache = os.path.join(home_dir, "AppData", "Local", "Mozilla", "Firefox", "Profiles")
            elif system == "Darwin":
                firefox_cache = os.path.join(home_dir, "Library", "Caches", "Firefox")
            elif system == "Linux":
                firefox_cache = os.path.join(home_dir, ".cache", "mozilla", "firefox")
            
            if firefox_cache and os.path.exists(firefox_cache):
                # 对于Firefox，我们需要扫描每个配置文件
                if system == "Windows":
                    # 扫描每个配置文件目录
                    for profile in os.listdir(firefox_cache):
                        profile_cache = os.path.join(firefox_cache, profile, "cache2")
                        if os.path.exists(profile_cache):
                            files.extend(self.scan_directory(profile_cache))
                else:
                    files.extend(self.scan_directory(firefox_cache))
            
            # Edge缓存（仅限Windows）
            if system == "Windows":
                edge_cache = os.path.join(home_dir, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Cache")
                if os.path.exists(edge_cache):
                    files.extend(self.scan_directory(edge_cache))
            
        except Exception as e:
            print(f"扫描浏览器缓存时出错: {e}")
        
        return files
    
    def scan_log_files(self):
        """扫描日志文件"""
        files = []
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows日志
                log_paths = [
                    os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Logs"),
                    os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Temp")
                ]
                
                for log_path in log_paths:
                    if os.path.exists(log_path):
                        for root, dirs, filenames in os.walk(log_path):
                            if self.stop_requested:
                                break
                                
                            for filename in filenames:
                                if filename.endswith(".log"):
                                    file_path = os.path.join(root, filename)
                                    try:
                                        file_size = os.path.getsize(file_path)
                                        files.append({
                                            "path": file_path,
                                            "name": filename,
                                            "size": file_size
                                        })
                                    except Exception as e:
                                        print(f"获取日志文件信息时出错: {e}")
            elif system == "Darwin" or system == "Linux":
                # macOS/Linux日志
                log_paths = [
                    "/var/log",
                    os.path.expanduser("~/Library/Logs") if system == "Darwin" else None,
                ]
                
                for log_path in log_paths:
                    if log_path and os.path.exists(log_path):
                        log_files = self.scan_directory(log_path)
                        # 仅包括.log文件
                        log_files = [f for f in log_files if f["name"].endswith(".log")]
                        files.extend(log_files)
        except Exception as e:
            print(f"扫描日志文件时出错: {e}")
        
        return files
    
    def format_size(self, size_bytes):
        """将字节格式化为人类可读的大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024

class SystemCleanerWidget(BaseComponent):
    def __init__(self, settings, parent=None):
        # 在调用setup_ui之前初始化属性
        self.worker = None
        self.scan_results = None
        self.exclusions = []
        self.extensions = [".tmp", ".temp", ".log", ".old", ".bak", ".dmp", ".dump", ".chk"]
        
        # 调用基类构造函数，该构造函数调用setup_ui
        super().__init__(settings, parent)
    
    def get_translation(self, key, default=None):
        """重写 get_translation 以使用正确的部分名称"""
        return self.settings.get_translation("system_cleaner", key, default)
    
    def setup_ui(self):
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # 标题
        self.title = QLabel(self.get_translation("title"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        self.main_layout.addWidget(self.title)
        
        # 描述
        self.description = QLabel(self.get_translation("description"))
        self.description.setStyleSheet("font-size: 14px; color: #a0a0a0;")
        self.main_layout.addWidget(self.description)
        
        # 选项卡小部件
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #252525;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #a0a0a0;
                border: 1px solid #3a3a3a;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #252525;
                color: #e0e0e0;
            }
            QTabBar::tab:hover {
                background-color: #303030;
            }
        """)
        
        # 扫描选项卡
        self.scan_tab = QWidget()
        self.setup_scan_tab()
        self.tab_widget.addTab(self.scan_tab, self.get_translation("scan_tab"))
        
        # 结果选项卡
        self.results_tab = QWidget()
        self.setup_results_tab()
        self.tab_widget.addTab(self.results_tab, self.get_translation("results_tab"))
        
        # 设置选项卡
        self.settings_tab = QWidget()
        self.setup_settings_tab()
        self.tab_widget.addTab(self.settings_tab, self.get_translation("settings_tab"))
        
        # 将选项卡小部件添加到主布局
        self.main_layout.addWidget(self.tab_widget)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                color: white;
                background-color: #2a2a2a;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00a8ff;
                border-radius: 4px;
            }
        """)
        self.main_layout.addWidget(self.progress_bar)
        
        # 威胁发现
        threats_group = QGroupBox(self.get_translation("threats_found", "检测到的威胁"))
        threats_group.setObjectName("threats_group")
        threats_layout = QVBoxLayout(threats_group)
        
        self.threats_table = QTableWidget(0, 3)
        self.threats_table.setObjectName("threats_table")
        self.threats_table.setHorizontalHeaderLabels([
            self.get_translation("file", "文件"),
            self.get_translation("threat_type", "威胁类型"),
            self.get_translation("status", "状态")
        ])
        self.threats_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.threats_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.threats_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        threats_layout.addWidget(self.threats_table)
        self.main_layout.addWidget(threats_group)
        
        # 日志输出
        log_group = QGroupBox(self.get_translation("log_output", "扫描日志"))
        log_group.setObjectName("log_group")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setObjectName("log_text")
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        self.main_layout.addWidget(log_group)
        
        # 操作按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.start_button = QPushButton(self.get_translation("scan_button"))
        self.start_button.setObjectName("start_button")
        self.start_button.setMinimumWidth(120)
        buttons_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton(self.get_translation("stop_button"))
        self.stop_button.setObjectName("stop_button")
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumWidth(120)
        buttons_layout.addWidget(self.stop_button)
        
        self.fix_button = QPushButton(self.get_translation("clean_threats"))
        self.fix_button.setObjectName("fix_button")
        self.fix_button.setEnabled(False)
        self.fix_button.setMinimumWidth(120)
        buttons_layout.addWidget(self.fix_button)
        
        self.main_layout.addLayout(buttons_layout)
        
        # 连接信号
        self.start_button.clicked.connect(self.start_scan)
        self.stop_button.clicked.connect(self.stop_scan)
        self.fix_button.clicked.connect(self.fix_threats)
        
        # 初始设置
        ready_message = self.get_translation("ready_to_scan", "系统清理工具准备就绪。选择清理选项并单击'开始扫描'。")
        self.log_text.append(ready_message)
    
    def setup_scan_tab(self):
        """设置扫描选项卡"""
        layout = QVBoxLayout(self.scan_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Scan options group
        self.scan_options_group = QGroupBox(self.get_translation("scan_options"))
        self.scan_options_group.setStyleSheet("""
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
        scan_layout = QVBoxLayout(self.scan_options_group)
        
        # Checkboxes for scan options
        self.temp_files_check = QCheckBox(self.get_translation("temp_files"))
        self.temp_files_check.setChecked(True)
        self.temp_files_check.setStyleSheet("color: #e0e0e0;")
        scan_layout.addWidget(self.temp_files_check)
        
        self.recycle_bin_check = QCheckBox(self.get_translation("recycle_bin"))
        self.recycle_bin_check.setChecked(True)
        self.recycle_bin_check.setStyleSheet("color: #e0e0e0;")
        scan_layout.addWidget(self.recycle_bin_check)
        
        self.cache_files_check = QCheckBox(self.get_translation("cache_files"))
        self.cache_files_check.setChecked(True)
        self.cache_files_check.setStyleSheet("color: #e0e0e0;")
        scan_layout.addWidget(self.cache_files_check)
        
        self.log_files_check = QCheckBox(self.get_translation("log_files"))
        self.log_files_check.setChecked(True)
        self.log_files_check.setStyleSheet("color: #e0e0e0;")
        scan_layout.addWidget(self.log_files_check)
        
        layout.addWidget(self.scan_options_group)
        
        # Add some spacing
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Scan button
        self.start_scan_button = QPushButton(self.get_translation("start_scan"))
        self.start_scan_button.setStyleSheet("""
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
        self.start_scan_button.clicked.connect(self.start_scan)
        
        # Button container (for right alignment)
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(self.start_scan_button)
        
        layout.addWidget(button_container)
    
    def setup_results_tab(self):
        """设置扫描结果选项卡"""
        layout = QVBoxLayout(self.results_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                color: #e0e0e0;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #303030;
            }
            QListWidget::item:selected {
                background-color: #353535;
            }
            QListWidget::item:hover {
                background-color: #303030;
            }
        """)
        layout.addWidget(self.results_list)
        
        # Summary
        self.summary_frame = QFrame()
        self.summary_frame.setObjectName("summaryFrame")
        self.summary_frame.setStyleSheet("""
            #summaryFrame {
                background-color: #2d2d2d;
                border-radius: 4px;
                border: 1px solid #3a3a3a;
            }
        """)
        
        summary_layout = QHBoxLayout(self.summary_frame)
        summary_layout.setContentsMargins(15, 10, 15, 10)
        
        # Items found
        self.items_found_label = QLabel(self.get_translation("items_found") + ":")
        self.items_found_label.setStyleSheet("color: #a0a0a0;")
        summary_layout.addWidget(self.items_found_label)
        
        self.items_found_value = QLabel("0")
        self.items_found_value.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        summary_layout.addWidget(self.items_found_value)
        
        summary_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Space to free
        self.space_label = QLabel(self.get_translation("space_to_free") + ":")
        self.space_label.setStyleSheet("color: #a0a0a0;")
        summary_layout.addWidget(self.space_label)
        
        self.space_value = QLabel("0 B")
        self.space_value.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        summary_layout.addWidget(self.space_value)
        
        layout.addWidget(self.summary_frame)
        
        # Clean button
        self.clean_button = QPushButton(self.get_translation("clean_selected"))
        self.clean_button.setEnabled(False)
        self.clean_button.setStyleSheet("""
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
        self.clean_button.clicked.connect(self.start_clean)
        
        # Button container (for right alignment)
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(self.clean_button)
        
        layout.addWidget(button_container)
    
    def setup_settings_tab(self):
        """设置设置选项卡"""
        layout = QVBoxLayout(self.settings_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Exclusions group
        self.exclusions_group = QGroupBox(self.get_translation("exclusions"))
        self.exclusions_group.setStyleSheet("""
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
        exclusions_layout = QVBoxLayout(self.exclusions_group)
        
        # Exclusions list
        self.exclusions_list = QListWidget()
        self.exclusions_list.setStyleSheet("""
            QListWidget {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                color: #e0e0e0;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #303030;
            }
            QListWidget::item:selected {
                background-color: #353535;
            }
            QListWidget::item:hover {
                background-color: #303030;
            }
        """)
        exclusions_layout.addWidget(self.exclusions_list)
        
        # Exclusion buttons
        exclusion_buttons = QWidget()
        exclusion_buttons_layout = QHBoxLayout(exclusion_buttons)
        exclusion_buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.add_exclusion_button = QPushButton(self.get_translation("add"))
        self.add_exclusion_button.clicked.connect(self.add_exclusion)
        exclusion_buttons_layout.addWidget(self.add_exclusion_button)
        
        self.remove_exclusion_button = QPushButton(self.get_translation("remove"))
        self.remove_exclusion_button.clicked.connect(self.remove_exclusion)
        exclusion_buttons_layout.addWidget(self.remove_exclusion_button)
        
        exclusions_layout.addWidget(exclusion_buttons)
        
        layout.addWidget(self.exclusions_group)
        
        # Extensions group
        self.extensions_group = QGroupBox(self.get_translation("file_extensions"))
        self.extensions_group.setStyleSheet("""
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
        extensions_layout = QVBoxLayout(self.extensions_group)
        
        # Extensions list
        self.extensions_list = QListWidget()
        self.extensions_list.setStyleSheet("""
            QListWidget {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                color: #e0e0e0;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #303030;
            }
            QListWidget::item:selected {
                background-color: #353535;
            }
            QListWidget::item:hover {
                background-color: #303030;
            }
        """)
        extensions_layout.addWidget(self.extensions_list)
        
        # Extension buttons
        extension_buttons = QWidget()
        extension_buttons_layout = QHBoxLayout(extension_buttons)
        extension_buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.add_extension_button = QPushButton(self.get_translation("add"))
        self.add_extension_button.clicked.connect(self.add_extension)
        extension_buttons_layout.addWidget(self.add_extension_button)
        
        self.remove_extension_button = QPushButton(self.get_translation("remove"))
        self.remove_extension_button.clicked.connect(self.remove_extension)
        extension_buttons_layout.addWidget(self.remove_extension_button)
        
        extensions_layout.addWidget(extension_buttons)
        
        layout.addWidget(self.extensions_group)
        
        # Add some default extensions
        default_extensions = [".tmp", ".temp", ".log", ".old", ".bak", ".cache"]
        for ext in default_extensions:
            if ext not in self.extensions:
                self.extensions.append(ext)
                self.extensions_list.addItem(ext)
    
    def start_scan(self):
        """开始扫描过程"""
        # Get scan options
        options = {
            "temp_files": self.temp_files_check.isChecked(),
            "recycle_bin": self.recycle_bin_check.isChecked(),
            "cache_files": self.cache_files_check.isChecked(),
            "log_files": self.log_files_check.isChecked()
        }
        
        # Clear previous results
        self.results_list.clear()
        self.items_found_value.setText("0")
        self.space_value.setText("0 B")
        self.scan_results = None
        self.clean_button.setEnabled(False)
        
        # Disable scan button during scan
        self.start_scan_button.setEnabled(False)
        self.start_scan_button.setText(self.get_translation("scanning"))
        
        # Start worker thread
        self.worker = CleanerWorker(options, self.exclusions, self.extensions, "scan")
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.scan_completed.connect(self.scan_completed)
        self.worker.start()
        
        # Update UI to show scan is in progress
        self.stop_button.setEnabled(True)
    
    def update_progress(self, progress, status):
        """更新进度条和状态标签"""
        self.progress_bar.setValue(progress)
        self.log_text.append(status)
    
    def scan_completed(self, results):
        """处理扫描完成"""
        self.scan_results = results
        
        # Re-enable scan button
        self.start_scan_button.setEnabled(True)
        self.start_scan_button.setText(self.get_translation("start_scan"))
        
        # Disable stop button
        self.stop_button.setEnabled(False)
        
        # Update results
        self.items_found_value.setText(str(results["count"]))
        self.space_value.setText(self.format_size(results["total_size"]))
        
        # Populate results list
        for file_info in results["files"]:
            item = QListWidgetItem(f"{file_info['name']} ({self.format_size(file_info['size'])})")
            item.setToolTip(file_info['path'])
            self.results_list.addItem(item)
        
        # Enable clean button if files were found
        self.clean_button.setEnabled(results["count"] > 0)
        
        # Switch to results tab
        self.tab_widget.setCurrentIndex(1)
    
    def start_clean(self):
        """开始清理过程"""
        if not self.scan_results:
            return
        
        # Disable clean button during cleaning
        self.clean_button.setEnabled(False)
        self.clean_button.setText(self.get_translation("cleaning"))
        
        # Start worker thread
        self.worker = CleanerWorker({"files": self.scan_results["files"]}, self.exclusions, self.extensions, "clean")
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.clean_completed.connect(self.clean_completed)
        self.worker.start()
    
    def clean_completed(self, results):
        """处理清理完成"""
        # Re-enable clean button
        self.clean_button.setEnabled(True)
        self.clean_button.setText(self.get_translation("clean_selected"))
        
        # Update status
        self.log_text.append(self.get_translation("clean_complete"))
        self.log_text.append(f"清理了 {results['cleaned_count']} 个文件 ({self.format_size(results['cleaned_size'])})")
        
        if results['failed_count'] > 0:
            self.log_text.append(f"清理失败: {results['failed_count']} 个文件")
        
        # Clear results after cleaning
        self.results_list.clear()
        self.items_found_value.setText("0")
        self.space_value.setText("0 B")
        self.scan_results = None
    
    def add_exclusion(self):
        """添加文件或目录到排除列表"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择要排除的目录")
        if dir_path and dir_path not in self.exclusions:
            self.exclusions.append(dir_path)
            self.exclusions_list.addItem(dir_path)
    
    def remove_exclusion(self):
        """从排除列表中删除文件或目录"""
        selected_items = self.exclusions_list.selectedItems()
        if selected_items:
            for item in selected_items:
                row = self.exclusions_list.row(item)
                item_text = item.text()
                self.exclusions_list.takeItem(row)
                if item_text in self.exclusions:
                    self.exclusions.remove(item_text)
    
    def add_extension(self):
        """添加文件扩展名到列表"""
        # Simple dialog for extension input would go here
        # For now, just add a default
        extension = ".tmp"  # This should come from user input
        if extension and extension not in self.extensions:
            self.extensions.append(extension)
            self.extensions_list.addItem(extension)
    
    def remove_extension(self):
        """从列表中删除文件扩展名"""
        selected_items = self.extensions_list.selectedItems()
        if selected_items:
            for item in selected_items:
                row = self.extensions_list.row(item)
                item_text = item.text()
                self.extensions_list.takeItem(row)
                if item_text in self.extensions:
                    self.extensions.remove(item_text)
    
    def format_size(self, size_bytes):
        """将字节格式化为人类可读的大小"""
        size_bytes = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024 or unit == 'TB':
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024

    def refresh_language(self):
        """使用新翻译更新UI元素"""
        self.title.setText(self.get_translation("title"))
        self.description.setText(self.get_translation("description"))
        self.tab_widget.setTabText(0, self.get_translation("scan_tab"))
        self.tab_widget.setTabText(1, self.get_translation("results_tab"))
        self.tab_widget.setTabText(2, self.get_translation("settings_tab"))
        
        # Update scan tab elements
        self.scan_options_group.setTitle(self.get_translation("scan_options"))
        self.temp_files_check.setText(self.get_translation("temp_files"))
        self.recycle_bin_check.setText(self.get_translation("recycle_bin"))
        self.cache_files_check.setText(self.get_translation("cache_files"))
        self.log_files_check.setText(self.get_translation("log_files"))
        self.start_scan_button.setText(self.get_translation("start_scan"))
        self.log_text.append(self.get_translation("ready_to_scan"))
        
        # Update results tab elements
        self.items_found_label.setText(self.get_translation("items_found") + ":")
        self.space_label.setText(self.get_translation("space_to_free") + ":")
        self.clean_button.setText(self.get_translation("clean_selected"))
        
        # Update settings tab elements
        self.exclusions_group.setTitle(self.get_translation("exclusions"))
        self.add_exclusion_button.setText(self.get_translation("add"))
        self.remove_exclusion_button.setText(self.get_translation("remove"))
        self.extensions_group.setTitle(self.get_translation("file_extensions"))
        self.add_extension_button.setText(self.get_translation("add"))
        self.remove_extension_button.setText(self.get_translation("remove"))
        
        # Add animation to highlight the change
        super().refresh_language()
    
    def stop_scan(self):
        """停止正在进行的扫描过程"""
        if self.worker and hasattr(self.worker, 'stop'):
            self.worker.stop()
            self.log_text.append(self.get_translation("scan_stopped", "扫描已停止"))
            
            # Re-enable scan button
            self.start_scan_button.setEnabled(True)
            self.start_scan_button.setText(self.get_translation("start_scan"))
            self.stop_button.setEnabled(False)
    
    def fix_threats(self):
        """修复检测到的威胁（即清理检测到的文件）"""
        if not self.scan_results or self.scan_results["count"] == 0:
            return
        
        # 确认操作
        reply = QMessageBox.question(
            self, 
            self.get_translation("confirm_action", "确认操作"), 
            self.get_translation("confirm_clean", "确定要清理检测到的{count}个文件吗？").format(count=self.scan_results["count"]),
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 开始清理过程
            self.start_clean() 