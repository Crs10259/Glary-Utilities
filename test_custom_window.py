#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自定义无边框窗口测试脚本
用于测试在Linux上使用自定义无边框窗口的效果
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                          QLabel, QPushButton, QHBoxLayout, QFrame)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QIcon

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.base_tools import PlatformManager

class CustomTitleBar(QFrame):
    """自定义标题栏"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.dragging = False
        self.drag_position = None
        
        self.setFixedHeight(40)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)
        
        # 标题
        title = QLabel("自定义窗口测试")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # 控制按钮
        minimize_btn = QPushButton("─")
        minimize_btn.setFixedSize(34, 34)
        minimize_btn.clicked.connect(self.parent.showMinimized)
        minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(34, 34)
        close_btn.clicked.connect(self.parent.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e81123;
            }
        """)
        
        layout.addWidget(minimize_btn)
        layout.addWidget(close_btn)
        
        # 设置标题栏样式
        self.setStyleSheet("""
            CustomTitleBar {
                background-color: #2b2b2b;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            new_pos = event.globalPos() - self.drag_position
            # 确保窗口不会移出屏幕
            screen_geometry = QApplication.primaryScreen().geometry()
            new_pos.setX(max(0, min(new_pos.x(), screen_geometry.width() - self.parent.width())))
            new_pos.setY(max(0, min(new_pos.y(), screen_geometry.height() - self.parent.height())))
            self.parent.move(new_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

class CustomWindow(QMainWindow):
    """自定义窗口类"""
    
    def __init__(self):
        super().__init__()
        self.platform_manager = PlatformManager()
        self.dragging = False
        self.drag_position = None
        
        # 设置窗口属性
        self.setWindowTitle("自定义无边框窗口测试")
        self.setGeometry(200, 200, 500, 400)
        self.setMinimumSize(400, 300)
        
        # 使用自定义无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Linux特定的窗口属性优化
        if self.platform_manager.is_linux():
            self.setAttribute(Qt.WA_X11NetWmWindowTypeDesktop, False)
            self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        
        # 设置UI
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 自定义标题栏
        self.title_bar = CustomTitleBar(self)
        layout.addWidget(self.title_bar)
        
        # 内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("自定义无边框窗口测试")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white;")
        content_layout.addWidget(title)
        
        # 说明
        info = QLabel("这是一个完全自定义的无边框窗口，包含自定义标题栏和控制按钮")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: white; margin: 10px;")
        info.setWordWrap(True)
        content_layout.addWidget(info)
        
        # 平台信息
        platform_info = QLabel(f"当前平台: {self.platform_manager.current_system}")
        platform_info.setAlignment(Qt.AlignCenter)
        platform_info.setStyleSheet("color: #cccccc;")
        content_layout.addWidget(platform_info)
        
        # 测试按钮
        test_btn = QPushButton("测试按钮")
        test_btn.clicked.connect(self.test_click)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        content_layout.addWidget(test_btn)
        
        # 添加伸缩空间
        content_layout.addStretch()
        
        # 设置内容区域样式
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        
        layout.addWidget(content_widget)
        
        # 设置主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: transparent;
            }
        """)
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 检查是否在窗口边缘
            edge_margin = 5
            if (event.pos().x() <= edge_margin or 
                event.pos().x() >= self.width() - edge_margin or
                event.pos().y() <= edge_margin or
                event.pos().y() >= self.height() - edge_margin):
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
            else:
                super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            new_pos = event.globalPos() - self.drag_position
            # 确保窗口不会移出屏幕
            screen_geometry = QApplication.primaryScreen().geometry()
            new_pos.setX(max(0, min(new_pos.x(), screen_geometry.width() - self.width())))
            new_pos.setY(max(0, min(new_pos.y(), screen_geometry.height() - self.height())))
            self.move(new_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def test_click(self):
        """测试按钮点击"""
        print("测试按钮被点击！自定义窗口功能正常工作。")

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 检查平台
    platform_manager = PlatformManager()
    print(f"当前平台: {platform_manager.current_system}")
    print(f"是否为Linux: {platform_manager.is_linux()}")
    
    # 创建自定义窗口
    window = CustomWindow()
    window.show()
    
    print("自定义无边框窗口已显示")
    print("功能测试:")
    print("1. 拖动标题栏移动窗口")
    print("2. 拖动窗口边缘移动窗口")
    print("3. 点击最小化按钮")
    print("4. 点击关闭按钮")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 