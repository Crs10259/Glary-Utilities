import os
import json
import shutil
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QCheckBox, QComboBox, QGroupBox, 
                             QMessageBox, QFileDialog, QTabWidget,
                             QSpinBox, QSlider, QLineEdit, QFormLayout,
                             QButtonGroup, QRadioButton, QColorDialog)
from PyQt5.QtCore import Qt, QSettings, QSize
from PyQt5.QtGui import QFont, QIcon, QColor

class SettingsWidget(QWidget):
    """Widget for application settings"""
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Set up the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title and description
        title_label = QLabel(self.get_translation("title"))
        title_label.setObjectName("title_label")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        desc_label = QLabel(self.get_translation("description"))
        desc_label.setObjectName("desc_label")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("settings_tabs")
        layout.addWidget(self.tabs)
        
        # General tab
        general_tab = QWidget()
        general_tab.setObjectName("general_tab")
        general_layout = QVBoxLayout(general_tab)
        
        # General settings group
        general_group = QGroupBox(self.get_translation("general_settings"))
        general_group.setObjectName("general_group")
        general_group_layout = QFormLayout(general_group)
        general_group_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Theme setting
        theme_label = QLabel(self.get_translation("theme") + ":")
        theme_label.setObjectName("theme_label")
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("theme_combo")
        self.theme_combo.addItems(["Light", "Dark", "System"])
        general_group_layout.addRow(theme_label, self.theme_combo)
        
        # Language setting
        language_label = QLabel(self.get_translation("language") + ":")
        language_label.setObjectName("language_label")
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("language_combo")
        self.language_combo.addItems(["English", "Chinese"])
        general_group_layout.addRow(language_label, self.language_combo)
        
        # Startup setting
        startup_label = QLabel(self.get_translation("start_with_windows") + ":")
        startup_label.setObjectName("startup_label")
        self.startup_checkbox = QCheckBox(self.get_translation("auto_start"))
        self.startup_checkbox.setObjectName("startup_checkbox")
        general_group_layout.addRow(startup_label, self.startup_checkbox)
        
        general_layout.addWidget(general_group)
        
        # Notifications group
        notifications_group = QGroupBox(self.get_translation("notifications"))
        notifications_group.setObjectName("notifications_group")
        notifications_layout = QVBoxLayout(notifications_group)
        
        self.enable_notifications_checkbox = QCheckBox(self.get_translation("enable_notifications"))
        self.enable_notifications_checkbox.setObjectName("enable_notifications_checkbox")
        self.enable_notifications_checkbox.setChecked(True)
        notifications_layout.addWidget(self.enable_notifications_checkbox)
        
        self.show_tips_checkbox = QCheckBox(self.get_translation("show_tips"))
        self.show_tips_checkbox.setObjectName("show_tips_checkbox")
        self.show_tips_checkbox.setChecked(True)
        notifications_layout.addWidget(self.show_tips_checkbox)
        
        self.maintenance_reminder_checkbox = QCheckBox(self.get_translation("maintenance_reminder"))
        self.maintenance_reminder_checkbox.setObjectName("maintenance_reminder_checkbox")
        self.maintenance_reminder_checkbox.setChecked(True)
        notifications_layout.addWidget(self.maintenance_reminder_checkbox)
        
        general_layout.addWidget(notifications_group)
        
        # Add general tab
        self.tabs.addTab(general_tab, self.get_translation("general"))
        
        # Privacy tab
        privacy_tab = QWidget()
        privacy_tab.setObjectName("privacy_tab")
        privacy_layout = QVBoxLayout(privacy_tab)
        
        privacy_group = QGroupBox(self.get_translation("privacy"))
        privacy_group.setObjectName("privacy_group")
        privacy_group_layout = QVBoxLayout(privacy_group)
        
        self.usage_stats_checkbox = QCheckBox(self.get_translation("collect_usage_statistics"))
        self.usage_stats_checkbox.setObjectName("usage_stats_checkbox")
        self.usage_stats_checkbox.setChecked(False)
        privacy_group_layout.addWidget(self.usage_stats_checkbox)
        
        self.auto_update_checkbox = QCheckBox(self.get_translation("automatic_updates"))
        self.auto_update_checkbox.setObjectName("auto_update_checkbox")
        self.auto_update_checkbox.setChecked(True)
        privacy_group_layout.addWidget(self.auto_update_checkbox)
        
        privacy_layout.addWidget(privacy_group)
        
        # Add privacy tab
        self.tabs.addTab(privacy_tab, self.get_translation("privacy"))
        
        # Advanced tab
        advanced_tab = QWidget()
        advanced_tab.setObjectName("advanced_tab")
        advanced_layout = QVBoxLayout(advanced_tab)
        
        advanced_group = QGroupBox(self.get_translation("advanced"))
        advanced_group.setObjectName("advanced_group")
        advanced_group_layout = QFormLayout(advanced_group)
        
        # Log level
        log_level_label = QLabel(self.get_translation("log_level") + ":")
        log_level_label.setObjectName("log_level_label")
        self.log_level_combo = QComboBox()
        self.log_level_combo.setObjectName("log_level_combo")
        self.log_level_combo.addItems(["Error", "Warning", "Info", "Debug"])
        advanced_group_layout.addRow(log_level_label, self.log_level_combo)
        
        advanced_layout.addWidget(advanced_group)
        
        # Add advanced tab
        self.tabs.addTab(advanced_tab, self.get_translation("advanced"))
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.save_button = QPushButton(self.get_translation("save_settings"))
        self.save_button.setObjectName("save_button")
        self.save_button.setMinimumWidth(120)
        buttons_layout.addWidget(self.save_button)
        
        self.restore_defaults_button = QPushButton(self.get_translation("restore_defaults"))
        self.restore_defaults_button.setObjectName("restore_defaults_button")
        self.restore_defaults_button.setMinimumWidth(140)
        buttons_layout.addWidget(self.restore_defaults_button)
        
        layout.addLayout(buttons_layout)
        
        # Connect signals
        self.save_button.clicked.connect(self.save_settings)
        self.restore_defaults_button.clicked.connect(self.restore_defaults)
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
    
    def select_color(self, color_type):
        """Open a color dialog to select a color"""
        current_color = None
        
        if color_type == "background":
            current_bg_color = self.bg_color_display.styleSheet().split("background-color:")[1].split(";")[0].strip()
            current_color = QColor(current_bg_color)
        elif color_type == "text":
            current_text_color = self.text_color_display.styleSheet().split("background-color:")[1].split(";")[0].strip()
            current_color = QColor(current_text_color)
        elif color_type == "accent":
            current_accent_color = self.accent_color_display.styleSheet().split("background-color:")[1].split(";")[0].strip()
            current_color = QColor(current_accent_color)
        
        color = QColorDialog.getColor(current_color, self, f"Select {color_type.title()} Color")
        
        if color.isValid():
            if color_type == "background":
                self.bg_color_display.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #444;")
            elif color_type == "text":
                self.text_color_display.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #444;")
            elif color_type == "accent":
                self.accent_color_display.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #444;")
    
    def setup_scan_tab(self):
        """Setup the scan options tab"""
        layout = QVBoxLayout(self.scan_tab)
        
        # System cleaner settings
        cleaner_group = QGroupBox("System Cleaner")
        cleaner_layout = QVBoxLayout(cleaner_group)
        
        self.check_clean_temp = QCheckBox("Clean temporary files")
        self.check_clean_temp.setChecked(True)
        cleaner_layout.addWidget(self.check_clean_temp)
        
        self.check_clean_recycle = QCheckBox("Empty recycle bin")
        self.check_clean_recycle.setChecked(True)
        cleaner_layout.addWidget(self.check_clean_recycle)
        
        self.check_clean_browser = QCheckBox("Clean browser caches")
        self.check_clean_browser.setChecked(True)
        cleaner_layout.addWidget(self.check_clean_browser)
        
        self.check_clean_prefetch = QCheckBox("Clean Windows prefetch")
        self.check_clean_prefetch.setChecked(True)
        cleaner_layout.addWidget(self.check_clean_prefetch)
        
        self.check_clean_logs = QCheckBox("Clean system logs")
        self.check_clean_logs.setChecked(False)
        cleaner_layout.addWidget(self.check_clean_logs)
        
        layout.addWidget(cleaner_group)
        
        # Disk check settings
        disk_check_group = QGroupBox("Disk Check")
        disk_check_layout = QVBoxLayout(disk_check_group)
        
        self.check_disk_readonly = QCheckBox("Run disk check in read-only mode by default")
        self.check_disk_readonly.setChecked(True)
        disk_check_layout.addWidget(self.check_disk_readonly)
        
        layout.addWidget(disk_check_group)
        
        # Virus scan settings
        virus_group = QGroupBox("Virus Scan")
        virus_layout = QVBoxLayout(virus_group)
        
        self.check_scan_archives = QCheckBox("Scan inside archives")
        self.check_scan_archives.setChecked(True)
        virus_layout.addWidget(self.check_scan_archives)
        
        self.check_scan_rootkits = QCheckBox("Scan for rootkits")
        self.check_scan_rootkits.setChecked(True)
        virus_layout.addWidget(self.check_scan_rootkits)
        
        self.check_scan_autofix = QCheckBox("Automatically fix detected issues")
        self.check_scan_autofix.setChecked(False)
        virus_layout.addWidget(self.check_scan_autofix)
        
        scan_level_layout = QHBoxLayout()
        scan_level_layout.addWidget(QLabel("Scan Thoroughness:"))
        
        self.slider_scan_level = QSlider(Qt.Horizontal)
        self.slider_scan_level.setRange(1, 3)
        self.slider_scan_level.setValue(2)
        self.slider_scan_level.setTickPosition(QSlider.TicksBelow)
        self.slider_scan_level.setTickInterval(1)
        scan_level_layout.addWidget(self.slider_scan_level)
        
        level_labels = QHBoxLayout()
        level_labels.addWidget(QLabel("Quick"))
        level_labels.addStretch()
        level_labels.addWidget(QLabel("Balanced"))
        level_labels.addStretch()
        level_labels.addWidget(QLabel("Thorough"))
        scan_level_layout.addLayout(level_labels)
        
        virus_layout.addLayout(scan_level_layout)
        
        layout.addWidget(virus_group)
        
        # Add a spacer
        layout.addStretch()
    
    def setup_advanced_tab(self):
        """Setup the advanced settings tab"""
        layout = QVBoxLayout(self.advanced_tab)
        
        # Backup settings
        backup_group = QGroupBox("Backup")
        backup_layout = QVBoxLayout(backup_group)
        
        self.check_backup_before_repair = QCheckBox("Create backup before system repairs")
        self.check_backup_before_repair.setChecked(True)
        backup_layout.addWidget(self.check_backup_before_repair)
        
        backup_location_layout = QHBoxLayout()
        backup_location_layout.addWidget(QLabel("Backup Location:"))
        
        self.edit_backup_location = QLineEdit()
        self.edit_backup_location.setText(os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups"))
        backup_location_layout.addWidget(self.edit_backup_location)
        
        self.btn_browse_backup = QPushButton("Browse...")
        self.btn_browse_backup.clicked.connect(self.browse_backup_location)
        backup_location_layout.addWidget(self.btn_browse_backup)
        
        backup_layout.addLayout(backup_location_layout)
        
        layout.addWidget(backup_group)
        
        # Log settings
        log_group = QGroupBox("Logging")
        log_layout = QVBoxLayout(log_group)
        
        self.check_enable_logging = QCheckBox("Enable detailed logging")
        self.check_enable_logging.setChecked(True)
        log_layout.addWidget(self.check_enable_logging)
        
        self.combo_log_level = QComboBox()
        self.combo_log_level.addItems(["Info", "Debug", "Warning", "Error", "Critical"])
        self.combo_log_level.setCurrentText("Info")
        log_layout.addWidget(QLabel("Log Level:"))
        log_layout.addWidget(self.combo_log_level)
        
        self.spin_log_retention = QSpinBox()
        self.spin_log_retention.setRange(1, 90)
        self.spin_log_retention.setValue(30)
        self.spin_log_retention.setSuffix(" days")
        log_layout.addWidget(QLabel("Keep logs for:"))
        log_layout.addWidget(self.spin_log_retention)
        
        layout.addWidget(log_group)
        
        # Performance settings
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout(perf_group)
        
        self.check_use_multithreading = QCheckBox("Use multithreading for operations")
        self.check_use_multithreading.setChecked(True)
        perf_layout.addWidget(self.check_use_multithreading)
        
        thread_layout = QHBoxLayout()
        thread_layout.addWidget(QLabel("Max threads:"))
        
        self.spin_max_threads = QSpinBox()
        self.spin_max_threads.setRange(1, 16)
        self.spin_max_threads.setValue(4)
        thread_layout.addWidget(self.spin_max_threads)
        
        perf_layout.addLayout(thread_layout)
        
        layout.addWidget(perf_group)
        
        # Add a spacer
        layout.addStretch()
    
    def browse_backup_location(self):
        """Open a file dialog to select backup location"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Backup Location", self.edit_backup_location.text(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder:
            self.edit_backup_location.setText(folder)
    
    def load_settings(self):
        """Load settings from the settings object"""
        # Try to load from settings object, otherwise use defaults
        try:
            # General settings
            language = self.settings.get_setting("language", "English")
            index = self.language_combo.findText(language)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)
                
            self.startup_checkbox.setChecked(self.settings.get_setting("start_with_windows", False))
            
            # Appearance settings
            theme = self.settings.get_setting("theme", "dark")
            if theme == "dark":
                self.theme_combo.setCurrentIndex(1)
            elif theme == "light":
                self.theme_combo.setCurrentIndex(0)
            elif theme == "system":
                self.theme_combo.setCurrentIndex(2)
            
            # Custom theme settings
            self.edit_theme_name.setText(self.settings.get_setting("custom_theme_name", "My Custom Theme"))
            
            bg_color = self.settings.get_setting("custom_bg_color", "#1e1e1e")
            self.bg_color_display.setStyleSheet(f"background-color: {bg_color}; border: 1px solid #444;")
            
            text_color = self.settings.get_setting("custom_text_color", "#e0e0e0")
            self.text_color_display.setStyleSheet(f"background-color: {text_color}; border: 1px solid #444;")
            
            accent_color = self.settings.get_setting("custom_accent_color", "#00a8ff")
            self.accent_color_display.setStyleSheet(f"background-color: {accent_color}; border: 1px solid #444;")
            
            # Default accent color
            default_accent_color = self.settings.get_setting("accent_color", "Blue")
            index = self.combo_accent_color.findText(default_accent_color)
            if index >= 0:
                self.combo_accent_color.setCurrentIndex(index)
            
            font_family = self.settings.get_setting("font_family", "System Default")
            index = self.combo_font_family.findText(font_family)
            if index >= 0:
                self.combo_font_family.setCurrentIndex(index)
            
            self.spin_font_size.setValue(self.settings.get_setting("font_size", 10))
            self.slider_icon_size.setValue(self.settings.get_setting("icon_size", 24))
            
            # Scan settings
            self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
            self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
            self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
            self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
            self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
            
            # Disk check settings
            self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
            
            self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
            self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
            self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
            self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
            
            # Advanced settings
            self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
            self.edit_backup_location.setText(self.settings.get_setting(
                "backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")
            ))
            
            self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
            
            log_level = self.settings.get_setting("log_level", "Info")
            index = self.combo_log_level.findText(log_level)
            if index >= 0:
                self.combo_log_level.setCurrentIndex(index)
            
            self.spin_log_retention.setValue(self.settings.get_setting("log_retention", 30))
            self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
            self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
            
        except Exception as e:
            QMessageBox.warning(self, "Settings Error", f"Error loading settings: {str(e)}")
    
    def save_settings(self):
        """Save settings to the settings object"""
        try:
            # General settings
            self.settings.set_setting("language", self.language_combo.currentText())
            self.settings.set_setting("start_with_windows", self.startup_checkbox.isChecked())
            
            # Appearance settings
            theme = self.theme_combo.currentText()
            if theme == "Dark":
                self.settings.set_setting("theme", "dark")
            elif theme == "Light":
                self.settings.set_setting("theme", "light")
            elif theme == "System":
                self.settings.set_setting("theme", "system")
            
            # Custom theme settings
            self.settings.set_setting("custom_theme_name", self.edit_theme_name.text())
            
            bg_color = self.bg_color_display.styleSheet().split("background-color:")[1].split(";")[0].strip()
            self.settings.set_setting("custom_bg_color", bg_color)
            
            text_color = self.text_color_display.styleSheet().split("background-color:")[1].split(";")[0].strip()
            self.settings.set_setting("custom_text_color", text_color)
            
            accent_color = self.accent_color_display.styleSheet().split("background-color:")[1].split(";")[0].strip()
            self.settings.set_setting("custom_accent_color", accent_color)
            
            # Default accent color
            self.settings.set_setting("accent_color", self.combo_accent_color.currentText())
            self.settings.set_setting("font_family", self.combo_font_family.currentText())
            self.settings.set_setting("font_size", self.spin_font_size.value())
            self.settings.set_setting("icon_size", self.slider_icon_size.value())
            
            # Scan settings
            self.settings.set_setting("clean_temp", self.check_clean_temp.isChecked())
            self.settings.set_setting("clean_recycle", self.check_clean_recycle.isChecked())
            self.settings.set_setting("clean_browser", self.check_clean_browser.isChecked())
            self.settings.set_setting("clean_prefetch", self.check_clean_prefetch.isChecked())
            self.settings.set_setting("clean_logs", self.check_clean_logs.isChecked())
            
            # Disk check settings
            self.settings.set_setting("disk_check_readonly", self.check_disk_readonly.isChecked())
            
            self.settings.set_setting("scan_archives", self.check_scan_archives.isChecked())
            self.settings.set_setting("scan_rootkits", self.check_scan_rootkits.isChecked())
            self.settings.set_setting("scan_autofix", self.check_scan_autofix.isChecked())
            self.settings.set_setting("scan_level", self.slider_scan_level.value())
            
            # Advanced settings
            self.settings.set_setting("backup_before_repair", self.check_backup_before_repair.isChecked())
            self.settings.set_setting("backup_location", self.edit_backup_location.text())
            self.settings.set_setting("enable_logging", self.check_enable_logging.isChecked())
            self.settings.set_setting("log_level", self.combo_log_level.currentText())
            self.settings.set_setting("log_retention", self.spin_log_retention.value())
            self.settings.set_setting("use_multithreading", self.check_use_multithreading.isChecked())
            self.settings.set_setting("max_threads", self.spin_max_threads.value())
            
            # Save settings to file
            self.settings.save_settings()
            
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")
            
        except Exception as e:
            QMessageBox.warning(self, "Settings Error", f"Error saving settings: {str(e)}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(self, "Reset Settings", 
                                   "Are you sure you want to reset all settings to defaults?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Clear settings
            try:
                # Reset to default values
                # General settings
                self.settings.set_setting("language", "English")
                self.settings.set_setting("start_with_windows", False)
                
                # Appearance settings
                self.settings.set_setting("theme", "dark")
                self.settings.set_setting("custom_theme_name", "My Custom Theme")
                self.settings.set_setting("custom_bg_color", "#1e1e1e")
                self.settings.set_setting("custom_text_color", "#e0e0e0")
                self.settings.set_setting("custom_accent_color", "#00a8ff")
                self.settings.set_setting("accent_color", "Blue")
                self.settings.set_setting("font_family", "System Default")
                self.settings.set_setting("font_size", 10)
                self.settings.set_setting("icon_size", 24)
                
                # Scan settings
                self.settings.set_setting("clean_temp", True)
                self.settings.set_setting("clean_recycle", True)
                self.settings.set_setting("clean_browser", True)
                self.settings.set_setting("clean_prefetch", True)
                self.settings.set_setting("clean_logs", False)
                
                # Disk check settings
                self.settings.set_setting("disk_check_readonly", True)
                
                self.settings.set_setting("scan_archives", True)
                self.settings.set_setting("scan_rootkits", True)
                self.settings.set_setting("scan_autofix", False)
                self.settings.set_setting("scan_level", 2)
                
                # Advanced settings
                self.settings.set_setting("backup_before_repair", True)
                self.settings.set_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups"))
                self.settings.set_setting("enable_logging", True)
                self.settings.set_setting("log_level", "Info")
                self.settings.set_setting("log_retention", 30)
                self.settings.set_setting("use_multithreading", True)
                self.settings.set_setting("max_threads", 4)
                
                # Save settings to file
                self.settings.save_settings()
                
                # Reload settings
                self.load_settings()
                
                QMessageBox.information(self, "Settings Reset", "Settings have been reset to defaults.")
                
            except Exception as e:
                QMessageBox.warning(self, "Settings Error", f"Error resetting settings: {str(e)}")
    
    def get_translation(self, key, default=None):
        """Override get_translation to use the correct section name"""
        return self.settings.get_translation("settings", key, default)
        
    def refresh_language(self):
        """Refresh all UI elements with current language translations"""
        # 鏇存柊鏍囬鍜屾弿杩?
        title_label = self.findChild(QLabel, "title_label")
        if title_label:
            title_label.setText(self.get_translation("title"))
            
        desc_label = self.findChild(QLabel, "desc_label")
        if desc_label:
            desc_label.setText(self.get_translation("description"))
        
        # 鏇存柊涓€鑸缃粍
        general_group = self.findChild(QGroupBox, "general_group")
        if general_group:
            general_group.setTitle(self.get_translation("general_settings"))
        
        # 鏇存柊涓€鑸缃腑鐨勬帶浠?
        theme_label = self.findChild(QLabel, "theme_label")
        if theme_label:
            theme_label.setText(self.get_translation("theme") + ":")
        
        # 鏇存柊璇█璁剧疆
        language_label = self.findChild(QLabel, "language_label")
        if language_label:
            language_label.setText(self.get_translation("language") + ":")
        
        # 鏇存柊鍚姩璁剧疆
        startup_label = self.findChild(QLabel, "startup_label")
        if startup_label:
            startup_label.setText(self.get_translation("start_with_windows") + ":")
        
        startup_checkbox = self.findChild(QCheckBox, "startup_checkbox")
        if startup_checkbox:
            startup_checkbox.setText(self.get_translation("auto_start"))
        
        # 鏇存柊閫氱煡璁剧疆缁?
        notifications_group = self.findChild(QGroupBox, "notifications_group")
        if notifications_group:
            notifications_group.setTitle(self.get_translation("notifications"))
        
        # 鏇存柊閫氱煡璁剧疆澶嶉€夋
        if hasattr(self, "enable_notifications_checkbox"):
            self.enable_notifications_checkbox.setText(self.get_translation("enable_notifications"))
        
        if hasattr(self, "show_tips_checkbox"):
            self.show_tips_checkbox.setText(self.get_translation("show_tips"))
        
        if hasattr(self, "maintenance_reminder_checkbox"):
            self.maintenance_reminder_checkbox.setText(self.get_translation("maintenance_reminder"))
        
        # 鏇存柊闅愮璁剧疆缁?
        privacy_group = self.findChild(QGroupBox, "privacy_group")
        if privacy_group:
            privacy_group.setTitle(self.get_translation("privacy"))
        
        # 鏇存柊闅愮璁剧疆澶嶉€夋
        if hasattr(self, "usage_stats_checkbox"):
            self.usage_stats_checkbox.setText(self.get_translation("collect_usage_statistics"))
        
        if hasattr(self, "auto_update_checkbox"):
            self.auto_update_checkbox.setText(self.get_translation("automatic_updates"))
        
        # 鏇存柊鍏朵粬璁剧疆缁?
        advanced_group = self.findChild(QGroupBox, "advanced_group")
        if advanced_group:
            advanced_group.setTitle(self.get_translation("advanced"))
            
        # 鏇存柊鏃ュ織绾у埆閫夐」
        log_level_label = self.findChild(QLabel, "log_level_label")
        if log_level_label:
            log_level_label.setText(self.get_translation("log_level") + ":")
        
        # 鏇存柊鎸夐挳
        if hasattr(self, "save_button"):
            self.save_button.setText(self.get_translation("save_settings"))
        
        if hasattr(self, "restore_defaults_button"):
            self.restore_defaults_button.setText(self.get_translation("restore_defaults"))
        
        # Refresh tab titles
        self.tabs.setTabText(0, self.get_translation("general", "General"))
        self.tabs.setTabText(1, self.get_translation("appearance", "Appearance"))
        self.tabs.setTabText(2, self.get_translation("scan_options", "Scan Options"))
        self.tabs.setTabText(3, self.get_translation("advanced", "Advanced"))
        
        # Update title and description
        title_label = self.findChild(QLabel, "title_label")
        if title_label:
            title_label.setText(self.get_translation("title"))
        
        desc_label = self.findChild(QLabel, "desc_label")
        if desc_label:
            desc_label.setText(self.get_translation("description"))
        
        # Update buttons
        self.save_button.setText(self.get_translation("save_settings"))
        self.restore_defaults_button.setText(self.get_translation("restore_defaults"))
        
        # General tab
        self.findChild(QGroupBox, "general_group").setTitle(self.get_translation("general_settings"))
        self.findChild(QLabel, "language_label").setText(self.get_translation("language_label", "Interface Language:"))
        
        self.findChild(QGroupBox, "general_group").setTitle(self.get_translation("general_settings"))
        self.findChild(QLabel, "startup_label").setText(self.get_translation("start_with_windows", "Start on boot"))
        self.findChild(QCheckBox, "startup_checkbox").setText(self.get_translation("auto_start", "Auto-start"))
        
        # Appearance tab
        self.findChild(QGroupBox, "theme_group").setTitle(self.get_translation("theme", "Theme"))
        self.theme_combo.clear()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        self.theme_combo.setCurrentText(self.settings.get_setting("theme", "dark"))
        
        # Update the default tab combo box items
        self.combo_default_tab.clear()
        self.combo_default_tab.addItems([
            self.settings.get_translation("general", "dashboard", "Dashboard"),
            self.settings.get_translation("general", "system_cleaner", "System Cleaner"),
            self.settings.get_translation("general", "gpu_information", "GPU Information"),
            self.settings.get_translation("general", "system_repair", "System Repair"),
            self.settings.get_translation("general", "dism_tool", "DISM Tool"),
            self.settings.get_translation("general", "network_reset", "Network Reset"),
            self.settings.get_translation("general", "disk_check", "Disk Check"),
            self.settings.get_translation("general", "boot_repair", "Boot Repair"),
            self.settings.get_translation("general", "virus_scan", "Virus Scan")
        ])
        
        # Update log level
        self.log_level_combo.clear()
        self.log_level_combo.addItems(["Error", "Warning", "Info", "Debug"])
        self.log_level_combo.setCurrentText(self.settings.get_setting("log_level", "Info"))
        
        # Update language
        self.language_combo.clear()
        self.language_combo.addItems(["English", "Chinese"])
        self.language_combo.setCurrentText(self.settings.get_setting("language", "English"))
        
        # Update notifications
        self.enable_notifications_checkbox.setChecked(self.settings.get_setting("enable_notifications", True))
        self.show_tips_checkbox.setChecked(self.settings.get_setting("show_tips", True))
        self.maintenance_reminder_checkbox.setChecked(self.settings.get_setting("maintenance_reminder", True))
        
        # Update privacy
        self.usage_stats_checkbox.setChecked(self.settings.get_setting("collect_usage_statistics", False))
        self.auto_update_checkbox.setChecked(self.settings.get_setting("automatic_updates", True))
        
        # Update theme
        self.theme_combo.clear()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        self.theme_combo.setCurrentText(self.settings.get_setting("theme", "dark"))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
import os
import json
import shutil
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QCheckBox, QComboBox, QGroupBox, 
                             QMessageBox, QFileDialog, QTabWidget,
                             QSpinBox, QSlider, QLineEdit, QFormLayout,
                             QButtonGroup, QRadioButton, QColorDialog)
from PyQt5.QtCore import Qt, QSettings, QSize
from PyQt5.QtGui import QFont, QIcon, QColor

class SettingsWidget(QWidget):
    """Widget for application settings"""
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Set up the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title and description
        title_label = QLabel(self.get_translation("title"))
        title_label.setObjectName("title_label")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        desc_label = QLabel(self.get_translation("description"))
        desc_label.setObjectName("desc_label")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("settings_tabs")
        layout.addWidget(self.tabs)
        
        # General tab
        general_tab = QWidget()
        general_tab.setObjectName("general_tab")
        general_layout = QVBoxLayout(general_tab)
        
        # General settings group
        general_group = QGroupBox(self.get_translation("general_settings"))
        general_group.setObjectName("general_group")
        general_group_layout = QFormLayout(general_group)
        general_group_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Theme setting
        theme_label = QLabel(self.get_translation("theme") + ":")
        theme_label.setObjectName("theme_label")
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("theme_combo")
        self.theme_combo.addItems(["Light", "Dark", "System"])
        general_group_layout.addRow(theme_label, self.theme_combo)
        
        # Language setting
        language_label = QLabel(self.get_translation("language") + ":")
        language_label.setObjectName("language_label")
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("language_combo")
        self.language_combo.addItems(["English", "Chinese"])
        general_group_layout.addRow(language_label, self.language_combo)
        
        # Startup setting
        startup_label = QLabel(self.get_translation("start_with_windows") + ":")
        startup_label.setObjectName("startup_label")
        self.startup_checkbox = QCheckBox(self.get_translation("auto_start"))
        self.startup_checkbox.setObjectName("startup_checkbox")
        general_group_layout.addRow(startup_label, self.startup_checkbox)
        
        general_layout.addWidget(general_group)
        
        # Notifications group
        notifications_group = QGroupBox(self.get_translation("notifications"))
        notifications_group.setObjectName("notifications_group")
        notifications_layout = QVBoxLayout(notifications_group)
        
        self.enable_notifications_checkbox = QCheckBox(self.get_translation("enable_notifications"))
        self.enable_notifications_checkbox.setObjectName("enable_notifications_checkbox")
        self.enable_notifications_checkbox.setChecked(True)
        notifications_layout.addWidget(self.enable_notifications_checkbox)
        
        self.show_tips_checkbox = QCheckBox(self.get_translation("show_tips"))
        self.show_tips_checkbox.setObjectName("show_tips_checkbox")
        self.show_tips_checkbox.setChecked(True)
        notifications_layout.addWidget(self.show_tips_checkbox)
        
        self.maintenance_reminder_checkbox = QCheckBox(self.get_translation("maintenance_reminder"))
        self.maintenance_reminder_checkbox.setObjectName("maintenance_reminder_checkbox")
        self.maintenance_reminder_checkbox.setChecked(True)
        notifications_layout.addWidget(self.maintenance_reminder_checkbox)
        
        general_layout.addWidget(notifications_group)
        
        # Add general tab
        self.tabs.addTab(general_tab, self.get_translation("general"))
        
        # Privacy tab
        privacy_tab = QWidget()
        privacy_tab.setObjectName("privacy_tab")
        privacy_layout = QVBoxLayout(privacy_tab)
        
        privacy_group = QGroupBox(self.get_translation("privacy"))
        privacy_group.setObjectName("privacy_group")
        privacy_group_layout = QVBoxLayout(privacy_group)
        
        self.usage_stats_checkbox = QCheckBox(self.get_translation("collect_usage_statistics"))
        self.usage_stats_checkbox.setObjectName("usage_stats_checkbox")
        self.usage_stats_checkbox.setChecked(False)
        privacy_group_layout.addWidget(self.usage_stats_checkbox)
        
        self.auto_update_checkbox = QCheckBox(self.get_translation("automatic_updates"))
        self.auto_update_checkbox.setObjectName("auto_update_checkbox")
        self.auto_update_checkbox.setChecked(True)
        privacy_group_layout.addWidget(self.auto_update_checkbox)
        
        privacy_layout.addWidget(privacy_group)
        
        # Add privacy tab
        self.tabs.addTab(privacy_tab, self.get_translation("privacy"))
        
        # Advanced tab
        advanced_tab = QWidget()
        advanced_tab.setObjectName("advanced_tab")
        advanced_layout = QVBoxLayout(advanced_tab)
        
        advanced_group = QGroupBox(self.get_translation("advanced"))
        advanced_group.setObjectName("advanced_group")
        advanced_group_layout = QFormLayout(advanced_group)
        
        # Log level
        log_level_label = QLabel(self.get_translation("log_level") + ":")
        log_level_label.setObjectName("log_level_label")
        self.log_level_combo = QComboBox()
        self.log_level_combo.setObjectName("log_level_combo")
        self.log_level_combo.addItems(["Error", "Warning", "Info", "Debug"])
        advanced_group_layout.addRow(log_level_label, self.log_level_combo)
        
        advanced_layout.addWidget(advanced_group)
        
        # Add advanced tab
        self.tabs.addTab(advanced_tab, self.get_translation("advanced"))
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.save_button = QPushButton(self.get_translation("save_settings"))
        self.save_button.setObjectName("save_button")
        self.save_button.setMinimumWidth(120)
        buttons_layout.addWidget(self.save_button)
        
        self.restore_defaults_button = QPushButton(self.get_translation("restore_defaults"))
        self.restore_defaults_button.setObjectName("restore_defaults_button")
        self.restore_defaults_button.setMinimumWidth(140)
        buttons_layout.addWidget(self.restore_defaults_button)
        
        layout.addLayout(buttons_layout)
        
        # Connect signals
        self.save_button.clicked.connect(self.save_settings)
        self.restore_defaults_button.clicked.connect(self.restore_defaults)
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
    
    def select_color(self, color_type):
        """Open a color dialog to select a color"""
        current_color = None
        
        if color_type == "background":
            current_bg_color = self.bg_color_display.styleSheet().split("background-color:")[1].split(";")[0].strip()
            current_color = QColor(current_bg_color)
        elif color_type == "text":
            current_text_color = self.text_color_display.styleSheet().split("background-color:")[1].split(";")[0].strip()
            current_color = QColor(current_text_color)
        elif color_type == "accent":
            current_accent_color = self.accent_color_display.styleSheet().split("background-color:")[1].split(";")[0].strip()
            current_color = QColor(current_accent_color)
        
        color = QColorDialog.getColor(current_color, self, f"Select {color_type.title()} Color")
        
        if color.isValid():
            if color_type == "background":
                self.bg_color_display.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #444;")
            elif color_type == "text":
                self.text_color_display.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #444;")
            elif color_type == "accent":
                self.accent_color_display.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #444;")
    
    def setup_scan_tab(self):
        """Setup the scan options tab"""
        layout = QVBoxLayout(self.scan_tab)
        
        # System cleaner settings
        cleaner_group = QGroupBox("System Cleaner")
        cleaner_layout = QVBoxLayout(cleaner_group)
        
        self.check_clean_temp = QCheckBox("Clean temporary files")
        self.check_clean_temp.setChecked(True)
        cleaner_layout.addWidget(self.check_clean_temp)
        
        self.check_clean_recycle = QCheckBox("Empty recycle bin")
        self.check_clean_recycle.setChecked(True)
        cleaner_layout.addWidget(self.check_clean_recycle)
        
        self.check_clean_browser = QCheckBox("Clean browser caches")
        self.check_clean_browser.setChecked(True)
        cleaner_layout.addWidget(self.check_clean_browser)
        
        self.check_clean_prefetch = QCheckBox("Clean Windows prefetch")
        self.check_clean_prefetch.setChecked(True)
        cleaner_layout.addWidget(self.check_clean_prefetch)
        
        self.check_clean_logs = QCheckBox("Clean system logs")
        self.check_clean_logs.setChecked(False)
        cleaner_layout.addWidget(self.check_clean_logs)
        
        layout.addWidget(cleaner_group)
        
        # Disk check settings
        disk_check_group = QGroupBox("Disk Check")
        disk_check_layout = QVBoxLayout(disk_check_group)
        
        self.check_disk_readonly = QCheckBox("Run disk check in read-only mode by default")
        self.check_disk_readonly.setChecked(True)
        disk_check_layout.addWidget(self.check_disk_readonly)
        
        layout.addWidget(disk_check_group)
        
        # Virus scan settings
        virus_group = QGroupBox("Virus Scan")
        virus_layout = QVBoxLayout(virus_group)
        
        self.check_scan_archives = QCheckBox("Scan inside archives")
        self.check_scan_archives.setChecked(True)
        virus_layout.addWidget(self.check_scan_archives)
        
        self.check_scan_rootkits = QCheckBox("Scan for rootkits")
        self.check_scan_rootkits.setChecked(True)
        virus_layout.addWidget(self.check_scan_rootkits)
        
        self.check_scan_autofix = QCheckBox("Automatically fix detected issues")
        self.check_scan_autofix.setChecked(False)
        virus_layout.addWidget(self.check_scan_autofix)
        
        scan_level_layout = QHBoxLayout()
        scan_level_layout.addWidget(QLabel("Scan Thoroughness:"))
        
        self.slider_scan_level = QSlider(Qt.Horizontal)
        self.slider_scan_level.setRange(1, 3)
        self.slider_scan_level.setValue(2)
        self.slider_scan_level.setTickPosition(QSlider.TicksBelow)
        self.slider_scan_level.setTickInterval(1)
        scan_level_layout.addWidget(self.slider_scan_level)
        
        level_labels = QHBoxLayout()
        level_labels.addWidget(QLabel("Quick"))
        level_labels.addStretch()
        level_labels.addWidget(QLabel("Balanced"))
        level_labels.addStretch()
        level_labels.addWidget(QLabel("Thorough"))
        scan_level_layout.addLayout(level_labels)
        
        virus_layout.addLayout(scan_level_layout)
        
        layout.addWidget(virus_group)
        
        # Add a spacer
        layout.addStretch()
    
    def setup_advanced_tab(self):
        """Setup the advanced settings tab"""
        layout = QVBoxLayout(self.advanced_tab)
        
        # Backup settings
        backup_group = QGroupBox("Backup")
        backup_layout = QVBoxLayout(backup_group)
        
        self.check_backup_before_repair = QCheckBox("Create backup before system repairs")
        self.check_backup_before_repair.setChecked(True)
        backup_layout.addWidget(self.check_backup_before_repair)
        
        backup_location_layout = QHBoxLayout()
        backup_location_layout.addWidget(QLabel("Backup Location:"))
        
        self.edit_backup_location = QLineEdit()
        self.edit_backup_location.setText(os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups"))
        backup_location_layout.addWidget(self.edit_backup_location)
        
        self.btn_browse_backup = QPushButton("Browse...")
        self.btn_browse_backup.clicked.connect(self.browse_backup_location)
        backup_location_layout.addWidget(self.btn_browse_backup)
        
        backup_layout.addLayout(backup_location_layout)
        
        layout.addWidget(backup_group)
        
        # Log settings
        log_group = QGroupBox("Logging")
        log_layout = QVBoxLayout(log_group)
        
        self.check_enable_logging = QCheckBox("Enable detailed logging")
        self.check_enable_logging.setChecked(True)
        log_layout.addWidget(self.check_enable_logging)
        
        self.combo_log_level = QComboBox()
        self.combo_log_level.addItems(["Info", "Debug", "Warning", "Error", "Critical"])
        self.combo_log_level.setCurrentText("Info")
        log_layout.addWidget(QLabel("Log Level:"))
        log_layout.addWidget(self.combo_log_level)
        
        self.spin_log_retention = QSpinBox()
        self.spin_log_retention.setRange(1, 90)
        self.spin_log_retention.setValue(30)
        self.spin_log_retention.setSuffix(" days")
        log_layout.addWidget(QLabel("Keep logs for:"))
        log_layout.addWidget(self.spin_log_retention)
        
        layout.addWidget(log_group)
        
        # Performance settings
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout(perf_group)
        
        self.check_use_multithreading = QCheckBox("Use multithreading for operations")
        self.check_use_multithreading.setChecked(True)
        perf_layout.addWidget(self.check_use_multithreading)
        
        thread_layout = QHBoxLayout()
        thread_layout.addWidget(QLabel("Max threads:"))
        
        self.spin_max_threads = QSpinBox()
        self.spin_max_threads.setRange(1, 16)
        self.spin_max_threads.setValue(4)
        thread_layout.addWidget(self.spin_max_threads)
        
        perf_layout.addLayout(thread_layout)
        
        layout.addWidget(perf_group)
        
        # Add a spacer
        layout.addStretch()
    
    def browse_backup_location(self):
        """Open a file dialog to select backup location"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Backup Location", self.edit_backup_location.text(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder:
            self.edit_backup_location.setText(folder)
    
    def load_settings(self):
        """Load settings from the settings object"""
        # Try to load from settings object, otherwise use defaults
        try:
            # General settings
            language = self.settings.get_setting("language", "English")
            index = self.language_combo.findText(language)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)
                
            self.startup_checkbox.setChecked(self.settings.get_setting("start_with_windows", False))
            
            # Appearance settings
            theme = self.settings.get_setting("theme", "dark")
            if theme == "dark":
                self.theme_combo.setCurrentIndex(1)
            elif theme == "light":
                self.theme_combo.setCurrentIndex(0)
            elif theme == "system":
                self.theme_combo.setCurrentIndex(2)
            
            # Custom theme settings
            self.edit_theme_name.setText(self.settings.get_setting("custom_theme_name", "My Custom Theme"))
            
            bg_color = self.settings.get_setting("custom_bg_color", "#1e1e1e")
            self.bg_color_display.setStyleSheet(f"background-color: {bg_color}; border: 1px solid #444;")
            
            text_color = self.settings.get_setting("custom_text_color", "#e0e0e0")
            self.text_color_display.setStyleSheet(f"background-color: {text_color}; border: 1px solid #444;")
            
            accent_color = self.settings.get_setting("custom_accent_color", "#00a8ff")
            self.accent_color_display.setStyleSheet(f"background-color: {accent_color}; border: 1px solid #444;")
            
            # Default accent color
            default_accent_color = self.settings.get_setting("accent_color", "Blue")
            index = self.combo_accent_color.findText(default_accent_color)
            if index >= 0:
                self.combo_accent_color.setCurrentIndex(index)
            
            font_family = self.settings.get_setting("font_family", "System Default")
            index = self.combo_font_family.findText(font_family)
            if index >= 0:
                self.combo_font_family.setCurrentIndex(index)
            
            self.spin_font_size.setValue(self.settings.get_setting("font_size", 10))
            self.slider_icon_size.setValue(self.settings.get_setting("icon_size", 24))
            
            # Scan settings
            self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
            self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
            self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
            self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
            self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
            
            # Disk check settings
            self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
            
            self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
            self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
            self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
            self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
            
            # Advanced settings
            self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
            self.edit_backup_location.setText(self.settings.get_setting(
                "backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")
            ))
            
            self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
            
            log_level = self.settings.get_setting("log_level", "Info")
            index = self.combo_log_level.findText(log_level)
            if index >= 0:
                self.combo_log_level.setCurrentIndex(index)
            
            self.spin_log_retention.setValue(self.settings.get_setting("log_retention", 30))
            self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
            self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
            
        except Exception as e:
            QMessageBox.warning(self, "Settings Error", f"Error loading settings: {str(e)}")
    
    def save_settings(self):
        """Save settings to the settings object"""
        try:
            # General settings
            self.settings.set_setting("language", self.language_combo.currentText())
            self.settings.set_setting("start_with_windows", self.startup_checkbox.isChecked())
            
            # Appearance settings
            theme = self.theme_combo.currentText()
            if theme == "Dark":
                self.settings.set_setting("theme", "dark")
            elif theme == "Light":
                self.settings.set_setting("theme", "light")
            elif theme == "System":
                self.settings.set_setting("theme", "system")
            
            # Custom theme settings
            self.settings.set_setting("custom_theme_name", self.edit_theme_name.text())
            
            bg_color = self.bg_color_display.styleSheet().split("background-color:")[1].split(";")[0].strip()
            self.settings.set_setting("custom_bg_color", bg_color)
            
            text_color = self.text_color_display.styleSheet().split("background-color:")[1].split(";")[0].strip()
            self.settings.set_setting("custom_text_color", text_color)
            
            accent_color = self.accent_color_display.styleSheet().split("background-color:")[1].split(";")[0].strip()
            self.settings.set_setting("custom_accent_color", accent_color)
            
            # Default accent color
            self.settings.set_setting("accent_color", self.combo_accent_color.currentText())
            self.settings.set_setting("font_family", self.combo_font_family.currentText())
            self.settings.set_setting("font_size", self.spin_font_size.value())
            self.settings.set_setting("icon_size", self.slider_icon_size.value())
            
            # Scan settings
            self.settings.set_setting("clean_temp", self.check_clean_temp.isChecked())
            self.settings.set_setting("clean_recycle", self.check_clean_recycle.isChecked())
            self.settings.set_setting("clean_browser", self.check_clean_browser.isChecked())
            self.settings.set_setting("clean_prefetch", self.check_clean_prefetch.isChecked())
            self.settings.set_setting("clean_logs", self.check_clean_logs.isChecked())
            
            # Disk check settings
            self.settings.set_setting("disk_check_readonly", self.check_disk_readonly.isChecked())
            
            self.settings.set_setting("scan_archives", self.check_scan_archives.isChecked())
            self.settings.set_setting("scan_rootkits", self.check_scan_rootkits.isChecked())
            self.settings.set_setting("scan_autofix", self.check_scan_autofix.isChecked())
            self.settings.set_setting("scan_level", self.slider_scan_level.value())
            
            # Advanced settings
            self.settings.set_setting("backup_before_repair", self.check_backup_before_repair.isChecked())
            self.settings.set_setting("backup_location", self.edit_backup_location.text())
            self.settings.set_setting("enable_logging", self.check_enable_logging.isChecked())
            self.settings.set_setting("log_level", self.combo_log_level.currentText())
            self.settings.set_setting("log_retention", self.spin_log_retention.value())
            self.settings.set_setting("use_multithreading", self.check_use_multithreading.isChecked())
            self.settings.set_setting("max_threads", self.spin_max_threads.value())
            
            # Save settings to file
            self.settings.save_settings()
            
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")
            
        except Exception as e:
            QMessageBox.warning(self, "Settings Error", f"Error saving settings: {str(e)}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(self, "Reset Settings", 
                                   "Are you sure you want to reset all settings to defaults?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Clear settings
            try:
                # Reset to default values
                # General settings
                self.settings.set_setting("language", "English")
                self.settings.set_setting("start_with_windows", False)
                
                # Appearance settings
                self.settings.set_setting("theme", "dark")
                self.settings.set_setting("custom_theme_name", "My Custom Theme")
                self.settings.set_setting("custom_bg_color", "#1e1e1e")
                self.settings.set_setting("custom_text_color", "#e0e0e0")
                self.settings.set_setting("custom_accent_color", "#00a8ff")
                self.settings.set_setting("accent_color", "Blue")
                self.settings.set_setting("font_family", "System Default")
                self.settings.set_setting("font_size", 10)
                self.settings.set_setting("icon_size", 24)
                
                # Scan settings
                self.settings.set_setting("clean_temp", True)
                self.settings.set_setting("clean_recycle", True)
                self.settings.set_setting("clean_browser", True)
                self.settings.set_setting("clean_prefetch", True)
                self.settings.set_setting("clean_logs", False)
                
                # Disk check settings
                self.settings.set_setting("disk_check_readonly", True)
                
                self.settings.set_setting("scan_archives", True)
                self.settings.set_setting("scan_rootkits", True)
                self.settings.set_setting("scan_autofix", False)
                self.settings.set_setting("scan_level", 2)
                
                # Advanced settings
                self.settings.set_setting("backup_before_repair", True)
                self.settings.set_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups"))
                self.settings.set_setting("enable_logging", True)
                self.settings.set_setting("log_level", "Info")
                self.settings.set_setting("log_retention", 30)
                self.settings.set_setting("use_multithreading", True)
                self.settings.set_setting("max_threads", 4)
                
                # Save settings to file
                self.settings.save_settings()
                
                # Reload settings
                self.load_settings()
                
                QMessageBox.information(self, "Settings Reset", "Settings have been reset to defaults.")
                
            except Exception as e:
                QMessageBox.warning(self, "Settings Error", f"Error resetting settings: {str(e)}")
    
    def get_translation(self, key, default=None):
        """Override get_translation to use the correct section name"""
        return self.settings.get_translation("settings", key, default)
        
    def refresh_language(self):
        """Refresh all UI elements with current language translations"""
        # 鏇存柊鏍囬鍜屾弿杩?
        title_label = self.findChild(QLabel, "title_label")
        if title_label:
            title_label.setText(self.get_translation("title"))
            
        desc_label = self.findChild(QLabel, "desc_label")
        if desc_label:
            desc_label.setText(self.get_translation("description"))
        
        # 鏇存柊涓€鑸缃粍
        general_group = self.findChild(QGroupBox, "general_group")
        if general_group:
            general_group.setTitle(self.get_translation("general_settings"))
        
        # 鏇存柊涓€鑸缃腑鐨勬帶浠?
        theme_label = self.findChild(QLabel, "theme_label")
        if theme_label:
            theme_label.setText(self.get_translation("theme") + ":")
        
        # 鏇存柊璇█璁剧疆
        language_label = self.findChild(QLabel, "language_label")
        if language_label:
            language_label.setText(self.get_translation("language") + ":")
        
        # 鏇存柊鍚姩璁剧疆
        startup_label = self.findChild(QLabel, "startup_label")
        if startup_label:
            startup_label.setText(self.get_translation("start_with_windows") + ":")
        
        startup_checkbox = self.findChild(QCheckBox, "startup_checkbox")
        if startup_checkbox:
            startup_checkbox.setText(self.get_translation("auto_start"))
        
        # 鏇存柊閫氱煡璁剧疆缁?
        notifications_group = self.findChild(QGroupBox, "notifications_group")
        if notifications_group:
            notifications_group.setTitle(self.get_translation("notifications"))
        
        # 鏇存柊閫氱煡璁剧疆澶嶉€夋
        if hasattr(self, "enable_notifications_checkbox"):
            self.enable_notifications_checkbox.setText(self.get_translation("enable_notifications"))
        
        if hasattr(self, "show_tips_checkbox"):
            self.show_tips_checkbox.setText(self.get_translation("show_tips"))
        
        if hasattr(self, "maintenance_reminder_checkbox"):
            self.maintenance_reminder_checkbox.setText(self.get_translation("maintenance_reminder"))
        
        # 鏇存柊闅愮璁剧疆缁?
        privacy_group = self.findChild(QGroupBox, "privacy_group")
        if privacy_group:
            privacy_group.setTitle(self.get_translation("privacy"))
        
        # 鏇存柊闅愮璁剧疆澶嶉€夋
        if hasattr(self, "usage_stats_checkbox"):
            self.usage_stats_checkbox.setText(self.get_translation("collect_usage_statistics"))
        
        if hasattr(self, "auto_update_checkbox"):
            self.auto_update_checkbox.setText(self.get_translation("automatic_updates"))
        
        # 鏇存柊鍏朵粬璁剧疆缁?
        advanced_group = self.findChild(QGroupBox, "advanced_group")
        if advanced_group:
            advanced_group.setTitle(self.get_translation("advanced"))
            
        # 鏇存柊鏃ュ織绾у埆閫夐」
        log_level_label = self.findChild(QLabel, "log_level_label")
        if log_level_label:
            log_level_label.setText(self.get_translation("log_level") + ":")
        
        # 鏇存柊鎸夐挳
        if hasattr(self, "save_button"):
            self.save_button.setText(self.get_translation("save_settings"))
        
        if hasattr(self, "restore_defaults_button"):
            self.restore_defaults_button.setText(self.get_translation("restore_defaults"))
        
        # Refresh tab titles
        self.tabs.setTabText(0, self.get_translation("general", "General"))
        self.tabs.setTabText(1, self.get_translation("appearance", "Appearance"))
        self.tabs.setTabText(2, self.get_translation("scan_options", "Scan Options"))
        self.tabs.setTabText(3, self.get_translation("advanced", "Advanced"))
        
        # Update title and description
        title_label = self.findChild(QLabel, "title_label")
        if title_label:
            title_label.setText(self.get_translation("title"))
        
        desc_label = self.findChild(QLabel, "desc_label")
        if desc_label:
            desc_label.setText(self.get_translation("description"))
        
        # Update buttons
        self.save_button.setText(self.get_translation("save_settings"))
        self.restore_defaults_button.setText(self.get_translation("restore_defaults"))
        
        # General tab
        self.findChild(QGroupBox, "general_group").setTitle(self.get_translation("general_settings"))
        self.findChild(QLabel, "language_label").setText(self.get_translation("language_label", "Interface Language:"))
        
        self.findChild(QGroupBox, "general_group").setTitle(self.get_translation("general_settings"))
        self.findChild(QLabel, "startup_label").setText(self.get_translation("start_with_windows", "Start on boot"))
        self.findChild(QCheckBox, "startup_checkbox").setText(self.get_translation("auto_start", "Auto-start"))
        
        # Appearance tab
        self.findChild(QGroupBox, "theme_group").setTitle(self.get_translation("theme", "Theme"))
        self.theme_combo.clear()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        self.theme_combo.setCurrentText(self.settings.get_setting("theme", "dark"))
        
        # Update the default tab combo box items
        self.combo_default_tab.clear()
        self.combo_default_tab.addItems([
            self.settings.get_translation("general", "dashboard", "Dashboard"),
            self.settings.get_translation("general", "system_cleaner", "System Cleaner"),
            self.settings.get_translation("general", "gpu_information", "GPU Information"),
            self.settings.get_translation("general", "system_repair", "System Repair"),
            self.settings.get_translation("general", "dism_tool", "DISM Tool"),
            self.settings.get_translation("general", "network_reset", "Network Reset"),
            self.settings.get_translation("general", "disk_check", "Disk Check"),
            self.settings.get_translation("general", "boot_repair", "Boot Repair"),
            self.settings.get_translation("general", "virus_scan", "Virus Scan")
        ])
        
        # Update log level
        self.log_level_combo.clear()
        self.log_level_combo.addItems(["Error", "Warning", "Info", "Debug"])
        self.log_level_combo.setCurrentText(self.settings.get_setting("log_level", "Info"))
        
        # Update language
        self.language_combo.clear()
        self.language_combo.addItems(["English", "Chinese"])
        self.language_combo.setCurrentText(self.settings.get_setting("language", "English"))
        
        # Update notifications
        self.enable_notifications_checkbox.setChecked(self.settings.get_setting("enable_notifications", True))
        self.show_tips_checkbox.setChecked(self.settings.get_setting("show_tips", True))
        self.maintenance_reminder_checkbox.setChecked(self.settings.get_setting("maintenance_reminder", True))
        
        # Update privacy
        self.usage_stats_checkbox.setChecked(self.settings.get_setting("collect_usage_statistics", False))
        self.auto_update_checkbox.setChecked(self.settings.get_setting("automatic_updates", True))
        
        # Update theme
        self.theme_combo.clear()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        self.theme_combo.setCurrentText(self.settings.get_setting("theme", "dark"))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", False))
        
        self.check_disk_readonly.setChecked(self.settings.get_setting("disk_check_readonly", True))
        
        self.check_scan_archives.setChecked(self.settings.get_setting("scan_archives", True))
        self.check_scan_rootkits.setChecked(self.settings.get_setting("scan_rootkits", True))
        self.check_scan_autofix.setChecked(self.settings.get_setting("scan_autofix", False))
        self.slider_scan_level.setValue(self.settings.get_setting("scan_level", 2))
        
        # Update backup settings
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups")))
        
        # Update log settings
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # Update performance settings
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # Update scan settings
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", True))

