import os
import sys
import platform
import subprocess
import time
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                          QLabel, QToolButton, QPushButton, QAction, QMenu, 
                          QSplitter, QToolBar, QStatusBar, QFrame, QSizePolicy, 
                          QStackedWidget, QLineEdit, QDialog, QDialogButtonBox, 
                          QTabWidget, QGridLayout, QSpacerItem, QScrollArea, 
                          QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
                          QGraphicsDropShadowEffect, QMenuBar, QApplication, QColorDialog,
                          QTextBrowser)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPainter, QPainterPath
from PyQt5.QtCore import (Qt, QSize, QPoint, QPropertyAnimation, 
                        QParallelAnimationGroup, QSequentialAnimationGroup,
                        QEasingCurve, pyqtSignal, QTimer, QAbstractAnimation,
                        QRect, QEvent, QObject)
import logging
import weakref
import json
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
import psutil

from components.base_component import BaseComponent
from components.dashboard import DashboardWidget
from components.system_cleaner import SystemCleanerWidget
from components.disk_check import DiskCheckWidget
from components.boot_repair import BootRepairWidget
from components.virus_scan import VirusScanWidget
from components.system_repair import SystemRepairWidget
from components.dism_tool import DismToolWidget
from components.network_reset import NetworkResetWidget
from components.system_info import SystemInfoWidget
from components.settings import SettingsWidget
from config import Icon, version

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GlaryUtilities")

