import os
import psutil
import shutil
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QSpacerItem, QSizePolicy, QFrame, QProgressBar,
    QToolButton, QApplication, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, QSize, QRectF, QPropertyAnimation, QEasingCurve, QMargins
from PyQt5.QtGui import (
    QColor, QPainter, QPainterPath, QIcon, QBrush, QPen, QFont, QCursor,
    QLinearGradient, QPalette
)
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis

from .base_component import BaseComponent
from config import App, Icon
from collections import deque

# Maximum data points
MAX_DATA_POINTS = App.MAX_DATA_POINTS  

class ChartTile(QFrame):
    """Custom chart widget for system metrics"""
    def __init__(self, title, icon_path=None, chart_color="#00a8ff", parent=None):
        super().__init__(parent)
        self.setObjectName("chartTile")
        self.setStyleSheet(f"""
            #chartTile {{
                background-color: #2d2d2d;
                border-radius: 12px;
            }}
        """)
        self.setMinimumHeight(200)
        self.chart_color = chart_color
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # Set size policy to ensure proper stretching when window is resized
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Data storage (using deque for efficient append/pop operations)
        self.data_points = deque(maxlen=MAX_DATA_POINTS)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Title container
        title_container = QHBoxLayout()
        
        # If icon path is provided and exists, add icon
        if icon_path and os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if not icon.isNull():
                self.icon_label = QLabel()
                self.icon_label.setPixmap(icon.pixmap(QSize(24, 24)))
                title_container.addWidget(self.icon_label)
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {chart_color}; font-size: 16px; font-weight: bold; background-color: transparent;")
        title_container.addWidget(self.title_label)
        
        # Current value label (right aligned)
        self.value_label = QLabel("0%")
        # Initial font size consistent with other pages (18px)
        self.value_label.setStyleSheet(f"color: {chart_color}; font-size: 18px; font-weight: bold; background-color: transparent;")
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        title_container.addWidget(self.value_label)
        
        # Add title container to main layout
        self.layout.addLayout(title_container)
        
        # Create chart
        self.chart = QChart()
        self.chart.setBackgroundVisible(False)
        self.chart.setMargins(QMargins(0, 0, 0, 0))
        self.chart.legend().hide()
        
        # Create chart series
        self.series = QLineSeries()
        pen = QPen(QColor(chart_color))
        pen.setWidth(3)  # Increase line width
        self.series.setPen(pen)
        self.chart.addSeries(self.series)
        
        # Add gradient fill
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0, QColor(chart_color).lighter(150))
        gradient.setColorAt(1, QColor(chart_color).darker(150))
        self.series.setBrush(QBrush(gradient))
        
        # Create X axis (time)
        self.axis_x = QValueAxis()
        self.axis_x.setRange(0, MAX_DATA_POINTS - 1)
        self.axis_x.setVisible(True)
        self.axis_x.setLabelsVisible(False)  # Hide labels but show grid lines
        self.axis_x.setGridLineVisible(True)
        self.axis_x.setGridLineColor(QColor(60, 60, 60))  # Dark grid lines
        self.axis_x.setMinorGridLineVisible(False)  # Do not show minor grid lines
        
        # Create Y axis (value)
        self.axis_y = QValueAxis()
        self.axis_y.setRange(0, 100)
        self.axis_y.setVisible(True)
        self.axis_y.setLabelsVisible(False)  # Hide labels but show grid lines
        self.axis_y.setGridLineVisible(True)
        self.axis_y.setGridLineColor(QColor(60, 60, 60))  # Dark grid lines
        self.axis_y.setMinorGridLineVisible(False)  # Do not show minor grid lines
        
        # Attach axes to chart
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
        
        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setStyleSheet("background-color: transparent;")
        self.chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Add chart view to layout
        self.layout.addWidget(self.chart_view, 1)  # Set stretch factor
        
        # Initialize to zero data
        for i in range(MAX_DATA_POINTS):
            self.data_points.append(0)
            self.series.append(i, 0)
    
    def update_value(self, value):
        """Update chart value, handle multiple input formats and error states"""
        if isinstance(value, (int, float)):
            # Is a number, display as percentage
            percent_text = f"{value:.1f}%"
            self._update_percent_display(value, percent_text)
        elif isinstance(value, str):
            if value.endswith("°C"):
                # Temperature value, special handling (remove °C first)
                try:
                    temp = float(value.replace("°C", ""))
                    self._update_temp_display(temp, value)
                except ValueError:
                    # Display original string
                    self.value_label.setText(value)
                    self._update_history_with_error()
            elif value.startswith("Retry in"):
                # Display retry countdown, use special style
                self.value_label.setText(value)
                self.value_label.setStyleSheet("color: #FFA500; font-size: 15px; font-weight: bold;")
           
                self._update_history_with_error()
            elif value == "N/A":
                # Display N/A
                self.value_label.setText("N/A")
                self.value_label.setStyleSheet("color: #a0a0a0; font-size: 18px; font-weight: bold;")
                # Keep no border style
                self.setStyleSheet("QFrame { background-color: #2d2d2d; border-radius: 8px; }")
                self._update_history_with_error()
            elif value == "Error":
                # Display error state
                self.value_label.setText("Error")
                self.value_label.setStyleSheet("color: #ff5555; font-size: 18px; font-weight: bold;")
                # Text use red, remove border
                self.setStyleSheet("QFrame { background-color: #2d2d2d; border-radius: 8px; }")
                self._update_history_with_error()
            else:
                # Try to parse as number
                try:
                    num_value = float(value.replace("%", ""))
                    self._update_percent_display(num_value, value)
                except ValueError:
                    # Display original string
                    self.value_label.setText(value)
                    self._update_history_with_error()
        else:
            # Unknown type, display as string
            self.value_label.setText(str(value))
            self._update_history_with_error()
    
    def _smooth_data(self, data_points, window_size=3):
        """Simple moving average smoothing algorithm
        
        Args:
            data_points: List of data points to smooth
            window_size: Moving window size
            
        Returns:
            Smoothed data points list
        """
        if window_size < 2:
            return data_points
            
        result = []
        for i in range(len(data_points)):
            # Calculate window start and end positions
            start = max(0, i - window_size // 2)
            end = min(len(data_points), i + window_size // 2 + 1)
            # Calculate average value in window
            window = data_points[start:end]
            result.append(sum(window) / len(window))
            
        return result
        
    def _update_percent_display(self, value_num, text):
        """Update percentage type data display"""
        self.value_label.setText(text)
        self.value_label.setStyleSheet("color: #e0e0e0; font-size: 18px; font-weight: bold;")
        
        # Keep no border style
        self.setStyleSheet("QFrame { background-color: #2d2d2d; border-radius: 8px; }")
        
        # Update chart data
        self._update_chart_data(value_num)
        
    def _update_temp_display(self, temp_value, text):
        """Update temperature type data display"""
        self.value_label.setText(text)
        # Set color based on temperature value
        border_color = "#10893E"  # Default green
        if temp_value >= 80:
            border_color = "#ff5555"  # High temperature is red
        elif temp_value >= 60:
            border_color = "#ffaa00"  # Medium temperature is yellow
        
        self.value_label.setStyleSheet(f"color: {border_color}; font-size: 18px; font-weight: bold;")
        
        # Update chart data
        self._update_chart_data(temp_value)
        
    def _update_history_with_error(self):
        """Handle chart history, when there is an error or special state"""
        # Keep current chart state, only add a zero value point
        # This can show the problematic time period on the chart
        self.data_points.append(0)
        
        # Only keep the most recent MAX_DATA_POINTS data points
        while len(self.data_points) > 60:  # Assume MAX_DATA_POINTS is 60
            self.data_points.pop(0)
        
        # Update chart
        self.series.clear()
        
        # Smooth data points (simple average) to make the chart look smoother
        smoothed_points = self._smooth_data(list(self.data_points), 3)
        
        for i, point in enumerate(smoothed_points):
            self.series.append(i, point)
            
    def _update_chart_data(self, value):
        """Update chart data"""
        # Add new data point
        self.data_points.append(value)
        
        # Only keep the most recent MAX_DATA_POINTS data points
        while len(self.data_points) > 60: 
            self.data_points.pop(0)
            
        # Update chart data
        self.series.clear()
        
        # Smooth data points (simple average) to make the chart look smoother
        smoothed_points = self._smooth_data(list(self.data_points), 3)
        
        for i, point in enumerate(smoothed_points):
            self.series.append(i, point)
            
        # If needed, adjust Y axis range
        max_value = max(self.data_points) if self.data_points else 0
        if max_value > 0:
            # Set upper limit to the next multiple of 25 of the maximum value, and add a little extra space
            upper_limit = ((int(max_value) // 25) + 1) * 25
            self.axis_y.setRange(0, max(100, upper_limit))

class ActionTile(QFrame):
    """Custom style action block widget"""
    def __init__(self, title, description, icon_path=None, parent=None, color="#4285F4"):
        super().__init__(parent)
        self.setObjectName("actionTile")
        self.color = color
        
        self.setStyleSheet(f"""
            #actionTile {{
                background-color: #2d2d2d;
                border-radius: 12px;
                border: none;
            }}
            #actionTile:hover {{
                background-color: #353535;
                border-left: 4px solid {color};
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(Qt.PointingHandCursor)
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(18, 18, 18, 18)
        
        # If icon path is provided and exists, add icon
        if icon_path and os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.icon_label = QLabel()
                    pixmap = icon.pixmap(QSize(42, 42))
                    if not pixmap.isNull():
                        self.icon_label.setPixmap(pixmap)
                        self.layout.addWidget(self.icon_label)
                    else:
                        self.logger.warning(f"Warning: Could not load pixmap for icon {icon_path}") 
                else:
                    self.logger.error(f"Warning: Could not load icon {icon_path}") 
            except Exception as e:
                self.logger.error(f"Error loading icon {icon_path}: {str(e)}")  
        
        # Text container
        self.text_container = QVBoxLayout()
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold; background-color: transparent;")
        
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("color: #a0a0a0; font-size: 13px; background-color: transparent;")
        self.desc_label.setWordWrap(True)
        
        self.text_container.addWidget(self.title_label)
        self.text_container.addWidget(self.desc_label)
        
        self.layout.addLayout(self.text_container, 1)  # Add stretch factor
        
        # Fix arrow icon loading
        try:
            # Explicitly use the path from the Icon class
            arrow_icon_path = Icon.DownArrow.Path 
            if arrow_icon_path and os.path.exists(arrow_icon_path):
                arrow_icon = QIcon(arrow_icon_path)
                if not arrow_icon.isNull():
                    self.arrow_label = QLabel()
                    arrow_pixmap = arrow_icon.pixmap(QSize(18, 18))
                    if not arrow_pixmap.isNull():
                        self.arrow_label.setPixmap(arrow_pixmap)
                        self.layout.addWidget(self.arrow_label, 0, Qt.AlignRight)
        except Exception as e:
            self.logger.error(f"Error loading arrow icon: {str(e)}")

class DashboardWidget(BaseComponent):
    def __init__(self, parent=None):
        # Initialize attributes
        self.update_timer = None
        
        # Call parent class constructor
        super().__init__(parent)
        
        # Check for missing translations (development mode only)
        missing_keys = self.check_all_translations()
        if missing_keys:
            self.logger.warning(f"Warning: Missing translations in DashboardWidget:")
            for language, keys in missing_keys.items():
                self.logger.warning(f"  Language: {language}, Missing keys: {', '.join(keys)}")
        
        # Set timer to update system information
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_system_info)
        self.update_timer.start(2000)
    
    def get_translation(self, key, default=None):
        return self.settings.get_translation("dashboard", key, default)
    
    def setup_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(25)
        
        # Dashboard title and welcome message
        title_container = QHBoxLayout()
        
        # Dashboard title
        self.title = QLabel(self.get_translation("system_status"))
        self.title.setStyleSheet("font-size: 28px; font-weight: bold; color: #e0e0e0; background-color: transparent;")
        title_container.addWidget(self.title)
        
        # Welcome message, right-aligned
        self.welcome_label = QLabel(self.get_translation("welcome_message", "Welcome to Glary Utilities"))
        self.welcome_label.setStyleSheet("color: #a0a0a0; font-size: 16px; background-color: transparent;")
        self.welcome_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        title_container.addWidget(self.welcome_label)
        
        self.main_layout.addLayout(title_container)
        
        # System statistics section
        self.create_system_stats_section()
        
        # Quick access section
        self.create_quick_access_section()
        
        # Add stretch item to ensure content is vertically centered and components distribute space reasonably
        self.main_layout.addStretch(1)
    
    def create_system_stats_section(self):        
        # Statistics container
        self.stats_frame = QFrame()
        self.stats_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stats_layout = QGridLayout(self.stats_frame)
        self.stats_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_layout.setSpacing(20)
        
        # CPU usage chart
        cpu_icon_path = Icon.CPU.Path
        self.cpu_chart = ChartTile(
            self.get_translation("cpu_usage"), 
            cpu_icon_path if os.path.exists(cpu_icon_path) else Icon.CPU.Path,
            chart_color="#E74856"  # Red, simulate Windows Task Manager CPU chart
        )
        self.stats_layout.addWidget(self.cpu_chart, 0, 0)
        
        # Memory usage chart
        memory_icon_path = Icon.Memory.Path
        self.memory_chart = ChartTile(
            self.get_translation("memory_usage"), 
            memory_icon_path if os.path.exists(memory_icon_path) else Icon.Memory.Path,
            chart_color="#00B7C3"  # Cyan, simulate Windows Task Manager memory chart
        )
        self.stats_layout.addWidget(self.memory_chart, 0, 1)
        
        # Disk usage chart
        disk_icon_path = Icon.Disk.Path
        self.disk_chart = ChartTile(
            self.get_translation("disk_usage"), 
            disk_icon_path if os.path.exists(disk_icon_path) else Icon.Disk.Path,
            chart_color="#FFB900"  # Yellow, simulate Windows Task Manager disk chart
        )
        self.stats_layout.addWidget(self.disk_chart, 1, 0)
        
        # Temperature chart
        temp_icon_path = Icon.Temperature.Path
        self.temp_chart = ChartTile(
            self.get_translation("system_temperature"), 
            temp_icon_path if os.path.exists(temp_icon_path) else Icon.Temperature.Path,
            chart_color="#10893E"  # Green, simulate Windows Task Manager temperature chart
        )
        self.stats_layout.addWidget(self.temp_chart, 1, 1)
        
        # Add statistics frame to main layout and set as expandable
        self.main_layout.addWidget(self.stats_frame, 4)  # Chart section takes more space
    
    def create_quick_access_section(self):
        # Quick access title
        self.quick_title = QLabel(self.get_translation("quick_access"))
        self.quick_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #e0e0e0; margin-top: 10px; background-color: transparent;")
        self.main_layout.addWidget(self.quick_title)
        
        # Quick access container
        self.quick_frame = QFrame()
        self.quick_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.quick_layout = QGridLayout(self.quick_frame)
        self.quick_layout.setContentsMargins(0, 0, 0, 0)
        self.quick_layout.setSpacing(20)
        
        # System Repair tile (Corrected)
        repair_icon_path = Icon.Repair.Path
        self.repair_tile = ActionTile(
            self.get_translation("system_repair", "System repair"), # Use correct translation key
            self.get_translation("system_repair_desc", "Repair system"), # Use correct description key
            repair_icon_path if os.path.exists(repair_icon_path) else Icon.Repair.Path,
            color="#4285F4" # Keep color or adjust as needed
        )
        self.quick_layout.addWidget(self.repair_tile, 0, 0)
        
        # Clean Junk tile
        clean_icon_path = Icon.Clean.Path
        self.clean_tile = ActionTile(
            self.get_translation("clean_junk", "Clean junk"),
            self.get_translation("clean_junk_desc", "Free up disk space by removing unnecessary files"),
            clean_icon_path if os.path.exists(clean_icon_path) else (None if not Icon.Clean.Exist else Icon.Clean.Path),
            color="#EA4335"  # Google Red
        )
        self.quick_layout.addWidget(self.clean_tile, 0, 1)
        
        # Virus Scan tile
        virus_icon_path = Icon.Virus.Path
        self.virus_tile = ActionTile(
            self.get_translation("scan_system", "Scan system"),
            self.get_translation("scan_system_desc", "Scan your system for viruses and malware"),
            virus_icon_path if os.path.exists(virus_icon_path) else (None if not Icon.Virus.Exist else Icon.Virus.Path),
            color="#FBBC05"  # Google Yellow
        )
        self.quick_layout.addWidget(self.virus_tile, 1, 0)
        
        # Get System Info tile
        info_icon_path = Icon.Info.Path
        self.info_tile = ActionTile(
            self.get_translation("get_system_info", "System information"),
            self.get_translation("get_system_info_desc", "Get system information"),
            info_icon_path if os.path.exists(info_icon_path) else (None if not Icon.Info.Exist else Icon.Info.Path),
            color="#34A853"  # Google Green
        )
        self.quick_layout.addWidget(self.info_tile, 1, 1)
        
        # Connect tiles to correct pages
        self.repair_tile.mousePressEvent = lambda event: self.navigate_to_page(3)  # System Tools
        self.clean_tile.mousePressEvent = lambda event: self.navigate_to_page(1)  # System Cleaner
        self.virus_tile.mousePressEvent = lambda event: self.navigate_to_page(5)  # Security Tools
        self.info_tile.mousePressEvent = lambda event: self.window().set_active_page("System Information") if self.window() else None

        self.main_layout.addWidget(self.quick_frame, 3)
    
    def update_system_info(self):
        """Update system statistics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent()
        self.cpu_chart.update_value(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        self.memory_chart.update_value(memory_percent)
        
        # Disk usage (system drive)
        try:
            if self.platform_manager == 'Windows':
                # On Windows, get C: drive usage
                total, used, free = shutil.disk_usage('C:')
                disk_percent = (used / total) * 100
            else:
                # On Unix/Linux/Mac, get root directory usage
                total, used, free = shutil.disk_usage('/')
                disk_percent = (used / total) * 100
            
            self.disk_chart.update_value(disk_percent)
        except Exception as e:
            self.disk_chart.update_value("Error")  
            self.logger.error(f"Error getting disk usage: {e}")  
        
        # Temperature detection - enhanced version
        self._update_temperature()
    
    def _update_temperature(self):
        """Update temperature display using SystemInformation to get temperature data"""
        try:
            # Use SystemInformation class get_temperature method to get temperature
            temperature_data = self.system_information.get_temperature()
            
            # Check if in retry delay
            if len(temperature_data) == 2 and "CPU" in temperature_data and "System" in temperature_data:
                if temperature_data["CPU"] == "N/A" and temperature_data["System"] == "N/A":
                    # If in delayed retry state, show special status indicator
                    if self.system_information._temp_failure_count > 1:
                        # Calculate remaining time until next attempt
                        import time
                        time_elapsed = time.time() - self.system_information._temp_last_attempt
                        remaining = max(0, self.system_information._temp_retry_delay - time_elapsed)
                        
                        if remaining > 60:
                            # If remaining time is over 1 minute, show minutes
                            self.temp_chart.update_value(f"Retry in {int(remaining/60)}m")
                        else:
                            # Otherwise show seconds
                            self.temp_chart.update_value(f"Retry in {int(remaining)}s")
                        return
            
            # If there's CPU temperature, prioritize it
            if "CPU" in temperature_data:
                self.temp_chart.update_value(temperature_data["CPU"])
                return
            
            # If no CPU temperature but other temperature data, show the first one
            if temperature_data:
                first_temp = next(iter(temperature_data.values()))
                self.temp_chart.update_value(first_temp)
                return
                
            # If no temperature data found, show N/A
            self.temp_chart.update_value("N/A")
        except Exception as e:
            self.temp_chart.update_value("N/A")
            self.logger.error(f"Error getting temperature: {e}")  # Error getting temperature
    
    def navigate_to_page(self, page_index):
        """Navigate to specific page in main window"""
        # Page index to page name mapping
        page_names = {
            0: "Dashboard",
            1: "System Cleaner",
            2: "System Tools",
            3: "Disk Tools",
            4: "Boot Tools",
            5: "Security Tools",
            6: "Network Tools",
            7: "DISM Tool",
            8: "System Information",
            9: "Settings"
        }
        
        # Find main window to change page
        main_window = self.window()
        if main_window and page_index in page_names:
            main_window.set_active_page(page_names[page_index])

    def refresh_language(self):
        # Update UI text elements
        self.title.setText(self.get_translation("system_status"))
        self.welcome_label.setText(self.get_translation("welcome_message", "Welcome to Glary Utilities"))
        self.quick_title.setText(self.get_translation("quick_access"))
        
        # Update chart titles
        self.cpu_chart.title_label.setText(self.get_translation("cpu_usage"))
        self.memory_chart.title_label.setText(self.get_translation("memory_usage"))
        self.disk_chart.title_label.setText(self.get_translation("disk_usage"))
        self.temp_chart.title_label.setText(self.get_translation("system_temperature"))
        
        # Update action blocks
        self.repair_tile.title_label.setText(self.get_translation("system_repair"))
        self.clean_tile.title_label.setText(self.get_translation("clean_junk"))
        self.virus_tile.title_label.setText(self.get_translation("scan_system"))
        self.info_tile.title_label.setText(self.get_translation("get_system_info"))
        
        # Add animation to highlight changes
        super().refresh_language()

    def check_all_translations(self):
        """Check if all translation keys used in this component exist
        
        Raises:
            KeyError: If any translation key is missing
        """
        # Try to get all translations used in this component
        keys = [
            "system_status", "cpu_usage", "memory_usage", "disk_usage",
            "system_temperature", "quick_access", "optimize_system", 
            "clean_junk", "scan_system", "get_system_info", 
            "system_resources", "welcome_message"
        ]
        
        for key in keys:
            # If key does not exist, raise KeyError
            self.get_translation(key, None) 
            