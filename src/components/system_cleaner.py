import os
import sys
import shutil
import tempfile
import platform
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QCheckBox, QLineEdit, QListWidget, QFileDialog,
                            QProgressBar, QTabWidget, QGroupBox, QFormLayout,
                            QListWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont
from components.base_component import BaseComponent

class CleanerWorker(QThread):
    """Worker thread for scanning and cleaning files"""
    progress_updated = pyqtSignal(int, str)
    scan_completed = pyqtSignal(dict)
    clean_completed = pyqtSignal(dict)
    
    def __init__(self, options, exclusions, extensions, operation="scan"):
        super().__init__()
        self.options = options  # Dictionary of options to scan for
        self.exclusions = exclusions  # List of excluded directories/files
        self.extensions = extensions  # List of file extensions to clean
        self.operation = operation  # "scan" or "clean"
        self.stop_requested = False
    
    def run(self):
        """Run the worker thread"""
        if self.operation == "scan":
            self.scan_files()
        elif self.operation == "clean":
            self.clean_files()
    
    def stop(self):
        """Request the worker to stop"""
        self.stop_requested = True
    
    def scan_files(self):
        """Scan for unnecessary files"""
        results = {
            "files": [],
            "total_size": 0,
            "count": 0
        }
        
        # Get temp directory
        temp_dir = tempfile.gettempdir()
        
        # Get user home directory
        home_dir = os.path.expanduser("~")
        
        progress = 0
        self.progress_updated.emit(progress, "Starting scan...")
        
        # Scan temporary files
        if self.options.get("temp_files", False):
            self.progress_updated.emit(progress, "Scanning temporary files...")
            temp_files = self.scan_directory(temp_dir)
            results["files"].extend(temp_files)
            progress += 20
            self.progress_updated.emit(progress, f"Found {len(temp_files)} temporary files")
        
        # Scan recycle bin
        if self.options.get("recycle_bin", False):
            self.progress_updated.emit(progress, "Scanning recycle bin...")
            recycle_files = self.scan_recycle_bin()
            results["files"].extend(recycle_files)
            progress += 20
            self.progress_updated.emit(progress, f"Found {len(recycle_files)} files in recycle bin")
        
        # Scan cache files (browsers)
        if self.options.get("cache_files", False):
            self.progress_updated.emit(progress, "Scanning cache files...")
            cache_files = self.scan_browser_caches(home_dir)
            results["files"].extend(cache_files)
            progress += 20
            self.progress_updated.emit(progress, f"Found {len(cache_files)} cache files")
        
        # Scan log files
        if self.options.get("log_files", False):
            self.progress_updated.emit(progress, "Scanning log files...")
            log_files = self.scan_log_files()
            results["files"].extend(log_files)
            progress += 20
            self.progress_updated.emit(progress, f"Found {len(log_files)} log files")
        
        # Calculate totals
        results["count"] = len(results["files"])
        results["total_size"] = sum(file["size"] for file in results["files"])
        
        self.progress_updated.emit(100, f"Scan completed. Found {results['count']} files ({self.format_size(results['total_size'])})")
        self.scan_completed.emit(results)
    
    def clean_files(self):
        """Clean selected files"""
        results = {
            "cleaned_count": 0,
            "cleaned_size": 0,
            "failed_count": 0
        }
        
        total_files = len(self.options.get("files", []))
        if total_files == 0:
            self.progress_updated.emit(100, "No files to clean")
            self.clean_completed.emit(results)
            return
        
        self.progress_updated.emit(0, f"Cleaning {total_files} files...")
        
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
                    self.progress_updated.emit(progress, f"Cleaned {results['cleaned_count']} files ({self.format_size(results['cleaned_size'])})")
                else:
                    results["failed_count"] += 1
            except Exception as e:
                print(f"Error cleaning {file_path}: {e}")
                results["failed_count"] += 1
        
        self.progress_updated.emit(100, f"Cleaning completed. Cleaned {results['cleaned_count']} files ({self.format_size(results['cleaned_size'])})")
        self.clean_completed.emit(results)
    
    def scan_directory(self, directory):
        """Scan a directory for files to clean"""
        files = []
        
        try:
            for root, dirs, filenames in os.walk(directory):
                if self.stop_requested:
                    break
                    
                # Skip excluded directories
                dirs[:] = [d for d in dirs if os.path.join(root, d) not in self.exclusions]
                
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    
                    # Skip excluded files
                    if file_path in self.exclusions:
                        continue
                    
                    # Only include files with specified extensions if extensions are provided
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
                        print(f"Error getting file info for {file_path}: {e}")
        except Exception as e:
            print(f"Error scanning directory {directory}: {e}")
        
        return files
    
    def scan_recycle_bin(self):
        """Scan the recycle bin for files"""
        files = []
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows recycle bin is at C:\\$Recycle.Bin
                recycle_bin = "C:\\$Recycle.Bin"
                if os.path.exists(recycle_bin):
                    files = self.scan_directory(recycle_bin)
            elif system == "Darwin":  # macOS
                # macOS trash is at ~/.Trash
                trash_path = os.path.expanduser("~/.Trash")
                if os.path.exists(trash_path):
                    files = self.scan_directory(trash_path)
            elif system == "Linux":
                # Linux trash is at ~/.local/share/Trash
                trash_path = os.path.expanduser("~/.local/share/Trash")
                if os.path.exists(trash_path):
                    files = self.scan_directory(trash_path)
        except Exception as e:
            print(f"Error scanning recycle bin: {e}")
        
        return files
    
    def scan_browser_caches(self, home_dir):
        """Scan browser cache directories"""
        files = []
        
        try:
            system = platform.system()
            
            # Chrome cache
            chrome_cache = None
            if system == "Windows":
                chrome_cache = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Cache")
            elif system == "Darwin":
                chrome_cache = os.path.join(home_dir, "Library", "Caches", "Google", "Chrome")
            elif system == "Linux":
                chrome_cache = os.path.join(home_dir, ".cache", "google-chrome")
            
            if chrome_cache and os.path.exists(chrome_cache):
                files.extend(self.scan_directory(chrome_cache))
            
            # Firefox cache
            firefox_cache = None
            if system == "Windows":
                firefox_cache = os.path.join(home_dir, "AppData", "Local", "Mozilla", "Firefox", "Profiles")
            elif system == "Darwin":
                firefox_cache = os.path.join(home_dir, "Library", "Caches", "Firefox")
            elif system == "Linux":
                firefox_cache = os.path.join(home_dir, ".cache", "mozilla", "firefox")
            
            if firefox_cache and os.path.exists(firefox_cache):
                # For Firefox, we need to scan each profile
                if system == "Windows":
                    # Scan each profile directory
                    for profile in os.listdir(firefox_cache):
                        profile_cache = os.path.join(firefox_cache, profile, "cache2")
                        if os.path.exists(profile_cache):
                            files.extend(self.scan_directory(profile_cache))
                else:
                    files.extend(self.scan_directory(firefox_cache))
            
            # Edge cache (Windows only)
            if system == "Windows":
                edge_cache = os.path.join(home_dir, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Cache")
                if os.path.exists(edge_cache):
                    files.extend(self.scan_directory(edge_cache))
            
        except Exception as e:
            print(f"Error scanning browser caches: {e}")
        
        return files
    
    def scan_log_files(self):
        """Scan for log files"""
        files = []
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows logs
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
                                        print(f"Error getting log file info: {e}")
            elif system == "Darwin" or system == "Linux":
                # macOS/Linux logs
                log_paths = [
                    "/var/log",
                    os.path.expanduser("~/Library/Logs") if system == "Darwin" else None,
                ]
                
                for log_path in log_paths:
                    if log_path and os.path.exists(log_path):
                        log_files = self.scan_directory(log_path)
                        # Filter to only include .log files
                        log_files = [f for f in log_files if f["name"].endswith(".log")]
                        files.extend(log_files)
        except Exception as e:
            print(f"Error scanning log files: {e}")
        
        return files
    
    def format_size(self, size_bytes):
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024 or unit == 'TB':
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024

class SystemCleanerWidget(BaseComponent):
    def __init__(self, settings, parent=None):
        # Initialize properties before calling setup_ui
        self.worker = None
        self.scan_results = None
        self.exclusions = []
        self.extensions = [".tmp", ".temp", ".log", ".old", ".bak", ".dmp", ".dump", ".chk"]
        
        # Call base class constructor which calls setup_ui
        super().__init__(settings, parent)
    
    def get_translation(self, key, default=None):
        """Override get_translation to use the correct section name"""
        return self.settings.get_translation("system_cleaner", key, default)
    
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
        
        # Tab widget
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
        
        # Scan tab
        self.scan_tab = QWidget()
        self.setup_scan_tab()
        self.tab_widget.addTab(self.scan_tab, self.get_translation("scan_tab"))
        
        # Results tab
        self.results_tab = QWidget()
        self.setup_results_tab()
        self.tab_widget.addTab(self.results_tab, self.get_translation("results_tab"))
        
        # Settings tab
        self.settings_tab = QWidget()
        self.setup_settings_tab()
        self.tab_widget.addTab(self.settings_tab, self.get_translation("settings_tab"))
        
        # Add tab widget to main layout
        self.main_layout.addWidget(self.tab_widget)
        
        # Progress bar
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
        
        # Status label
        self.status_label = QLabel(self.get_translation("ready_to_scan"))
        self.status_label.setStyleSheet("color: #a0a0a0;")
        self.main_layout.addWidget(self.status_label)
    
    def setup_scan_tab(self):
        """Setup the scan options tab"""
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
        """Setup the scan results tab"""
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
        """Setup the settings tab"""
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
        """Start the scan process"""
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
    
    def update_progress(self, progress, status):
        """Update progress bar and status label"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
    
    def scan_completed(self, results):
        """Handle scan completion"""
        self.scan_results = results
        
        # Re-enable scan button
        self.start_scan_button.setEnabled(True)
        self.start_scan_button.setText(self.get_translation("start_scan"))
        
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
        """Start the cleaning process"""
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
        """Handle clean completion"""
        # Re-enable clean button
        self.clean_button.setEnabled(True)
        self.clean_button.setText(self.get_translation("clean_selected"))
        
        # Update status
        self.status_label.setText(self.get_translation("clean_complete"))
        
        # Clear results after cleaning
        self.results_list.clear()
        self.items_found_value.setText("0")
        self.space_value.setText("0 B")
        self.scan_results = None
    
    def add_exclusion(self):
        """Add a file or directory to exclusions"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory to Exclude")
        if dir_path and dir_path not in self.exclusions:
            self.exclusions.append(dir_path)
            self.exclusions_list.addItem(dir_path)
    
    def remove_exclusion(self):
        """Remove a file or directory from exclusions"""
        selected_items = self.exclusions_list.selectedItems()
        if selected_items:
            for item in selected_items:
                row = self.exclusions_list.row(item)
                item_text = item.text()
                self.exclusions_list.takeItem(row)
                if item_text in self.exclusions:
                    self.exclusions.remove(item_text)
    
    def add_extension(self):
        """Add a file extension to the list"""
        # Simple dialog for extension input would go here
        # For now, just add a default
        extension = ".tmp"  # This should come from user input
        if extension and extension not in self.extensions:
            self.extensions.append(extension)
            self.extensions_list.addItem(extension)
    
    def remove_extension(self):
        """Remove a file extension from the list"""
        selected_items = self.extensions_list.selectedItems()
        if selected_items:
            for item in selected_items:
                row = self.extensions_list.row(item)
                item_text = item.text()
                self.extensions_list.takeItem(row)
                if item_text in self.extensions:
                    self.extensions.remove(item_text)
    
    def format_size(self, size_bytes):
        """Format bytes to human-readable size"""
        size_bytes = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024 or unit == 'TB':
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024

    def refresh_language(self):
        """Update UI text elements after language change"""
        # Update main title and tab names
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
        self.status_label.setText(self.get_translation("ready_to_scan"))
        
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