class MainWindow(QMainWindow):
    """主应用程序窗口"""
    
    # 语言更改信号
    language_changed = pyqtSignal(str)
    page_changed = pyqtSignal(str)
    
    def __init__(self, settings):
        """初始化主窗口
        
        Args:
            settings: 设置管理器实例
        """
        super().__init__()
        
        # 保存设置实例
        self.settings = settings
        
        # 设置属性
        self.dragging = False
        self.drag_position = None
        self.current_page = "Dashboard"
        
        # 初始化字典
        self.page_buttons = {}
        
        # 设置窗口基本属性
        self.setWindowTitle("Glary Utilities")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)
        
        # 设置无边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # 设置样式表（基本样式，主题将在稍后应用）
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 初始化UI
        self.initUI()
        
        # 应用主题
        self.apply_theme()
        
        # 设置窗口图标
        self.apply_window_icon()
        
        # 初始化页面到Dashboard
        self.set_active_page("Dashboard")
        
        # 全局事件过滤器
        self.installEventFilter(self)
        
        # 语言更改信号
        self.language_changed.connect(self.change_language)
        
        # 验证翻译 - 查找缺失的键
        missing_translations = self.settings.validate_translations(raise_error=False)
        if missing_translations:
            logger.warning("Found missing translations!")
            for language, sections in missing_translations.items():
                logger.warning(f"\nLanguage: {language}")
                for section, keys in sections.items():
                    logger.warning(f"  Section: {section}")
                    for key in keys:
                        logger.warning(f"    - {key}")
        
        self.show_status_message(self.settings.get_translation("general", "welcome"), 5000)
        
        # 使用淡入动画显示窗口
        self.setWindowOpacity(0.0)

        # 检查是否启用动画 - 确保正确读取布尔值
        enable_animations = self.settings.get_setting("enable_animations", True)
        if isinstance(enable_animations, str):
            enable_animations = enable_animations.lower() in ('true', 'yes', '1', 'on')
        elif isinstance(enable_animations, int):
            enable_animations = enable_animations != 0
        else:
            enable_animations = bool(enable_animations)
            
        if enable_animations:
            self.fade_in_effect = QPropertyAnimation(self, b"windowOpacity")
            self.fade_in_effect.setDuration(400)  # 缩短时间，更快显示
            self.fade_in_effect.setStartValue(0.0)
            self.fade_in_effect.setEndValue(1.0)
            self.fade_in_effect.setEasingCurve(QEasingCurve.OutQuint)  # 使用更平滑的缓动曲线
            self.fade_in_effect.start(QAbstractAnimation.DeleteWhenStopped)
        else:
            # 如果动画被禁用，直接设置为完全不透明
            self.setWindowOpacity(1.0)
        
    def initUI(self):
        """初始化用户界面"""
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 自定义标题栏
        if self.settings.get_setting("use_system_title_bar", False) != True:
            self.title_bar = self.setup_title_bar()
            main_layout.addWidget(self.title_bar)
        
        # 内容布局
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 添加侧边栏
        self.sidebar = self.setup_sidebar()
        content_layout.addWidget(self.sidebar)
        
        # 添加内容区域
        self.setup_content_area()
        content_layout.addWidget(self.content_area)
        
        # 添加内容布局到主布局
        main_layout.addLayout(content_layout, 1)
        
        # 添加底部状态栏
        self.status_bar = self.setup_status_bar()
        main_layout.addWidget(self.status_bar)
        
        # 创建中心窗口部件
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        central_widget.setLayout(main_layout)
        
        # 设置窗口的主样式
        central_widget.setStyleSheet("""
            QWidget#central_widget {
                background-color: #252525;
                border-radius: 10px;
            }
        """)
        
        # 为窗口设置阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        central_widget.setGraphicsEffect(shadow)
        
        # 设置中心窗口部件
        self.setCentralWidget(central_widget)
        
        # 设置初始大小和最小大小
        self.resize(1200, 800)
        self.setMinimumSize(1000, 700)
        
        # 设置默认起始页面
        self.set_active_page("Dashboard")

        # 获取翻译的欢迎消息（从常规翻译中获取，而不是从main_window中获取，避免递归）
        welcome_message = "Welcome to Glary Utilities"
        try:
            lang = self.settings.get_setting("language", "en")
            language_map = {
                "en": "en", "english": "en", "English": "en",
                "zh": "zh", "中文": "zh", "chinese": "zh", "Chinese": "zh"
            }
            lang_code = language_map.get(lang.lower(), lang)
            
            if lang_code in self.settings.translations:
                translations = self.settings.translations[lang_code]
                if "general" in translations and "welcome" in translations["general"]:
                    welcome_message = translations["general"]["welcome"]
        except Exception as e:
            print(f"Error getting welcome message: {e}")
            
        self.show_status_message(welcome_message, 5000)
        
        # 使用淡入动画显示窗口
        self.setWindowOpacity(0.0)
        # 检查是否启用动画 - 确保正确读取布尔值
        enable_animations = self.settings.get_setting("enable_animations", True)
        if isinstance(enable_animations, str):
            enable_animations = enable_animations.lower() in ('true', 'yes', '1', 'on')
        elif isinstance(enable_animations, int):
            enable_animations = enable_animations != 0
        else:
            enable_animations = bool(enable_animations)
            
        if enable_animations:
            self.fade_in_effect = QPropertyAnimation(self, b"windowOpacity")
            self.fade_in_effect.setDuration(400)  # 缩短时间，更快显示
            self.fade_in_effect.setStartValue(0.0)
            self.fade_in_effect.setEndValue(1.0)
            self.fade_in_effect.setEasingCurve(QEasingCurve.OutQuint)  # 使用更平滑的缓动曲线
            self.fade_in_effect.start(QAbstractAnimation.DeleteWhenStopped)
        else:
            # 如果动画被禁用，直接设置为完全不透明
            self.setWindowOpacity(1.0)
        
    def setup_title_bar(self):
        """设置自定义标题栏"""
        # 创建标题栏
        self.title_bar = QFrame(self)
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(0)
        
        # 设置标题栏样式
        self.title_bar.setStyleSheet("""
            #titleBar {
                background-color: #2b2b2b;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            
            QLabel {
                background-color: transparent;
                color: #ffffff;
                font-weight: bold;
            }
            
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
            
            #closeButton:hover {
                background-color: #e81123;
                color: white;
            }
        """)
        
        # 添加应用图标
        app_icon = QLabel()
        app_icon.setPixmap(QPixmap(Icon.Icon.Path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        app_icon.setStyleSheet("background-color: transparent;")
        title_layout.addWidget(app_icon)
        
        # 添加标题文本
        self.title_label = QLabel("Glary Utilities")
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white; background-color: transparent; margin-left: 5px;")
        title_layout.addWidget(self.title_label)
        
        # 添加伸缩项以便将控制按钮推到右侧
        title_layout.addStretch(1)
        
        # 窗口控制按钮（最小化、最大化、关闭）
        # 最小化按钮
        self.minimize_button = QPushButton()
        self.minimize_button.setIcon(QIcon(Icon.Minimize.Path))
        self.minimize_button.setIconSize(QSize(16, 16))
        self.minimize_button.setFixedSize(34, 34)
        self.minimize_button.setToolTip("最小化")
        self.minimize_button.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.minimize_button)
        
        # 最大化/还原按钮
        self.maximize_button = QPushButton()
        self.maximize_button.setIcon(QIcon(Icon.Maximize.Path))
        self.maximize_button.setIconSize(QSize(16, 16))
        self.maximize_button.setFixedSize(34, 34)
        self.maximize_button.setToolTip("最大化")
        self.maximize_button.clicked.connect(self.toggle_maximize)
        title_layout.addWidget(self.maximize_button)
        
        # 关闭按钮
        self.close_button = QPushButton()
        self.close_button.setObjectName("closeButton")
        self.close_button.setIcon(QIcon(Icon.Close.Path))
        self.close_button.setIconSize(QSize(16, 16))
        self.close_button.setFixedSize(34, 34)
        self.close_button.setToolTip("关闭")
        self.close_button.clicked.connect(self.close)
        title_layout.addWidget(self.close_button)
        
        # 允许通过标题栏拖动窗口
        self.draggable = True
        
        return self.title_bar

    def toggle_maximize(self):
        """切换窗口最大化/还原状态"""
        if self.isMaximized():
            self.showNormal()
            self.maximize_button.setToolTip("最大化")
            self.maximize_button.setIcon(QIcon(Icon.Maximize.Path))
        else:
            self.showMaximized()
            self.maximize_button.setToolTip("还原")
            self.maximize_button.setIcon(QIcon(Icon.Restore.Path))
    
    # 事件处理用于窗口拖动与调整
    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            if self.title_bar.geometry().contains(event.pos()):
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
            else:
                super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            if self.isMaximized():
                # 如果窗口最大化，则先恢复到正常大小
                self.showNormal()
                # 调整拖拽位置，使光标位于窗口的相对位置
                ratio = event.pos().x() / self.width()
                self.drag_position = QPoint(int(self.width() * ratio), event.pos().y())
            
            self.move(event.globalPos() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """处理鼠标双击事件"""
        if event.button() == Qt.LeftButton:
            if self.title_bar.geometry().contains(event.pos()):
                self.toggle_maximize()
                event.accept()
            else:
                super().mouseDoubleClickEvent(event)
    
    def create_animated_action(self, icon, text, callback):
        """创建带有动画效果的工具栏操作"""
        action = QAction(icon, text, self)
        action.triggered.connect(callback)
        
        # 获取该操作对应的QToolButton
        action.button = None
        
        # 在下一个事件循环中查找按钮
        QTimer.singleShot(0, lambda: self.find_action_button(action))
        
        return action
    
    def setup_sidebar(self):
        """设置侧边栏"""
        # 创建侧边栏容器
        sidebar_container = QWidget()
        sidebar_container.setObjectName("sidebar_container")
        sidebar_container.setMaximumWidth(220)
        sidebar_container.setMinimumWidth(220)
        sidebar_container.setStyleSheet("""
            QWidget#sidebar_container {
                background-color: #1e1e1e;
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
                border-right: 1px solid #333333;
            }
        """)
        
        # 创建侧边栏垂直布局
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(12, 20, 12, 15)
        sidebar_layout.setSpacing(8)
        
        # 添加应用标志和标题
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(5, 0, 0, 15)
        
        # 将logo布局添加到侧边栏
        sidebar_layout.addLayout(logo_layout)

        # 添加分类标题：常用
        common_title = QLabel("Common")
        common_title.setStyleSheet("color: #999999; font-size: 13px; margin-top: 5px; background-color: transparent; font-weight: bold; padding-left: 2px;")
        sidebar_layout.addWidget(common_title)

        # 添加主要功能按钮
        self.dashboard_btn = self.create_sidebar_button(self.get_translation("dashboard", "Dashboard"), Icon.Dashboard.Path, "Dashboard", self.get_translation("dashboard_tooltip", "仪表盘"))
        sidebar_layout.addWidget(self.dashboard_btn)
        self.page_buttons["Dashboard"] = self.dashboard_btn
        
        self.system_cleaner_btn = self.create_sidebar_button(self.get_translation("system_cleaner", "System Cleaner"), Icon.Cleaner.Path, "System Cleaner", self.get_translation("system_cleaner_tooltip", "系统清理"))
        sidebar_layout.addWidget(self.system_cleaner_btn)
        self.page_buttons["System Cleaner"] = self.system_cleaner_btn
        
        self.registry_btn = self.create_sidebar_button(self.get_translation("system_repair", "System Repair"), Icon.Repair.Path, "System Repair", self.get_translation("system_repair_tooltip", "系统修复"))
        sidebar_layout.addWidget(self.registry_btn)
        self.page_buttons["System Repair"] = self.registry_btn
        
        self.disk_tools_btn = self.create_sidebar_button(self.get_translation("disk_check", "Disk Check"), Icon.Disk.Path, "Disk Check", self.get_translation("disk_check_tooltip", "磁盘检查"))
        sidebar_layout.addWidget(self.disk_tools_btn)
        self.page_buttons["Disk Check"] = self.disk_tools_btn
        
        self.startup_btn = self.create_sidebar_button(self.get_translation("boot_repair", "Boot Repair"), Icon.Boot.Path, "Boot Repair", self.get_translation("boot_repair_tooltip", "启动修复"))
        sidebar_layout.addWidget(self.startup_btn)
        self.page_buttons["Boot Repair"] = self.startup_btn
        
        self.uninstaller_btn = self.create_sidebar_button(self.get_translation("virus_scan", "Virus Scan"), Icon.Virus.Path, "Virus Scan", self.get_translation("virus_scan_tooltip", "病毒扫描"))
        sidebar_layout.addWidget(self.uninstaller_btn)
        self.page_buttons["Virus Scan"] = self.uninstaller_btn
        
        # 添加分类标题：安全
        security_title = QLabel(self.get_translation("security_section", "Security"))
        security_title.setStyleSheet("color: #999999; font-size: 13px; margin-top: 15px; background-color: transparent; font-weight: bold; padding-left: 12px;")
        sidebar_layout.addWidget(security_title)
        
        self.privacy_btn = self.create_sidebar_button(self.get_translation("network_reset", "Network Reset"), Icon.Privacy.Path, "Network Reset", self.get_translation("network_reset_tooltip", "网络重置"))
        sidebar_layout.addWidget(self.privacy_btn)
        self.page_buttons["Network Reset"] = self.privacy_btn
        
        # 添加分类标题：高级
        advanced_title = QLabel(self.get_translation("advanced_section", "Advanced"))
        advanced_title.setStyleSheet("color: #999999; font-size: 13px; margin-top: 15px; background-color: transparent; font-weight: bold; padding-left: 12px;")
        sidebar_layout.addWidget(advanced_title)
        
        # Use Icon.Dism.Path for DISM Tool
        self.driver_btn = self.create_sidebar_button(self.get_translation("dism_tool", "DISM Tool"), Icon.Dism.Path, "DISM Tool", self.get_translation("dism_tool_tooltip", "DISM工具"))
        sidebar_layout.addWidget(self.driver_btn)
        self.page_buttons["DISM Tool"] = self.driver_btn
        
        # Use Icon.SystemInfo.Path for System Information
        self.optimizer_btn = self.create_sidebar_button(self.get_translation("system_information", "System Information"), Icon.SystemInfo.Path, "System Information", self.get_translation("system_information_tooltip", "系统信息"))
        sidebar_layout.addWidget(self.optimizer_btn)
        self.page_buttons["System Information"] = self.optimizer_btn
        
        # 添加分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #333333; max-height: 1px;")
        sidebar_layout.addWidget(separator)
        sidebar_layout.addSpacing(8)

        # 添加设置按钮
        self.settings_btn = self.create_sidebar_button(self.get_translation("settings", "Settings"), Icon.Settings.Path, "Settings", self.get_translation("settings_tooltip", "设置"))
        sidebar_layout.addWidget(self.settings_btn)
        self.page_buttons["Settings"] = self.settings_btn

        # 添加弹性空间
        sidebar_layout.addStretch()

        # 添加版本信息
        version_label = QLabel(f"{self.get_translation('version', 'Version')} {version}")
        version_label.setStyleSheet("color: #666666; font-size: 11px; margin-top: 8px; background-color: transparent; text-align: center;")
        version_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(version_label)
        
        # 返回侧边栏容器
        return sidebar_container

    def create_sidebar_button(self, name, icon, page_name, tooltip=None):
        """创建侧边栏按钮"""
        try:
            # 获取主题颜色
            accent_color = self.settings.get_setting("accent_color", "#3498db")
        
            # 创建按钮
            button = QPushButton(name)
            button.setCheckable(True)
            button.setObjectName(f"sidebar_btn_{page_name}")
            button.setProperty("page", page_name)  # 使用自定义属性标记关联的页面
        
            # 设置图标
            if icon:
                button.setIcon(QIcon(icon))
        
            # 设置工具提示
            if tooltip:
                button.setToolTip(tooltip)
            
            # 设置图标大小 - 增大为28x28尺寸
            icon_size = QSize(28, 28)
            button.setIconSize(icon_size)
            
            # 保存原始图标大小
            button._original_icon_size = icon_size
        
        except Exception as e:
            logger.error(f"创建侧边栏按钮时出错: {e}")
            # 创建不带图标的按钮
            button = QPushButton(name)
            button.setCheckable(True)
            button.setObjectName(f"sidebar_btn_{page_name}")
            button.setProperty("page", page_name)
            if tooltip:
                button.setToolTip(tooltip)
        
        # 设置基本样式，添加过渡动画和左侧彩色指示条
        base_style = f"""
            QPushButton {{
                text-align: left;
                padding-left: 15px;
                border: none;
                border-radius: 10px;
                color: #cccccc;
                font-size: 14px;
                background-color: transparent;
                margin: 6px 5px;
                border-left: 3px solid transparent;
                font-weight: normal;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.15);
                color: #ffffff;
                border-left: 3px solid {accent_color}80;
            }}
            QPushButton:checked {{
                background-color: rgba(52, 152, 219, 0.25);
                color: #ffffff;
                font-weight: bold;
                border-left: 3px solid {accent_color};
            }}
            QPushButton:pressed {{
                background-color: rgba(52, 152, 219, 0.15);
            }}
        """
        button.setStyleSheet(base_style)
        
        # 固定按钮高度和最小宽度，调整高度为52px
        button.setMinimumHeight(52)
        button.setMaximumHeight(52)
        button.setMinimumWidth(170)
        
        # 检查是否启用动画
        enable_animations = self.settings.get_setting("enable_animations", True)
        if isinstance(enable_animations, str):
            enable_animations = enable_animations.lower() in ('true', 'yes', '1', 'on')
        elif isinstance(enable_animations, int):
            enable_animations = enable_animations != 0
        else:
            enable_animations = bool(enable_animations)
        
        # 如果启用了动画，则设置悬停和按下时的图标大小变化效果
        if enable_animations:
            # 创建动画组
            self.hover_animation = QParallelAnimationGroup()
            self.press_animation = QParallelAnimationGroup()
            
            # 当鼠标悬停时增大图标
            def on_hover(hovered):
                if hovered:
                    target_size = QSize(32, 32)  # 悬停时图标大小增加
                    anim = QPropertyAnimation(button, b"iconSize")
                    anim.setDuration(150)
                    anim.setStartValue(button.iconSize())
                    anim.setEndValue(target_size)
                    anim.start()
                else:
                    # 恢复原始大小
                    anim = QPropertyAnimation(button, b"iconSize")
                    anim.setDuration(150)
                    anim.setStartValue(button.iconSize())
                    anim.setEndValue(button._original_icon_size)
                    anim.start()
            
            # 当按下时缩小图标
            def on_press(pressed):
                if pressed:
                    target_size = QSize(26, 26)  # 按下时图标大小减小
                    anim = QPropertyAnimation(button, b"iconSize")
                    anim.setDuration(100)
                    anim.setStartValue(button.iconSize())
                    anim.setEndValue(target_size)
                    anim.start()
            
            # 连接事件
            button.installEventFilter(self)
            button.enterEvent = lambda e: on_hover(True)
            button.leaveEvent = lambda e: on_hover(False)
            button.pressed.connect(lambda: on_press(True))
            button.released.connect(lambda: on_hover(True))  # 释放后恢复为悬停状态
        
        # 连接按钮点击事件
        button.clicked.connect(lambda: self.set_active_page(page_name))
        
        return button

    def setup_content_area(self):
        """设置主要内容区域"""
        # 创建QStackedWidget以便在不同页面之间切换
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("content_area")
        self.content_area.setStyleSheet("""
            QStackedWidget {
                background-color: transparent;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        
        # 创建页面实例
        self.dashboard_page = DashboardWidget(self)
        self.dashboard_page.setObjectName("Dashboard")
        
        self.system_cleaner_page = SystemCleanerWidget(self)
        self.system_cleaner_page.setObjectName("System Cleaner")
        
        self.registry_page = SystemRepairWidget(self)
        self.registry_page.setObjectName("System Repair")
        
        self.disk_tools_page = DiskCheckWidget(self)
        self.disk_tools_page.setObjectName("Disk Check")
        
        self.startup_page = BootRepairWidget(self)
        self.startup_page.setObjectName("Boot Repair")
        
        self.uninstaller_page = VirusScanWidget(self)
        self.uninstaller_page.setObjectName("Virus Scan")
        
        self.privacy_page = NetworkResetWidget(self)
        self.privacy_page.setObjectName("Network Reset")
        
        self.driver_page = DismToolWidget(self)
        self.driver_page.setObjectName("DISM Tool")
        
        self.optimizer_page = SystemInfoWidget(self)
        self.optimizer_page.setObjectName("System Information")
        
        self.settings_page = SettingsWidget(self.settings, self)
        self.settings_page.setObjectName("Settings")
        
        # 将页面添加到内容区域
        self.content_area.addWidget(self.dashboard_page)
        self.content_area.addWidget(self.system_cleaner_page)
        self.content_area.addWidget(self.registry_page)
        self.content_area.addWidget(self.disk_tools_page)
        self.content_area.addWidget(self.startup_page)
        self.content_area.addWidget(self.uninstaller_page)
        self.content_area.addWidget(self.privacy_page)
        self.content_area.addWidget(self.driver_page)
        self.content_area.addWidget(self.optimizer_page)
        self.content_area.addWidget(self.settings_page)
        
        # 创建页面索引字典
        self.page_indices = {
            "Dashboard": 0,
            "System Cleaner": 1,
            "System Repair": 2,
            "Disk Check": 3,
            "Boot Repair": 4,
            "Virus Scan": 5,
            "Network Reset": 6,
            "DISM Tool": 7,
            "System Information": 8,
            "Settings": 9
        }
        
        # 页面初始化后，将所有页面的边距设为0
        for i in range(self.content_area.count()):
            page = self.content_area.widget(i)
            if isinstance(page, QWidget):
                page.setContentsMargins(0, 0, 0, 0)

    def apply_theme(self):
        """应用当前主题"""
        theme_name = self.settings.get_setting("theme", "dark")
        
        # 加载主题数据
        theme_data = self.settings.load_theme(theme_name)
        
        if not theme_data:
            # 如果主题数据不可用，使用内置的暗色主题
            default_style = """
                QWidget {
                    background-color: #1e1e1e;
                color: #cccccc;
                    font-family: 'Segoe UI', Arial, sans-serif;
            }
                QLabel {
                background-color: transparent;
                    color: #cccccc;
            }
            QPushButton {
                background-color: #3a3a3a;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    color: #e0e0e0;
                    padding: 4px 8px;
            }
            QPushButton:hover {
                    background-color: #505050;
                }
                QPushButton:pressed {
                    background-color: #2a2a2a;
                }
                QLineEdit {
                    background-color: #2d2d2d;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    color: #e0e0e0;
                    padding: 4px;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                }
                QTabBar::tab {
                    background-color: #3a3a3a;
                    border: 1px solid #555555;
                    border-bottom-color: #555555;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 6px 10px;
                    color: #bbbbbb;
                }
                QTabBar::tab:selected {
            background-color: #1e1e1e;
                    border-bottom-color: #1e1e1e;
                    color: #ffffff;
                }
                QTabBar::tab:!selected {
                    margin-top: 2px;
                }
                QScrollBar:vertical {
            border: none;
                    background: #2d2d2d;
                    width: 12px;
                    margin: 0px 0px 0px 0px;
                }
                QScrollBar::handle:vertical {
                    background: #4d4d4d;
                    min-height: 20px;
                    border-radius: 6px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar:horizontal {
                    border: none;
                    background: #2d2d2d;
                    height: 12px;
                    margin: 0px 0px 0px 0px;
                }
                QScrollBar::handle:horizontal {
                    background: #4d4d4d;
                    min-width: 20px;
                    border-radius: 6px;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
            QMenuBar {
                    background-color: #252525;
                    border-bottom: 1px solid #333333;
            }
            QMenuBar::item {
                    spacing: 6px;
                    padding: 3px 10px;
                    background: transparent;
                    color: #e0e0e0;
            }
            QMenuBar::item:selected {
                    background: #3a3a3a;
                    border-radius: 4px;
            }
            QMenu {
                    background-color: #2d2d2d;
                    border: 1px solid #555555;
                    border-radius: 4px;
            }
            QMenu::item {
                    padding: 5px 30px 5px 15px;
                    color: #e0e0e0;
            }
            QMenu::item:selected {
                background-color: #3a3a3a;
                    color: #ffffff;
                }
                QMenu::separator {
                    height: 1px;
                    background: #555555;
                    margin: 5px 10px;
                }
            """
            self.setStyleSheet(default_style)
        else:
            # 使用加载的主题数据
            accent_color = self.settings.get_setting("accent_color", theme_data.get("accent_color", "#3498db"))
            theme_style = theme_data.get("style", "")
            # 替换任何颜色占位符
            if "{accent_color}" in theme_style:
                theme_style = theme_style.replace("{accent_color}", accent_color)
            self.setStyleSheet(theme_style)
            
        # 更新组件主题
        self.update_component_themes()
            
    def update_component_themes(self):
        """Update the theme for all components"""
        # 检查content_area是否存在
        try:
            # Find all BaseComponent widgets and refresh their themes
            for i in range(self.content_area.count()):
                widget = self.content_area.widget(i)
                if widget:
                    # Recursively update all child components
                    self.refresh_component_theme(widget)
        except AttributeError:
            pass
                
    def refresh_component_theme(self, widget):
        """Recursively refresh theme for a widget and its children"""
        # 检查是否为特殊的组件类型，这些类型需要调用特定的主题方法
        component_name = widget.__class__.__name__
        
        # 优先使用特定组件的apply_current_theme方法
        if component_name in ["BootRepairWidget", "VirusScanWidget"]:
            try:
                if hasattr(widget, 'apply_current_theme') and callable(widget.apply_current_theme):
                    widget.apply_current_theme()
                    return  # 已应用特定组件的主题方法，无需继续
            except Exception as e:
                print(f"Error applying custom theme to {component_name}: {str(e)}")
        
        # 对于其他标准组件，应用通用的apply_theme方法
        try:
            if hasattr(widget, 'apply_theme') and callable(widget.apply_theme):
                widget.apply_theme()
        except Exception as e:
            print(f"Error applying theme to widget: {str(e)}")
            
        # Process children
        for child in widget.findChildren(QWidget):
            self.refresh_component_theme(child)

    def apply_window_icon(self):
        """设置窗口图标"""
        try:
            # 直接使用资源目录中的图标文件
            icon_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "icon.png")
            if not os.path.exists(icon_path):
                self.logger.warning(f"警告: 窗口图标文件不存在: {icon_path}")
                return
                
            self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            self.logger.error(f"设置窗口图标时出错: {str(e)}")
    
    def set_active_page(self, page_name):
        """设置活动页面
        
        Args:
            page_name: 页面名称
        """
        # 如果页面名称无效，使用默认值
        if not page_name:
            page_name = "Dashboard"
            
        # 如果是相同页面，不执行任何操作
        if self.current_page == page_name:
            return
            
        # 检查页面是否存在于索引字典中
        if page_name not in self.page_indices:
            print(f"错误: 找不到页面 '{page_name}'")
            return
            
        # 获取页面索引
        page_index = self.page_indices[page_name]
        
        # 获取当前页面和新页面
        old_page = self.content_area.currentWidget()
        new_page = self.content_area.widget(page_index)
        
        # 更新当前页面
        old_page_name = self.current_page
        self.current_page = page_name
        
        # 检查是否启用动画
        enable_animations = self.settings.get_setting("enable_animations", True)
        if isinstance(enable_animations, str):
            enable_animations = enable_animations.lower() in ('true', 'yes', '1', 'on')
        elif isinstance(enable_animations, int):
            enable_animations = enable_animations != 0
        else:
            enable_animations = bool(enable_animations)
            
        # 如果动画被禁用，直接切换
        if not enable_animations:
            self.content_area.setCurrentIndex(page_index)
            self._update_active_button(page_name)
            self.page_changed.emit(page_name)
            return
        
        # 设置页面过渡方向（根据页面名称确定方向）
        page_order = list(self.page_indices.keys())
        
        try:
            old_index = page_order.index(old_page_name)
            new_index = page_order.index(page_name)
            direction = "left" if new_index > old_index else "right"
        except (ValueError, IndexError):
            # 如果页面不在列表中，默认向左滑动
            direction = "left"
            
        # 获取页面宽度
        width = self.content_area.width()
        
        # 首先确保两个页面都可见（但只显示当前页面）
        new_page.show()
        old_page.show()
        
        # 设置初始位置 - 新页面位于边界之外
        old_page_pos = old_page.pos()
        if direction == "left":
            new_page.move(old_page_pos.x() + width, old_page_pos.y())
        else:
            new_page.move(old_page_pos.x() - width, old_page_pos.y())
            
        # 如果已有动画正在运行，停止它
        if hasattr(self, '_page_animation') and self._page_animation is not None:
            try:
                self._page_animation.stop()
            except RuntimeError:
                # 动画可能已被删除或处于无效状态
                pass
        
        # 创建动画组
        self._page_animation = QParallelAnimationGroup()
        
        # 旧页面动画
        old_anim = QPropertyAnimation(old_page, b"pos")
        old_anim.setDuration(300) # 略微加快过渡
        old_anim.setStartValue(old_page_pos)
        if direction == "left":
            old_anim.setEndValue(QPoint(old_page_pos.x() - width, old_page_pos.y()))
        else:
            old_anim.setEndValue(QPoint(old_page_pos.x() + width, old_page_pos.y()))
        old_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # 新页面动画
        new_anim = QPropertyAnimation(new_page, b"pos")
        new_anim.setDuration(300) # 和旧页面动画相同的时长
        if direction == "left":
            new_anim.setStartValue(QPoint(old_page_pos.x() + width, old_page_pos.y()))
        else:
            new_anim.setStartValue(QPoint(old_page_pos.x() - width, old_page_pos.y()))
        new_anim.setEndValue(old_page_pos)
        new_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # 添加动画到组
        self._page_animation.addAnimation(old_anim)
        self._page_animation.addAnimation(new_anim)
        
        # 动画结束后的处理
        self._page_animation.finished.connect(lambda: animation_finished())
        
        # 启动动画
        self._page_animation.start(QAbstractAnimation.DeleteWhenStopped)
        
        # 在动画开始时更新活动按钮
        self._update_active_button(page_name)
        
        # 触发页面更改信号
        self.page_changed.emit(page_name)
        
        def animation_finished():
            # 隐藏旧页面，将新页面设置为当前页面
            old_page.hide()
            self.content_area.setCurrentWidget(new_page)
            
            # 标记动画已完成
            self._page_animation = None
            
            # 确保设置窗口标题和焦点等
            self.setWindowTitle(f"Glary Utilities - {page_name}")
        
    def _update_page_content(self, page_name):
        """根据页面名称更新内容区域"""
        logger.info(f"切换到页面: {page_name}")
        
        # 获取页面的本地化显示名称
        page_display_name = self.settings.get_translation("general", page_name.lower().replace(' ', '_'))
        
        # 更新窗口标题和工具栏标题
        self.setWindowTitle(f"Glary Utilities - {page_display_name}")
        if hasattr(self, 'title_label'):
            self.title_label.setText(f"Glary Utilities - {page_display_name}")
        
        # 更新激活的按钮状态
        self._update_active_button(page_name)
        
        # 如果有搜索框，清除搜索
        if hasattr(self, 'search_box'):
            self.search_box.clear()
            
        try:
            # 如果页面索引存在，则直接切换到该页面
            if page_name in self.page_indices:
                self.content_area.setCurrentIndex(self.page_indices[page_name])
                
                # 获取当前页面部件
                current_widget = self.content_area.currentWidget()
                
                # 切换到此页面后，让页面部件自动更新数据
                if hasattr(current_widget, 'update_data') and callable(getattr(current_widget, 'update_data')):
                    current_widget.update_data()
                    
                # 保存当前页面名称
                self.current_page = page_name
                
                # 发射页面切换信号
                self.page_changed.emit(page_name)
            else:
                # 如果页面不存在，显示一个错误消息
                logger.warning(f"未找到页面 '{page_name}' 的索引")
                self.show_status_message(f"页面 '{page_name}' 不存在", 3000)
                
        except Exception as e:
            # 处理异常情况
            logger.error(f"切换到页面 '{page_name}' 时出错：{e}")
            error_widget = QLabel(f"加载页面时出错：{e}")
            error_widget.setStyleSheet("color: red;")
            error_widget.setAlignment(Qt.AlignCenter)
            
            # 创建一个临时页面显示错误
            temp_page = QWidget()
            temp_layout = QVBoxLayout(temp_page)
            temp_layout.addWidget(error_widget)
            
            # 将错误页面添加到内容区域
            error_index = self.content_area.addWidget(temp_page)
            self.content_area.setCurrentIndex(error_index)
    
    def change_language(self, language):
        """Change application language
        
        Args:
            language: Language code or name to set
        """
        try:
            # Save language setting
            self.settings.set_setting("language", language)
            self.settings.sync()
            
            # Update UI to reflect new language
            self.update_ui_language()
            
            # Emit language change signal
            self.language_changed.emit(language)
            
            # Show a message indicating language was changed
            language_display = "English" if language == "en" else "中文"
            self.show_status_message(f"Language changed to {language_display}")
        except Exception as e:
            print(f"Error changing language: {str(e)}")
    
    def update_ui_texts(self):
        """Update all UI text elements with current language translations"""
        # Loop through all defined page buttons and update their text
        for button_name, button in self.page_buttons.items():
            translated_name = self.settings.get_translation("general", button_name.lower().replace(' ', '_'))
            button.setText(translated_name)
    
    def update_ui_language(self):
        """更新 UI 的语言"""
        # 获取当前活动页面并更新相关UI
        active_page = self.current_page
        page_display_name = self.settings.get_translation("general", active_page.lower().replace(' ', '_'))
        
        # 更新按钮文本
        for button_name, button in self.page_buttons.items():
            translated_name = self.settings.get_translation("general", button_name.lower().replace(' ', '_'))
            button.setText(translated_name)
        
        # 更新标题
        self.setWindowTitle(f"Glary Utilities - {page_display_name}")
        if hasattr(self, 'title_label'):
            self.title_label.setText(f"Glary Utilities - {page_display_name}")
        
        # 刷新所有支持语言更新的组件
        for widget_name in dir(self):
            widget = getattr(self, widget_name)
            if hasattr(widget, 'update_language') and callable(getattr(widget, 'update_language')):
                widget.update_language()
    
    def refresh_all_components(self):
        """刷新所有组件"""
        # 循环浏览所有内容页面并更新它们
        for i in range(self.content_area.count()):
            widget = self.content_area.widget(i)
            # (无限递归问题修复) 如果组件有refresh_language方法，调用它
            if hasattr(widget, 'refresh_language') and callable(getattr(widget, 'refresh_language')):
                QTimer.singleShot(i * 10, lambda w=widget: w.refresh_language())  # 延迟执行以避免UI冻结
                
        # (无限递归问题修复) 更新所有侧边栏按钮 - 避免使用get_translation
        for button in self.findChildren(QPushButton):
            if hasattr(button, 'property') and button.property("page"):
                page_name = button.property("page")
                # 直接从main_window部分获取翻译，而不是从general部分
                translation_key = page_name.lower().replace(' ', '_')
                try:
                    # 尝试从main_window部分获取翻译文本
                    lang = self.settings.get_setting("language", "en")
                    translated_text = None
                    
                    # 获取语言代码
                    language_map = {
                        "en": "en", "english": "en", "English": "en",
                        "zh": "zh", "中文": "zh", "chinese": "zh", "Chinese": "zh"
                    }
                    lang_code = language_map.get(lang.lower(), lang)
                    
                    # 直接从翻译字典获取翻译文本
                    if lang_code in self.settings.translations:
                        translations = self.settings.translations[lang_code]
                        if "main_window" in translations and translation_key in translations["main_window"]:
                            translated_text = translations["main_window"][translation_key]
                        elif "en" in self.settings.translations and "main_window" in self.settings.translations["en"] and translation_key in self.settings.translations["en"]["main_window"]:
                            translated_text = self.settings.translations["en"]["main_window"][translation_key]
                    
                    # 如果找到翻译，则设置按钮文本
                    if translated_text:
                        button.setText(translated_text)
                except Exception as e:
                    # 如果出错，使用原始页面名称
                    print(f"Error updating button text: {e}")
                    # 保持原有文本，不做更改
                
        # 更新工具栏
        self.update_ui_texts()
                
        # 强制重绘整个UI
        self.update()
        
        # 处理任何等待的事件，确保UI即时更新
        QApplication.processEvents()
    
    def check_all_translations(self):
        """检查所有必要的翻译是否都存在"""
        # 修复递归问题：使用新添加的settings.validate_translations方法
        # 而不是手动调用get_translation检查每个键
        try:
            missing = self.settings.validate_translations()
            
            if missing:
                current_lang = self.settings.get_setting("language", "en")
                if current_lang in missing:
                    missing_in_current = missing[current_lang]
                    # 记录当前语言中缺失的翻译
                    for section, keys in missing_in_current.items():
                        for key in keys:
                            logging.warning(f"Missing translation for '{section}.{key}' in language '{current_lang}'")
            return True
        except Exception as e:
            logging.error(f"Error checking translations: {e}")
            return False

    def apply_transparency(self):
        """Apply window transparency from settings"""
        try:
            # Get transparency value from settings (100 means fully opaque)
            transparency = int(self.settings.get_setting("window_transparency", 100))
            
            # Ensure value is within valid range
            transparency = max(70, min(100, transparency))
            
            # Only apply transparency if less than 100%
            if transparency < 100:
                try:
                    # Set window transparency
                    self.setWindowOpacity(transparency / 100.0)
                    print(f"Applied window transparency: {transparency}%")
                except Exception as e:
                    # Log the error but continue
                    print(f"Error applying window transparency: {str(e)}")
                    # Reset to fully opaque
                    self.settings.set_setting("window_transparency", 100)
            else:
                # Fully opaque
                self.setWindowOpacity(1.0)
        except Exception as e:
            print(f"Error in apply_transparency: {str(e)}")
            # Reset to default
            self.setWindowOpacity(1.0)
    
    def show_status_message(self, message, timeout=2000):
        """显示状态栏消息"""
        # 在控制台记录消息
        logging.debug(f"状态消息: {message}")
        
        # 更新状态栏标签
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)
            
            # 设置临时样式以突出显示
            self.status_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
            
            # 使用定时器恢复正常样式
            QTimer.singleShot(timeout, lambda: self.status_label.setStyleSheet("color: #bbbbbb; font-size: 12px;"))

    def setup_status_bar(self):
        """创建底部状态栏"""
        status_bar = QFrame()
        status_bar.setObjectName("status_bar")
        status_bar.setFixedHeight(30)
        status_bar.setStyleSheet("""
            QFrame#status_bar {
                background-color: #2d2d2d;
                border-top: 1px solid #444444;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        
        # 状态栏布局
        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        
        # 状态信息标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #bbbbbb; font-size: 12px; background-color: transparent;")
        layout.addWidget(self.status_label)
        
        # 添加弹性空间
        layout.addStretch(1)
        
        return status_bar
        

    def _update_active_button(self, page_name):
        """更新侧边栏中活动页面按钮的状态
        
        Args:
            page_name: 活动页面的名称
        """
        # 遍历所有侧边栏按钮，更新它们的状态
        for button in self.findChildren(QPushButton):
            if hasattr(button, 'property') and button.property("page"):
                # 检查按钮是否对应当前活动页面
                is_active = button.property("page") == page_name
                
                # 设置选中状态
                button.setChecked(is_active)
                
                # 更新样式以反映选中状态
                if is_active:
                    button.setProperty("active", "true")
                else:
                    button.setProperty("active", "false")
                
                # 强制重新应用样式表
                button.style().unpolish(button)
                button.style().polish(button)
                button.update()

    def clear_layout(self, layout):
        """清除布局中的所有部件
        
        Args:
            layout: 要清除的布局对象
        """
        if layout is None:
            return
            
        # 移除布局中的所有项目
        while layout.count():
            item = layout.takeAt(0)
            
            # 如果项目是部件，则删除
            if item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()
            # 如果项目是布局，递归清除
            elif item.layout():
                self.clear_layout(item.layout())

    def get_translation(self, key, default=None):
        """Get translation for UI text using the main window section
        
        Args:
            key: Translation key
            default: Default text if translation not found
            
        Returns:
            Translated text
        """
        return self.settings.get_translation("main_window", key, default)
 