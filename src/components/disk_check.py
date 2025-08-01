import os
import subprocess
import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QCheckBox, QTextEdit, QGroupBox, QComboBox,
                            QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from components.base_component import BaseComponent
from tools.disk_check import DiskCheckThread

class DiskCheckWidget(BaseComponent):
    def __init__(self, parent=None):
        self.disk_worker = None
        super().__init__(parent)
    
    def get_translation(self, key, default=None):
        """Override get_translation to use the correct section name"""
        return self.settings.get_translation("disk_check", key, default)
    
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
        
        # Warning for non-Windows systems
        if not self.platform_manager.is_windows():
            warning_label = QLabel("⚠️ " + self.get_translation("windows_only", "disk check features are only available on Windows"))
            warning_label.setStyleSheet("color: #ff9900; font-weight: bold;")
            self.main_layout.addWidget(warning_label)
        
        # Drive selection
        self.drive_group = QGroupBox(self.get_translation("select_drive"))
        self.drive_group.setStyleSheet("""
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
        drive_layout = QVBoxLayout(self.drive_group)
        
        # Drive dropdown
        self.drive_combo = QComboBox()
        self.drive_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: none;
                selection-background-color: #3a3a3a;
            }
        """)
        drive_layout.addWidget(self.drive_combo)
        
        self.main_layout.addWidget(self.drive_group)
        
        # Check types
        self.check_group = QGroupBox(self.get_translation("check_types"))
        self.check_group.setStyleSheet("""
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
        check_layout = QVBoxLayout(self.check_group)
        
        # Checkboxes for check types
        self.file_system_cb = QCheckBox(self.get_translation("file_system"))
        self.file_system_cb.setChecked(True)
        self.file_system_cb.setObjectName("disk_check_file_system")
        self.file_system_cb.setStyleSheet("color: #e0e0e0;")
        self.file_system_cb.stateChanged.connect(lambda state: self.on_checkbox_changed("disk_check_file_system", state))
        check_layout.addWidget(self.file_system_cb)
        
        self.bad_sectors_cb = QCheckBox(self.get_translation("bad_sectors"))
        self.bad_sectors_cb.setChecked(False)
        self.bad_sectors_cb.setObjectName("disk_check_bad_sectors")
        self.bad_sectors_cb.setStyleSheet("color: #e0e0e0;")
        self.bad_sectors_cb.stateChanged.connect(lambda state: self.on_checkbox_changed("disk_check_bad_sectors", state))
        check_layout.addWidget(self.bad_sectors_cb)
        
        # Read-only mode checkbox
        self.read_only_cb = QCheckBox(self.get_translation("read_only"))
        self.read_only_cb.setChecked(self.settings.get_setting("disk_check_readonly", True))
        self.read_only_cb.setObjectName("disk_check_readonly")
        self.read_only_cb.setStyleSheet("color: #e0e0e0;")
        self.read_only_cb.stateChanged.connect(lambda state: self.on_checkbox_changed("disk_check_readonly", state))
        check_layout.addWidget(self.read_only_cb)
        
        self.main_layout.addWidget(self.check_group)
        
        # Warning label
        self.warning_label = QLabel(self.get_translation("warning"))
        self.warning_label.setStyleSheet("color: #ff9900; font-weight: bold;")
        self.main_layout.addWidget(self.warning_label)
        
        # Buttons
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        # Check button
        self.check_button = QPushButton(self.get_translation("check_button"))
        self.check_button.setStyleSheet("""
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
        self.check_button.clicked.connect(self.check_disk)
        self.check_button.setEnabled(self.platform_manager.is_windows())
        buttons_layout.addWidget(self.check_button)
        
        # Repair button
        self.repair_button = QPushButton(self.get_translation("repair_button"))
        self.repair_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5555;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff3333;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.repair_button.clicked.connect(self.repair_disk)
        self.repair_button.setEnabled(self.platform_manager.is_windows())
        buttons_layout.addWidget(self.repair_button)
        
        self.main_layout.addWidget(buttons_container)
        
        # Log output
        self.log_label = QLabel(self.get_translation("log_output"))
        self.log_label.setStyleSheet("color: #a0a0a0; margin-top: 10px;")
        self.main_layout.addWidget(self.log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        self.main_layout.addWidget(self.log_output)
        
        # Set a minimum size for the log
        self.log_output.setMinimumHeight(200)
        
        # Initial status information
        self.log_output.append(self.get_translation("ready_message", "Disk check tool is ready. Please select a drive and check options, then click the check button."))
        
        # Populate drive list after all UI elements are initialized
        if self.platform_manager.is_windows():
            self.populate_drives()

        # Apply theme after UI is fully built
        self.apply_theme()
    
    def populate_drives(self):
        """Populate drive dropdown list"""
        # Ensure log_output is initialized
        if not hasattr(self, 'log_output') or self.log_output is None:
            self.logger.warning("Warning: log_output not yet initialized")
            return
        
        try:
            # Get available drives
            drives = self.system_information.get_drives()
            
            if drives:
                for drive in drives:
                    if drive.get("accessible", False):
                        # Add accessible drives
                        display_name = drive.get("display_name")
                        name = drive.get("name")
                        self.drive_combo.addItem(display_name, name)
                        
                        # Log
                        drive_type = drive.get("type", "Unknown")
                        self.log_output.append(f"Found drive: {name} - Type: {drive_type}")
                    else:
                        # Log inaccessible drives
                        self.log_output.append(f"Skipping inaccessible drive: {drive.get('name')}")
                
                # Default to first drive
                if self.drive_combo.count() > 0:
                    self.drive_combo.setCurrentIndex(0)
                    
                # On Windows, try to select C: as default drive (if available)
                if self.platform_manager.is_windows():
                    c_drive_index = -1
                    for i in range(self.drive_combo.count()):
                        if self.drive_combo.itemData(i) == "C:":
                            c_drive_index = i
                            break
                            
                    if c_drive_index >= 0:
                        self.drive_combo.setCurrentIndex(c_drive_index)
            else:
                self.log_output.append("No available drives found")
                # Disable check buttons
                self.check_button.setEnabled(False)
                self.repair_button.setEnabled(False)
                
        except Exception as e:
            self.log_output.append(f"Error populating drive list: {str(e)}")
            self.logger.error(f"Error populating drive list: {str(e)}")
    
    def check_disk(self):
        """Check disk errors"""
        # Get selected drive
        drive = self.drive_combo.currentText()
        
        # Validate drive
        if not drive:
            self.log_output.append("Please select a drive")
            return
        
        # Additional validation: ensure drive exists and is accessible
        if not os.path.exists(drive):
            self.log_output.append(f"Drive {drive} does not exist or is not accessible")
            return
        
        # Check drive type (Windows only)
        if self.platform_manager.is_windows():
            from ctypes import windll
            drive_type = windll.kernel32.GetDriveTypeW(f"{drive}\\")
            # Type 2 is removable drive, type 5 is CD-ROM
            if drive_type in [2, 5]:
                self.log_output.append(f"Warning: {drive} is a removable drive or CD-ROM, may not be checked correctly")
            # Type 0 or 1 is unknown or invalid drive
            elif drive_type in [0, 1]:
                self.log_output.append(f"Error: {drive} is an invalid drive")
                return
        
        # Get check types
        check_file_system = self.file_system_cb.isChecked()
        check_bad_sectors = self.bad_sectors_cb.isChecked()
        read_only = self.read_only_cb.isChecked()
        
        if not check_file_system and not check_bad_sectors:
            self.log_output.append("Please select at least one check type")
            return
        
        # Clear log and disable buttons
        self.log_output.clear()
        self.check_button.setEnabled(False)
        self.repair_button.setEnabled(False)
        
        self.log_output.append(f"Starting disk check for drive {drive}...")
        
        # Start worker thread
        self.disk_worker = DiskCheckThread(drive, check_file_system, check_bad_sectors, read_only, "check")
        self.disk_worker.progress_updated.connect(self.update_log)
        self.disk_worker.operation_completed.connect(self.operation_completed)
        self.disk_worker.start()
    
    def repair_disk(self):
        """Repair disk errors"""
        # Get selected drive
        drive = self.drive_combo.currentText()
        
        if not drive:
            self.log_output.append("Please select a drive")
            return
        
        # Get check types
        check_file_system = self.file_system_cb.isChecked()
        check_bad_sectors = self.bad_sectors_cb.isChecked()
        read_only = self.read_only_cb.isChecked()
        
        if not check_file_system and not check_bad_sectors:
            self.log_output.append("Please select at least one check type")
            return
        
        # Clear log and disable buttons
        self.log_output.clear()
        self.check_button.setEnabled(False)
        self.repair_button.setEnabled(False)
        
        if read_only:
            self.log_output.append(f"Read-only mode is enabled. Running in check-only mode for drive {drive}...")
        else:
            self.log_output.append(f"Starting disk repair for drive {drive}...")
        
        # Start worker thread
        self.disk_worker = DiskCheckThread(drive, check_file_system, check_bad_sectors, read_only, "repair")
        self.disk_worker.progress_updated.connect(self.update_log)
        self.disk_worker.operation_completed.connect(self.operation_completed)
        self.disk_worker.start()
    
    def update_log(self, message):
        """Update the log output"""
        # Translate Chinese log messages if current UI language is not Chinese
        current_lang = self.settings.get_setting("language", "en")
        lang_code = ("zh" if str(current_lang).lower() in ["zh", "中文", "chinese"] else "en")

        translated = message
        if lang_code != "zh":
            mapping = {
                "开始对驱动器": self.get_translation("starting_check", "Starting disk check for"),
                "开始对驱动器": self.get_translation("starting_repair", "Starting disk repair for"),
                "未找到可用驱动器": self.get_translation("no_drives", "No available drives found"),
                "跳过不可访问的驱动器": self.get_translation("skip_inaccessible", "Skip inaccessible drive"),
                "发现驱动器": self.get_translation("found_drive", "Found drive"),
                "开始操作": self.get_translation("starting_operation", "Starting operation"),
            }
            for cn, en in mapping.items():
                if message.startswith(cn):
                    translated = message.replace(cn, en)
                    break

        self.log_output.append(translated)
        # Scroll to bottom
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def operation_completed(self, success):
        """Handle operation completion"""
        # Re-enable buttons
        self.check_button.setEnabled(True)
        self.repair_button.setEnabled(True)
        
        # Add completion message to log
        if success:
            self.log_output.append("✅ Operation completed")
        else:
            self.log_output.append("❌ Operation failed")
    
    def refresh_language(self):
        """Update all UI elements with new translations when language changes"""
        # Update all text elements
        self.title.setText(self.get_translation("title"))
        self.description.setText(self.get_translation("description"))
        self.drive_group.setTitle(self.get_translation("select_drive"))
        self.check_group.setTitle(self.get_translation("check_types"))
        self.file_system_cb.setText(self.get_translation("file_system"))
        self.bad_sectors_cb.setText(self.get_translation("bad_sectors"))
        self.read_only_cb.setText(self.get_translation("read_only"))
        self.warning_label.setText(self.get_translation("warning"))
        self.check_button.setText(self.get_translation("check_button"))
        self.repair_button.setText(self.get_translation("repair_button"))
        self.log_label.setText(self.get_translation("log_output"))
        
        # Animate to show that language has changed
        self._animate_refresh()
    
    def check_all_translations(self):
        """Check if all translation keys used in this component exist
        
        Raises:
            KeyError: If any translation key is missing
        """
        # Try to get all translations used in this component
        keys = [
            "title", "description", "select_drive", "check_types",
            "file_system", "bad_sectors", "read_only", "warning",
            "check_button", "repair_button", "log_output", "windows_only", "ready_message"
        ]
        
        for key in keys:
            # This will raise KeyError if the key doesn't exist
            self.get_translation(key, None)

    def on_checkbox_changed(self, checkbox_name, state):
        """Handle checkbox state change"""
        checked = state == Qt.Checked
        self.logger.info(f"Disk check setting: {checkbox_name} = {checked}")
        
        # Save settings
        self.settings.set_setting(checkbox_name, checked)
        self.settings.sync()
        
        # Update UI state
        if checkbox_name == "disk_check_file_system":
            self.file_system_cb.setChecked(checked)
        elif checkbox_name == "disk_check_bad_sectors":
            self.bad_sectors_cb.setChecked(checked)
        elif checkbox_name == "disk_check_readonly":
            self.read_only_cb.setChecked(checked)
        else:
            self.logger.warning(f"Unknown checkbox: {checkbox_name}") 

    def apply_theme(self):
        """Apply theme colors dynamically."""
        try:
            # Skip if UI not ready (called from BaseComponent before setup_ui)
            if not hasattr(self, "drive_group") or not hasattr(self, "drive_combo"):
                return

            super().apply_theme()

            colors = self.theme_manager.get_theme_colors()
            bg_color = colors.get("bg_color", "#1e1e1e")
            text_color = colors.get("text_color", "#e0e0e0")
            accent_color = colors.get("accent_color", "#00a8ff")
            bg_lighter = colors.get("bg_lighter", self.theme_manager.lighten_color(bg_color, 10))
            bg_darker = colors.get("bg_darker", self.theme_manager.lighten_color(bg_color, -10))

            # Group box style
            groupbox_style = f"""
                QGroupBox {{
                    color: {text_color};
                    font-weight: bold;
                    border: 1px solid {accent_color};
                    border-radius: 4px;
                    margin-top: 1em;
                    padding-top: 10px;
                    background-color: {bg_color};
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                    background-color: {bg_color};
                }}
            """
            self.drive_group.setStyleSheet(groupbox_style)
            self.check_group.setStyleSheet(groupbox_style)

            # Combo style
            self.drive_combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: {bg_lighter};
                    color: {text_color};
                    border: 1px solid {accent_color};
                    border-radius: 4px;
                    padding: 5px;
                    min-height: 25px;
                }}
                QComboBox::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 25px;
                    border-left: none;
                }}
                QComboBox QAbstractItemView {{
                    background-color: {bg_lighter};
                    color: {text_color};
                    border: none;
                    selection-background-color: {self.theme_manager.lighten_color(bg_lighter, 10)};
                }}
            """)

            # TextEdit log
            self.log_output.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {bg_darker};
                    color: {text_color};
                    border: 1px solid {accent_color};
                    border-radius: 4px;
                    padding: 5px;
                }}
            """)

            # Progress bar style etc handled by base stylesheet
        except Exception as e:
            self.logger.error(f"Error applying theme in DiskCheckWidget: {e}") 