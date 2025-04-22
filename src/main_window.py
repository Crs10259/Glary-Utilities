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
                          QGraphicsDropShadowEffect, QMenuBar, QApplication, QColorDialog)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPainter, QPainterPath
from PyQt5.QtCore import (Qt, QSize, QPoint, QPropertyAnimation, 
                        QParallelAnimationGroup, QSequentialAnimationGroup,
                        QEasingCurve, pyqtSignal, QTimer, QAbstractAnimation,
                        QRect, QEvent, QObject)
import logging
import weakref
import json
from typing import Dict, List, Tuple, Any, Optional, Union, Callable

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
from components.icons import Icon
from utils.animations import AnimationUtils
from utils.settings_manager import Settings
from utils.theme_manager import ThemeManager

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GlaryUtilities")

class MainWindow(QMainWindow):
    """主应用程序窗口"""
    
    # 语言更改信号
    language_changed = pyqtSignal(str)
    
    def __init__(self, settings):
        """初始化主窗口"""
        super().__init__()
        
        # 设置窗口标题和属性
        self.setWindowTitle("Glary Utilities")
        self.settings = settings
        
        # 应用当前主题
        self.apply_theme()
        
        # 移除默认的窗口边框
        if self.settings.get_setting("use_system_title_bar", False) != True:
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)
            
        # 当前激活的页面
        self.current_page = None
        
        # 动画存储
        self._page_animation = None
        
        # 初始化用户界面
        self.initUI()
        
        # 全局事件过滤器
        self.installEventFilter(self)
        
        # 语言更改信号
        self.language_changed.connect(self.change_language)
        
        # 验证翻译 - 查找缺失的键
        missing_translations = self.settings.validate_translations(raise_error=False)
        if missing_translations:
            print("Warning: Found missing translations!")
            for language, sections in missing_translations.items():
                print(f"\nLanguage: {language}")
                for section, keys in sections.items():
                    print(f"  Section: {section}")
                    for key in keys:
                        print(f"    - {key}")
        
        # 应用窗口图标
        self.apply_window_icon()
        
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

        self.show_status_message(self.settings.get_translation("general", "welcome"), 5000)
        
        # 使用淡入动画显示窗口
        self.setWindowOpacity(0.0)
        # 检查是否启用动画
        if self.settings.get_setting("enable_animations", True):
            self.fade_in_effect = QPropertyAnimation(self, b"windowOpacity")
            self.fade_in_effect.setDuration(800)
            self.fade_in_effect.setStartValue(0.0)
            self.fade_in_effect.setEndValue(1.0)
            self.fade_in_effect.setEasingCurve(QEasingCurve.OutCubic)
            self.fade_in_effect.start()
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
        app_icon.setPixmap(QPixmap("resources/icons/icon.png").scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
        self.minimize_button.setIcon(QIcon("resources/icons/minimize.svg"))
        self.minimize_button.setIconSize(QSize(16, 16))
        self.minimize_button.setFixedSize(34, 34)
        self.minimize_button.setToolTip("最小化")
        self.minimize_button.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.minimize_button)
        
        # 最大化/还原按钮
        self.maximize_button = QPushButton()
        self.maximize_button.setIcon(QIcon("resources/icons/maximize.svg"))
        self.maximize_button.setIconSize(QSize(16, 16))
        self.maximize_button.setFixedSize(34, 34)
        self.maximize_button.setToolTip("最大化")
        self.maximize_button.clicked.connect(self.toggle_maximize)
        title_layout.addWidget(self.maximize_button)
        
        # 关闭按钮
        self.close_button = QPushButton()
        self.close_button.setObjectName("closeButton")
        self.close_button.setIcon(QIcon("resources/icons/close.svg"))
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
            self.maximize_button.setIcon(QIcon("resources/icons/maximize.svg"))
        else:
            self.showMaximized()
            self.maximize_button.setToolTip("还原")
            self.maximize_button.setIcon(QIcon("resources/icons/restore.svg"))
    
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
    
    def find_action_button(self, action_obj):
        """查找与操作相关联的按钮"""
        # 不再使用toolbar，直接返回
        return None
    
    def setup_sidebar(self):
        """设置侧边栏"""
        # 创建侧边栏容器
        sidebar_container = QWidget()
        sidebar_container.setObjectName("sidebar_container")
        sidebar_container.setMaximumWidth(200)
        sidebar_container.setMinimumWidth(200)
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
        sidebar_layout.setContentsMargins(10, 15, 10, 10)
        sidebar_layout.setSpacing(6)
        
        # 添加应用标志和标题
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(5, 0, 0, 10)
        
        # 添加应用图标
        app_icon = QLabel()
        app_icon.setPixmap(QPixmap("resources/icons/icon.png").scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        app_icon.setStyleSheet("background-color: transparent;")
        logo_layout.addWidget(app_icon)
        
        # 添加应用名称
        app_name = QLabel("Glary Utilities")
        app_name.setStyleSheet("color: #e0e0e0; font-size: 18px; font-weight: bold; background-color: transparent;")
        logo_layout.addWidget(app_name)
        
        # 将logo布局添加到侧边栏
        sidebar_layout.addLayout(logo_layout)
        
        # 添加分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #333333; max-height: 1px;")
        sidebar_layout.addWidget(separator)
        sidebar_layout.addSpacing(5)
        
        # 添加主要功能按钮
        self.dashboard_btn = self.create_sidebar_button("Dashboard", "dashboard.png", "Dashboard", "仪表盘")
        sidebar_layout.addWidget(self.dashboard_btn)
        
        self.system_cleaner_btn = self.create_sidebar_button("System Cleaner", "clean.png", "System Cleaner", "系统清理")
        sidebar_layout.addWidget(self.system_cleaner_btn)
        
        self.registry_btn = self.create_sidebar_button("System Repair", "registry.png", "System Repair", "系统修复")
        sidebar_layout.addWidget(self.registry_btn)
        
        self.disk_tools_btn = self.create_sidebar_button("Disk Check", "disk.png", "Disk Check", "磁盘检查")
        sidebar_layout.addWidget(self.disk_tools_btn)
        
        self.startup_btn = self.create_sidebar_button("Boot Repair", "startup.png", "Boot Repair", "启动修复")
        sidebar_layout.addWidget(self.startup_btn)
        
        self.uninstaller_btn = self.create_sidebar_button("Virus Scan", "uninstall.png", "Virus Scan", "病毒扫描")
        sidebar_layout.addWidget(self.uninstaller_btn)
        
        # 添加分类标题：安全
        security_title = QLabel("Security")
        security_title.setStyleSheet("color: #888888; font-size: 12px; margin-top: 10px; background-color: transparent; font-weight: bold; padding-left: 10px;")
        sidebar_layout.addWidget(security_title)
        
        self.privacy_btn = self.create_sidebar_button("Network Reset", "privacy.png", "Network Reset", "网络重置")
        sidebar_layout.addWidget(self.privacy_btn)
        
        # 添加分类标题：高级
        advanced_title = QLabel("Advanced")
        advanced_title.setStyleSheet("color: #888888; font-size: 12px; margin-top: 10px; background-color: transparent; font-weight: bold; padding-left: 10px;")
        sidebar_layout.addWidget(advanced_title)
        
        self.driver_btn = self.create_sidebar_button("DISM Tool", "driver.png", "DISM Tool", "DISM工具")
        sidebar_layout.addWidget(self.driver_btn)
        
        self.optimizer_btn = self.create_sidebar_button("System Information", "optimize.png", "System Information", "系统信息")
        sidebar_layout.addWidget(self.optimizer_btn)
        
        # 添加弹性空间
        sidebar_layout.addStretch()
        
        # 添加设置按钮
        self.settings_btn = self.create_sidebar_button("Settings", "settings.png", "Settings", "设置")
        sidebar_layout.addWidget(self.settings_btn)
        
        # 添加版本信息
        version_label = QLabel("Version 1.0.0")
        version_label.setStyleSheet("color: #666666; font-size: 11px; margin-top: 5px; background-color: transparent; text-align: center;")
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
            
            # 设置图标 - 增强图标加载逻辑
            icon_loaded = False
            icon_path = ""
            
            if isinstance(icon, str):
                # 1. 检查是否为SVG图标路径
                if icon.endswith('.svg') and os.path.exists(icon):
                    icon_path = icon
                    button.setIcon(QIcon(icon_path))
                    icon_loaded = True
                    
                # 2. 检查资源目录下的图标 (SVG优先)
                elif not icon.startswith(':'):
                    base_icon_name = os.path.basename(icon)
                    svg_resource_path = os.path.join("resources", "icons", base_icon_name.replace('.png', '.svg'))
                    png_resource_path = os.path.join("resources", "icons", base_icon_name)
                    
                    if os.path.exists(svg_resource_path):
                        icon_path = svg_resource_path
                        button.setIcon(QIcon(icon_path))
                        icon_loaded = True
                    elif os.path.exists(png_resource_path):
                        icon_path = png_resource_path
                        button.setIcon(QIcon(icon_path))
                        icon_loaded = True
                        
                # 3. 检查Qt资源路径
                elif icon.startswith(':'):
                    icon_path = icon
                    button.setIcon(QIcon(icon_path))
                    icon_loaded = True
                    
                # 4. 尝试使用Icon类加载
                if not icon_loaded:
                    # 尝试从Icon类获取图标
                    icon_parts = icon.split('/')[-1].split('.')[0]  # 提取基本图标名
                    icon_parts = icon_parts.title().replace('-', '').replace('_', '')  # 转换为首字母大写形式
                    
                    if hasattr(Icon, icon_parts):
                        icon_class = getattr(Icon, icon_parts)
                        if hasattr(icon_class, 'Path') and Icon.IconBase.exists(icon_class.Path):
                            icon_path = icon_class.Path
                            button.setIcon(QIcon(icon_path))
                            icon_loaded = True
            elif isinstance(icon, QIcon) and not icon.isNull():
                button.setIcon(icon)
                icon_loaded = True
                
            # 如果所有方法都失败，使用占位符图标
            if not icon_loaded:
                placeholder_path = os.path.join("resources", "icons", "placeholder.svg")
                if os.path.exists(placeholder_path):
                    button.setIcon(QIcon(placeholder_path))
                    print(f"使用占位符图标: {placeholder_path}")
                else:
                    print(f"警告: 无法加载图标: {icon}, 也没有找到占位符图标")
                
            # 设置工具提示
            if tooltip:
                button.setToolTip(tooltip)
            
            # 设置图标大小
            button.setIconSize(QSize(20, 20))
            
            # 保存原始图标大小
            button._original_icon_size = QSize(20, 20)
        
        except Exception as e:
            print(f"创建侧边栏按钮时出错: {e}")
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
                border-radius: 6px;
                color: #cccccc;
                font-size: 14px;
                background-color: transparent;
                margin: 2px 0px;
                border-left: 3px solid transparent;
                font-weight: normal;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.08);
                color: #e0e0e0;
                border-left: 3px solid {accent_color}80;
            }}
            QPushButton:checked {{
                background-color: rgba(52, 152, 219, 0.2);
                color: #ffffff;
                font-weight: bold;
                border-left: 3px solid {accent_color};
            }}
            QPushButton:pressed {{
                background-color: rgba(52, 152, 219, 0.1);
            }}
        """
        button.setStyleSheet(base_style)
        
        # 固定按钮高度和最小宽度
        button.setMinimumHeight(40)
        button.setMaximumHeight(40)
        button.setMinimumWidth(160)
        
        # 创建鼠标悬停动画效果
        def enterEvent(e):
            # 创建图标大小动画
            anim = QPropertyAnimation(button, b"iconSize")
            button._hover_animation = anim
            anim.setDuration(150)  # 减少动画持续时间，使其更快响应
            anim.setStartValue(button.iconSize())
            anim.setEndValue(QSize(24, 24))  # 轻微增大图标
            anim.setEasingCurve(QEasingCurve.OutQuad)  # 更平滑的缓动曲线
            anim.start()
            QApplication.instance().processEvents()
            QPushButton.enterEvent(button, e)
            
        def leaveEvent(e):
            # 如果按钮未选中，则恢复原始图标大小
            if not button.isChecked():
                anim = QPropertyAnimation(button, b"iconSize")
                button._hover_animation = anim
                anim.setDuration(150)
                anim.setStartValue(button.iconSize())
                anim.setEndValue(button._original_icon_size)
                anim.setEasingCurve(QEasingCurve.OutQuad)
                anim.start()
            QPushButton.leaveEvent(button, e)
        
        # 添加点击动画
        def mousePressEvent(e):
            # 创建点击时的收缩动画
            anim = QPropertyAnimation(button, b"iconSize")
            anim.setDuration(100)
            anim.setStartValue(button.iconSize())
            anim.setEndValue(QSize(18, 18))  # 轻微缩小图标
            anim.setEasingCurve(QEasingCurve.OutQuad)
            anim.start()
            QPushButton.mousePressEvent(button, e)
            
        def mouseReleaseEvent(e):
            # 点击释放时的展开动画
            if not button.isChecked():
                anim = QPropertyAnimation(button, b"iconSize")
                anim.setDuration(100)
                anim.setStartValue(button.iconSize())
                anim.setEndValue(QSize(24, 24))
                anim.setEasingCurve(QEasingCurve.OutQuad)
                anim.start()
            else:
                # 如果按钮被选中，保持较大的图标尺寸
                anim = QPropertyAnimation(button, b"iconSize")
                anim.setDuration(100)
                anim.setStartValue(button.iconSize())
                anim.setEndValue(QSize(24, 24))
                anim.setEasingCurve(QEasingCurve.OutQuad)
                anim.start()
            QPushButton.mouseReleaseEvent(button, e)
        
        # 覆盖按钮的事件处理方法
        button.enterEvent = enterEvent
        button.leaveEvent = leaveEvent
        button.mousePressEvent = mousePressEvent
        button.mouseReleaseEvent = mouseReleaseEvent
        
        # 连接点击事件
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
        self.system_cleaner_page = SystemCleanerWidget(self)
        self.registry_page = SystemRepairWidget(self)  # 使用真实组件
        self.disk_tools_page = DiskCheckWidget(self)  # 使用真实组件
        self.startup_page = BootRepairWidget(self)  # 使用真实组件
        self.uninstaller_page = VirusScanWidget(self)  # 使用真实组件
        self.privacy_page = NetworkResetWidget(self)  # 使用真实组件
        self.driver_page = DismToolWidget(self)  # 使用真实组件
        self.optimizer_page = SystemInfoWidget(self)  # 使用真实组件
        self.settings_page = SettingsWidget(self.settings, self)
        
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

    def setup_menu_bar(self):
        """设置菜单栏"""
        # 不再需要菜单栏
        pass
    
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
        if not hasattr(self, 'content_area'):
            return
            
        # Find all BaseComponent widgets and refresh their themes
        for i in range(self.content_area.count()):
            widget = self.content_area.widget(i)
            if widget:
                # Recursively update all child components
                self.refresh_component_theme(widget)
                
    def refresh_component_theme(self, widget):
        """Recursively refresh theme for a widget and its children"""
        # If this is a BaseComponent, apply theme
        if hasattr(widget, 'apply_theme') and callable(widget.apply_theme):
            widget.apply_theme()
            
        # Process children
        for child in widget.findChildren(QWidget):
            self.refresh_component_theme(child)

    def apply_window_icon(self):
        """应用窗口图标"""
        # 检查图标是否存在
        icon_path = Icon.Icon.Path
        if os.path.exists(icon_path):
            window_icon = QIcon(icon_path)
            if not window_icon.isNull():
                self.setWindowIcon(window_icon)
            else:
                print(f"警告: 无法加载窗口图标: {icon_path}")
        else:
            print(f"警告: 窗口图标文件不存在: {icon_path}")
 
    
    def set_active_page(self, page_name):
        """设置活动页面"""
        # 如果页面名称相同，则不执行任何操作
        if hasattr(self, 'current_page') and self.current_page == page_name:
            return
            
        previous_page = getattr(self, 'current_page', None)
        self.current_page = page_name
        
        # 更新侧边栏按钮状态
        for button in self.findChildren(QPushButton):
            if hasattr(button, 'property') and button.property("page") == page_name:
                button.setChecked(True)
                # 停止该按钮的任何正在运行的动画
                if hasattr(button, '_hover_animation') and button._hover_animation is not None:
                    try:
                        if isinstance(button._hover_animation, QPropertyAnimation) and button._hover_animation.state() == QAbstractAnimation.Running:
                            button._hover_animation.stop()
                    except (RuntimeError, ReferenceError):
                        # 如果动画对象已经被删除，清空引用
                        button._hover_animation = None
            elif hasattr(button, 'property') and button.property("page"):
                button.setChecked(False)
                
        # 如果找不到页面索引，则不执行任何操作
        if page_name not in self.page_indices:
            logging.error(f"页面 '{page_name}' 不存在")
            return
            
        target_index = self.page_indices[page_name]
        current_index = self.content_area.currentIndex()
        
        # 显示状态消息
        message = f"{self.settings.get_translation('general', 'switched_to', 'Switched to')} {page_name}"
        self.show_status_message(message, 2000)
        
        # 如果当前没有活动页面或点击的是当前页面，直接设置
        if current_index == -1 or current_index == target_index:
            self.content_area.setCurrentIndex(target_index)
            self._update_page_content(page_name, target_index)
            return
        
        # 停止所有正在运行的页面切换动画
        if hasattr(self, '_page_animation') and self._page_animation is not None:
            try:
                if isinstance(self._page_animation, QParallelAnimationGroup) and self._page_animation.state() == QAbstractAnimation.Running:
                    self._page_animation.stop()
            except (RuntimeError, ReferenceError):
                # 如果动画对象已经被删除，清空引用
                self._page_animation = None
                
        # 创建页面切换动画
        self._page_animation = QParallelAnimationGroup()
        
        # 当前页面和目标页面
        current_widget = self.content_area.widget(current_index)
        target_widget = self.content_area.widget(target_index)
        
        # 确定动画方向（左或右）
        direction = 1 if target_index > current_index else -1
        
        # 创建淡出效果和移动效果的组合
        
        # 当前页面淡出+滑动动画
        fade_out = QPropertyAnimation(current_widget, b"geometry")
        fade_out.setDuration(300)  # 增加持续时间
        current_geo = current_widget.geometry()
        fade_out.setStartValue(current_geo)
        fade_out.setEndValue(QRect(
            current_geo.x() - direction * current_geo.width() // 2,  # 减少移动距离
            current_geo.y(),
            current_geo.width(),
            current_geo.height()
        ))
        fade_out.setEasingCurve(QEasingCurve.OutQuint)  # 更平滑的缓动曲线
        
        # 当前页面透明度动画
        opacity_out = QPropertyAnimation(current_widget, b"windowOpacity")
        opacity_out.setDuration(300)
        opacity_out.setStartValue(1.0)
        opacity_out.setEndValue(0.0)
        opacity_out.setEasingCurve(QEasingCurve.OutQuint)
        
        # 目标页面淡入+滑动动画
        fade_in = QPropertyAnimation(target_widget, b"geometry")
        fade_in.setDuration(300)
        target_geo = target_widget.geometry()
        fade_in.setStartValue(QRect(
            target_geo.x() + direction * target_geo.width() // 2,  # 减少移动距离
            target_geo.y(),
            target_geo.width(),
            target_geo.height()
        ))
        fade_in.setEndValue(target_geo)
        fade_in.setEasingCurve(QEasingCurve.OutQuint)
        
        # 目标页面透明度动画
        opacity_in = QPropertyAnimation(target_widget, b"windowOpacity")
        opacity_in.setDuration(300)
        opacity_in.setStartValue(0.0)
        opacity_in.setEndValue(1.0)
        opacity_in.setEasingCurve(QEasingCurve.OutQuint)
        
        # 添加动画到组
        self._page_animation.addAnimation(fade_out)
        self._page_animation.addAnimation(opacity_out)
        self._page_animation.addAnimation(fade_in)
        self._page_animation.addAnimation(opacity_in)
        
        # 准备动画
        current_widget.setWindowOpacity(1.0)
        target_widget.setWindowOpacity(0.0)
        target_widget.show()
        
        # 在动画结束时切换页面并更新内容
        def animation_finished():
            self.content_area.setCurrentIndex(target_index)
            self._update_page_content(page_name, target_index)
            
        # 连接动画完成信号
        self._page_animation.finished.connect(animation_finished)
        
        # 启动动画
        self._page_animation.start(QAbstractAnimation.DeleteWhenStopped)
    
    def _update_page_content(self, page_name, target_index):
        """更新页面内容和标题"""
        # 更新活动页面的内容（如果需要）
        active_widget = self.content_area.widget(target_index)
        
        # 更新窗口标题
        self.setWindowTitle(f"Glary Utilities - {page_name}")
        
        # 更新主工具栏标题
        self.title_label.setText(self.settings.get_translation("general", page_name.lower().replace(' ', '_')))
        
        # 如果页面有刷新方法，则调用它
        if hasattr(active_widget, 'refresh'):
            active_widget.refresh()
    
    def change_language(self, language):
        """Handle language changes"""
        # Update UI elements with new translations
        self.update_ui_texts()
        
        # Notify all child components of the language change
        for i in range(self.content_area.count()):
            widget = self.content_area.widget(i)
            if hasattr(widget, 'refresh_language') and callable(getattr(widget, 'refresh_language')):
                widget.refresh_language()
    
    def update_ui_texts(self):
        """Update all UI text elements with current language translations"""
        # Update sidebar buttons
        for name, button in self.page_buttons.items():
            button.setText(self.tr(name))
    
    def update_ui_language(self, language):
        """在语言更改后更新UI元素"""
        for name in self.page_indices.keys():
            label = getattr(self, f"label_{name.lower().replace(' ', '_')}", None)
            if label:
                label.setText(self.settings.get_translation("general", name.lower().replace(' ', '_')))
        
        # 更新窗口控制按钮文本
        self.minimize_button.setToolTip(self.settings.get_translation("general", "minimize"))
        if self.isMaximized():
            self.maximize_button.setToolTip(self.settings.get_translation("general", "restore"))
        else:
            self.maximize_button.setToolTip(self.settings.get_translation("general", "maximize"))
        self.close_button.setToolTip(self.settings.get_translation("general", "close"))
        
        active_page = None
        for name, index in self.page_indices.items():
            if self.content_area.currentIndex() == index:
                active_page = name
                break
                
        if active_page:
            self.title_label.setText(self.settings.get_translation("general", active_page.lower().replace(' ', '_')))
        
        self.refresh_all_components()
        
        self.status_bar.showMessage(f"语言已更改为 {language}", 3000)
        
        AnimationUtils.highlight(self.central_widget, duration=300)
    
    def refresh_all_components(self):
        """刷新所有组件"""
        # 循环浏览所有内容页面并更新它们
        for i in range(self.content_area.count()):
            widget = self.content_area.widget(i)
            # 如果组件有refresh_language方法，调用它
            if hasattr(widget, 'refresh_language') and callable(getattr(widget, 'refresh_language')):
                QTimer.singleShot(i * 10, lambda w=widget: w.refresh_language())  # 延迟执行以避免UI冻结
                
        # 更新所有侧边栏按钮
        for button in self.findChildren(QPushButton):
            if hasattr(button, 'property') and button.property("page"):
                page_name = button.property("page")
                button.setText(self.settings.get_translation("general", page_name.lower().replace(' ', '_')))
                
        # 更新工具栏
        self.update_ui_texts()
                
        # 强制重绘整个UI
        self.update()
        
        # 处理任何等待的事件，确保UI即时更新
        QApplication.processEvents()
    
    def check_all_translations(self):
        """检查所有组件中的所有翻译是否存在
        
        引发:
            KeyError: 如果缺少任何翻译键
        """
        menu_keys = ["exit", "help", "about", "system_info", "language"]
        for key in menu_keys:
            self.settings.get_translation("menu", key)
        
        # 检查所有组件页面的翻译
        if hasattr(self, 'dashboard_page'):
            self.dashboard_page.check_all_translations()
        if hasattr(self, 'system_cleaner_page'):
            self.system_cleaner_page.check_all_translations()
        if hasattr(self, 'registry_page'):
            self.registry_page.check_all_translations()
        if hasattr(self, 'disk_tools_page'):
            self.disk_tools_page.check_all_translations()
        if hasattr(self, 'startup_page'):
            self.startup_page.check_all_translations()
        if hasattr(self, 'uninstaller_page'):
            self.uninstaller_page.check_all_translations()
        if hasattr(self, 'privacy_page'):
            self.privacy_page.check_all_translations()
        if hasattr(self, 'driver_page'):
            self.driver_page.check_all_translations()
        if hasattr(self, 'optimizer_page'):
            self.optimizer_page.check_all_translations()
        if hasattr(self, 'settings_page'):
            self.settings_page.check_all_translations()
    
    def show_about_dialog(self):
        """显示关于对话框"""
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle(self.settings.get_translation("menu", "about"))
        about_dialog.setMinimumSize(500, 400)
        about_dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
            QTextBrowser {
                background-color: #252526;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #444444;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        
        layout = QVBoxLayout(about_dialog)
        
        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/images/icon.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(logo_label)
        
        title_layout = QVBoxLayout()
        title_label = QLabel("Glary Utilities")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        version_label = QLabel("Version 1.0.0")
        version_label.setStyleSheet("color: #a0a0a0;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(version_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        about_text = QTextBrowser()
        about_text.setOpenExternalLinks(True)
        about_text.setHtml("""
            <h3>Development Team</h3>
            <p>Glary Utilities is developed by a dedicated team of software engineers and UX designers passionate about creating efficient system maintenance tools.</p>
            
            <h3>Core Team</h3>
            <ul>
                <li><b>Chen Runsen</b> - Project Lead & Senior Developer</li>
                <li><b>Zhang Wei</b> - UI/UX Designer</li>
                <li><b>Li Mei</b> - Backend Developer</li>
                <li><b>Wang Jian</b> - QA Engineer</li>
            </ul>
            
            <h3>Special Thanks</h3>
            <p>We would like to thank all our users for their valuable feedback and support.</p>
            
            <p>&copy; 2025 Glary Utilities Team. All rights reserved.</p>
        """)
        
        layout.addWidget(about_text)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(about_dialog.accept)
        layout.addWidget(button_box)
        
        about_dialog.exec_()

    def show_help_dialog(self):
        """显示帮助对话框，提供使用说明"""
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle(self.settings.get_translation("menu", "help"))
        help_dialog.setMinimumSize(700, 500)
        help_dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
            QTextBrowser {
                background-color: #252526;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #444444;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """) 
        
        layout = QVBoxLayout(help_dialog)
        
        # 标题
        title_label = QLabel("Glary Utilities - User Guide")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        help_content = QTextBrowser()
        help_content.setOpenExternalLinks(True)
        help_content.setHtml("""
            <h2>Getting Started with Glary Utilities</h2>
            
            <p>Glary Utilities is a comprehensive system maintenance tool designed to help you keep your computer running efficiently. This guide will walk you through the main features and how to use them.</p>
            
            <h3>Main Features</h3>
            
            <h4>Dashboard</h4>
            <p>The Dashboard provides an overview of your system status, including CPU usage, memory usage, and disk space. It also offers quick access to the most commonly used tools.</p>
            
            <h4>System Cleaner</h4>
            <p>The System Cleaner helps you remove unnecessary files to free up disk space. To use it:</p>
            <ol>
                <li>Select the types of files you want to scan for (temporary files, cache files, etc.)</li>
                <li>Click "Scan Now" to find unnecessary files</li>
                <li>Review the scan results and select the files you want to remove</li>
                <li>Click "Clean Selected" to delete the selected files</li>
            </ol>
            
            <h4>Disk Check</h4>
            <p>The Disk Check utility checks for disk errors and fixes them:</p>
            <ol>
                <li>Select the drive you want to check</li>
                <li>Choose the type of check you want to perform</li>
                <li>Click "Check Disk" to begin the scan</li>
                <li>If errors are found, click "Repair Disk" to fix them</li>
            </ol>
            
            <h4>Virus Scan</h4>
            <p>The Virus Scan feature helps you detect malware on your system:</p>
            <ol>
                <li>Select the locations you want to scan</li>
                <li>Choose the scan type (quick, full, or custom)</li>
                <li>Click "Start Scan" to begin scanning for viruses</li>
                <li>If threats are found, click "Clean Threats" to remove them</li>
            </ol>
            
            <h4>System Repair</h4>
            <p>The System Repair tool checks for and fixes system issues:</p>
            <ol>
                <li>Select the types of issues you want to scan for</li>
                <li>Click "Scan Now" to identify issues</li>
                <li>Review the results and select the issues you want to fix</li>
                <li>Click "Repair Selected" to fix the selected issues</li>
            </ol>
            
            <h4>Boot Repair</h4>
            <p>The Boot Repair utility helps fix Windows boot issues:</p>
            <ol>
                <li>Select the operations you want to perform (rebuild BCD, fix MBR, etc.)</li>
                <li>Click "Repair Boot" to fix boot problems</li>
            </ol>
            
            <h4>Network Reset</h4>
            <p>The Network Reset tool helps resolve network connectivity issues:</p>
            <ol>
                <li>Select the operations you want to perform</li>
                <li>Click "Reset Network" to reset your network settings</li>
            </ol>
            
            <h4>Settings</h4>
            <p>The Settings page allows you to customize the application according to your preferences:</p>
            <ul>
                <li>Change the language</li>
                <li>Choose a theme (light, dark, or custom)</li>
                <li>Set startup options</li>
                <li>Configure advanced settings</li>
            </ul>
            
            <h3>Keyboard Shortcuts</h3>
            <ul>
                <li><b>Alt+F4:</b> Exit the application</li>
                <li><b>Ctrl+S:</b> Save settings</li>
                <li><b>F1:</b> Open this help</li>
                <li><b>F5:</b> Refresh current view</li>
            </ul>
            
            <p>For additional help or support, please visit our website or contact our support team.</p>
        """)
        
        layout.addWidget(help_content)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(help_dialog.accept)
        layout.addWidget(button_box)
        
        help_dialog.exec_()

    def show_system_info(self):
        """显示系统信息对话框"""
        system_info_dialog = QDialog(self)
        system_info_dialog.setWindowTitle(self.settings.get_translation("menu", "system_info"))
        system_info_dialog.setMinimumSize(500, 400)
        system_info_dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
            QTextBrowser {
                background-color: #252526;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #444444;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """) 
        
        layout = QVBoxLayout(system_info_dialog)
        
        try:
            cpu_info = self.settings.get_system_info("cpu")
            memory_info = self.settings.get_system_info("memory")
            disk_info = self.settings.get_system_info("disk")
            os_info = self.settings.get_system_info("os")
            app_list = self.settings.get_system_info("app_list")
            env_vars = self.settings.get_system_info("env_vars")
            ip_address = self.settings.get_system_info("ip_address")
            mac_address = self.settings.get_system_info("mac_address")
        except Exception as e:
            print(f"Error retrieving system info: {e}")
            cpu_info = "Not available"
            memory_info = "Not available"
            disk_info = "Not available"
            os_info = "Not available"
            app_list = "Not available"
            env_vars = "Not available"
            ip_address = "Not available"
            mac_address = "Not available"
        
        # 系统信息内容
        system_info_content = QTextBrowser()
        system_info_content.setOpenExternalLinks(True)
        system_info_content.setHtml(f"""
            <h2>System Information</h2>
            
            <p>This section provides detailed information about your system.</p>
            
            <h3>Hardware</h3>
            <ul>
                <li><b>CPU:</b> {cpu_info}</li>
                <li><b>Memory:</b> {memory_info}</li>
                <li><b>Disk:</b> {disk_info}</li>
            </ul>
            
            <h3>Operating System</h3>
            <p><b>OS:</b> {os_info}</p>
            
            <h3>Installed Applications</h3>
            <ul>
                {app_list}
            </ul>
            
            <h3>Environment Variables</h3>
            <ul>
                {env_vars}
            </ul>
            
            <h3>Network</h3>
            <p><b>IP Address:</b> {ip_address}</p>
            <p><b>MAC Address:</b> {mac_address}</p>
            
            <h3>System Logs</h3>
            <p>For more detailed system information, please check the system logs.</p>
        """)
        
        layout.addWidget(system_info_content)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(system_info_dialog.accept)
        layout.addWidget(button_box)
        
        system_info_dialog.exec_()

    def apply_transparency(self):
        """应用窗口透明度设置"""
        # 获取透明度设置（0-100）
        transparency = self.settings.get_setting("window_transparency", 100)
        
        # 将百分比转换为0.0-1.0范围
        opacity = transparency / 100.0
        
        # 确保在有效范围内
        opacity = max(0.3, min(1.0, opacity))  # 限制最小透明度为30%，避免窗口完全看不见
        
        # 应用透明度
        self.setWindowOpacity(opacity)
        
        # 如果透明度低于100%，确保窗口背景能够正确显示
        if opacity < 1.0:
            # 允许背景透明
            self.setAttribute(Qt.WA_TranslucentBackground, True)
        else:
            # 完全不透明时无需设置透明背景
            self.setAttribute(Qt.WA_TranslucentBackground, False)
    
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
        
        # 系统资源指标
        self.resource_layout = QHBoxLayout()
        
        # CPU 使用率
        cpu_container = QHBoxLayout()
        cpu_label = QLabel("CPU:")
        cpu_label.setStyleSheet("color: #bbbbbb; background-color: transparent;")
        self.cpu_value = QLabel("0%")
        self.cpu_value.setStyleSheet("color: #FBBC05; font-weight: bold; background-color: transparent;")
        cpu_container.addWidget(cpu_label)
        cpu_container.addWidget(self.cpu_value)
        self.resource_layout.addLayout(cpu_container)
        
        # 内存使用率
        memory_container = QHBoxLayout()
        memory_label = QLabel("Memory:")
        memory_label.setStyleSheet("color: #bbbbbb; background-color: transparent;")
        self.memory_value = QLabel("0%")
        self.memory_value.setStyleSheet("color: #34A853; font-weight: bold; background-color: transparent;")
        memory_container.addWidget(memory_label)
        memory_container.addWidget(self.memory_value)
        self.resource_layout.addLayout(memory_container)
        
        # 磁盘使用率
        disk_container = QHBoxLayout()
        disk_label = QLabel("Disk:")
        disk_label.setStyleSheet("color: #bbbbbb; background-color: transparent;")
        self.disk_value = QLabel("0%")
        self.disk_value.setStyleSheet("color: #4285F4; font-weight: bold; background-color: transparent;")
        disk_container.addWidget(disk_label)
        disk_container.addWidget(self.disk_value)
        self.resource_layout.addLayout(disk_container)
        
        layout.addLayout(self.resource_layout)
        
        # 更新资源指示器
        self.resource_timer = QTimer(self)
        self.resource_timer.timeout.connect(self.update_resource_indicators)
        self.resource_timer.start(2000)  # 每2秒更新一次
        
        return status_bar
        
    def update_resource_indicators(self):
        """更新资源指示器"""
        try:
            # 使用psutil获取CPU和内存使用率
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            # 更新标签
            self.cpu_value.setText(f"{cpu_percent:.1f}%")
            self.memory_value.setText(f"{memory_percent:.1f}%")
            
            # 根据使用率设置颜色
            cpu_color = "#3498db"  # 默认蓝色
            if cpu_percent > 80:
                cpu_color = "#e74c3c"  # 高使用率-红色
            elif cpu_percent > 50:
                cpu_color = "#f39c12"  # 中使用率-橙色
                
            memory_color = "#3498db"  # 默认蓝色
            if memory_percent > 80:
                memory_color = "#e74c3c"  # 高使用率-红色
            elif memory_percent > 50:
                memory_color = "#f39c12"  # 中使用率-橙色
                
            self.cpu_value.setStyleSheet(f"color: {cpu_color}; font-size: 12px;")
            self.memory_value.setStyleSheet(f"color: {memory_color}; font-size: 12px;")
            
        except ImportError:
            # 如果psutil不可用，则显示N/A
            self.cpu_value.setText("N/A")
            self.memory_value.setText("N/A")
        except Exception as e:
            # 出现其他错误，记录并显示N/A
            print(f"Error updating resource indicators: {e}")
            self.cpu_value.setText("N/A")
            self.memory_value.setText("N/A")

from components.settings import SettingsWidget 