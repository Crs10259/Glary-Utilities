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
from tools.system_cleaner import CleanerWorker

class SystemCleanerWidget(BaseComponent):
    def __init__(self, parent=None):
        # Initialize attributes before calling setup_ui
        self.scan_worker = None
        self.clean_worker = None
        self.scan_results = None
        self.exclusions = []
        self.extensions = []
        
        # Call parent class constructor
        super().__init__(parent)
        
        # Load exclusions and extensions
        self.load_exclusions()
        self.load_extensions()

        # Re-apply theme once UI is built so dynamic colors propagate
        self.apply_theme()
    
    def get_translation(self, key, default=None):
        """Override get_translation to use correct section name"""
        return self.settings.get_translation("system_cleaner", key, default)
    
    def setup_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Title and description
        self.title = QLabel(self.get_translation("title"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        self.main_layout.addWidget(self.title)
        
        self.description = QLabel(self.get_translation("description"))
        self.description.setStyleSheet("font-size: 14px; color: #a0a0a0;")
        self.description.setWordWrap(True)
        self.main_layout.addWidget(self.description)
        
        # Create horizontal split main layout area
        self.content_layout = QHBoxLayout()
        self.main_layout.addLayout(self.content_layout, 1)  # Set stretch factor
        
        # Left panel - tabs and buttons
        self.left_panel = QWidget()
        self.left_panel_layout = QVBoxLayout(self.left_panel)
        self.left_panel_layout.setContentsMargins(0, 0, 10, 0)
        self.left_panel.setMaximumWidth(500)  # Limit left panel width
        
        # Tab widgets
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
        
        # Create tabs
        self.scan_tab = QWidget()
        self.results_tab = QWidget()
        self.settings_tab = QWidget()
        
        # Set tab content
        self.setup_scan_tab()
        self.setup_results_tab()
        self.setup_settings_tab()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.scan_tab, self.get_translation("scan_tab"))
        self.tab_widget.addTab(self.results_tab, self.get_translation("results_tab"))
        self.tab_widget.addTab(self.settings_tab, self.get_translation("settings_tab"))
        
        # Add tab widget to left panel
        self.left_panel_layout.addWidget(self.tab_widget)
        
        # Add buttons to left panel
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
        
        # Add left panel to main content layout
        self.content_layout.addWidget(self.left_panel)
        
        # Right panel - log and progress
        self.right_panel = QWidget()
        self.right_panel_layout = QVBoxLayout(self.right_panel)
        self.right_panel_layout.setContentsMargins(10, 0, 0, 0)
        
        # Log label and scroll area
        log_label = QLabel(self.get_translation("log_output"))
        log_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        self.right_panel_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(400)  # Increase log area height
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
        self.right_panel_layout.addWidget(self.log_text, 1)  # Set stretch factor
        
        # Progress bar
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
        
        # Add right panel to main content layout
        self.content_layout.addWidget(self.right_panel, 1)  # Set stretch factor, give right panel more space
        
        # Initialize default content
        self.log_text.append(self.get_translation("welcome_message", "The cleaning tool is ready. Please select the cleaning options and click 'Start Scan'。"))
    
    def setup_scan_tab(self):
        """Setup scan tab"""
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
        """Setup scan results tab"""
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
        """Setup settings tab"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create exclusions group
        self.exclusions_group = QGroupBox(self.get_translation("exclusions"))
        exclusions_layout = QVBoxLayout()
        
        self.exclusions_list = QListWidget()
        
        # Load exclusions from settings
        for item in self.exclusions:
            self.exclusions_list.addItem(item)
        
        # Exclusion buttons
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
        
        # Create extensions group
        self.extensions_group = QGroupBox(self.get_translation("file_extensions"))
        extensions_layout = QVBoxLayout()
        
        # Add input box for entering extensions
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
        
        # Load extensions from settings
        for ext in self.extensions:
            self.extensions_list.addItem(ext)
        
        # Extension buttons
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
        
        # Set layout for labels
        self.settings_tab.setLayout(layout)
        
        # Check if there are any preset extensions, if not add default extensions
        if not self.extensions or len(self.extensions) == 0:
            # Add some default extensions
            default_extensions = [".tmp", ".temp", ".log", ".old", ".bak", ".cache", ".dmp", ".dump", ".chk"]
            
            # Iterate through default extensions and add to list
            for ext in default_extensions:
                if ext not in self.extensions:
                    self.extensions.append(ext)
                    self.extensions_list.addItem(ext)
            
            # Save default extensions to settings
            self.save_extensions()
    
    def start_scan(self):
        """Start scanning process"""
        # Get scanning options
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
        
        # Disable scan button during scanning
        self.start_scan_button.setEnabled(False)
        self.start_scan_button.setText(self.get_translation("scanning"))
        
        # Start worker thread
        self.scan_worker = CleanerWorker(options, self.exclusions, self.extensions, "scan")
        self.scan_worker.progress_updated.connect(self.update_progress)
        self.scan_worker.scan_completed.connect(self.scan_completed)
        self.scan_worker.start()
        
        # Update UI to show scanning is in progress
        self.stop_button.setEnabled(True)
    
    def update_progress(self, progress, status):
        """Update progress bar and status label"""
        self.progress_bar.setValue(progress)

        # If current language is not Chinese, translate known Chinese status strings
        current_lang = self.settings.get_setting("language", "en")
        language_map = {
            "en": "en", "english": "en", "English": "en",
            "zh": "zh", "中文": "zh", "chinese": "zh", "Chinese": "zh"
        }
        lang_code = language_map.get(str(current_lang).lower(), current_lang)

        translated_status = status
        if lang_code != "zh":
            translations_map = {
                "开始扫描...": self.get_translation("scanning", "Scanning..."),
                "扫描临时文件...": self.get_translation("scanning_temp", "Scanning temporary files..."),
                "扫描回收站...": self.get_translation("scanning_recycle", "Scanning recycle bin..."),
                "扫描缓存文件...": self.get_translation("scanning_cache", "Scanning cache files..."),
                "扫描日志文件...": self.get_translation("scanning_logs", "Scanning log files..."),
                "扫描完成。": self.get_translation("scan_complete", "Scan complete."),
                "清理": self.get_translation("cleaning", "Cleaning"),
                "清理完成。": self.get_translation("clean_complete", "Clean complete."),
            }

            for cn, en in translations_map.items():
                if status.startswith(cn):
                    suffix = status[len(cn):]  # Preserve counts etc.
                    translated_status = en + suffix
                    break

        self.log_text.append(translated_status)
    
    def scan_completed(self, results):
        """Handle scan completion"""
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
        """Start cleaning process"""
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
        """Handle cleaning completion"""
        # Re-enable clean button
        self.clean_button.setEnabled(True)
        self.clean_button.setText(self.get_translation("clean_selected"))
        
        # Update status
        self.log_text.append(self.get_translation("clean_complete"))
        self.log_text.append(f"Cleaned {results['cleaned_count']} files ({self.format_size(results['cleaned_size'])})")
        
        if results['failed_count'] > 0:
            self.log_text.append(f"Failed to clean: {results['failed_count']} files")
        
        # Clear results after cleaning
        self.results_list.clear()
        self.items_found_value.setText("0")
        self.space_value.setText("0 B")
        self.scan_results = None
    
    def add_exclusion(self):
        """Add file or directory to exclusion list"""
        # Use file dialog to select file or directory
        dir_path = QFileDialog.getExistingDirectory(
            self,
            self.get_translation("select_directory", "选择要排除的目录"),
            os.path.expanduser("~")
        )
        
        # If user selected directory
        if dir_path:
            if dir_path not in self.exclusions:
                self.exclusions.append(dir_path)
                self.exclusions_list.addItem(dir_path)
                # Show confirmation message after successful addition
                self.log_text.append(self.get_translation("exclusion_added", f"已添加排除项: {dir_path}"))
                # Save immediately to settings
                self.save_exclusions()
            else:
                # Show message if path already exists
                self.log_text.append(self.get_translation("exclusion_exists", f"排除项 {dir_path} 已存在"))
    
    def remove_exclusion(self):
        """Remove file or directory from exclusion list"""
        selected_items = self.exclusions_list.selectedItems()
        if selected_items:
            for item in selected_items:
                row = self.exclusions_list.row(item)
                item_text = item.text()
                self.exclusions_list.takeItem(row)
                if item_text in self.exclusions:
                    self.exclusions.remove(item_text)
                    # Show confirmation message after successful removal
                    self.log_text.append(self.get_translation("exclusion_removed", f"已移除排除项: {item_text}"))
            
            # Save immediately to settings
            self.save_exclusions()
    
    def add_extension(self):
        """Add file extension to filter list"""
        # Get currently selected text and remove leading dot
        text = self.extension_input.text().strip()
        if text:
            # Ensure extension format is correct
            extension = text if text.startswith('.') else '.' + text
            
            # Avoid adding duplicates
            if extension not in self.extensions:
                self.extensions.append(extension)
                self.extensions_list.addItem(extension)
                # Show confirmation message after successful addition
                self.log_text.append(f"已添加扩展名: {extension}")
                # Switch to settings tab to display new added extension
                self.tab_widget.setCurrentIndex(2)
                # Save to settings
                self.save_extensions()
            else:
                # Show message if extension already exists
                self.log_text.append(f"扩展名 {extension} 已存在")
            
            # Clear input box
            self.extension_input.clear()
    
    def remove_extension(self):
        """Remove file extension from list"""
        selected_items = self.extensions_list.selectedItems()
        if selected_items:
            for item in selected_items:
                row = self.extensions_list.row(item)
                item_text = item.text()
                self.extensions_list.takeItem(row)
                if item_text in self.extensions:
                    self.extensions.remove(item_text)
                    # Show confirmation message after successful removal
                    self.log_text.append(self.get_translation("extension_removed", f"已移除扩展名: {item_text}"))
            
            # Save immediately to settings
            self.save_extensions()
    
    def format_size(self, size_bytes):
        """Format bytes to human readable size"""
        size_bytes = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024 or unit == 'TB':
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024

    def refresh_language(self):
        """Update UI elements with new translations"""
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
        """Stop ongoing scanning process"""
        if self.scan_worker and hasattr(self.scan_worker, 'stop'):
            self.scan_worker.stop()
            self.log_text.append(self.get_translation("scan_stopped", "扫描已停止"))
            
            # Re-enable scan button
            self.start_scan_button.setEnabled(True)
            self.start_scan_button.setText(self.get_translation("start_scan"))
            self.stop_button.setEnabled(False)
    
    def fix_threats(self):
        """Fix detected threats (i.e. clean detected files)"""
        if not self.scan_results or self.scan_results["count"] == 0:
            return
        
        # Confirm action
        reply = QMessageBox.question(
            self, 
            self.get_translation("confirm_action", "确认操作"), 
            self.get_translation("confirm_clean", "确定要清理检测到的{count}个文件吗？").format(count=self.scan_results["count"]),
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Start cleaning process
            self.start_clean() 

    def load_exclusions(self):
        """Load exclusion list from settings"""
        try:
            saved_exclusions = self.settings.get_setting("system_cleaner_exclusions", [])
            if saved_exclusions:
                self.exclusions = saved_exclusions
                # Update UI list
                self.exclusions_list.clear()
                for excl in self.exclusions:
                    self.exclusions_list.addItem(excl)
                self.logger.debug(f"Loaded {len(self.exclusions)} exclusions")
        except Exception as e:
            self.logger.error(f"Failed to load exclusions: {str(e)}")
    
    def save_exclusions(self):
        """Save exclusion list to settings"""
        try:
            self.settings.set_setting("system_cleaner_exclusions", self.exclusions)
            self.logger.debug(f"Saved {len(self.exclusions)} exclusions")
        except Exception as e:
            self.logger.error(f"Failed to save exclusions: {str(e)}")

    def load_extensions(self):
        """Load extension list from settings"""
        try:
            saved_extensions = self.settings.get_setting("system_cleaner_extensions", [])
            if saved_extensions:
                self.extensions = saved_extensions
                # Update UI list
                self.extensions_list.clear()
                for ext in self.extensions:
                    self.extensions_list.addItem(ext)
                self.logger.debug(f"Loaded {len(self.extensions)} extensions")
        except Exception as e:
            self.logger.error(f"Failed to load extensions: {str(e)}")
    
    def save_extensions(self):
        """Save extension list to settings"""
        try:
            self.settings.set_setting("system_cleaner_extensions", self.extensions)
            self.logger.debug(f"Saved {len(self.extensions)} extensions")
        except Exception as e:
            self.logger.error(f"Failed to save extensions: {str(e)}") 

    def apply_theme(self):
        """Apply theme colors dynamically instead of hard-coded dark scheme."""
        try:
            # If UI not yet built, skip styling – BaseComponent will call again post-init
            if not hasattr(self, "tab_widget"):
                return

            # Call base implementation to setup default palette
            super().apply_theme()

            colors = self.theme_manager.get_theme_colors()
            bg_color = colors.get("bg_color", "#1e1e1e")
            text_color = colors.get("text_color", "#e0e0e0")
            accent_color = colors.get("accent_color", "#00a8ff")
            bg_lighter = colors.get("bg_lighter", self.theme_manager.lighten_color(bg_color, 10))
            bg_darker = colors.get("bg_darker", self.theme_manager.lighten_color(bg_color, -10))

            # Update tab styles with dynamic colors
            self.tab_widget.setStyleSheet(f"""
                QTabWidget::pane {{
                    border: 1px solid {accent_color};
                    border-radius: 6px;
                    background-color: {bg_lighter};
                }}
                QTabBar::tab {{
                    background-color: {bg_darker};
                    color: {text_color};
                    border: 1px solid {accent_color};
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 8px 12px;
                    margin-right: 4px;
                }}
                QTabBar::tab:selected {{
                    background-color: {bg_lighter};
                    color: {text_color};
                }}
                QTabBar::tab:hover {{
                    background-color: {self.theme_manager.lighten_color(bg_lighter, 10)};
                }}
            """)

            # Progress bar colors
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {bg_darker};
                    color: {text_color};
                    border: 1px solid {accent_color};
                    border-radius: 4px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {accent_color};
                    border-radius: 3px;
                }}
            """)

            # Text edit background
            self.log_text.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {bg_darker};
                    color: {text_color};
                    border: 1px solid {accent_color};
                    border-radius: 4px;
                    font-family: monospace;
                    font-size: 12px;
                    line-height: 1.4;
                }}
            """)
        except Exception as e:
            self.logger.error(f"Error applying theme in SystemCleanerWidget: {e}") 