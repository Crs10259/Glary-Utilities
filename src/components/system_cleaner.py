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
                            QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from components.base_component import BaseComponent
from utils.logger import Logger

# 获取logger实例
logger = Logger().get_logger()

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
                logger.error(f"清理 {file_path} 时出错: {e}")
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
                        logger.error(f"获取文件信息时出错 {file_path}: {e}")
        except Exception as e:
            logger.error(f"扫描目录 {directory} 时出错: {e}")
        
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
            logger.error(f"扫描回收站时出错: {e}")
        
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
            logger.error(f"扫描浏览器缓存时出错: {e}")
        
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
                                        logger.error(f"获取日志文件信息时出错: {e}")
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
            logger.error(f"扫描日志文件时出错: {e}")
        
        return files
    
    def format_size(self, size_bytes):
        """将字节格式化为人类可读的大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024

class SystemCleanerWidget(BaseComponent):
    def __init__(self, parent=None):
        # 在调用setup_ui之前初始化属性
        self.scan_worker = None
        self.clean_worker = None
        self.scan_results = None
        self.exclusions = []
        self.extensions = []
        
        # 调用父类构造函数
        super().__init__(parent)
        
        # 加载排除项和扩展名
        self.load_exclusions()
        self.load_extensions()
    
    def get_translation(self, key, default=None):
        """重写 get_translation 以使用正确的部分名称"""
        return self.settings.get_translation("system_cleaner", key, default)
    
    def setup_ui(self):
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # 标题和描述
        self.title = QLabel(self.get_translation("title"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        self.main_layout.addWidget(self.title)
        
        self.description = QLabel(self.get_translation("description"))
        self.description.setStyleSheet("font-size: 14px; color: #a0a0a0;")
        self.description.setWordWrap(True)
        self.main_layout.addWidget(self.description)
        
        # 创建水平分割的主布局区域
        self.content_layout = QHBoxLayout()
        self.main_layout.addLayout(self.content_layout, 1)  # 设置伸展因子
        
        # 左侧面板 - 选项卡和按钮
        self.left_panel = QWidget()
        self.left_panel_layout = QVBoxLayout(self.left_panel)
        self.left_panel_layout.setContentsMargins(0, 0, 10, 0)
        self.left_panel.setMaximumWidth(500)  # 限制左侧面板宽度
        
        # 选项卡小部件
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                background-color: #252525;
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
        
        # 创建选项卡
        self.scan_tab = QWidget()
        self.results_tab = QWidget()
        self.settings_tab = QWidget()
        
        # 设置选项卡内容
        self.setup_scan_tab()
        self.setup_results_tab()
        self.setup_settings_tab()
        
        # 添加选项卡到选项卡小部件
        self.tab_widget.addTab(self.scan_tab, self.get_translation("scan_tab"))
        self.tab_widget.addTab(self.results_tab, self.get_translation("results_tab"))
        self.tab_widget.addTab(self.settings_tab, self.get_translation("settings_tab"))
        
        # 添加选项卡小部件到左面板
        self.left_panel_layout.addWidget(self.tab_widget)
        
        # 添加按钮到左面板
        buttons_layout = QHBoxLayout()
        
        self.start_scan_button = QPushButton(self.get_translation("start_scan"))
        self.start_scan_button.setStyleSheet("""
            QPushButton {
                background-color: #00a8ff;
                color: white;
                border: none;
                border-radius: 4px;
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
                color: #888888;
            }
        """)
        self.start_scan_button.clicked.connect(self.start_scan)
        buttons_layout.addWidget(self.start_scan_button)
        
        self.stop_button = QPushButton(self.get_translation("stop"))
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.stop_button.clicked.connect(self.stop_scan)
        buttons_layout.addWidget(self.stop_button)
        
        self.clean_button = QPushButton(self.get_translation("clean_selected"))
        self.clean_button.setEnabled(False)
        self.clean_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.clean_button.clicked.connect(self.start_clean)
        buttons_layout.addWidget(self.clean_button)
        
        self.left_panel_layout.addLayout(buttons_layout)
        
        # 添加左面板到主内容布局
        self.content_layout.addWidget(self.left_panel)
        
        # 右侧面板 - 日志和进度
        self.right_panel = QWidget()
        self.right_panel_layout = QVBoxLayout(self.right_panel)
        self.right_panel_layout.setContentsMargins(10, 0, 0, 0)
        
        # 日志标签和滚动区域
        log_label = QLabel(self.get_translation("log_output"))
        log_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        self.right_panel_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(400)  # 增加日志区域高度
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
                line-height: 1.5;
            }
        """)
        self.right_panel_layout.addWidget(self.log_text, 1)  # 设置伸展因子
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00a8ff;
                border-radius: 3px;
            }
        """)
        self.right_panel_layout.addWidget(self.progress_bar)
        
        # 添加右面板到主内容布局
        self.content_layout.addWidget(self.right_panel, 1)  # 设置伸展因子，优先给右面板更多空间
        
        # 初始化默认内容
        self.log_text.append(self.get_translation("welcome_message", "The cleaning tool is ready. Please select the cleaning options and click 'Start Scan'。"))
    
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
        self.temp_files_check.setObjectName("cleaner_temp_files")
        self.temp_files_check.setChecked(True)
        scan_layout.addWidget(self.temp_files_check)
        
        self.recycle_bin_check = QCheckBox(self.get_translation("recycle_bin"))
        self.recycle_bin_check.setObjectName("cleaner_recycle_bin")
        self.recycle_bin_check.setChecked(True)
        scan_layout.addWidget(self.recycle_bin_check)
        
        self.cache_files_check = QCheckBox(self.get_translation("cache_files"))
        self.cache_files_check.setObjectName("cleaner_cache_files")
        self.cache_files_check.setChecked(True)
        scan_layout.addWidget(self.cache_files_check)
        
        self.log_files_check = QCheckBox(self.get_translation("log_files"))
        self.log_files_check.setObjectName("cleaner_log_files")
        self.log_files_check.setChecked(True)
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
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建排除组
        self.exclusions_group = QGroupBox(self.get_translation("exclusions"))
        exclusions_layout = QVBoxLayout()
        
        self.exclusions_list = QListWidget()
        
        # 从设置加载排除项
        for item in self.exclusions:
            self.exclusions_list.addItem(item)
        
        # 排除项按钮
        exclusion_buttons = QWidget()
        exclusion_buttons_layout = QHBoxLayout(exclusion_buttons)
        exclusion_buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.add_exclusion_button = QPushButton(self.get_translation("add"))
        self.add_exclusion_button.clicked.connect(self.add_exclusion)
        
        self.remove_exclusion_button = QPushButton(self.get_translation("remove"))
        self.remove_exclusion_button.clicked.connect(self.remove_exclusion)
        
        exclusion_buttons_layout.addWidget(self.add_exclusion_button)
        exclusion_buttons_layout.addWidget(self.remove_exclusion_button)
        
        exclusions_layout.addWidget(self.exclusions_list)
        exclusions_layout.addWidget(exclusion_buttons)
        
        self.exclusions_group.setLayout(exclusions_layout)
        layout.addWidget(self.exclusions_group)
        
        # 创建扩展名组
        self.extensions_group = QGroupBox(self.get_translation("file_extensions"))
        extensions_layout = QVBoxLayout()
        
        # 添加输入框用于输入扩展名
        input_layout = QHBoxLayout()
        self.extension_input = QLineEdit()
        self.extension_input.setPlaceholderText(self.get_translation("add_extension_placeholder", "输入文件扩展名 (例如 .tmp)"))
        self.extension_input.returnPressed.connect(self.add_extension)
        
        self.add_extension_button = QPushButton(self.get_translation("add"))
        self.add_extension_button.clicked.connect(self.add_extension)
        
        input_layout.addWidget(self.extension_input)
        input_layout.addWidget(self.add_extension_button)
        
        extensions_layout.addLayout(input_layout)
        
        self.extensions_list = QListWidget()
        
        # 从设置加载扩展名列表
        for ext in self.extensions:
            self.extensions_list.addItem(ext)
        
        # 扩展名按钮
        extension_buttons = QWidget()
        extension_buttons_layout = QHBoxLayout(extension_buttons)
        extension_buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.remove_extension_button = QPushButton(self.get_translation("remove"))
        self.remove_extension_button.clicked.connect(self.remove_extension)
        
        extension_buttons_layout.addWidget(self.remove_extension_button)
        
        extensions_layout.addWidget(self.extensions_list)
        extensions_layout.addWidget(extension_buttons)
        
        self.extensions_group.setLayout(extensions_layout)
        layout.addWidget(self.extensions_group)
        
        # 设置标签的布局
        self.settings_tab.setLayout(layout)
        
        # 检查是否有预设的扩展名，如果没有则添加默认扩展名
        if not self.extensions or len(self.extensions) == 0:
            # 添加一些默认扩展名
            default_extensions = [".tmp", ".temp", ".log", ".old", ".bak", ".cache", ".dmp", ".dump", ".chk"]
            
            # 遍历默认扩展名并添加到列表中
            for ext in default_extensions:
                if ext not in self.extensions:
                    self.extensions.append(ext)
                    self.extensions_list.addItem(ext)
            
            # 保存默认扩展名到设置
            self.save_extensions()
    
    def start_scan(self):
        """开始扫描过程"""
        # 获取扫描选项
        options = {
            "temp_files": self.temp_files_check.isChecked(),
            "recycle_bin": self.recycle_bin_check.isChecked(),
            "cache_files": self.cache_files_check.isChecked(),
            "log_files": self.log_files_check.isChecked()
        }
        
        # 清除之前的结果
        self.results_list.clear()
        self.items_found_value.setText("0")
        self.space_value.setText("0 B")
        self.scan_results = None
        self.clean_button.setEnabled(False)
        
        # 扫描期间禁用扫描按钮
        self.start_scan_button.setEnabled(False)
        self.start_scan_button.setText(self.get_translation("scanning"))
        
        # 启动工作线程
        self.scan_worker = CleanerWorker(options, self.exclusions, self.extensions, "scan")
        self.scan_worker.progress_updated.connect(self.update_progress)
        self.scan_worker.scan_completed.connect(self.scan_completed)
        self.scan_worker.start()
        
        # 更新UI以显示扫描正在进行中
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
        self.clean_worker = CleanerWorker({"files": self.scan_results["files"]}, self.exclusions, self.extensions, "clean")
        self.clean_worker.progress_updated.connect(self.update_progress)
        self.clean_worker.clean_completed.connect(self.clean_completed)
        self.clean_worker.start()
    
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
        # 使用文件对话框选择文件或目录
        dir_path = QFileDialog.getExistingDirectory(
            self,
            self.get_translation("select_directory", "选择要排除的目录"),
            os.path.expanduser("~")
        )
        
        # 如果用户选择了目录
        if dir_path:
            if dir_path not in self.exclusions:
                self.exclusions.append(dir_path)
                self.exclusions_list.addItem(dir_path)
                # 添加成功后显示确认消息
                self.log_text.append(self.get_translation("exclusion_added", f"已添加排除项: {dir_path}"))
                # 立即保存到设置
                self.save_exclusions()
            else:
                # 如果路径已存在，显示提示消息
                self.log_text.append(self.get_translation("exclusion_exists", f"排除项 {dir_path} 已存在"))
    
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
                    # 添加移除确认消息
                    self.log_text.append(self.get_translation("exclusion_removed", f"已移除排除项: {item_text}"))
            
            # 立即保存到设置
            self.save_exclusions()
    
    def add_extension(self):
        """添加文件扩展名到过滤列表"""
        # 获取目前选定的文本并去除前导点
        text = self.extension_input.text().strip()
        if text:
            # 确保扩展名格式正确
            extension = text if text.startswith('.') else '.' + text
            
            # 避免重复添加
            if extension not in self.extensions:
                self.extensions.append(extension)
                self.extensions_list.addItem(extension)
                # 添加成功后显示确认消息
                self.log_text.append(f"已添加扩展名: {extension}")
                # 切换到设置选项卡以显示新添加的扩展名
                self.tab_widget.setCurrentIndex(2)
                # 保存到设置
                self.save_extensions()
            else:
                # 显示扩展名已存在的消息
                self.log_text.append(f"扩展名 {extension} 已存在")
            
            # 清空输入框
            self.extension_input.clear()
    
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
                    # 添加移除确认消息
                    self.log_text.append(self.get_translation("extension_removed", f"已移除扩展名: {item_text}"))
            
            # 立即保存到设置
            self.save_extensions()
    
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
        if self.scan_worker and hasattr(self.scan_worker, 'stop'):
            self.scan_worker.stop()
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

    def load_exclusions(self):
        """从设置加载排除项列表"""
        try:
            saved_exclusions = self.settings.get_setting("system_cleaner_exclusions", [])
            if saved_exclusions:
                self.exclusions = saved_exclusions
                # 更新UI列表
                self.exclusions_list.clear()
                for excl in self.exclusions:
                    self.exclusions_list.addItem(excl)
                logger.debug(f"已加载 {len(self.exclusions)} 个排除项")
        except Exception as e:
            logger.error(f"加载排除项失败: {str(e)}")
    
    def save_exclusions(self):
        """保存排除项列表到设置"""
        try:
            self.settings.set_setting("system_cleaner_exclusions", self.exclusions)
            logger.debug(f"已保存 {len(self.exclusions)} 个排除项")
        except Exception as e:
            logger.error(f"保存排除项失败: {str(e)}")

    def load_extensions(self):
        """从设置加载扩展名列表"""
        try:
            saved_extensions = self.settings.get_setting("system_cleaner_extensions", [])
            if saved_extensions:
                self.extensions = saved_extensions
                # 更新UI列表
                self.extensions_list.clear()
                for ext in self.extensions:
                    self.extensions_list.addItem(ext)
                logger.debug(f"已加载 {len(self.extensions)} 个扩展名")
        except Exception as e:
            logger.error(f"加载扩展名失败: {str(e)}")
    
    def save_extensions(self):
        """保存扩展名列表到设置"""
        try:
            self.settings.set_setting("system_cleaner_extensions", self.extensions)
            logger.debug(f"已保存 {len(self.extensions)} 个扩展名")
        except Exception as e:
            logger.error(f"保存扩展名失败: {str(e)}") 