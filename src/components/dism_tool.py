import os
import sys
import platform
import subprocess
import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QRadioButton, QTextEdit, QButtonGroup, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from components.base_component import BaseComponent


class DismThread(QThread):
    """DISM操作的工作线程"""
    progress_updated = pyqtSignal(str)
    operation_completed = pyqtSignal(bool, str)
    
    def __init__(self, operation):
        super().__init__()
        self.operation = operation  # 其中之一: check_health, scan_health, restore_health, cleanup_image
    
    def run(self):
        """运行工作线程"""
        if platform.system() != "Windows":
            self.progress_updated.emit("DISM仅在Windows上可用")
            self.operation_completed.emit(False, "此平台不支持该操作")
            return
        
        try:
            if self.operation == "check_health":
                self.check_health()
            elif self.operation == "scan_health":
                self.scan_health()
            elif self.operation == "restore_health":
                self.restore_health()
            elif self.operation == "cleanup_image":
                self.cleanup_image()
            else:
                self.progress_updated.emit(f"未知操作: {self.operation}")
                self.operation_completed.emit(False, "未知操作")
        except Exception as e:
            self.progress_updated.emit(f"执行操作时出错: {str(e)}")
            self.operation_completed.emit(False, str(e))
    
    def check_health(self):
        """检查Windows映像的健康状况"""
        self.progress_updated.emit("正在检查Windows映像健康状况...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/CheckHealth"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def scan_health(self):
        """扫描Windows映像的健康状况"""
        self.progress_updated.emit("正在扫描Windows映像健康状况...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/ScanHealth"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def restore_health(self):
        """恢复Windows映像的健康状况"""
        self.progress_updated.emit("正在恢复Windows映像健康状况...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/RestoreHealth"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def cleanup_image(self):
        """清理Windows映像"""
        self.progress_updated.emit("正在清理Windows映像...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/StartComponentCleanup"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def _process_output(self, proc):
        """处理DISM命令的输出"""
        success = True
        last_line = ""
        
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            
            line = line.strip()
            if line:
                self.progress_updated.emit(line)
                last_line = line
        
        proc.wait()
        
        if proc.returncode != 0:
            success = False
            last_line = f"操作失败，返回代码 {proc.returncode}"
        
        self.operation_completed.emit(success, last_line)

class DismToolWidget(BaseComponent):
    def __init__(self, parent=None):
        # 初始化属性
        self.dism_worker = None
        
        # 调用父类构造函数
        super().__init__(parent)
    
    def get_translation(self, key, default=None):
        """重写 get_translation 以使用正确的部分名称"""
        return self.settings.get_translation("dism_tool", key, default)
    
    def apply_theme(self):
        """应用主题样式到组件"""
        # 调用父类的应用主题方法，使用统一样式
        super().apply_theme()
        
    def setup_ui(self):
        # 主布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # 标题
        self.title = QLabel(self.get_translation("title"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0; background-color: transparent;")
        self.main_layout.addWidget(self.title)
        
        # 描述
        self.description = QLabel(self.get_translation("description"))
        self.description.setStyleSheet("font-size: 14px; color: #a0a0a0; background-color: transparent;")
        self.main_layout.addWidget(self.description)
        
        # 非Windows系统的警告标签
        if platform.system() != "Windows":
            warning_label = QLabel("⚠️ DISM仅在Windows系统上可用")
            warning_label.setStyleSheet("color: #ff9900; font-weight: bold; background-color: transparent;")
            self.main_layout.addWidget(warning_label)
        
        # 操作组
        self.operations_group = QGroupBox(self.get_translation("operations"))
        self.operations_group.setStyleSheet(""" 
            QGroupBox {
                color: #c0c0c0;
                font-weight: bold;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
                background-color: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: transparent;
            }
        """)
        operations_layout = QVBoxLayout(self.operations_group)
        
        # 操作选择的复选框
        self.operation_group = QButtonGroup(self)
        self.operation_group.setObjectName("dism_operation_group")
        
        self.check_health_rb = QRadioButton(self.get_translation("check_health"))
        self.check_health_rb.setChecked(True)
        self.check_health_rb.setObjectName("dism_check_health")
        operations_layout.addWidget(self.check_health_rb)
        self.operation_group.addButton(self.check_health_rb)
        
        self.scan_health_rb = QRadioButton(self.get_translation("scan_health"))
        self.scan_health_rb.setObjectName("dism_scan_health")
        operations_layout.addWidget(self.scan_health_rb)
        self.operation_group.addButton(self.scan_health_rb)
        
        self.restore_health_rb = QRadioButton(self.get_translation("restore_health"))
        self.restore_health_rb.setObjectName("dism_restore_health")
        operations_layout.addWidget(self.restore_health_rb)
        self.operation_group.addButton(self.restore_health_rb)
        
        self.cleanup_image_rb = QRadioButton(self.get_translation("cleanup_image"))
        self.cleanup_image_rb.setObjectName("dism_cleanup_image")
        operations_layout.addWidget(self.cleanup_image_rb)
        self.operation_group.addButton(self.cleanup_image_rb)
        
        # Connect button group to handler
        self.operation_group.buttonClicked.connect(self.on_operation_changed)
        
        self.main_layout.addWidget(self.operations_group)
        
        # 开始按钮
        self.start_button = QPushButton(self.get_translation("start_button"))
        self.start_button.setStyleSheet(""" 
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
        self.start_button.clicked.connect(self.start_operation)
        self.start_button.setEnabled(platform.system() == "Windows")
        
        # 按钮容器（用于右对齐）
        button_container = QWidget()
        button_container.setStyleSheet("background-color: transparent;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(self.start_button)
        
        self.main_layout.addWidget(button_container)
        
        # 日志输出
        self.log_label = QLabel(self.get_translation("log_output"))
        self.log_label.setStyleSheet("color: #a0a0a0; margin-top: 10px; background-color: transparent;")
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
        
        # 设置日志的最小高度
        self.log_output.setMinimumHeight(200)
        
        # 设置布局
        self.setLayout(self.main_layout)
        
        # 确保样式正确应用
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # 应用主题样式到单选按钮
        self.apply_theme()
    
    def start_operation(self):
        """开始选定的DISM操作"""
        operation = None
        
        if self.check_health_rb.isChecked():
            operation = "check_health"
        elif self.scan_health_rb.isChecked():
            operation = "scan_health"
        elif self.restore_health_rb.isChecked():
            operation = "restore_health"
        elif self.cleanup_image_rb.isChecked():
            operation = "cleanup_image"
        
        if not operation:
            return
        
        # 清除日志并禁用开始按钮
        self.log_output.clear()
        self.start_button.setEnabled(False)
        self.log_output.append(f"开始操作: {operation}")
        
        # 启动工作线程
        self.dism_worker = DismThread(operation)
        self.dism_worker.progress_updated.connect(self.update_log)
        self.dism_worker.operation_completed.connect(self.operation_completed)
        self.dism_worker.start()
    
    def update_log(self, message):
        """更新日志输出"""
        self.log_output.append(message)
        # 滚动到底部
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def operation_completed(self, success, message):
        """处理操作完成"""
        # 重新启用开始按钮
        self.start_button.setEnabled(True)
        
        # 将完成消息添加到日志
        if success:
            self.log_output.append("✅ 操作成功完成")
            self.log_output.append(message)
        else:
            self.log_output.append("❌ 操作失败")
            self.log_output.append(message)

    def refresh_language(self):
        """使用新翻译更新UI元素"""
        self.title.setText(self.get_translation("title"))
        self.description.setText(self.get_translation("description"))
        self.operations_group.setTitle(self.get_translation("operations"))
        self.check_health_rb.setText(self.get_translation("check_health"))
        self.scan_health_rb.setText(self.get_translation("scan_health"))
        self.restore_health_rb.setText(self.get_translation("restore_health"))
        self.cleanup_image_rb.setText(self.get_translation("cleanup_image"))
        self.start_button.setText(self.get_translation("start_button"))
        self.log_label.setText(self.get_translation("log_output"))
        
        # 添加动画以突出显示更改
        super().refresh_language()

    def check_all_translations(self):
        """检查此组件中使用的所有翻译键是否存在
        
        引发:
            KeyError: 如果缺少任何翻译键
        """
        # 尝试获取此组件中使用的所有翻译
        keys = [
            "title", "description", "operations", "check_health", 
            "scan_health", "restore_health", "cleanup_image",
            "start_button", "log_output"
        ]
        
        for key in keys:
            # 如果键不存在，将引发KeyError
            self.get_translation(key, None)

    def on_operation_changed(self, button):
        """处理操作选择的单选按钮变化"""
        # 获取当前选中的按钮
        selected_button = None
        
        if self.check_health_rb.isChecked():
            selected_button = self.check_health_rb
        elif self.scan_health_rb.isChecked():
            selected_button = self.scan_health_rb
        elif self.restore_health_rb.isChecked():
            selected_button = self.restore_health_rb
        elif self.cleanup_image_rb.isChecked():
            selected_button = self.cleanup_image_rb
            
        if selected_button:
            # 保存用户的选择到设置
            operation_key = selected_button.objectName()
            self.settings.set_setting("dism_operation", operation_key)
            self.settings.sync()  # 确保设置被保存
