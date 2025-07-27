#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Linux窗口移动功能测试脚本
用于测试主窗口在Linux上的移动功能是否正常工作
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.base_tools import PlatformManager

class TestWindow(QMainWindow):
    """测试窗口类"""
    
    def __init__(self):
        super().__init__()
        self.platform_manager = PlatformManager()
        self.dragging = False
        self.drag_position = None
        
        # 设置窗口属性
        self.setWindowTitle("Linux窗口移动测试")
        self.setGeometry(200, 200, 400, 300)
        self.setMinimumSize(300, 200)
        
        # 使用自定义无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Linux特定的窗口属性优化
        if self.platform_manager.is_linux():
            self.setAttribute(Qt.WA_X11NetWmWindowTypeDesktop, False)
            self.setAttribute(Qt.WA_ShowWithoutActivating, False)
            self.setAttribute(Qt.WA_X11NetWmWindowTypeNormal, True)
        
        # 设置UI
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("Linux窗口移动测试")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 说明
        info = QLabel("请尝试拖动窗口标题栏或边缘来移动窗口")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        # 平台信息
        platform_info = QLabel(f"当前平台: {self.platform_manager.current_system}")
        platform_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(platform_info)
        
        # 测试按钮
        test_btn = QPushButton("测试按钮")
        test_btn.clicked.connect(self.test_click)
        layout.addWidget(test_btn)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: white;
            }
            QLabel {
                color: white;
                background-color: transparent;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 检查是否在标题栏区域或边缘
            if (event.pos().y() <= 40 or  # 标题栏区域
                event.pos().x() <= 5 or   # 左边缘
                event.pos().x() >= self.width() - 5 or  # 右边缘
                event.pos().y() <= 5 or   # 上边缘
                event.pos().y() >= self.height() - 5):  # 下边缘
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
            else:
                super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            # 使用统一的移动方法，适用于所有平台
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
        print("测试按钮被点击！窗口移动功能正常工作。")

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 检查平台
    platform_manager = PlatformManager()
    print(f"当前平台: {platform_manager.current_system}")
    print(f"是否为Linux: {platform_manager.is_linux()}")
    
    # 创建测试窗口
    window = TestWindow()
    window.show()
    
    print("测试窗口已显示，请尝试拖动窗口来测试移动功能")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 