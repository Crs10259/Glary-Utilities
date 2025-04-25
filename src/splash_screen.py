import os
import sys
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                            QProgressBar, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QPixmap, QColor, QPainter, QFont
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from config import Icon, version

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

class SplashScreen(QWidget):
    """启动画面窗口"""
    def __init__(self):
        super().__init__()
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
        self.fade_anim.setStartValue(0.0)
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
        # 预加载图标以确保显示正常
        self.app_icon = None
        icon_path = Icon.Icon.Path
        if os.path.exists(icon_path):
            try:
                self.app_icon = QPixmap(icon_path)
            except Exception as e:
                print(f"无法加载图标: {e}")
                self.app_icon = None
    
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
        
        # 添加描述
        desc_label = QLabel("系统优化和清理工具")
        desc_label.setStyleSheet("""
            color: #bbbbbb;
            font-size: 16px;
        """)
        desc_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(desc_label)
        
        # 添加空白
        container_layout.addStretch()
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)  # 隐藏百分比文本
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2d2d2d;
                border-radius: 5px;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 5px;
            }
        """)
        container_layout.addWidget(self.progress_bar)
        
        # 添加进度文字
        self.progress_label = QLabel("正在加载组件... 0%")
        self.progress_label.setStyleSheet("""
            color: #999999;
            font-size: 14px;
        """)
        self.progress_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.progress_label)
        
        # 添加版权信息
        version_label = QLabel(f"Version {version} | Copyright © 2025")
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
        self.progress_label.setText(f"正在加载组件... {value}%")
        
        # 根据进度更新提示信息
        if value < 20:
            self.progress_label.setText("正在初始化界面...")
        elif value < 40:
            self.progress_label.setText("正在加载系统组件...")
        elif value < 60:
            self.progress_label.setText("正在检查系统状态...")
        elif value < 80:
            self.progress_label.setText("正在准备工具组件...")
        else:
            self.progress_label.setText("即将完成...")
    
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
        