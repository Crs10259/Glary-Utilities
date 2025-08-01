import os
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                            QProgressBar, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QPixmap, QColor, QPainter, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from src.config import Icon
from src.config import App
from src.utils.settings import Settings
from src.utils.logger import Logger

class LoadingThread(QThread):
    """Loading thread, simulates time-consuming operations"""
    progress_updated = pyqtSignal(int)
    loading_finished = pyqtSignal()
    
    def run(self):
        """Run loading thread"""
        for i in range(101):
            self.progress_updated.emit(i)
            # Shorten loading time, reduce to 0.06 seconds, total time about 6 seconds
            time.sleep(0.06)
        self.loading_finished.emit()

class CustomProgressBar(QProgressBar):
    """Custom progress bar, displays percentage in the center"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger().get_logger()
        # Hide default text to avoid overlap with custom percentage drawing
        self.setTextVisible(False)
        self.setAlignment(Qt.AlignCenter)
        
    def paintEvent(self, event):
        # Call original paint method
        super().paintEvent(event)
        
        # Draw text in the center of progress bar
        painter = QPainter(self)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        
        # Get current progress text
        text = f"{self.value()}%"
        
        # Draw text in center
        painter.drawText(self.rect(), Qt.AlignCenter, text)

class SplashScreen(QWidget):
    """Splash screen window"""
    def __init__(self):
        super().__init__()
        
        # Load settings, get language
        self.settings = Settings()
        self.current_language = self.settings.get_setting("language", "en").lower()
        
        self.setWindowTitle("Glary Utilities")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(600, 400)
        
        # Preload icons
        self._preload_resources()
        
        # Setup UI
        self.setup_ui()
        
        # Set window opacity to 0, prepare fade-in effect
        self.setWindowOpacity(0.0)
        
        # Create fade-in animation
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(400) 
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutQuint)
        self.fade_anim.start()
        
        # Center display
        screen_geo = QApplication.desktop().screenGeometry()
        x = (screen_geo.width() - self.width()) // 2
        y = (screen_geo.height() - self.height()) // 2
        self.move(x, y)
        
        # Create and start loading thread
        self.loading_thread = LoadingThread()
        self.loading_thread.progress_updated.connect(self.update_progress)
        self.loading_thread.loading_finished.connect(self.finish_loading)
        self.loading_thread.start()
    
    def _preload_resources(self):
        """Preload resource files"""
        icon_path = Icon.Icon.Path
        # Directly try to load icon, if file doesn't exist keep None
        self.app_icon = QPixmap(icon_path) if os.path.exists(icon_path) else None
    
    def get_translation(self, key, default):
        """Get translation text"""
        # Use settings to get current language translation
        return self.settings.get_translation("splash_screen", key, default)
    
    def setup_ui(self):
        """Setup UI interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create container
        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet("""
            QWidget#container {
                background-color: #1e1e1e;
                border-radius: 10px;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 0)
        container.setGraphicsEffect(shadow)
        
        # Container layout
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(15)
        
        # Add title
        title_label = QLabel("Glary Utilities")
        title_label.setStyleSheet("""
            color: #3498db;
            font-size: 36px;
            font-weight: bold;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)
        
        # Add application icon
        if self.app_icon:
            logo_label = QLabel(self)
            logo_label.setPixmap(self.app_icon.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(logo_label)
        
        # Add description - use translation
        desc_text = self.get_translation("description", 
                                        "System optimization and cleanup tool" if self.current_language == "en" else "系统优化和清理工具")
        
        desc_label = QLabel(desc_text)
        desc_label.setStyleSheet("""
            color: #bbbbbb;
            font-size: 16px;
        """)
        desc_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(desc_label)
        
        # Add spacing
        container_layout.addStretch()
        
        # Add custom progress bar (display percentage in center)
        self.progress_bar = CustomProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)  # Increase height to better display text
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2d2d2d;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 5px;
            }
        """)
        container_layout.addWidget(self.progress_bar)
        
        # Add status text - no longer display percentage, only show status description
        self.status_label = QLabel(self.get_translation("initializing", 
                                                      "Initializing interface..." if self.current_language == "en" else "正在初始化界面..."))
        self.status_label.setStyleSheet("""
            color: #999999;
            font-size: 14px;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.status_label)
        
        # Add copyright information
        copyright_text = self.get_translation("copyright", f"Version {App.version} | Copyright © 2025")
        # Replace version variable
        copyright_text = copyright_text.replace("{version}", App.version)
        version_label = QLabel(copyright_text)
        version_label.setStyleSheet("""
            color: #777777;
            font-size: 12px;
        """)
        version_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(version_label)
        
        # Add container to main layout
        layout.addWidget(container)
        self.setLayout(layout)
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        
        # Update prompt information based on progress - use translation
        if value < 20:
            self.status_label.setText(self.get_translation("initializing", 
                                                         "Initializing interface..." if self.current_language == "en" else "正在初始化界面..."))
        elif value < 40:
            self.status_label.setText(self.get_translation("loading_components", 
                                                         "Loading system components..." if self.current_language == "en" else "正在加载系统组件..."))
        elif value < 60:
            self.status_label.setText(self.get_translation("checking_system", 
                                                         "Checking system status..." if self.current_language == "en" else "正在检查系统状态..."))
        elif value < 80:
            self.status_label.setText(self.get_translation("preparing_tools", 
                                                         "Preparing tool components..." if self.current_language == "en" else "正在准备工具组件..."))
        else:
            self.status_label.setText(self.get_translation("finishing", 
                                                         "Finishing..." if self.current_language == "en" else "即将完成..."))
    
    def finish_loading(self):
        """Finish loading"""
        # Create fade out animation
        self.fade_out_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_anim.setDuration(300)
        self.fade_out_anim.setStartValue(1.0)
        self.fade_out_anim.setEndValue(0.0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.OutQuint)
        self.fade_out_anim.finished.connect(self.close)
        self.fade_out_anim.start() 
        