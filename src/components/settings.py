import os
import sys
import platform
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QPushButton, 
                          QComboBox, QCheckBox, QGroupBox, QFormLayout, QSlider, QLineEdit,
                          QColorDialog, QFileDialog, QDialog, QScrollArea, QSpinBox, QStatusBar,
                          QApplication, QMessageBox, QFrame, QRadioButton)
from PyQt5.QtCore import Qt, QSize, QSettings, QTranslator, QCoreApplication, QTimer
from PyQt5.QtGui import QColor, QIcon, QMovie
from src.utils.animations import AnimationUtils
from src.utils.theme_manager import ThemeManager
from src.utils.logger import Logger
import logging

class SettingsWidget(QWidget):
    """Widget for application settings"""
    
    def __init__(self, settings, parent=None) -> None:
        """Initialize settings component"""
        self.settings = settings
        self.logger = Logger().get_logger()
        self.main_window = parent
        super().__init__(parent)
        self.background_image_path = ""
        self.theme_manager = ThemeManager()
        self.animations = AnimationUtils()
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self) -> None:
        """Setup UI components"""
        # Create overall layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title and description
        title_label = QLabel(self.get_translation("title", "Settings"))
        title_label.setObjectName("title_label")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 5px;")
        main_layout.addWidget(title_label)
        
        desc_label = QLabel(self.get_translation("description", "Customize Glary Utilities to suit your needs"))
        desc_label.setObjectName("desc_label")
        desc_label.setStyleSheet("font-size: 14px; color: #a0a0a0; margin-bottom: 15px;")
        main_layout.addWidget(desc_label)
        
        # Create tabs
        self.settings_tabs = QTabWidget()
        self.settings_tabs.setObjectName("settings_tabs")
        self.settings_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: transparent;
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
                background-color: #333333;
                color: #e0e0e0;
            }
            QTabBar::tab:hover {
                background-color: #303030;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
        """)
        
        # General tab
        general_tab = QWidget()
        self.setup_general_tab(general_tab)
        self.settings_tabs.addTab(general_tab, "")  # Empty title, add when language is updated
        
        # Scan tab
        scan_tab = QWidget()
        self.setup_scan_tab(scan_tab)
        self.settings_tabs.addTab(scan_tab, "")
        
        # Advanced tab
        advanced_tab = QWidget()
        self.setup_advanced_tab(advanced_tab)
        self.settings_tabs.addTab(advanced_tab, "")
        
        # Appearance tab
        appearance_tab = QWidget()
        self.setup_appearance_tab(appearance_tab)
        self.settings_tabs.addTab(appearance_tab, "")
        
        # Add tabs
        main_layout.addWidget(self.settings_tabs)
        
        # Button area
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # Restore defaults button - left aligned
        self.restore_defaults_button = QPushButton(self.get_translation("restore_defaults", "Restore Defaults"))
        self.restore_defaults_button.setObjectName("restore_defaults_button")
        self.restore_defaults_button.clicked.connect(self.reset_settings)
        self.restore_defaults_button.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: #e0e0e0;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #383838;
            }
        """)
        button_layout.addWidget(self.restore_defaults_button)
        
        # Elastic space
        button_layout.addStretch()
        
        # Save button - right aligned
        self.save_button = QPushButton(self.get_translation("save_settings", "Save Settings"))
        self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self._on_save_settings_clicked)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #00a8ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0096e0;
            }
            QPushButton:pressed {
                background-color: #0085c7;
            }
        """)
        button_layout.addWidget(self.save_button)
        
        # Apply button
        self.apply_button = QPushButton(self.get_translation("apply_settings", "Apply"))
        self.apply_button.setObjectName("apply_button")
        self.apply_button.clicked.connect(self.apply_settings)
        self.apply_button.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: #e0e0e0;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #383838;
            }
        """)
        button_layout.addWidget(self.apply_button)

        # Restart button - prompt and relaunch application
        self.restart_button = QPushButton(self.get_translation("restart_now", "Restart Now"))
        self.restart_button.setObjectName("restart_button")
        self.restart_button.clicked.connect(self._on_restart_clicked)
        self.restart_button.setStyleSheet("""
            QPushButton {
                background-color: #d35400;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #ba4a00;
            }
        """)
        button_layout.addWidget(self.restart_button)
        
        # Add button layout
        main_layout.addLayout(button_layout)
        
        # Load settings
        self.load_settings()
        
        # Update localization
        self.refresh_language()
        
    
    def setup_general_tab(self, general_tab) -> None:
        """Setup general tab"""
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # Content container
        general_container = QWidget()
        
        # Create general tab content
        general_layout = QVBoxLayout(general_container)
        general_layout.setContentsMargins(15, 15, 15, 15)
        general_layout.setSpacing(20)  
        
        # General settings title
        title_label = QLabel(self.get_translation("general_title", "General Settings"))
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e0e0e0; margin-bottom: 10px;")
        general_layout.addWidget(title_label)

        # Language selection
        language_frame = QFrame()
        language_frame.setStyleSheet("background-color: rgba(40, 40, 40, 0.7); border-radius: 6px; padding: 10px;")
        language_layout = QVBoxLayout(language_frame)
        language_layout.setContentsMargins(15, 15, 15, 15)
        
        language_title = QLabel(self.get_translation("language_title", "Language"))
        language_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        language_layout.addWidget(language_title)
        
        language_desc = QLabel(self.get_translation("language_desc", "Select your preferred language."))
        language_desc.setStyleSheet("color: #b0b0b0; margin-bottom: 10px;")
        language_layout.addWidget(language_desc)
        
        # Language dropdown
        language_select_layout = QHBoxLayout()
        language_label = QLabel(self.get_translation("language", "Language:"))
        language_label.setStyleSheet("color: #e0e0e0;")
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("中文", "zh")
        self.language_combo.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #555555;
                border-radius: 4px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: #e0e0e0;
                selection-background-color: #444444;
            }
        """)
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        
        language_select_layout.addWidget(language_label)
        language_select_layout.addWidget(self.language_combo)
        language_select_layout.addStretch()
        language_layout.addLayout(language_select_layout)
        
        # Add language frame to tab layout
        general_layout.addWidget(language_frame)
        
        # Behavior settings frame
        behavior_frame = QFrame()
        behavior_frame.setStyleSheet("background-color: rgba(40, 40, 40, 0.7); border-radius: 6px; padding: 10px;")
        behavior_layout = QVBoxLayout(behavior_frame)
        behavior_layout.setContentsMargins(15, 15, 15, 15)
        
        behavior_title = QLabel(self.get_translation("behavior_title", "Application Behavior"))
        behavior_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        behavior_layout.addWidget(behavior_title)
        
        # Startup settings
        self.start_minimized_check = QCheckBox(self.get_translation("start_minimized", "Start minimized"))
        self.start_minimized_check.setStyleSheet("color: #e0e0e0; margin-top: 5px;")
        self.start_minimized_check.setObjectName("start_minimized")
        
        self.close_to_tray_check = QCheckBox(self.get_translation("close_to_tray", "Close to system tray"))
        self.close_to_tray_check.setStyleSheet("color: #e0e0e0; margin-top: 5px;")
        self.close_to_tray_check.setObjectName("close_to_tray")
        
        self.enable_animations_check = QCheckBox(self.get_translation("enable_animations", "启用动画效果"))
        self.enable_animations_check.setStyleSheet("color: #e0e0e0; margin-top: 5px;")
        self.enable_animations_check.setObjectName("enable_animations")
        self.enable_animations_check.stateChanged.connect(self.on_animations_changed)
        
        # Linux performance optimization option
        from src.tools.base_tools import PlatformManager
        platform_manager = PlatformManager()
        if platform_manager.is_linux():
            self.optimize_linux_performance_check = QCheckBox(self.get_translation("optimize_linux_performance", "优化Linux性能（禁用复杂动画）"))
            self.optimize_linux_performance_check.setStyleSheet("color: #e0e0e0; margin-top: 5px;")
            self.optimize_linux_performance_check.setObjectName("optimize_linux_performance")
            self.optimize_linux_performance_check.setChecked(True)  # Default enabled
            behavior_layout.addWidget(self.optimize_linux_performance_check)
        
        behavior_layout.addWidget(self.start_minimized_check)
        behavior_layout.addWidget(self.close_to_tray_check)
        behavior_layout.addWidget(self.enable_animations_check)
        
        # Add behavior frame to tab layout
        general_layout.addWidget(behavior_frame)
        
        # Add spacer at bottom
        general_layout.addStretch()
        
        # Set scroll area content
        scroll_area.setWidget(general_container)
        
        # Set tab layout
        tab_layout = QVBoxLayout(general_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
        
    def setup_appearance_tab(self, appearance_tab):
        """Setup appearance tab"""
        layout = QVBoxLayout(appearance_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel(self.get_translation("appearance_title", "Appearance Settings"))
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e0e0e0; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Theme settings frame
        theme_frame = QFrame()
        theme_frame.setStyleSheet("background-color: rgba(40, 40, 40, 0.7); border-radius: 6px; padding: 10px;")
        theme_layout = QVBoxLayout(theme_frame)
        theme_layout.setContentsMargins(15, 15, 15, 15)
        
        # Theme settings title
        theme_title = QLabel(self.get_translation("theme_title", "Theme"))
        theme_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        theme_layout.addWidget(theme_title)
        
        # Theme description
        theme_desc = QLabel(self.get_translation("theme_desc", "Select your preferred theme."))
        theme_desc.setStyleSheet("color: #b0b0b0; margin-bottom: 10px;")
        theme_layout.addWidget(theme_desc)
        
        # Theme selection
        theme_select_layout = QHBoxLayout()
        theme_label = QLabel(self.get_translation("theme", "Theme:"))
        theme_label.setStyleSheet("color: #e0e0e0;")
        
        self.theme_combo = QComboBox()
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #555555;
                border-radius: 4px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: #e0e0e0;
                selection-background-color: #444444;
            }
        """)
        
        # Load available themes and insert them in predefined order, ensure index matches language refresh
        available_names = self.theme_manager.get_theme_names()
        theme_display = self.theme_manager.get_theme_display_names()

        preferred_order = ["dark", "light", "custom"]
        ordered_names = [n for n in preferred_order if n in available_names]
        # Append any additional themes not in the predefined list
        ordered_names.extend([n for n in available_names if n not in ordered_names])

        for theme_name in ordered_names:
            display_name = theme_display.get(theme_name, theme_name.capitalize())
            self.theme_combo.addItem(display_name, theme_name)
        
        # Connect signal
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        
        theme_select_layout.addWidget(theme_label)
        theme_select_layout.addWidget(self.theme_combo)
        theme_select_layout.addStretch()
        theme_layout.addLayout(theme_select_layout)
        
        # Add theme settings frame
        layout.addWidget(theme_frame)
        
        # UI settings frame
        ui_frame = QFrame()
        ui_frame.setStyleSheet("background-color: rgba(40, 40, 40, 0.7); border-radius: 6px; padding: 10px;")
        ui_layout = QVBoxLayout(ui_frame)
        ui_layout.setContentsMargins(15, 15, 15, 15)
        ui_layout.setSpacing(10)
        
        # UI title
        ui_title = QLabel(self.get_translation("ui_title", "User Interface"))
        ui_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        ui_layout.addWidget(ui_title)
        
        # Window transparency settings
        transparency_layout = QVBoxLayout()
        transparency_title = QLabel(self.get_translation("transparency", "Window Transparency:"))
        transparency_title.setStyleSheet("color: #e0e0e0; margin-top: 5px;")
        
        # Create transparency slider
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(70, 100)  # 70%-100% transparency range
        self.transparency_slider.setValue(100)  # Default fully transparent
        self.transparency_slider.setTickPosition(QSlider.TicksBelow)
        self.transparency_slider.setTickInterval(5)
        self.transparency_slider.valueChanged.connect(self.on_transparency_changed)
        
        # Add label to display current transparency
        transparency_value_layout = QHBoxLayout()
        transparency_value_layout.addWidget(QLabel("70%"))
        
        self.transparency_value_label = QLabel("100%")
        self.transparency_value_label.setAlignment(Qt.AlignRight)
        transparency_value_layout.addWidget(self.transparency_value_label)
        
        transparency_layout.addWidget(transparency_title)
        transparency_layout.addWidget(self.transparency_slider)
        transparency_layout.addLayout(transparency_value_layout)
        
        ui_layout.addLayout(transparency_layout)
        
        # Add UI frame
        layout.addWidget(ui_frame)
        
        # Add stretch space
        layout.addStretch()
        
        # Add to tabs
        self.settings_tabs.addTab(appearance_tab, self.get_translation("appearance", "Appearance"))
        
    def setup_scan_tab(self, scan_tab) -> None:
        """Setup scan tab"""
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # Content container
        scan_container = QWidget()
        
        # Create scan tab content
        scan_layout = QVBoxLayout(scan_container)
        scan_layout.setContentsMargins(15, 15, 15, 15)
        scan_layout.setSpacing(20)
        
        # Scan settings group
        scan_group = QGroupBox(self.get_translation("scan_settings"))
        scan_group.setStyleSheet(""" 
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        scan_settings_layout = QVBoxLayout(scan_group)
        scan_settings_layout.setContentsMargins(15, 15, 15, 15)
        
        # Auto scan
        auto_scan_layout = QHBoxLayout()
        auto_scan_label = QLabel(self.get_translation("auto_scan"))
        auto_scan_label.setMinimumWidth(120)
        auto_scan_label.setMaximumWidth(120)
        
        self.auto_scan_checkbox = QCheckBox()
        self.auto_scan_checkbox.setObjectName("auto_scan_checkbox")
        
        auto_scan_layout.addWidget(auto_scan_label)
        auto_scan_layout.addWidget(self.auto_scan_checkbox)
        
        scan_settings_layout.addLayout(auto_scan_layout)
        
        # Scan frequency
        scan_freq_layout = QHBoxLayout()
        scan_freq_label = QLabel(self.get_translation("scan_frequency"))
        scan_freq_label.setMinimumWidth(120)
        scan_freq_label.setMaximumWidth(120)
        
        self.scan_freq_combo = QComboBox()
        self.scan_freq_combo.addItem(self.get_translation("daily"), "daily")
        self.scan_freq_combo.addItem(self.get_translation("weekly"), "weekly")
        self.scan_freq_combo.addItem(self.get_translation("monthly"), "monthly")
        
        scan_freq_layout.addWidget(scan_freq_label)
        scan_freq_layout.addWidget(self.scan_freq_combo, 1)
        
        scan_settings_layout.addLayout(scan_freq_layout)
        
        # Add to main layout
        scan_layout.addWidget(scan_group)
        
        # Scan options group
        scan_options_group = QGroupBox(self.get_translation("scan_options"))
        scan_options_group.setStyleSheet(""" 
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        scan_options_layout = QVBoxLayout(scan_options_group)
        scan_options_layout.setContentsMargins(15, 15, 15, 15)
        
        # Scan items options
        self.temp_files_checkbox = QCheckBox(self.get_translation("temp_files"))
        self.temp_files_checkbox.setObjectName("temp_files_checkbox")
        self.temp_files_checkbox.setChecked(True)
        scan_options_layout.addWidget(self.temp_files_checkbox)
        
        self.recycle_bin_checkbox = QCheckBox(self.get_translation("recycle_bin"))
        self.recycle_bin_checkbox.setObjectName("recycle_bin_checkbox")
        self.recycle_bin_checkbox.setChecked(True)
        scan_options_layout.addWidget(self.recycle_bin_checkbox)
        
        self.cache_files_checkbox = QCheckBox(self.get_translation("cache_files"))
        self.cache_files_checkbox.setObjectName("cache_files_checkbox")
        self.cache_files_checkbox.setChecked(True)
        scan_options_layout.addWidget(self.cache_files_checkbox)
        
        self.log_files_checkbox = QCheckBox(self.get_translation("log_files"))
        self.log_files_checkbox.setObjectName("log_files_checkbox")
        self.log_files_checkbox.setChecked(True)
        scan_options_layout.addWidget(self.log_files_checkbox)
        
        # Add to main layout
        scan_layout.addWidget(scan_options_group)
        
        # Add stretch space
        scan_layout.addStretch(1)
        
        # Set scroll area content
        scroll_area.setWidget(scan_container)
        
        # Set tab layout
        tab_layout = QVBoxLayout(scan_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
        
    def setup_advanced_tab(self, advanced_tab):
        """Setup advanced tab"""
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # Content container
        advanced_container = QWidget()
        
        # Create advanced tab content
        advanced_layout = QVBoxLayout(advanced_container)
        advanced_layout.setContentsMargins(15, 15, 15, 15)
        advanced_layout.setSpacing(20)
        
        # Backup settings group
        backup_group = QGroupBox(self.get_translation("backup_settings"))
        backup_group.setStyleSheet(""" 
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        backup_layout = QVBoxLayout(backup_group)
        backup_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create backup before repair
        self.check_backup_before_repair = QCheckBox(self.get_translation("backup_before_repair", "修复前创建备份"))
        self.check_backup_before_repair.setObjectName("check_backup_before_repair")
        self.check_backup_before_repair.setChecked(True)
        backup_layout.addWidget(self.check_backup_before_repair)
        
        # Backup location
        backup_location_layout = QHBoxLayout()
        backup_location_label = QLabel(self.get_translation("backup_location"))
        backup_location_label.setMinimumWidth(120)
        
        self.edit_backup_location = QLineEdit()
        self.edit_backup_location.setObjectName("edit_backup_location")
        self.edit_backup_location.setText(os.path.join(os.environ.get("USERPROFILE", ""), "GlaryBackups"))
        
        self.browse_backup_button = QPushButton(self.get_translation("browse"))
        self.browse_backup_button.setObjectName("browse_backup_button")
        self.browse_backup_button.clicked.connect(self.browse_backup_location)
        
        backup_location_layout.addWidget(backup_location_label)
        backup_location_layout.addWidget(self.edit_backup_location, 1)
        backup_location_layout.addWidget(self.browse_backup_button)
        
        backup_layout.addLayout(backup_location_layout)
        
        # Maximum backups
        max_backups_layout = QHBoxLayout()
        max_backups_label = QLabel(self.get_translation("max_backups"))
        max_backups_label.setMinimumWidth(120)
        
        self.spinbox_max_backups = QSpinBox()
        self.spinbox_max_backups.setMinimum(1)
        self.spinbox_max_backups.setMaximum(20)
        self.spinbox_max_backups.setValue(5)
        
        max_backups_layout.addWidget(max_backups_label)
        max_backups_layout.addWidget(self.spinbox_max_backups)
        max_backups_layout.addStretch()
        
        backup_layout.addLayout(max_backups_layout)
        
        # Add to main layout
        advanced_layout.addWidget(backup_group)
        
        # Logs settings group
        logs_group = QGroupBox(self.get_translation("logs"))
        logs_group.setStyleSheet(""" 
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        logs_layout = QVBoxLayout(logs_group)
        logs_layout.setContentsMargins(15, 15, 15, 15)
        
        # Enable logging
        self.check_enable_logging = QCheckBox(self.get_translation("logs", "日志记录"))
        self.check_enable_logging.setObjectName("check_enable_logging")
        self.check_enable_logging.setChecked(True)
        logs_layout.addWidget(self.check_enable_logging)
        
        # Save logs time
        logs_retention_layout = QHBoxLayout()
        logs_retention_label = QLabel(self.get_translation("keep_logs"))
        logs_retention_label.setMinimumWidth(120)
        
        self.spinbox_log_days = QSpinBox()
        self.spinbox_log_days.setMinimum(1)
        self.spinbox_log_days.setMaximum(90)
        self.spinbox_log_days.setValue(30)
        
        days_label = QLabel(self.get_translation("days"))
        
        logs_retention_layout.addWidget(logs_retention_label)
        logs_retention_layout.addWidget(self.spinbox_log_days)
        logs_retention_layout.addWidget(days_label)
        logs_retention_layout.addStretch()
        
        logs_layout.addLayout(logs_retention_layout)
        
        # Clear logs button
        clear_logs_button = QPushButton(self.get_translation("clear_logs"))
        clear_logs_button.setObjectName("clear_logs_button")
        logs_layout.addWidget(clear_logs_button)
        
        # Add to main layout
        advanced_layout.addWidget(logs_group)
        
        # Add stretch space
        advanced_layout.addStretch(1)
        
        # Set scroll area content
        scroll_area.setWidget(advanced_container)
        
        # Set tab layout
        tab_layout = QVBoxLayout(advanced_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

    def on_animations_changed(self, state):
        """Handle animations checkbox state change"""
        is_enabled = (state == Qt.Checked)
        # Save the setting
        self.settings.set_setting("enable_animations", is_enabled)
        self.settings.sync()
        
        # Apply the setting
        try:
            if self.main_window is not None:
                # Notify main window of animation setting change
                self.logger.info(f"Animation setting changed to: {is_enabled}")
        except AttributeError:
            pass

    def on_theme_changed(self, index):
        """Handle theme selection change"""
        try:
            if index >= 0:
                theme_id = self.theme_combo.itemData(index)
                if theme_id:
                    current_theme = self.settings.get_setting("theme", "dark")
                    if theme_id != current_theme:
                        # Save but don't apply – require restart
                        self.settings.set_setting("theme", theme_id)
                        self.settings.sync()

                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.information(self, self.get_translation("restart_required", "Restart Required"),
                                                self.get_translation("restart_theme_note", "The theme change will take effect after restarting the application."))
                        self.logger.info(f"Theme set to {theme_id}; restart required to apply.")
        except AttributeError:
            pass
    
    def load_settings(self):
        """Load settings from settings"""
        try:
            # Apply settings to interface
            current_language = self.settings.get_setting("language", "en")
            
            # Ensure language dropdown shows correctly
            try:
                language_index = 0  # Default English
                if self.language_combo:
                    for i in range(self.language_combo.count()):
                        if self.language_combo.itemData(i) == current_language:
                            language_index = i
                            break
                    self.language_combo.setCurrentIndex(language_index)
            except AttributeError:
                pass
            
            # Set theme selector value
            current_theme = self.settings.get_setting("theme", "dark")
            try:
                theme_index = 0  # Default dark theme
                for i in range(self.theme_combo.count()):
                    if self.theme_combo.itemData(i) == current_theme:
                        theme_index = i
                        break
                self.theme_combo.setCurrentIndex(theme_index)
            except AttributeError:
                pass
            
            # Load custom colors
            try:
                self.update_color_buttons()
            except AttributeError:
                pass
            
            # Load startup settings
            try:
                if hasattr(self, 'startup_check'):
                    self.startup_check.setChecked(self.settings.get_setting("start_with_windows", False))
            except AttributeError:
                pass
            
            # Load startup minimization settings
            try:
                if hasattr(self, 'start_minimized_check'):
                    self.start_minimized_check.setChecked(self.settings.get_setting("start_minimized", False))
            except AttributeError:
                pass
            
            # Load animation enable settings
            try:
                if hasattr(self, 'enable_animations_check'):
                    animation_enabled = self.settings.get_setting("enable_animations", True)
                    # Convert to proper boolean value
                    if isinstance(animation_enabled, str):
                        animation_enabled = animation_enabled.lower() in ('true', 'yes', '1', 'on')
                    elif isinstance(animation_enabled, int):
                        animation_enabled = animation_enabled != 0
                    else:
                        animation_enabled = bool(animation_enabled)
                        
                    self.enable_animations_check.setChecked(animation_enabled)
            except AttributeError:
                pass
            
            # Load transparency settings
            try:
                transparency = int(self.settings.get_setting("window_transparency", 100))
                if hasattr(self, 'transparency_slider'):
                    self.transparency_slider.setValue(transparency)
                if hasattr(self, 'transparency_value_label'):
                    self.transparency_value_label.setText(f"{transparency}%")
            except (AttributeError, ValueError):
                pass
            
            # Load all custom checkbox settings
            for checkbox in self.findChildren(QCheckBox):
                setting_key = checkbox.objectName()
                if setting_key:
                    try:
                        value = self.settings.get_setting(setting_key, False)
                        # Convert value to boolean type
                        if isinstance(value, str):
                            value = value.lower() in ('true', 'yes', '1', 'on')
                        checkbox.setChecked(bool(value))
                    except Exception as e:
                        self.logger.error(f"Error loading setting for {setting_key}: {e}")
            
            self.logger.info("Settings loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
    
    def reset_settings(self):
        """Reset settings to default values"""
        # Reset general settings
        try:
            self.language_combo.setCurrentText("English")
        except AttributeError:
            self.logger.error("Cannot reset language settings")
        
        try:
            self.start_minimized_check.setChecked(False)
        except AttributeError:
            self.logger.error("Cannot reset minimize settings")
        
        try:
            self.close_to_tray_check.setChecked(False)
        except AttributeError:
            self.logger.error("Cannot reset tray settings")
        
        try:
            self.enable_animations_check.setChecked(False)
        except AttributeError:
            self.logger.error("Cannot reset animation settings")
        
        # Reset theme settings
        try:
            # Find index of "dark" theme
            dark_index = -1
            for i in range(self.theme_combo.count()):
                if self.theme_combo.itemData(i) == "dark":
                    dark_index = i
                    break
            
            if dark_index >= 0:
                self.theme_combo.setCurrentIndex(dark_index)
        except AttributeError:
            self.logger.error("Cannot reset theme settings")
        
        # Reset custom colors
        try:
            self.update_color_buttons()
        except AttributeError:
            self.logger.error("Cannot reset custom colors")
        
        # Reset advanced settings
        try:
            self.check_backup_before_repair.setChecked(True)
        except AttributeError:
            self.logger.error("Cannot reset backup settings")
        
        try:
            self.edit_backup_location.setText(os.path.join(os.environ.get("USERPROFILE", ""), "GlaryBackups"))
        except AttributeError:
            self.logger.error("Cannot reset backup location")
        
        try:
            self.check_enable_logging.setChecked(True)
        except AttributeError:
            self.logger.error("Cannot reset logging settings")
        
        try:
            self.spinbox_max_backups.setValue(5)
        except AttributeError:
            self.logger.error("Cannot reset max backup count")
        
        # Reset scan settings
        try:
            self.auto_scan_checkbox.setChecked(True)
        except AttributeError:
            self.logger.error("Cannot reset auto scan settings")
        
        try:
            self.scan_freq_combo.setCurrentText("daily")
        except AttributeError:
            self.logger.error("Cannot reset scan frequency")
        
        try:
            self.temp_files_checkbox.setChecked(True)
        except AttributeError:
            self.logger.error("Cannot reset temp files settings")
        
        try:
            self.recycle_bin_checkbox.setChecked(True)
        except AttributeError:
            self.logger.error("Cannot reset recycle bin settings")
        
        try:
            self.cache_files_checkbox.setChecked(True)
        except AttributeError:
            self.logger.error("Cannot reset cache files settings")
        
        try:
            self.log_files_checkbox.setChecked(True)
        except AttributeError:
            self.logger.error("Cannot reset log files settings")
        
        # Reset scan options
        try:
            self.check_scan_archives.setChecked(True)
        except AttributeError:
            self.logger.error("Cannot reset scan archives settings")
        
        try:
            self.check_scan_rootkits.setChecked(True)
        except AttributeError:
            self.logger.error("Cannot reset scan rootkits settings")
        
        try:
            self.check_scan_autofix.setChecked(False)
        except AttributeError:
            self.logger.error("Cannot reset scan autofix settings")
        
        try:
            self.slider_scan_level.setValue(2)
        except AttributeError:
            self.logger.error("Cannot reset scan level settings")
            
        # Reset other settings
        for attr_name in ['deep_scan_check', 'auto_clean_check', 'auto_backup_check', 
                         'check_updates_check', 'auto_update_check', 'show_notifications_check',
                         'notification_sound_check', 'schedule_restarts_check', 
                         'startup_scan_check', 'system_titlebar_check', 'window_blur_check',
                         'start_minimized_check', 'close_to_tray_check']:
            try:
                getattr(self, attr_name).setChecked(False)
            except (AttributeError, TypeError):
                self.logger.error(f"Cannot reset {attr_name} settings")
                
        # Reset main window transparency
        try:
            self.transparency_slider.setValue(100)
            self.transparency_value_label.setText("100%")
        except AttributeError:
            self.logger.error("Cannot reset main window transparency")
            
        # Notify user that settings have been reset
        try:
            # Show status message
            if self.main_window is not None:
                self.main_window.show_status_message("Settings have been reset to default values", 3000)
        except AttributeError:
            self.logger.error("Cannot show status message - main_window is not available")
    
    def get_translation(self, key, default=None):
        """Get translation for key"""
        return self.settings.get_translation("settings", key, default)
        
    def on_language_changed(self, index):
        """Handle language selection change"""
        try:
            if index >= 0:
                # Get language code from the combobox
                language_code = self.language_combo.itemData(index)
                if language_code:
                    current_lang = self.settings.get_setting("language", "en")
                    # Only proceed if language actually changed
                    if language_code != current_lang:
                        self.settings.set_language(language_code)
                        self.settings.sync()
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.information(self, self.get_translation("restart_required", "Restart Required"),
                                                self.get_translation("restart_language_note", "The language change will take effect after restarting the application."))
                        self.logger.info(f"Language changed from {current_lang} to {language_code}; restart required.")
        except AttributeError:
            pass
    
    def refresh_language(self):
        """Update interface text based on current language"""
        # Update tab titles
        self.settings_tabs.setTabText(0, self.get_translation("general_tab", "常规"))
        self.settings_tabs.setTabText(1, self.get_translation("scan_tab", "扫描"))
        self.settings_tabs.setTabText(2, self.get_translation("advanced_tab", "高级"))
        self.settings_tabs.setTabText(3, self.get_translation("appearance_tab", "外观"))
        
        # Update general tab
        general_group = self.findChild(QGroupBox, "general_group")
        if general_group:
            general_group.setTitle(self.get_translation("general_settings", "常规设置"))
            
        language_label = self.findChild(QLabel, "language_label")
        if language_label:
            language_label.setText(self.get_translation("language", "语言："))
            
        startup_label = self.findChild(QLabel, "startup_label")
        if startup_label:
            startup_label.setText(self.get_translation("start_with_windows", "开机启动："))
            
        self.start_minimized_check.setText(self.get_translation("start_minimized", "Start minimized"))
        
        # Update theme settings
        theme_group = self.findChild(QGroupBox, "theme_group")
        if theme_group:
            theme_group.setTitle(self.get_translation("theme_settings", "主题设置"))
            
        theme_label = self.findChild(QLabel, "theme_label")
        if theme_label:
            theme_label.setText(self.get_translation("theme", "主题："))
            
        # Update theme options
        if self.theme_combo.count() >= 3:
            self.theme_combo.setItemText(0, self.get_translation("dark", "深色"))
            self.theme_combo.setItemText(1, self.get_translation("light", "浅色"))
            self.theme_combo.setItemText(2, self.get_translation("custom", "自定义"))
            
        # Update custom colors - consider changing layout to QVBoxLayout
        try:
            bg_color_label = None
            text_color_label = None
            accent_color_label = None
            
            # Iterate through all labels, find custom color labels
            for label in self.findChildren(QLabel):
                if "背景颜色" in label.text():
                    label.setText(self.get_translation("background_color", "背景颜色："))
                elif "文本颜色" in label.text():
                    label.setText(self.get_translation("text_color", "文本颜色："))
                elif "强调颜色" in label.text():
                    label.setText(self.get_translation("accent_color", "强调颜色："))
        except Exception as e:
            self.logger.error(f"Error updating custom color labels: {str(e)}")
                
        # Update color selection buttons
        for button in self.findChildren(QPushButton):
            if "选择颜色" in button.text():
                button.setText(self.get_translation("choose_color", "选择颜色"))
        
        # Update notifications group
        notifications_group = self.findChild(QGroupBox, "notifications_group")
        if notifications_group:
            notifications_group.setTitle(self.get_translation("notifications", "通知"))
            
        self.enable_animations_check.setText(self.get_translation("enable_animations", "启用动画效果"))
        
        # Update buttons
        self.save_button.setText(self.get_translation("save_settings", "保存设置"))
        self.apply_button.setText(self.get_translation("apply_settings", "应用设置"))
        self.restore_defaults_button.setText(self.get_translation("restore_defaults", "恢复默认"))
        if hasattr(self, "restart_button"):
            self.restart_button.setText(self.get_translation("restart_now", "立即重启"))
    
    def check_all_translations(self):
        """Check if all required translations exist"""
        # General tab translations
        self.get_translation("general_tab")
        self.get_translation("general_settings")
        self.get_translation("language")
        self.get_translation("start_with_windows")
        self.get_translation("auto_start")
        self.get_translation("notifications")
        self.get_translation("enable_notifications")
        self.get_translation("show_tips")
        self.get_translation("maintenance_reminder")
        
        # Scan tab translations
        self.get_translation("scan_tab")
        
        # Advanced tab translations
        self.get_translation("advanced_tab")
        
        # Appearance tab translations
        self.get_translation("appearance_tab")
        
        # Button translations
        self.get_translation("save_settings")
        self.get_translation("restore_defaults")

    def on_transparency_changed(self, value):
        """Handle transparency slider value change"""
        self.transparency_value_label.setText(f"{value}%")
        self.settings.set_setting("window_transparency", value)
        
        # Try to apply transparency
        main_window = self.window()
        if main_window and hasattr(main_window, 'apply_transparency'):
            main_window.apply_transparency()
    
    def browse_backup_location(self):
        """Open dialog to select backup folder"""
        from PyQt5.QtWidgets import QFileDialog
        
        current_path = self.edit_backup_location.text()
        folder = QFileDialog.getExistingDirectory(
            self, self.get_translation("select_backup_folder", "选择备份文件夹"), 
            current_path if os.path.exists(current_path) else os.environ.get("USERPROFILE", "")
        )
        
        if folder:
            self.edit_backup_location.setText(folder)
            self.settings.set_setting("backup_location", folder)
    
    def apply_settings(self):
        """Apply settings changes"""
        # Handle any remaining old-style checkbox references
        try:
            # Language setting
            try:
                current_idx = self.language_combo.currentIndex()
                language_code = self.language_combo.itemData(current_idx)
                current_lang = self.settings.get_setting("language", "en")
                if language_code != current_lang:
                    self.settings.set_language(language_code)
                    # Prompt user restart; do not update UI immediately
                    from PyQt5.QtWidgets import QMessageBox
                    try:
                        if self.main_window:
                            QMessageBox.information(self, self.get_translation("restart_required", "Restart Required"),
                                                    self.get_translation("restart_language_note", "The language change will take effect after restarting the application."))
                    except AttributeError:
                        pass
            except AttributeError:
                pass
            
            # Theme setting
            try:
                current_idx = self.theme_combo.currentIndex()
                theme_id = self.theme_combo.itemData(current_idx)
                current_theme = self.settings.get_setting("theme", "dark")
                if theme_id != current_theme:
                    self.settings.set_setting("theme", theme_id)
                    # Prompt user restart
                    from PyQt5.QtWidgets import QMessageBox
                    try:
                        if self.main_window:
                            QMessageBox.information(self, self.get_translation("restart_required", "Restart Required"),
                                                    self.get_translation("restart_theme_note", "The theme change will take effect after restarting the application."))
                    except AttributeError:
                        pass
            except AttributeError:
                pass
            
            # Window transparency
            try:
                transparency = self.transparency_slider.value()
                self.settings.set_setting("window_transparency", transparency)
                # Apply transparency if window available
                try:
                    if self.main_window:
                        self.main_window.apply_transparency()
                except AttributeError:
                    pass
            except AttributeError:
                pass
            
            # Process all checkboxes automatically
            for checkbox in self.findChildren(QCheckBox):
                setting_key = checkbox.objectName()
                if setting_key:
                    is_checked = checkbox.isChecked()
                    self.settings.set_setting(setting_key, is_checked)
            
            # Save settings to disk
            self.settings.sync()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                self.get_translation("settings_applied_title", "Settings Applied"),
                self.get_translation("settings_applied", "Settings applied successfully.")
            )
            self.logger.info("Settings saved successfully")
            # Emit signal that settings were saved (if it exists)
            try:
                self.settings_saved.emit()
            except AttributeError:
                pass
            # Show status message in main window if available
            try:
                if self.main_window is not None and hasattr(self.main_window, 'show_status_message'):
                    self.main_window.show_status_message(self.get_translation("settings_saved", "Settings saved successfully."))
            except AttributeError:
                pass
            return True
        except Exception as e:
            self.logger.error(f"Error applying settings: {str(e)}")
            return False

    def _finish_applying(self, loading_label=None, movie=None):
        """Finish applying settings process"""
        try:
            # Restore button state
            self.apply_button.setEnabled(True)
            self.apply_button.setText(self.get_translation("apply_settings", "应用设置"))
            
            # Remove loading animation
            if loading_label:
                if movie:
                    movie.stop()
                loading_label.hide()
                loading_label.deleteLater()
            
            # Ensure layout is updated
            self.updateGeometry()
            self.update()
        except Exception as e:
            self.logger.error(f"Error cleaning up applying settings interface: {str(e)}")

    def save_custom_theme(self):
        """Save current custom theme settings to theme file"""
        # Get current custom colors
        bg_color = self.settings.get_setting("custom_bg_color", "#1e1e1e")
        text_color = self.settings.get_setting("custom_text_color", "#e0e0e0")
        accent_color = self.settings.get_setting("custom_accent_color", "#555555")
        
        # Create theme data structure
        theme_data = {
            "name": "custom",
            "display_name": {
                "en": "Custom",
                "zh": "自定义"  
            },
            "colors": {
                "bg_color": bg_color,
                "text_color": text_color,
                "accent_color": accent_color,
                "bg_lighter": self.lighten_color(bg_color, 10),
                "bg_darker": self.lighten_color(bg_color, -10)
            },
            "component_specific": {
                "button": {
                    "primary_bg": accent_color,
                    "primary_text": "#ffffff",
                    "primary_hover": self.lighten_color(accent_color, 10),
                    "primary_pressed": self.lighten_color(accent_color, -10)
                },
                "progressbar": {
                    "chunk_color": accent_color
                }
            }
        }
        
        # Save theme to file
        try:
            theme_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "themes")
            if not os.path.exists(theme_dir):
                os.makedirs(theme_dir)
            
            theme_file = os.path.join(theme_dir, "custom.json")
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=4, ensure_ascii=False)
            
            # Show success message
            self.status_bar = QStatusBar(self)
            self.status_bar.setStyleSheet("color: #4CAF50;")
            self.layout().addWidget(self.status_bar)
            self.status_bar.showMessage(self.get_translation("custom_theme_saved", "自定义主题已保存"), 3000)
        except Exception as e:
            # Show error message
            self.status_bar = QStatusBar(self)
            self.status_bar.setStyleSheet("color: #F44336;")
            self.layout().addWidget(self.status_bar)
            self.status_bar.showMessage(self.get_translation("custom_theme_save_error", f"保存自定义主题时出错: {str(e)}"), 3000)

    def lighten_color(self, color, amount=0):
        """Lighten or darken color
        
        Args:
            color: Hex color code
            amount: Change amount, positive lightens, negative darkens
            
        Returns:
            New hex color code
        """
        try:
            c = color.lstrip('#')
            c = tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
            
            r, g, b = c
            
            r = min(255, max(0, r + amount * 2.55))
            g = min(255, max(0, g + amount * 2.55))
            b = min(255, max(0, b + amount * 2.55))
            
            return '#{:02x}{:02x}{:02x}'.format(int(r), int(g), int(b))
        except Exception as e:
            self.logger.error(f"Error calculating color change: {str(e)}")
            return color

    def update_color_buttons(self):
        """Update custom color buttons display"""
        bg_color = self.settings.get_setting("custom_bg_color", "#1e1e1e")
        text_color = self.settings.get_setting("custom_text_color", "#e0e0e0")
        accent_color = self.settings.get_setting("custom_accent_color", "#555555")
        
        self.bg_color_button.setStyleSheet(f"background-color: {bg_color}; min-width: 80px; min-height: 24px;")
        self.text_color_button.setStyleSheet(f"background-color: {text_color}; min-width: 80px; min-height: 24px;")
        self.accent_color_button.setStyleSheet(f"background-color: {accent_color}; min-width: 80px; min-height: 24px;")

    def apply_theme(self):
        """Apply selected theme"""
        index = self.theme_combo.currentIndex()
        if index >= 0:
            theme_name = self.theme_combo.itemData(index)
            self.theme_manager.apply_theme(theme_name)

    def save_settings(self):
        """Save all settings"""
        try:
            # Save language setting
            try:
                lang_idx = self.language_combo.currentIndex()
                lang_data = self.language_combo.itemData(lang_idx)
                current_lang = self.settings.get_setting("language", "en")
                if lang_data != current_lang:
                    self.settings.set_language(lang_data)
            except AttributeError:
                pass
            
            # Save theme setting
            try:  
                theme_idx = self.theme_combo.currentIndex()
                theme_id = self.theme_combo.itemData(theme_idx)
                self.settings.set_setting("theme", theme_id)
            except AttributeError:
                pass
            
            # Save checkbox settings directly from their state
            for checkbox in self.findChildren(QCheckBox):
                setting_key = checkbox.objectName()
                if setting_key:
                    self.settings.set_setting(setting_key, checkbox.isChecked())
            
            # Save window transparency
            try:
                self.settings.set_setting("window_transparency", self.transparency_slider.value())
            except AttributeError:
                pass
            
            # Sync settings to save them immediately
            self.settings.sync()
            
            # Apply theme if main window is available
            try:
                if self.main_window is not None:
                    self.main_window.apply_theme()
            except AttributeError:
                pass
                
            return True
        except Exception as e:
            self.logger.error(f"Error saving settings: {str(e)}")
            return False

    # Add save_settings button click handler
    def _on_save_settings_clicked(self):
        """Save settings and close settings window"""
        # Save all settings
        success = self.save_settings()
        
        if success:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                self.get_translation("settings_saved_title", "Settings Saved"),
                self.get_translation("settings_saved", "Settings saved successfully.")
            )
            self.logger.info("Settings saved successfully")
            # Emit signal that settings were saved (if it exists)
            try:
                self.settings_saved.emit()
            except AttributeError:
                pass
            # Show status message in main window if available
            try:
                if self.main_window is not None and hasattr(self.main_window, 'show_status_message'):
                    self.main_window.show_status_message(self.get_translation("settings_saved", "Settings saved successfully."))
            except AttributeError:
                pass
        else:
            # Show error message
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error",
                "Failed to save settings. Please try again."
            )

    def on_checkbox_changed(self, setting_key, state):
        """Handle checkbox state change
        
        Args:
            setting_key: Setting key name
            state: Checkbox state (Qt.Checked or Qt.Unchecked)
        """
        try:
            # Convert Qt.Checked/Qt.Unchecked to boolean
            checked = (state == Qt.Checked)
            
            # Save settings
            self.settings.set_setting(setting_key, checked)
            self.settings.sync()
            
            # Log setting change
            self.logger.info(f"Setting changed: {setting_key} = {checked}")
            
            # Execute specific operations based on setting key
            if setting_key == "enable_animations":
                # Update animation settings
                self.apply_animation_settings(checked)
            elif setting_key == "use_system_title_bar":
                # Update title bar settings
                self.apply_titlebar_settings(checked)
            elif setting_key == "show_tooltips":
                # Update tooltip settings
                self.apply_tooltip_settings(checked)
            elif setting_key == "enable_logging":
                # Update logging settings
                self.apply_logging_settings(checked)
            
            # Apply setting changes
            self.apply_settings()
            
        except Exception as e:
            self.logger.error(f"Error changing setting: {str(e)}")
            # Restore checkbox state
            sender = self.sender()
            if sender:
                sender.setChecked(not checked)
                
    def apply_animation_settings(self, enabled):
        """Apply animation settings
        
        Args:
            enabled: Whether to enable animations
        """
        try:
            # Update all components that support animations
            main_window = self.window()
            if main_window:
                main_window.refresh_all_components()
        except Exception as e:
            self.logger.error(f"Error applying animation settings: {str(e)}")
            
    def apply_titlebar_settings(self, use_system):
        """Apply title bar settings
        
        Args:
            use_system: Whether to use system title bar
        """
        try:
            # Notify main window to update title bar
            main_window = self.window()
            if main_window and hasattr(main_window, 'update_titlebar'):
                main_window.update_titlebar(use_system)
        except Exception as e:
            self.logger.error(f"Error applying title bar settings: {str(e)}")
            
    def apply_tooltip_settings(self, show):
        """Apply tooltip settings
        
        Args:
            show: Whether to show tooltips
        """
        try:
            # Update all tooltips
            main_window = self.window()
            if main_window:
                for widget in main_window.findChildren(QWidget):
                    if widget.toolTip():
                        widget.setToolTipDuration(-1 if show else 0)
        except Exception as e:
            self.logger.error(f"Error applying tooltip settings: {str(e)}")
            
    def apply_logging_settings(self, enabled):
        """Apply logging settings
        
        Args:
            enabled: Whether to enable logging
        """
        try:
            # Update log level
            log_level = logging.DEBUG if enabled else logging.WARNING
            logging.getLogger().setLevel(log_level)
        except Exception as e:
            self.logger.error(f"Error applying logging settings: {str(e)}")

    def _on_restart_clicked(self):
        """Save settings and restart the application"""
        try:
            from PyQt5.QtWidgets import QMessageBox, QApplication
            import subprocess, sys, os
 
            # Confirm restart
            reply = QMessageBox.question(
                self,
                self.get_translation("restart_required", "Restart Required"),
                self.get_translation("restart_confirm", "The application needs to restart to apply changes. Restart now?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.No:
                return
 
            # Save any pending settings
            self.save_settings()
 
            # Relaunch
            python = sys.executable
            args = sys.argv
            self.logger.info("Restarting application with: %s %s", python, " ".join(args))
            try:
                subprocess.Popen([python] + args)
            except Exception as e:
                self.logger.error(f"Failed to relaunch application: {e}")
 
            # Quit current instance
            QApplication.instance().quit()
        except Exception as e:
            self.logger.error(f"Error during restart: {e}")

   