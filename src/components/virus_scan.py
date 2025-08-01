import os
import sys
import platform
import subprocess
import time
import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QProgressBar, QMessageBox,
                             QGroupBox, QCheckBox, QFileDialog, QListWidget,
                             QListWidgetItem, QRadioButton, QComboBox, QTableWidget,
                             QHeaderView, QTableWidgetItem, QTextBrowser, QTabWidget,
                             QLineEdit, QButtonGroup)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QDir, QDateTime
from PyQt5.QtWidgets import QApplication
from src.components.base_component import BaseComponent
from src.tools.virus_scan import VirusScanThread

class VirusScanWidget(BaseComponent):
    """Widget for virus scanning operations"""
    def __init__(self, parent=None):
        # Initialize attributes
        self.scanner_worker = None
        self.scan_thread = None
        self.custom_scan_targets = []
        self.detected_threats = []
        self.main_window = parent
        
        # Call parent constructor
        super().__init__(parent)
        
        # Set up the UI (called by parent but we need to ensure it exists)
        if not hasattr(self, 'quick_scan_rb'):
            self.setup_ui()
        
    def get_translation(self, key, default=None):
        """Return translated text from the correct section (virus_scan)."""
        return self.settings.get_translation("virus_scan", key, default)

    def setup_ui(self):
        """Setup UI elements"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        # Consistent margins and spacing with other pages
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Add title
        self.title_label = QLabel(self.get_translation("title"))
        self.title_label.setObjectName("title_label")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0; background-color: transparent;")
        self.main_layout.addWidget(self.title_label)
        
        # Description
        self.desc_label = QLabel(self.get_translation("scan_description"))
        self.desc_label.setObjectName("desc_label")
        self.desc_label.setStyleSheet("font-size: 14px;")
        self.desc_label.setWordWrap(True)
        self.main_layout.addWidget(self.desc_label)

        # Create tab widget
        self.tabs = QTabWidget()
        
        # Scan tab
        self.scan_tab = QWidget()
        self.setup_scan_tab(self.scan_tab)
        self.tabs.addTab(self.scan_tab, self.get_translation("scan_tab", "Scan"))
        
        # Quarantine tab
        self.quarantine_tab = QWidget()
        self.setup_quarantine_tab(self.quarantine_tab)
        self.tabs.addTab(self.quarantine_tab, self.get_translation("quarantine_tab", "Quarantine"))
        
        # Add to main layout
        self.main_layout.addWidget(self.tabs)
        
    
    def apply_theme(self):
        """Apply theme styles to component"""
        # Call parent class apply theme method, use unified style
        super().apply_theme()
        
        # Get current theme
        theme_name = self.settings.get_setting("theme", "dark")
        theme_data = self.settings.load_theme(theme_name)
        
        if theme_data and "colors" in theme_data:
            bg_color = theme_data["colors"].get("bg_color", "#2d2d2d")
            text_color = theme_data["colors"].get("text_color", "#dcdcdc")
            accent_color = theme_data["colors"].get("accent_color", "#007acc")
            border_color = theme_data["colors"].get("border_color", "#444444")
            table_bg_color = theme_data["colors"].get("table_bg_color", self.lighten_color(bg_color, -5))
            header_bg_color = theme_data["colors"].get("header_bg_color", self.lighten_color(bg_color, 10))
            disabled_bg_color = theme_data["colors"].get("disabled_bg_color", self.lighten_color(bg_color, -10))
            disabled_text_color = theme_data["colors"].get("disabled_text_color", self.lighten_color(text_color, -30))
            button_bg_color = theme_data["colors"].get("button_bg_color", self.lighten_color(bg_color, 10))
            button_hover_bg_color = theme_data["colors"].get("button_hover_bg_color", self.lighten_color(bg_color, 15))
            button_pressed_bg_color = theme_data["colors"].get("button_pressed_bg_color", self.lighten_color(bg_color, 5))
            input_bg_color = theme_data["colors"].get("input_bg_color", self.lighten_color(bg_color, -5))

            # Get icon path for check icon
            from src.config import Icon
            check_icon_path = Icon.get_path("resources/icons/check.svg")

            # Update component styles - more comprehensive style coverage
            self.setStyleSheet(f"""
                QWidget {{ background-color: transparent; color: {text_color}; }}
                QTabWidget::pane {{ border: 1px solid {border_color}; border-radius: 4px; background-color: {bg_color}; }}
                QTabBar::tab {{ background-color: {header_bg_color}; color: {text_color}; padding: 8px 16px; border-top-left-radius: 4px; border-top-right-radius: 4px; }}
                QTabBar::tab:selected {{ background-color: {bg_color}; border-bottom: none; }}
                QGroupBox {{ background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 4px; margin-top: 1em; padding-top: 10px; }}
                QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {text_color}; }}
                QTextEdit, QTextBrowser {{ background-color: {table_bg_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 4px; }}
                QTableWidget {{ background-color: {table_bg_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 4px; gridline-color: {border_color}; selection-background-color: {accent_color}40; }}
                QTableWidget::item {{ padding: 4px; color: {text_color}; }}
                QTableWidget::item:selected {{ background-color: {accent_color}80; color: #ffffff; }}
                QHeaderView::section {{ background-color: {header_bg_color}; color: {text_color}; padding: 4px; border: 1px solid {border_color}; }}
                QProgressBar {{ border: 1px solid {border_color}; border-radius: 4px; background-color: {table_bg_color}; text-align: center; color: {text_color}; }}
                QProgressBar::chunk {{ background-color: {accent_color}; width: 10px; border-radius: 3px; margin: 1px; }}
                QPushButton {{ background-color: {button_bg_color}; color: {text_color}; border: 1px solid #555; border-radius: 4px; padding: 6px 12px; }}
                QPushButton:hover {{ background-color: {button_hover_bg_color}; }}
                QPushButton:pressed {{ background-color: {button_pressed_bg_color}; }}
                QPushButton:disabled {{ background-color: {disabled_bg_color}; color: {disabled_text_color}; }}
                QComboBox, QLineEdit {{ background-color: {input_bg_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 4px; padding: 4px; }}
                
                QCheckBox, QRadioButton {{ color: {text_color}; background-color: transparent; spacing: 5px; }}
                
                QCheckBox::indicator {{ width: 16px; height: 16px; border: 2px solid {accent_color}; border-radius: 3px; background-color: {bg_color}; }}
                QCheckBox::indicator:unchecked {{ background-color: {bg_color}; }}
                QCheckBox::indicator:checked {{ 
                    background-color: {accent_color}; 
                    border: 2px solid {accent_color};
                                            image: url("{check_icon_path}");
                }}
                QCheckBox::indicator:unchecked:hover {{ border-color: {self.lighten_color(accent_color, 20)}; background-color: {self.lighten_color(bg_color, 10)}; }}
                QCheckBox::indicator:checked:hover {{ background-color: {self.lighten_color(accent_color, 10)}; }}
                
                QRadioButton::indicator {{ width: 16px; height: 16px; border: 2px solid {accent_color}; border-radius: 9px; background-color: {bg_color}; }}
                QRadioButton::indicator:unchecked {{ background-color: {bg_color}; }}
                QRadioButton::indicator:checked {{ background-color: {bg_color}; border: 4px solid {accent_color}; }}
                QRadioButton::indicator:unchecked:hover {{ border-color: {self.lighten_color(accent_color, 20)}; background-color: {self.lighten_color(bg_color, 10)}; }}
                QRadioButton::indicator:checked:hover {{ border-color: {self.lighten_color(accent_color, 10)}; }}
                
                QLabel {{ color: {text_color}; background-color: transparent; }}
                
                QComboBox::drop-down {{ 
                    subcontrol-origin: padding; 
                    subcontrol-position: center right; 
                    width: 20px; 
                    border-left: 1px solid {border_color}; 
                }}
            """)
        
            if hasattr(self, 'clean_button'):
                self.clean_button.setStyleSheet(f"""
                    QPushButton {{ 
                        background-color: {button_bg_color}; 
                        color: {text_color}; 
                        border: 1px solid #555; 
                        border-radius: 4px; 
                        padding: 6px 12px; 
                        padding-left: 30px; 
                        text-align: left;
                    }}
                    QPushButton:hover {{ background-color: {button_hover_bg_color}; }}
                    QPushButton:pressed {{ background-color: {button_pressed_bg_color}; }}
                    QPushButton:disabled {{ background-color: {disabled_bg_color}; color: {disabled_text_color}; }}
                """)
            
            if hasattr(self, 'scan_button'):
                self.scan_button.setStyleSheet(f"""
                    QPushButton {{ 
                        background-color: {accent_color}; 
                        color: white; 
                        border: 1px solid {self.lighten_color(accent_color, -10)}; 
                        border-radius: 4px; 
                        padding: 6px 12px; 
                        padding-left: 30px;
                        text-align: left;
                    }}
                    QPushButton:hover {{ background-color: {self.lighten_color(accent_color, 10)}; }}
                    QPushButton:pressed {{ background-color: {self.lighten_color(accent_color, -10)}; }}
                    QPushButton:disabled {{ background-color: {disabled_bg_color}; color: {disabled_text_color}; }}
                """)
                
            # Apply alternating row colors specifically for the table
            try:
                if self.result_table:
                    self.result_table.setAlternatingRowColors(True)
                    self.result_table.setStyleSheet(f"QTableWidget {{ alternate-background-color: {self.lighten_color(table_bg_color, 5)}; background-color: {table_bg_color}; color: {text_color}; border: 1px solid {border_color}; gridline-color: {border_color};}} QTableWidget::item {{ padding: 4px; color: {text_color}; }} QTableWidget::item:selected {{ background-color: {accent_color}80; color: #ffffff; }}")
            except AttributeError:
                pass
                
            try:
                if self.quarantined_list:
                    self.quarantined_list.setAlternatingRowColors(True)
                    self.quarantined_list.setStyleSheet(f"QTableWidget {{ alternate-background-color: {self.lighten_color(table_bg_color, 5)}; background-color: {table_bg_color}; color: {text_color}; border: 1px solid {border_color}; gridline-color: {border_color};}} QTableWidget::item {{ padding: 4px; color: {text_color}; }} QTableWidget::item:selected {{ background-color: {accent_color}80; color: #ffffff; }}")
            except AttributeError:
                pass
        
    def apply_current_theme(self):
        """Apply current theme colors - this method is called by MainWindow's refresh_component_theme"""
        try:
            # Call specific theme application method
            self.apply_theme()
        except Exception as e:
            self.logger.error(f"Error applying current theme in VirusScanWidget: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
    def lighten_color(self, color, amount=0):
        """Lighten or darken color
        
        Args:
            color: Hex color code
            amount: Change amount, positive number lightens, negative number darkens
            
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
        
    def setup_scan_tab(self, tab):
        """Setup scan tab UI"""
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Scan options group
        scan_options_group = QGroupBox(self.get_translation("scan_options", "Scan Options"))
        options_layout = QVBoxLayout(scan_options_group)
        
        # Create scan type button group
        # Do not use QButtonGroup, let checkboxes work independently
        
        # Quick scan option
        self.quick_scan_rb = QCheckBox(self.get_translation("quick_scan", "Quick Scan"))
        self.quick_scan_rb.setChecked(True)
        self.quick_scan_rb.setObjectName("virus_scan_quick")
        self.quick_scan_rb.clicked.connect(lambda: self.on_scan_option_clicked(self.quick_scan_rb))
        options_layout.addWidget(self.quick_scan_rb)
        
        # Full scan option
        self.full_scan_rb = QCheckBox(self.get_translation("full_scan", "Full Scan"))
        self.full_scan_rb.setObjectName("virus_scan_full")
        self.full_scan_rb.clicked.connect(lambda: self.on_scan_option_clicked(self.full_scan_rb))
        options_layout.addWidget(self.full_scan_rb)
        
        # Custom scan option
        self.custom_scan_rb = QCheckBox(self.get_translation("custom_scan", "Custom Scan"))
        self.custom_scan_rb.setObjectName("virus_scan_custom")
        self.custom_scan_rb.clicked.connect(lambda: self.on_scan_option_clicked(self.custom_scan_rb))
        options_layout.addWidget(self.custom_scan_rb)
        
        # Custom scan path selection
        custom_scan_layout = QHBoxLayout()
        self.custom_path_edit = QLineEdit()
        self.custom_path_edit.setPlaceholderText(self.get_translation("select_path", "Select directory or file to scan"))
        self.custom_path_edit.setEnabled(False)
        custom_scan_layout.addWidget(self.custom_path_edit)
        
        self.browse_button = QPushButton(self.get_translation("browse", "Browse..."))
        self.browse_button.setEnabled(False)
        self.browse_button.clicked.connect(self.browse_path)
        custom_scan_layout.addWidget(self.browse_button)
        
        options_layout.addLayout(custom_scan_layout)
        layout.addWidget(scan_options_group)
        
        # Scan and stop buttons
        button_layout = QHBoxLayout()
        
        self.scan_button = QPushButton(self.get_translation("start_scan", "Start Scan"))
        self.scan_button.clicked.connect(self.start_scan)
        button_layout.addWidget(self.scan_button)
        
        self.stop_button = QPushButton(self.get_translation("stop_scan", "Stop Scan"))
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        # Result list
        result_group = QGroupBox(self.get_translation("scan_results", "Scan Results"))
        result_layout = QVBoxLayout(result_group)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels([
            self.get_translation("file", "File"),
            self.get_translation("location", "Location"),
            self.get_translation("threat", "Threat"),
            self.get_translation("status", "Status")
        ])
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setAlternatingRowColors(True)
        result_layout.addWidget(self.result_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.clean_button = QPushButton(self.get_translation("clean_all", "Clean All"))
        self.clean_button.clicked.connect(self.clean_threats)
        self.clean_button.setEnabled(False)
        action_layout.addWidget(self.clean_button)
        
        self.quarantine_button = QPushButton(self.get_translation("quarantine", "Quarantine Selected"))
        self.quarantine_button.clicked.connect(self.quarantine_selected)
        self.quarantine_button.setEnabled(False)
        action_layout.addWidget(self.quarantine_button)
        
        result_layout.addLayout(action_layout)
        layout.addWidget(result_group)
        
        # Statistics
        self.stats_label = QLabel(self.get_translation("scan_stats", "Scan Statistics: Scanned 0 files, Found 0 threats"))
        layout.addWidget(self.stats_label)
        
    def setup_quarantine_tab(self, tab):
        """Setup quarantine tab"""
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Quarantine description
        description = QLabel(self.get_translation("quarantine_description", 
            "Files in quarantine have been detected as potential threats and isolated. You can delete these files or choose to restore them."))
        description.setWordWrap(True)
        description.setStyleSheet("color: #a0a0a0;")
        layout.addWidget(description)
        
        # Quarantine file list
        self.quarantined_list = QTableWidget()
        self.quarantined_list.setColumnCount(3)
        self.quarantined_list.setHorizontalHeaderLabels([
            self.get_translation("file_name", "File Name"),
            self.get_translation("threat_type", "Threat Type"),
            self.get_translation("date", "Date")
        ])
        self.quarantined_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.quarantined_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.quarantined_list.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout.addWidget(self.quarantined_list)
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Restore button
        self.restore_button = QPushButton(self.get_translation("restore", "Restore"))
        self.restore_button.setEnabled(False)
        button_layout.addWidget(self.restore_button)
        
        # Delete button
        self.delete_button = QPushButton(self.get_translation("delete", "Delete"))
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        layout.addWidget(button_container)

    def refresh_language(self):
        """Refresh all UI elements with current language translations"""
        # Find title and description labels
        title_label = self.findChild(QLabel, "title_label")
        if title_label:
            title_label.setText(self.get_translation("title"))
            
        desc_label = self.findChild(QLabel, "desc_label")
        if desc_label:
            desc_label.setText(self.get_translation("scan_description"))
        
        # Update scan options
        scan_options_group = self.findChild(QGroupBox, "scan_options_group")
        if scan_options_group:
            scan_options_group.setTitle(self.get_translation("scan_types"))
        
        # Update progress group
        progress_group = self.findChild(QGroupBox, "progress_group")
        if progress_group:
            progress_group.setTitle(self.get_translation("progress", "Scan Progress"))
        
        # Update threats group
        threats_group = self.findChild(QGroupBox, "threats_group")
        if threats_group:
            threats_group.setTitle(self.get_translation("threats_found", "Detected Threats"))
        
        # Update log group
        log_group = self.findChild(QGroupBox, "log_group")
        if log_group:
            log_group.setTitle(self.get_translation("log_output", "Scan Log"))

    def clear_log(self):
        """Clear log output"""
        self.log_text.clear()
        self.log_text.append(self.get_translation("ready_message", "Virus scan ready. Select scan type and click 'Start Scan'."))
        
    def start_scan(self):
        """Start the virus scan process"""
        # Determine scan type - choose the first selected option
        scan_type = "quick"  # Default to quick scan
        
        if self.custom_scan_rb.isChecked():
            scan_type = "custom"
            if not self.custom_scan_targets:
                QMessageBox.warning(self, 
                                  self.get_translation("no_targets", "No targets selected"), 
                                  self.get_translation("select_targets_msg", "Please select at least one file or folder to scan."))
                return
        elif self.full_scan_rb.isChecked():
            scan_type = "full"
        elif self.quick_scan_rb.isChecked():
            scan_type = "quick"
        else:
            # If nothing is selected, default to quick scan
            self.quick_scan_rb.setChecked(True)
        
        # Collect scan options
        scan_options = {
            'scan_type': scan_type,
            'scan_targets': self.custom_scan_targets.copy() if scan_type == "custom" else [],
            'options': {
                'archives': False,
                'rootkits': False,
                'autofix': False
            }
        }
        
        # Confirmation dialog
        reply = QMessageBox.question(self, 
                                   self.get_translation("start_scan_confirm", "Start Virus Scan"), 
                                   self.get_translation("start_scan_msg", "Start {scan_type} scan now?"),
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:
            # Clear previous results
            self.result_table.setRowCount(0)
            self.detected_threats = []
            self.clean_button.setEnabled(False)
            self.quarantine_button.setEnabled(False)
            
            # Reset progress bar
            self.progress.setValue(0)
            
            # Check if animations are enabled
            if self.settings.get_setting("enable_animations", True):
                # Add scan animation effect
                self.progress.setStyleSheet("QProgressBar {border: 1px solid grey; border-radius: 2px; text-align: center;} "
                                          "QProgressBar::chunk {background-color: #4CAF50; width: 20px;}")
            else:
                # Do not use animation effect, use simple style
                self.progress.setStyleSheet("QProgressBar {border: 1px solid grey; border-radius: 2px; text-align: center;} "
                                          "QProgressBar::chunk {background-color: #4CAF50;}")
            
            # Create and start thread
            self.scan_thread = VirusScanThread(scan_options)
            self.scan_thread.update_progress.connect(self.update_progress)
            self.scan_thread.update_log.connect(self.add_log)
            self.scan_thread.found_threat.connect(self.add_threat)
            self.scan_thread.finished_scan.connect(self.scan_finished)
            self.scan_thread.start()
            
            # Update UI
            self.scan_button.setEnabled(False)
            self.stop_button.setEnabled(True)

    def stop_scan(self):
        """Stop the virus scan process"""
        if self.scan_thread and self.scan_thread.is_running:
            reply = QMessageBox.question(self, 'Stop Scan', 
                                       "Are you sure you want to stop the scan?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.scan_thread.stop()
                self.update_log("Stopping scan, please wait...")
    
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress.setValue(value)
        
    def update_log(self, message):
        """Update log output"""
        # Format log message, add timestamp
        timestamp = QDateTime.currentDateTime().toString('hh:mm:ss')
        formatted_message = f"[{timestamp}] {message}"
        
        # Set different colors based on message type
        if "完成" in message or "成功" in message or "✓" in message:
            # Success message uses green
            formatted_message = f"<span style='color:#4CAF50;'>{formatted_message}</span>"
        elif "警告" in message or "注意" in message:
            # Warning message uses yellow
            formatted_message = f"<span style='color:#FFC107;'>{formatted_message}</span>"
        elif "错误" in message or "失败" in message or "✗" in message or "威胁" in message:
            # Error or threat message uses red
            formatted_message = f"<span style='color:#F44336;'>{formatted_message}</span>"
        elif "扫描" in message and "文件" in message:
            # Scan file message uses gray, reduce visual interference
            formatted_message = f"<span style='color:#9E9E9E;'>{formatted_message}</span>"
        
        self.log_text.append(formatted_message)
        
        # Scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        
        # Update UI immediately, avoid freezing during long operations
        QApplication.processEvents() 
    
    def add_log(self, message):
        """Add log message"""
        # Temporary implementation, display message on status label
        self.stats_label.setText(message)
        self.logger.info(f"[Virus Scan] {message}")

    def add_threat(self, file_path: str, threat_type: str) -> None:
        """Add detected threat to result table"""
        row = self.result_table.rowCount()
        self.result_table.insertRow(row)
        
        # File name
        filename = os.path.basename(file_path)
        self.result_table.setItem(row, 0, QTableWidgetItem(filename))
        
        # File location (directory)
        location = os.path.dirname(file_path)
        self.result_table.setItem(row, 1, QTableWidgetItem(location))
        
        # Threat type
        self.result_table.setItem(row, 2, QTableWidgetItem(threat_type))
        
        # Status
        self.result_table.setItem(row, 3, QTableWidgetItem(self.get_translation("detected", "已检测")))
        
        # Store complete threat information
        self.detected_threats.append({
            'path': file_path,
            'type': threat_type
        })
        
        # Enable clean and quarantine buttons
        self.clean_button.setEnabled(True)
        self.quarantine_button.setEnabled(True)
        
        # Update statistics
        self.update_stats()
    
    def update_stats(self):
        """Update scan statistics"""
        files_scanned = random.randint(100, 1000)  # Simulate file scan count
        threats_found = len(self.detected_threats)
        
        stats_text = self.get_translation(
            "scan_stats", 
            "Scan Statistics: Scanned {files} files, Found {threats} threats"
        ).format(files=files_scanned, threats=threats_found)
        
        self.stats_label.setText(stats_text)
    
    def scan_finished(self, success, message, threats_found):
        """Handle scan completion event"""
        # Re-enable scan button
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Set progress to 100%
        self.progress.setValue(100)
        
        # Display completion message
        if success:
            if threats_found > 0:
                QMessageBox.warning(
                    self, 
                    self.get_translation("scan_complete", "扫描完成"), 
                    self.get_translation("threats_found_msg", f"{message}\n\n发现 {threats_found} 个潜在威胁。")
                )
            else:
                QMessageBox.information(
                    self, 
                    self.get_translation("scan_complete", "扫描完成"), 
                    self.get_translation("no_threats_msg", f"{message}\n\n未检测到威胁。")
                )
        else:
            QMessageBox.warning(
                self, 
                self.get_translation("scan_incomplete", "扫描未完成"), 
                message
            )
        
        # Add final log message
        result = self.get_translation("success", "Success") if success else self.get_translation("incomplete", "Incomplete")
        self.add_log(f"{self.get_translation('scan_completed', 'Scan completed')}. {self.get_translation('result', 'Result')}: {result}")
        self.add_log(f"{self.get_translation('total_threats', 'Total threats found')}: {threats_found}")
        
        # If threats found, enable clean button
        self.clean_button.setEnabled(threats_found > 0)
        self.quarantine_button.setEnabled(threats_found > 0)

    def browse_path(self):
        """Browse and select file or directory to scan"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        
        if file_dialog.exec_():
            selected_paths = file_dialog.selectedFiles()
            if selected_paths:
                # Set custom path to edit box
                self.custom_path_edit.setText(selected_paths[0])
                # Add to scan target list
                if selected_paths[0] not in self.custom_scan_targets:
                    self.custom_scan_targets.append(selected_paths[0])

    def toggle_custom_scan(self, checked):
        """Toggle availability of related controls based on custom scan option selection state"""
        self.custom_path_edit.setEnabled(checked)
        self.browse_button.setEnabled(checked)
        
        # If unchecked, clear custom scan targets
        if not checked:
            self.custom_scan_targets = []
            self.custom_path_edit.clear()

    def clean_threats(self):
        """Clear detected threats"""
        reply = QMessageBox.question(self, 
                                    self.get_translation("confirm_clean", "Confirm Clean"), 
                                    self.get_translation("confirm_clean_msg", "Are you sure you want to clear all detected threats?"), 
                                    QMessageBox.Yes | QMessageBox.No, 
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            row_count = self.result_table.rowCount()
            for row in range(row_count):
                self.result_table.item(row, 2).setText(self.get_translation("cleaned", "Cleaned"))
            
            QMessageBox.information(self, 
                                   self.get_translation("clean_complete", "Clean Complete"), 
                                   self.get_translation("clean_success", "All threats have been successfully cleared!"))
            
            self.clean_button.setEnabled(False)
            self.quarantine_button.setEnabled(False)

    def quarantine_selected(self):
        """Quarantine selected threats"""
        # Get selected rows
        selected_items = self.result_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 
                              self.get_translation("no_selection", "No selection"), 
                              self.get_translation("select_threats", "Please select threats to quarantine."))
            return
        
        # Get unique row indices
        rows = set()
        for item in selected_items:
            rows.add(item.row())
        
        if not rows:
            return
        
        reply = QMessageBox.question(self, 
                                    self.get_translation("confirm_quarantine", "Confirm Quarantine"), 
                                    self.get_translation("confirm_quarantine_msg", "Are you sure you want to quarantine selected threats?"), 
                                    QMessageBox.Yes | QMessageBox.No, 
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            for row in rows:
                self.result_table.item(row, 2).setText(self.get_translation("quarantined", "Quarantined"))
            
            QMessageBox.information(self, 
                                   self.get_translation("quarantine_complete", "Quarantine Complete"), 
                                   self.get_translation("quarantine_success", "Selected threats have been successfully quarantined!")) 

    def apply_settings(self, settings=None):
        """Apply settings to this component
        
        Args:
            settings: Optional settings object. If None, use parent object's settings.
        """
        try:
            # Get settings object
            if settings is None:
                if hasattr(self, 'settings'):
                    settings = self.settings
                elif hasattr(self, 'main_window') and self.main_window:
                    settings = self.main_window.settings
            
            if settings:
                # Apply theme
                self.apply_theme()
                
                # Refresh language
                self.refresh_language()
                
                # Update radio button size and style
                self.update_radio_buttons_size()
                
                # Apply any component-specific settings
                if hasattr(settings, 'get_setting'):
                    # Animation settings
                    enable_animations = settings.get_setting('enable_animations', True)
                    # Apply animation settings (if needed)
                    
                    # Apply scan-specific settings
                    auto_quarantine = settings.get_setting('auto_quarantine', False)
                    if hasattr(self, 'auto_quarantine_check') and self.auto_quarantine_check:
                        self.auto_quarantine_check.setChecked(auto_quarantine)
                    
                    # Apply saved scan type
                    scan_type = settings.get_setting('virus_scan_type', 'virus_scan_quick')
                    self._apply_saved_scan_type(scan_type)

        except Exception as e:
            self.logger.error(f"Error applying settings in VirusScanWidget: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def _apply_saved_scan_type(self, scan_type):
        """Apply saved scan type settings
        
        Args:
            scan_type: Scan type ID to apply
        """
        try:
            # First uncheck all options
            self.quick_scan_rb.setChecked(False)
            self.full_scan_rb.setChecked(False)
            self.custom_scan_rb.setChecked(False)
            self.toggle_custom_scan(False)
                
            # Set corresponding checkbox to checked state
            if scan_type == 'virus_scan_quick':
                self.quick_scan_rb.setChecked(True)
            elif scan_type == 'virus_scan_full':
                self.full_scan_rb.setChecked(True)
            elif scan_type == 'virus_scan_custom':
                self.custom_scan_rb.setChecked(True)
                self.toggle_custom_scan(True)
            else:
                # Default to quick scan
                self.quick_scan_rb.setChecked(True)
        except Exception as e:
            self.logger.error(f"Error applying scan type: {str(e)}")

    def on_scan_option_clicked(self, checkbox):
        """Handle scan type selection change"""
        button_id = checkbox.objectName()
        self.logger.info(f"Virus scan type changed to: {checkbox.text()}")
        
        # If user selects an option
        if checkbox.isChecked():
            # Save settings
            self.settings.set_setting("virus_scan_type", button_id)
            self.settings.sync()
            
            # Ensure other options are unchecked (mutual exclusivity)
            if button_id == "virus_scan_quick":
                self.full_scan_rb.setChecked(False)
                self.custom_scan_rb.setChecked(False)
                self.toggle_custom_scan(False)
            elif button_id == "virus_scan_full":
                self.quick_scan_rb.setChecked(False)
                self.custom_scan_rb.setChecked(False)
                self.toggle_custom_scan(False)
            elif button_id == "virus_scan_custom":
                self.quick_scan_rb.setChecked(False)
                self.full_scan_rb.setChecked(False)
                self.toggle_custom_scan(True)
        else:
            # If user unchecks current option, ensure at least one option is selected
            if not (self.quick_scan_rb.isChecked() or 
                   self.full_scan_rb.isChecked() or 
                   self.custom_scan_rb.isChecked()):
                # Default to current option (don't allow no option to be selected)
                checkbox.setChecked(True) 