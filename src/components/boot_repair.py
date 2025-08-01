import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QProgressBar, QMessageBox,
                             QGroupBox, QRadioButton, QCheckBox, QTabWidget,
                             QTableWidget, QTableWidgetItem, QFrame, QSizePolicy,
                             QSpacerItem, QHeaderView, QButtonGroup, QFileDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from src.components.base_component import BaseComponent
from PyQt5.QtGui import QBrush, QColor
from src.tools.boot_repair import BootRepairThread
from src.tools.boot_repair import StartupManager

class BootToolsWidget(BaseComponent):
    """Widget for boot tools operations including repair and startup management"""
    def __init__(self, parent=None):
        self.boot_worker = None
        super().__init__(parent)
        
    def setup_ui(self):
        """Setup UI elements"""
        # Set main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # Enable stylesheet background
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # Title
        self.title = QLabel(self.get_translation("title", "Boot Tools & Startup Manager"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.main_layout.addWidget(self.title)
        
        # Description
        self.description = QLabel(self.get_translation("description", "Repair Windows boot issues and manage startup programs."))
        self.description.setStyleSheet("font-size: 14px;")
        self.description.setWordWrap(True)
        self.main_layout.addWidget(self.description)
        
        # Warning label for non-Windows systems
        if not self.platform_manager.is_windows():
            warning_label = QLabel("⚠️ Boot tools features are only available on Windows")
            warning_label.setStyleSheet("color: #ff9900; font-weight: bold;")
            self.main_layout.addWidget(warning_label)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        # Repair tab
        self.repair_tab = QWidget()
        
        # Startup management tab
        self.startup_tab = QWidget()
        
        # Setup tab contents
        self.setup_repair_tab(self.repair_tab)
        self.setup_startup_manager_tab(self.startup_tab)
        
        # Add tabs
        self.tabs.addTab(self.repair_tab, self.get_translation("repair_tab", "Boot Repair"))
        self.tabs.addTab(self.startup_tab, self.get_translation("startup_tab", "Startup Manager"))
        
        # Add to main layout
        self.main_layout.addWidget(self.tabs)
        
        # Apply current theme
        self.apply_theme()
        
    def apply_theme(self):
        """Apply theme styles to component"""
        try:
            # First call the base class apply theme method
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

                # Get icon path for check icon
                from src.config import Icon
                check_icon_path = Icon.get_path("resources/icons/check.svg")

                # Update title and description colors (if they exist)
                if hasattr(self, 'title') and self.title is not None:
                    self.title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {text_color};")
                
                if hasattr(self, 'description') and self.description is not None:
                    self.description.setStyleSheet(f"font-size: 14px; color: {text_color};")

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
                """)
                 # Apply alternating row colors specifically for the table
                try:
                    if hasattr(self, 'startup_table') and self.startup_table is not None:
                        self.startup_table.setAlternatingRowColors(True)
                        self.startup_table.setStyleSheet(f"QTableWidget {{ alternate-background-color: {self.lighten_color(table_bg_color, 5)}; background-color: {table_bg_color}; color: {text_color}; border: 1px solid {border_color}; gridline-color: {border_color};}} QTableWidget::item {{ padding: 4px; color: {text_color}; }} QTableWidget::item:selected {{ background-color: {accent_color}80; color: #ffffff; }}")
                except AttributeError:
                    pass
                
        except Exception as e:
            self.logger.error(f"Error applying theme in BootToolsWidget: {e}")
            
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
            
    def setup_repair_tab(self, tab):
        """Setup repair tab"""
        # Create tab layout
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(10, 10, 10, 10)
        
        # Options group
        options_group = QGroupBox(self.get_translation("repair_options", "Repair Options"))
        options_layout = QVBoxLayout(options_group)
        
        # Repair options
        self.repair_mbr_radio = QCheckBox(self.get_translation("fix_mbr", "Fix Boot Sector"))
        self.repair_mbr_radio.setObjectName("repair_mbr_radio")
        self.repair_mbr_radio.setChecked(True)
        self.repair_mbr_radio.clicked.connect(lambda: self.on_repair_option_clicked(self.repair_mbr_radio))
        
        self.repair_bcd_radio = QCheckBox(self.get_translation("rebuild_bcd", "Repair Boot Configuration Data (BCD)"))
        self.repair_bcd_radio.setObjectName("repair_bcd_radio")
        self.repair_bcd_radio.clicked.connect(lambda: self.on_repair_option_clicked(self.repair_bcd_radio))
        
        self.repair_bootmgr_radio = QCheckBox(self.get_translation("fix_boot", "Repair Boot Manager"))
        self.repair_bootmgr_radio.setObjectName("repair_bootmgr_radio")
        self.repair_bootmgr_radio.clicked.connect(lambda: self.on_repair_option_clicked(self.repair_bootmgr_radio))
        
        self.repair_winload_radio = QCheckBox(self.get_translation("repair_winload", "Repair Windows Loader"))
        self.repair_winload_radio.setObjectName("repair_winload_radio")
        self.repair_winload_radio.clicked.connect(lambda: self.on_repair_option_clicked(self.repair_winload_radio))
        
        self.repair_full_radio = QCheckBox(self.get_translation("full_repair", "Full Repair"))
        self.repair_full_radio.setObjectName("repair_full_radio")
        self.repair_full_radio.clicked.connect(lambda: self.on_repair_option_clicked(self.repair_full_radio))
        
        options_layout.addWidget(self.repair_mbr_radio)
        options_layout.addWidget(self.repair_bcd_radio)
        options_layout.addWidget(self.repair_bootmgr_radio)
        options_layout.addWidget(self.repair_winload_radio)
        options_layout.addWidget(self.repair_full_radio)
        
        # Add options group to tab
        tab_layout.addWidget(options_group)
        
        # Log output area
        log_group = QGroupBox(self.get_translation("operation_log", "Operation Log"))
        log_layout = QVBoxLayout(log_group)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setText(self.get_translation("boot_repair_ready", "Boot repair tool is ready, please select a repair option and click the \"Start Repair\" button."))
        
        log_layout.addWidget(self.log_output)
        
        # Add log group to tab
        tab_layout.addWidget(log_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        tab_layout.addWidget(self.progress_bar)
        
        # Buttons area
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton(self.get_translation("repair_button", "Start Repair"))
        self.start_button.clicked.connect(self.start_repair)
        
        self.stop_button = QPushButton(self.get_translation("stop_button", "Stop"))
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_repair)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        
        # Add buttons area to tab
        tab_layout.addLayout(buttons_layout)
    
    def setup_startup_manager_tab(self, tab):
        """Setup startup manager tab"""
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Description
        description = QLabel(self.get_translation("startup_desc", "Manage Windows startup items, enable or disable self-starting programs."))
        description.setStyleSheet("font-size: 14px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Startup table
        self.startup_table = QTableWidget()
        self.startup_table.setColumnCount(4)
        self.startup_table.setHorizontalHeaderLabels([
            self.get_translation("startup_name", "Name"),
            self.get_translation("startup_path", "Path"),
            self.get_translation("startup_status", "Status"),
            self.get_translation("startup_type", "Type")
        ])
        
        # Set table properties
        self.startup_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.startup_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.startup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.startup_table.setAlternatingRowColors(True)
        layout.addWidget(self.startup_table)
        
        # Buttons area
        button_layout = QHBoxLayout()

        # Add button
        self.add_button = QPushButton(self.get_translation("add_startup_item", "Add Startup Item"))
        self.add_button.clicked.connect(self.add_startup_item)
        button_layout.addWidget(self.add_button)
        
        # Refresh button
        self.refresh_button = QPushButton(self.get_translation("refresh", "Refresh"))
        self.refresh_button.clicked.connect(self.refresh_startup_items)
        button_layout.addWidget(self.refresh_button)
        
        # Enable/disable buttons
        self.enable_button = QPushButton(self.get_translation("enable", "Enable Selected"))
        self.enable_button.clicked.connect(self.enable_startup_item)
        button_layout.addWidget(self.enable_button)
        
        self.disable_button = QPushButton(self.get_translation("disable", "Disable Selected"))
        self.disable_button.clicked.connect(self.disable_startup_item)
        button_layout.addWidget(self.disable_button)
        
        # Delete button
        self.delete_button = QPushButton(self.get_translation("delete", "Delete Selected"))
        self.delete_button.clicked.connect(self.delete_startup_item)
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
        
        # Load example data
        self.load_startup_items()
        
        # Connect selection signal
        self.startup_table.itemSelectionChanged.connect(self.update_button_states)
        
        # Initialize button states
        self.update_button_states()
        
        # If not Windows system, disable all buttons
        if not self.platform_manager.is_windows():
            self.add_button.setEnabled(False)
            self.refresh_button.setEnabled(False)
            self.enable_button.setEnabled(False)
            self.disable_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            # Add warning label
            warning_label = QLabel(self.get_translation("startup_warning", "⚠️ Startup management is only available on Windows systems"))
            warning_label.setStyleSheet("color: #ff9900; font-weight: bold;")
            layout.addWidget(warning_label)

    def load_startup_items(self):
        """Load system startup items data"""
        self.startup_table.setRowCount(0)  # Clear existing rows
        
        try:
            # Get actual startup items
            startup_items = StartupManager.get_startup_items()
            
            for item in startup_items:
                row = self.startup_table.rowCount()
                self.startup_table.insertRow(row)
                
                # Add data to each column
                self.startup_table.setItem(row, 0, QTableWidgetItem(item["name"]))
                self.startup_table.setItem(row, 1, QTableWidgetItem(item["path"]))
                self.startup_table.setItem(row, 2, QTableWidgetItem(item["status"]))
                self.startup_table.setItem(row, 3, QTableWidgetItem(item["type"]))
                
                # Set gray for disabled items
                if item["status"] == "已禁用":
                    for col in range(4):
                        self.startup_table.item(row, col).setForeground(QBrush(QColor("#888888")))
                        
        except Exception as e:
            self.log_output.append(f"Error loading startup items: {str(e)}")
            # If error, load demo data
            self.load_demo_items()
    
    def load_demo_items(self):
        """Load demo startup items data"""
        demo_items = [
            ["Microsoft Edge", "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe", "已启用", "注册表"],
            ["Spotify", "C:\\Users\\AppData\\Roaming\\Spotify\\Spotify.exe", "已启用", "启动文件夹"],
            ["Steam", "C:\\Program Files\\Steam\\steam.exe", "已禁用", "注册表"],
            ["Discord", "C:\\Users\\AppData\\Local\\Discord\\app-1.0.9002\\Discord.exe", "已启用", "任务计划程序"],
            ["OneDrive", "C:\\Program Files\\Microsoft OneDrive\\OneDrive.exe", "已禁用", "注册表"],
        ]
        
        for item in demo_items:
            row = self.startup_table.rowCount()
            self.startup_table.insertRow(row)
            
            for col, text in enumerate(item):
                self.startup_table.setItem(row, col, QTableWidgetItem(text))
                
            # Set different color for disabled items
            if item[2] == "已禁用":
                for col in range(4):
                    self.startup_table.item(row, col).setForeground(QBrush(QColor("#888888")))
    
    def enable_startup_item(self):
        """Enable selected startup items"""
        selected_rows = self.get_selected_rows()
        if not selected_rows:
            return
            
        for row in selected_rows:
            name = self.startup_table.item(row, 0).text()
            item_type = self.startup_table.item(row, 3).text()
            
            self.log_output.append(self.get_translation("enabling", f"Enabling {name}..."))
            
            # Try to enable startup item
            if StartupManager.enable_startup_item(name, item_type):
                # Update status
                status_item = self.startup_table.item(row, 2)
                status_item.setText("Enabled")
                
                # Restore normal color
                for col in range(4):
                    self.startup_table.item(row, col).setForeground(QBrush(QColor("#000000")))
                    
                self.log_output.append(f"✓ {name} enabled successfully")
            else:
                self.log_output.append(f"✗ Failed to enable {name}")
                
        self.update_button_states()
    
    def disable_startup_item(self):
        """Disable selected startup items"""
        selected_rows = self.get_selected_rows()
        if not selected_rows:
            return
            
        for row in selected_rows:
            name = self.startup_table.item(row, 0).text()
            item_type = self.startup_table.item(row, 3).text()
            
            self.log_output.append(self.get_translation("disabling", f"Disabling {name}..."))
            
            # Try to disable startup item
            if StartupManager.disable_startup_item(name, item_type):
                # Update status
                status_item = self.startup_table.item(row, 2)
                status_item.setText("Disabled")
                
                # Set gray
                for col in range(4):
                    self.startup_table.item(row, col).setForeground(QBrush(QColor("#888888")))
                    
                self.log_output.append(f"✓ {name} disabled successfully")
            else:
                self.log_output.append(f"✗ Failed to disable {name}")
                
        self.update_button_states()
    
    def delete_startup_item(self):
        """Delete selected startup items"""
        selected_rows = self.get_selected_rows()
        if not selected_rows:
            return
        
        # Confirm dialog
        reply = QMessageBox.question(
            self,
            self.get_translation("confirm_delete", "Confirm Delete"),
            self.get_translation("confirm_delete_msg", "Are you sure you want to delete the selected startup items? This action cannot be undone."),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete from bottom to avoid index change problem
            for row in sorted(selected_rows, reverse=True):
                name = self.startup_table.item(row, 0).text()
                path = self.startup_table.item(row, 1).text()
                item_type = self.startup_table.item(row, 3).text()
                
                self.log_output.append(self.get_translation("deleting", f"Deleting {name}..."))
                
                # Try to delete startup item
                if StartupManager.delete_startup_item(name, path, item_type):
                    self.startup_table.removeRow(row)
                    self.log_output.append(f"✓ {name} deleted successfully")
                else:
                    self.log_output.append(f"✗ Failed to delete {name}")
            
            self.update_button_states()
    
    def add_startup_item(self):
        """Add new startup item"""
        # Select executable file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.get_translation("select_program", "Select Program"),
            "",
            self.get_translation("exe_files", "Executable Files (*.exe);;All Files (*.*)")
        )
        
        if not file_path:
            return
            
        # Get program name (without extension)
        name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Select add method
        item_type = "注册表"  # Default use registry
        
        # Try to add startup item
        if StartupManager.add_startup_item(name, file_path, item_type):
            self.log_output.append(f"✓ {name} added to startup items successfully")
            # Refresh list
            self.load_startup_items()
        else:
            self.log_output.append(f"✗ Failed to add {name} to startup items")

    def get_selected_rows(self):
        """Get selected row index"""
        selected_indexes = self.startup_table.selectedIndexes()
        if not selected_indexes:
            return []
            
        # Extract unique row indices
        rows = set()
        for index in selected_indexes:
            rows.add(index.row())
            
        return list(rows)

    def update_button_states(self):
        """Update button enable/disable state"""
        has_selection = bool(self.get_selected_rows())
        self.enable_button.setEnabled(has_selection)
        self.disable_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
    
    def start_repair(self):
        """Start the boot repair process"""
        # Find the selected repair option (now only one can be selected)
        selected_repair = None
        repair_name = None
        
        if self.repair_mbr_radio.isChecked():
            selected_repair = "mbr"
            repair_name = "MBR"
        elif self.repair_bcd_radio.isChecked():
            selected_repair = "bcd"
            repair_name = "BCD"
        elif self.repair_bootmgr_radio.isChecked():
            selected_repair = "bootmgr"
            repair_name = "Boot Manager"
        elif self.repair_winload_radio.isChecked():
            selected_repair = "winload"
            repair_name = "Windows Loader"
        elif self.repair_full_radio.isChecked():
            selected_repair = "full"
            repair_name = "Full Repair"
        
        # Check if any repair option is selected
        if not selected_repair:
            QMessageBox.warning(self, "No Selection", 
                                "Please select at least one repair option.")
            return
        
        # Check if we're on Windows
        if not self.platform_manager.is_windows():
            QMessageBox.warning(self, "Compatibility Error", 
                                "Boot repair features are only available on Windows systems.")
            return
            
        # Confirmation dialog
        reply = QMessageBox.question(self, 'Confirm Boot Repair', 
                                    f"Are you sure you want to perform this repair: {repair_name}?\n\n"
                                    "Note: This is a simulated operation for safety.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Clear previous log
            self.log_output.clear()
            self.log_output.append(f"Starting boot repair: {repair_name}...")
            
            # Reset progress bar
            self.progress_bar.setValue(0)
            
            # Create and start thread
            self.boot_worker = BootRepairThread(selected_repair)
            self.boot_worker.update_progress.connect(self.update_progress)
            self.boot_worker.update_log.connect(self.update_log)
            self.boot_worker.finished_operation.connect(self.repair_finished)
            self.boot_worker.start()
            
            # Update UI
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
    
    def stop_repair(self):
        """Stop the boot repair process"""
        if self.boot_worker and self.boot_worker.is_running:
            reply = QMessageBox.question(self, 'Confirm Stop', 
                                        "Are you sure you want to stop the repair process?\n"
                                        "This may leave your system in an inconsistent state.",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.boot_worker.terminate()
                self.boot_worker.wait()
                
                self.update_log("Repair process stopped by user.")
                self.repair_finished(False, "Operation cancelled")
    
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_bar.setValue(value)
    
    def update_log(self, message):
        """Update the log output"""
        self.log_output.append(message)
        # Scroll to bottom
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )
    
    def repair_finished(self, success, message):
        """Handle repair completion"""
        # Re-enable the start button
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Set progress to 100%
        self.progress_bar.setValue(100)
        
        # Show message
        if success:
            QMessageBox.information(self, "Boot Repair Complete", message)
        else:
            QMessageBox.warning(self, "Boot Repair Failed", message)
        
        # Add final log message
        self.update_log(f"Boot repair process completed. Result: {'Success' if success else 'Failed'}")

    def get_translation(self, key, default=None):
        """Override get_translation to use the correct section name"""
        return self.settings.get_translation("boot_repair", key, default)

    def refresh_language(self):
        """Refresh all UI text elements with current language translations"""
        # Tab titles
        self.tabs.setTabText(0, self.get_translation("repair_tab", "Boot Repair"))
        self.tabs.setTabText(1, self.get_translation("startup_tab", "Startup Manager"))
        
        # Update radio buttons
        self.repair_mbr_radio.setText(self.get_translation("fix_mbr", "Fix Boot Sector"))
        self.repair_bcd_radio.setText(self.get_translation("rebuild_bcd", "Repair Boot Configuration Data (BCD)"))
        self.repair_bootmgr_radio.setText(self.get_translation("fix_boot", "Repair Boot Manager"))
        self.repair_winload_radio.setText(self.get_translation("repair_winload", "Repair Windows Loader"))
        self.repair_full_radio.setText(self.get_translation("full_repair", "Full Repair"))
        
        # Update buttons
        self.start_button.setText(self.get_translation("repair_button", "Start Repair"))
        self.stop_button.setText(self.get_translation("stop_button", "Stop"))
        
        # Update log group
        log_group = self.findChild(QGroupBox, "log_group")
        if log_group:
            log_group.setTitle(self.get_translation("log_output", "Log Output"))
        
        # Update startup manager tab
        if hasattr(self, "enable_button"):
            self.enable_button.setText(self.get_translation("enable", "Enable Selected"))
        if hasattr(self, "disable_button"):
            self.disable_button.setText(self.get_translation("disable", "Disable Selected"))
        if hasattr(self, "delete_button"):
            self.delete_button.setText(self.get_translation("delete", "Delete Selected"))
        if hasattr(self, "refresh_button"):
            self.refresh_button.setText(self.get_translation("refresh", "Refresh List"))
            
        # Update startup table
        startup_list = self.findChild(QTableWidget, "startup_list")
        if startup_list:
            startup_list.setHorizontalHeaderLabels([
                self.get_translation("name", "Name"),
                self.get_translation("publisher", "Publisher"),
                self.get_translation("status", "Status"),
                self.get_translation("impact", "Impact")
            ]) 
            
        # Update page headline and description
        if hasattr(self, "title"):
            self.title.setText(self.get_translation("title", "Boot Tools"))
        if hasattr(self, "description"):
            self.description.setText(self.get_translation("description", ""))
            
    def on_repair_option_clicked(self, checkbox):
        """Handle repair option click"""
        button_id = checkbox.objectName()
        self.logger.info(f"Boot repair option changed to: {checkbox.text()}")
        
        # If user selects an option
        if checkbox.isChecked():
            # Save settings
            self.settings.set_setting("boot_repair_type", button_id)
            self.settings.sync()
            
            # Ensure other options are unchecked (mutual exclusivity)
            if checkbox != self.repair_mbr_radio:
                self.repair_mbr_radio.setChecked(False)
            if checkbox != self.repair_bcd_radio:
                self.repair_bcd_radio.setChecked(False)
            if checkbox != self.repair_bootmgr_radio:
                self.repair_bootmgr_radio.setChecked(False)
            if checkbox != self.repair_winload_radio:
                self.repair_winload_radio.setChecked(False)
            if checkbox != self.repair_full_radio:
                self.repair_full_radio.setChecked(False)
            
            # Log selected repair option
            repair_type = button_id.replace("_radio", "")
            self.log_output.append(self.get_translation("selected_repair", f"Selected repair: {checkbox.text()}"))
        else:
            # If user unchecks current option, ensure at least one option is selected
            if not (self.repair_mbr_radio.isChecked() or 
                    self.repair_bcd_radio.isChecked() or 
                    self.repair_bootmgr_radio.isChecked() or 
                    self.repair_winload_radio.isChecked() or 
                    self.repair_full_radio.isChecked()):
                # Default to current option (don't allow no option to be selected)
                checkbox.setChecked(True)

    def toggle_startup_item(self, state):
        """Handle startup item checkbox state change"""
        if state == Qt.Checked:
            self.enable_startup_cb.setText(self.get_translation("enable_startup_checked", "Enable Selected"))
        else:
            self.enable_startup_cb.setText(self.get_translation("enable_startup", "Enable Selected"))
        
    def toggle_service(self, state):
        """Handle service checkbox state change"""
        if state == Qt.Checked:
            self.disable_service_cb.setText(self.get_translation("disable_service_checked", "Disable Selected"))
        else:
            self.disable_service_cb.setText(self.get_translation("disable_service", "Disable Selected"))
            
    def refresh_startup_items(self):
        """Refresh startup items list"""
        self.log_output.append(self.get_translation("refreshing", "Refreshing startup items..."))
        self.load_startup_items()
        self.log_output.append(self.get_translation("refresh_complete", "Refresh complete"))
            