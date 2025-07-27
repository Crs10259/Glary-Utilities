import os
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                            QProgressBar, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QPixmap, QColor, QPainter, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from config import Icon
from config import App
from utils.settings import Settings
from utils.logger import Logger

class LoadingThread(QThread):
    """加载线程，模拟耗时操作"""
    progress_updated = pyqtSignal(int)
    loading_finished = pyqtSignal()
    
    def run(self):
        """运行加载线程"""
        for i in range(101):
            self.progress_updated.emit(i)
            # 缩短加载时间，减少到0.06秒，总耗时约6秒
            time.sleep(0.06)
        self.loading_finished.emit()

class CustomProgressBar(QProgressBar):
    """自定义进度条，在中间显示百分比"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger().get_logger()
        # Hide default text to avoid overlap with custom percentage drawing
        self.setTextVisible(False)
        self.setAlignment(Qt.AlignCenter)
        
    def paintEvent(self, event):
        # 调用原始绘制方法
        super().paintEvent(event)
        
        # 在进度条中间绘制文本
        painter = QPainter(self)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        
        # 获取当前进度文本
        text = f"{self.value()}%"
        
        # 在中间绘制文本
        painter.drawText(self.rect(), Qt.AlignCenter, text)

class SplashScreen(QWidget):
    """启动画面窗口"""
    def __init__(self):
        super().__init__()
        
        # 加载设置，获取语言
        self.settings = Settings()
        self.current_language = self.settings.get_setting("language", "en").lower()
        
        self.setWindowTitle("Glary Utilities")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(600, 400)
        
        # 预先加载图标
        self._preload_resources()
        
        # 设置UI
        self.setup_ui()
        
        # 设置窗口的透明度为0，准备渐显效果
        self.setWindowOpacity(0.0)
        
        # 创建渐显动画
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(400) 
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutQuint)
        self.fade_anim.start()
        
        # 居中显示
        screen_geo = QApplication.desktop().screenGeometry()
        x = (screen_geo.width() - self.width()) // 2
        y = (screen_geo.height() - self.height()) // 2
        self.move(x, y)
        
        # 创建并启动加载线程
        self.loading_thread = LoadingThread()
        self.loading_thread.progress_updated.connect(self.update_progress)
        self.loading_thread.loading_finished.connect(self.finish_loading)
        self.loading_thread.start()
    
    def _preload_resources(self):
        """预加载资源文件"""
        icon_path = Icon.Icon.Path
        # 直接尝试加载图标，若文件不存在则保持 None
        self.app_icon = QPixmap(icon_path) if os.path.exists(icon_path) else None
    
    def get_translation(self, key, default):
        """获取翻译文本"""
        # 使用settings获取当前语言的翻译
        return self.settings.get_translation("splash_screen", key, default)
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建容器
        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet("""
            QWidget#container {
                background-color: #1e1e1e;
                border-radius: 10px;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 0)
        container.setGraphicsEffect(shadow)
        
        # 容器布局
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(15)
        
        # 添加标题
        title_label = QLabel("Glary Utilities")
        title_label.setStyleSheet("""
            color: #3498db;
            font-size: 36px;
            font-weight: bold;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)
        
        # 添加应用程序图标
        if self.app_icon:
            logo_label = QLabel(self)
            logo_label.setPixmap(self.app_icon.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(logo_label)
        
        # 添加描述 - 使用翻译
        desc_text = self.get_translation("description", 
                                        "System optimization and cleanup tool" if self.current_language == "en" else "系统优化和清理工具")
        
        desc_label = QLabel(desc_text)
        desc_label.setStyleSheet("""
            color: #bbbbbb;
            font-size: 16px;
        """)
        desc_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(desc_label)
        
        # 添加空白
        container_layout.addStretch()
        
        # 添加自定义进度条（在中间显示百分比）
        self.progress_bar = CustomProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)  # 增加高度以更好地显示文本
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
        
        # 添加状态文字 - 不再显示百分比，只显示状态描述
        self.status_label = QLabel(self.get_translation("initializing", 
                                                      "Initializing interface..." if self.current_language == "en" else "正在初始化界面..."))
        self.status_label.setStyleSheet("""
            color: #999999;
            font-size: 14px;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.status_label)
        
        # 添加版权信息
        copyright_text = self.get_translation("copyright", f"Version {App.version} | Copyright © 2025")
        # 替换版本号变量
        copyright_text = copyright_text.replace("{version}", App.version)
        version_label = QLabel(copyright_text)
        version_label.setStyleSheet("""
            color: #777777;
            font-size: 12px;
        """)
        version_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(version_label)
        
        # 将容器添加到主布局
        layout.addWidget(container)
        self.setLayout(layout)
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
        # 根据进度更新提示信息 - 使用翻译
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
        """完成加载"""
        # 创建渐隐动画
        self.fade_out_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_anim.setDuration(300)
        self.fade_out_anim.setStartValue(1.0)
        self.fade_out_anim.setEndValue(0.0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.OutQuint)
        self.fade_out_anim.finished.connect(self.close)
        self.fade_out_anim.start() 
        