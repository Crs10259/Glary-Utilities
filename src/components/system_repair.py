import os
import sys
import platform
import subprocess
import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QCheckBox, QListWidget, QProgressBar, QTabWidget, 
                            QGroupBox, QListWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from src.components.base_component import BaseComponent
from src.tools.system_repair import RepairThread

class SystemRepairWidget(BaseComponent):
    """System repair widget, display system repair options"""
    
    def __init__(self, parent=None):
        # Initialize properties
        self.scan_results = None
        self.selected_issues = []
        self.repair_worker = None
        
        # Call parent constructor
        super().__init__(parent)
    
    def get_translation(self, key, default=None):
        """Override get_translation to use the correct section name"""
        return self.settings.get_translation("system_repair", key, default)
    
    def setup_ui(self):
        """Setup UI components"""
        # Clear old layout (if any)
        # if self.layout():
        #     # Clear all widgets in old layout
        #     while self.layout().count():
        #         item = self.layout().takeAt(0)
        #         if item.widget():
        #             item.widget().deleteLater()
            
        #     # Delete old layout
        #     old_layout = self.layout()
        #     QWidget().setLayout(old_layout)  # Set old layout to a temporary widget for deletion
        
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Title
        self.title = QLabel(self.get_translation("title"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0; background-color: transparent;")
        self.main_layout.addWidget(self.title)
        
        # Description
        self.description = QLabel(self.get_translation("description"))
        self.description.setStyleSheet("font-size: 14px; color: #a0a0a0; background-color: transparent;")
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
        self.scan_tab.setStyleSheet("background-color: transparent;")
        self.setup_scan_tab()
        self.tab_widget.addTab(self.scan_tab, self.get_translation("scan_tab"))
        
        # Results tab
        self.results_tab = QWidget()
        self.results_tab.setStyleSheet("background-color: transparent;")
        self.setup_results_tab()
        self.tab_widget.addTab(self.results_tab, self.get_translation("results_tab"))
        
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
        self.status_label = QLabel("Ready to scan")
        self.status_label.setStyleSheet("color: #a0a0a0; background-color: transparent;")
        self.main_layout.addWidget(self.status_label)
        
        # Set layout
        self.setLayout(self.main_layout)
        
        # Ensure styles are applied correctly
        self.setAttribute(Qt.WA_StyledBackground, True)
    
    def setup_scan_tab(self):
        """Setup the scan options tab"""
        layout = QVBoxLayout(self.scan_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Scan options group
        self.repair_options_group = QGroupBox(self.get_translation("scan_options"))
        self.repair_options_group.setStyleSheet("""
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
        scan_layout = QVBoxLayout(self.repair_options_group)
        
        # Checkboxes for scan options
        self.registry_check = QCheckBox(self.get_translation("registry_issues"))
        self.registry_check.setObjectName("repair_registry_issues")
        self.registry_check.setChecked(True)
        self.registry_check.setStyleSheet("color: #e0e0e0;")
        scan_layout.addWidget(self.registry_check)
        
        self.system_files_check = QCheckBox(self.get_translation("system_files"))
        self.system_files_check.setObjectName("repair_system_files")
        self.system_files_check.setChecked(True)
        self.system_files_check.setStyleSheet("color: #e0e0e0;")
        scan_layout.addWidget(self.system_files_check)
        
        self.startup_check = QCheckBox(self.get_translation("startup_items"))
        self.startup_check.setObjectName("repair_startup_items")
        self.startup_check.setChecked(True)
        self.startup_check.setStyleSheet("color: #e0e0e0;")
        scan_layout.addWidget(self.startup_check)
        
        self.services_check = QCheckBox(self.get_translation("services"))
        self.services_check.setObjectName("repair_services")
        self.services_check.setChecked(True)
        self.services_check.setStyleSheet("color: #e0e0e0;")
        scan_layout.addWidget(self.services_check)
        
        layout.addWidget(self.repair_options_group)
        
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
        
        # Issues found
        self.issues_found_label = QLabel(self.get_translation("issues_found") + ":")
        self.issues_found_label.setStyleSheet("color: #a0a0a0;")
        summary_layout.addWidget(self.issues_found_label)
        
        self.issues_found_value = QLabel("0")
        self.issues_found_value.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        summary_layout.addWidget(self.issues_found_value)
        
        summary_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        layout.addWidget(self.summary_frame)
        
        # Repair button
        self.repair_button = QPushButton(self.get_translation("repair_selected"))
        self.repair_button.setEnabled(False)
        self.repair_button.setStyleSheet("""
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
        self.repair_button.clicked.connect(self.start_repair)
        
        # Button container (for right alignment)
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(self.repair_button)
        
        layout.addWidget(button_container)
    
    def start_scan(self):
        """Start the scan process"""
        # Get scan options
        options = {
            "registry_issues": self.registry_check.isChecked(),
            "system_files": self.system_files_check.isChecked(),
            "startup_items": self.startup_check.isChecked(),
            "services": self.services_check.isChecked()
        }
        
        # Clear previous results
        self.results_list.clear()
        self.issues_found_value.setText("0")
        self.scan_results = None
        self.repair_button.setEnabled(False)
        
        # Disable scan button during scan
        self.start_scan_button.setEnabled(False)
        self.start_scan_button.setText(self.get_translation("scanning"))
        
        # Start worker thread
        self.repair_worker = RepairThread(options, "scan")
        self.repair_worker.progress_updated.connect(self.update_progress)
        self.repair_worker.scan_completed.connect(self.scan_completed)
        self.repair_worker.start()
    
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
        self.issues_found_value.setText(str(results["total_issues"]))
        
        # Populate results list
        for issue in results["issues"]:
            severity_icon = "⚠️" if issue["severity"] == "high" else "ℹ️"
            item = QListWidgetItem(f"{severity_icon} {issue['description']} ({issue['location']})")
            item.setData(Qt.UserRole, issue)
            self.results_list.addItem(item)
        
        # Enable repair button if issues were found
        self.repair_button.setEnabled(results["total_issues"] > 0)
        
        # Switch to results tab
        self.tab_widget.setCurrentIndex(1)
    
    def start_repair(self):
        """Start the repair process"""
        if not self.scan_results:
            return
        
        # Get selected issues or all issues if none selected
        selected_items = self.results_list.selectedItems()
        issues_to_fix = []
        
        if selected_items:
            # Only fix selected issues
            for item in selected_items:
                issue = item.data(Qt.UserRole)
                issues_to_fix.append(issue)
        else:
            # Fix all issues
            issues_to_fix = self.scan_results["issues"]
        
        # Disable repair button during repair
        self.repair_button.setEnabled(False)
        self.repair_button.setText(self.get_translation("repairing"))
        
        # Start worker thread
        self.repair_worker = RepairThread({"issues": issues_to_fix}, "repair")
        self.repair_worker.progress_updated.connect(self.update_progress)
        self.repair_worker.repair_completed.connect(self.repair_completed)
        self.repair_worker.start()
    
    def repair_completed(self, results):
        """Handle repair completion"""
        # Re-enable repair button
        self.repair_button.setEnabled(True)
        self.repair_button.setText(self.get_translation("repair_selected"))
        
        # Update status
        self.status_label.setText(self.get_translation("repair_complete"))
        
        # Clear results after repair
        self.results_list.clear()
        self.issues_found_value.setText("0")
        self.scan_results = None 

    def refresh_language(self):
        """Update UI text elements after language change"""
        # Update main title and description
        self.title.setText(self.get_translation("title"))
        self.description.setText(self.get_translation("description"))
        
        # Update tab names
        self.tab_widget.setTabText(0, self.get_translation("scan_tab"))
        self.tab_widget.setTabText(1, self.get_translation("results_tab"))
        
        # Update scan tab elements
        self.repair_options_group.setTitle(self.get_translation("scan_options"))
        self.registry_check.setText(self.get_translation("registry_issues"))
        self.system_files_check.setText(self.get_translation("system_files"))
        self.startup_check.setText(self.get_translation("startup_items"))
        self.services_check.setText(self.get_translation("services"))
        self.start_scan_button.setText(self.get_translation("start_scan"))
        
        # Update results tab elements
        self.issues_found_label.setText(self.get_translation("issues_found") + ":")
        self.repair_button.setText(self.get_translation("repair_selected"))
        
        # Add animation to highlight the change
        super().refresh_language() 