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
                        QEasingCurve, pyqtSignal, QTimer, QAbstractAnimation, QThread,
                        QRect, QEvent, QObject)
from utils.logger import Logger
from tools.base_tools import PlatformManager

from components.base_component import BaseComponent
from components.dashboard import DashboardWidget
from components.system_cleaner import SystemCleanerWidget
from components.disk_check import DiskCheckWidget
from components.boot_repair import BootToolsWidget
from components.virus_scan import VirusScanWidget
from components.system_repair import SystemRepairWidget
from components.dism_tool import DismToolWidget
from components.network_reset import NetworkResetWidget
from components.system_info import SystemInfoWidget
from components.settings import SettingsWidget
from config import Icon
from config import App

class MainWindow(QMainWindow):
    """Main application window"""
    
    # Language change signal
    language_changed = pyqtSignal(str)
    page_changed = pyqtSignal(str)
    
    def __init__(self, settings):
        """Initialize main window
        
        Args:
            settings: Settings manager instance
        """
        super().__init__()
        
        # Configure logging
        self.logger = Logger().get_logger()

        # Save settings instance
        self.settings = settings
        
        # Platform manager
        self.platform_manager = PlatformManager()
        
        # Set properties
        self.dragging = False
        self.drag_position = None
        self.current_page = "Dashboard"
        
        # Initialize dictionary
        self.page_buttons = {}
        
        # Set window basic properties
        self.setWindowTitle("Glary Utilities")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)
        
        # Set window properties based on platform
        if self.platform_manager.is_linux():
            # Linux: Use system native title bar
            self.setWindowFlags(Qt.Window)
            self.setAttribute(Qt.WA_TranslucentBackground, False)
            self.setFocusPolicy(Qt.StrongFocus)
        else:
            # Windows/macOS: Use custom borderless window
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setFocusPolicy(Qt.StrongFocus)
        
        # Initialize UI
        self.initUI()
        
        # Apply theme
        self.apply_theme()
        
        # Set window icon
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
            self.logger.warning("Found missing translations!")
            for language, sections in missing_translations.items():
                self.logger.warning(f"\nLanguage: {language}")
                for section, keys in sections.items():
                    self.logger.warning(f"  Section: {section}")
                    for key in keys:
                        self.logger.warning(f"    Missing: {key}")

    def initUI(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 只在非Linux平台上设置自定义标题栏
        if not self.platform_manager.is_linux():
            self.setup_title_bar()
            main_layout.addWidget(self.title_bar)
        
        # 创建内容区域
        self.setup_content_area()
        main_layout.addWidget(self.content_widget)
        
        # 设置状态栏
        self.setup_status_bar()
        
        # 设置工具提示
        self.setup_tooltips()
        
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
        app_icon.setToolTip(self.get_translation("click_for_about", "Click for About"))
        # Make the icon clickable
        app_icon.mousePressEvent = lambda event: self.show_about_dialog()
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
        
        # 为标题栏设置鼠标事件处理
        self.title_bar.mousePressEvent = self.title_bar_mouse_press_event
        self.title_bar.mouseMoveEvent = self.title_bar_mouse_move_event
        self.title_bar.mouseReleaseEvent = self.title_bar_mouse_release_event
        
        # Linux特定优化：确保标题栏可以接收鼠标事件
        if self.platform_manager.is_linux():
            # 只在非Wayland环境下设置这些属性
            if 'WAYLAND_DISPLAY' not in os.environ:
                self.title_bar.setAttribute(Qt.WA_TransparentForMouseEvents, False)
                self.title_bar.setFocusPolicy(Qt.NoFocus)
                # 设置标题栏为可拖拽区域
                self.title_bar.setProperty("draggable", True)
        
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
    
    def title_bar_mouse_press_event(self, event):
        """标题栏鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            # 只在非Wayland环境下激活窗口
            if 'WAYLAND_DISPLAY' not in os.environ:
                self.activateWindow()
                self.raise_()
    
    def title_bar_mouse_move_event(self, event):
        """标题栏鼠标移动事件"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            # 获取屏幕几何信息
            screen_geometry = self.screen().availableGeometry()
            new_pos = event.globalPos() - self.drag_position
            
            # 限制窗口在屏幕范围内
            new_pos.setX(max(0, min(new_pos.x(), screen_geometry.width() - self.width())))
            new_pos.setY(max(0, min(new_pos.y(), screen_geometry.height() - self.height())))
            self.move(new_pos)
            event.accept()
        else:
            # 如果不在拖拽状态，检查是否需要开始拖拽
            if event.buttons() == Qt.LeftButton and not self.dragging:
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
    
    def title_bar_mouse_release_event(self, event):
        """标题栏鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    
    # 事件处理用于窗口拖动与调整 - 优化Linux兼容性
    def mousePressEvent(self, event):
        """处理鼠标按下事件 - 只在非Linux平台上处理窗口拖拽"""
        if not self.platform_manager.is_linux():
            if event.button() == Qt.LeftButton:
                # 检查是否点击在标题栏上
                if hasattr(self, 'title_bar') and self.title_bar.geometry().contains(event.pos()):
                    self.dragging = True
                    self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                    # 只在非Wayland环境下激活窗口
                    if 'WAYLAND_DISPLAY' not in os.environ:
                        self.activateWindow()
                        self.raise_()
                    event.accept()
                # 允许通过窗口边缘拖动（适用于所有平台）
                else:
                    edge_margin = 5
                    if (event.pos().x() <= edge_margin or
                        event.pos().x() >= self.width() - edge_margin or
                        event.pos().y() <= edge_margin or
                        event.pos().y() >= self.height() - edge_margin):
                        self.dragging = True
                        self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                        # 只在非Wayland环境下激活窗口
                        if 'WAYLAND_DISPLAY' not in os.environ:
                            self.activateWindow()
                            self.raise_()
                        event.accept()
                    else:
                        super().mousePressEvent(event)
            else:
                super().mousePressEvent(event)
        else:
            # Linux上使用系统标题栏，不需要自定义拖拽处理
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件 - 只在非Linux平台上处理窗口拖拽"""
        if not self.platform_manager.is_linux():
            if self.dragging and event.buttons() == Qt.LeftButton:
                new_pos = event.globalPos() - self.drag_position
                self.move(new_pos)
                event.accept()
            else:
                super().mouseMoveEvent(event)
        else:
            # Linux上使用系统标题栏，不需要自定义拖拽处理
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件 - 只在非Linux平台上处理窗口拖拽"""
        if not self.platform_manager.is_linux():
            if event.button() == Qt.LeftButton:
                self.dragging = False
                event.accept()
            else:
                super().mouseReleaseEvent(event)
        else:
            # Linux上使用系统标题栏，不需要自定义拖拽处理
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """处理鼠标双击事件 - 只在非Linux平台上处理最大化"""
        if not self.platform_manager.is_linux():
            if hasattr(self, 'title_bar') and self.title_bar.geometry().contains(event.pos()):
                self.toggle_maximize()
                event.accept()
            else:
                super().mouseDoubleClickEvent(event)
        else:
            # Linux上使用系统标题栏，不需要自定义双击处理
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
        common_title = QLabel(self.get_translation("common_section", "Common"))
        common_title.setStyleSheet("color: #999999; font-size: 13px; margin-top: 5px; background-color: transparent; font-weight: bold; padding-left: 2px;")
        sidebar_layout.addWidget(common_title)

        # 添加主要功能按钮
        self.dashboard_btn = self.create_sidebar_button(self.get_translation("dashboard", "Dashboard"), Icon.Dashboard.Path, "Dashboard", self.get_translation("dashboard_tooltip", "仪表盘"))
        sidebar_layout.addWidget(self.dashboard_btn)
        self.page_buttons["Dashboard"] = self.dashboard_btn
        
        self.system_cleaner_btn = self.create_sidebar_button(self.get_translation("system_cleaner", "System Cleaner"), Icon.Cleaner.Path, "System Cleaner", self.get_translation("system_cleaner_tooltip", "系统清理"))
        sidebar_layout.addWidget(self.system_cleaner_btn)
        self.page_buttons["System Cleaner"] = self.system_cleaner_btn
        
        # System Tools (previously System Repair)
        self.registry_btn = self.create_sidebar_button(self.get_translation("system_repair", "System Tools"), Icon.Repair.Path, "System Tools", self.get_translation("system_repair_tooltip", "系统工具"))
        sidebar_layout.addWidget(self.registry_btn)
        self.page_buttons["System Tools"] = self.registry_btn
        
        # Disk Tools (previously Disk Check)
        self.disk_tools_btn = self.create_sidebar_button(self.get_translation("disk_check", "Disk Tools"), Icon.Disk.Path, "Disk Tools", self.get_translation("disk_check_tooltip", "磁盘工具"))
        sidebar_layout.addWidget(self.disk_tools_btn)
        self.page_buttons["Disk Tools"] = self.disk_tools_btn
        
        # Boot Tools (previously Boot Repair)
        self.startup_btn = self.create_sidebar_button(self.get_translation("boot_repair", "Boot Tools"), Icon.Boot.Path, "Boot Tools", self.get_translation("boot_repair_tooltip", "启动工具"))
        sidebar_layout.addWidget(self.startup_btn)
        self.page_buttons["Boot Tools"] = self.startup_btn
        
        # Security Tools (previously Virus Scan)
        self.uninstaller_btn = self.create_sidebar_button(self.get_translation("virus_scan", "Security Tools"), Icon.Virus.Path, "Security Tools", self.get_translation("virus_scan_tooltip", "安全工具"))
        sidebar_layout.addWidget(self.uninstaller_btn)
        self.page_buttons["Security Tools"] = self.uninstaller_btn
        
        # 添加分类标题：安全
        security_title = QLabel(self.get_translation("security_section", "Security"))
        security_title.setStyleSheet("color: #999999; font-size: 13px; margin-top: 15px; background-color: transparent; font-weight: bold; padding-left: 12px;")
        sidebar_layout.addWidget(security_title)
        
        # Network Tools (previously Network Reset)
        self.privacy_btn = self.create_sidebar_button(self.get_translation("network_reset", "Network Tools"), Icon.Privacy.Path, "Network Tools", self.get_translation("network_reset_tooltip", "网络工具"))
        sidebar_layout.addWidget(self.privacy_btn)
        self.page_buttons["Network Tools"] = self.privacy_btn
        
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
        version_label = QLabel(f"{self.get_translation('version', 'Version')} {App.version}")
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
            self.logger.error(f"Error creating sidebar button: {e}")
            # Create button without icon
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
            # 检查Linux性能优化设置
            optimize_linux = self.settings.get_setting("optimize_linux_performance", True)
            if isinstance(optimize_linux, str):
                optimize_linux = optimize_linux.lower() in ('true', 'yes', '1', 'on')
            elif isinstance(optimize_linux, int):
                optimize_linux = optimize_linux != 0
            else:
                optimize_linux = bool(optimize_linux)
                
            # 在Linux上禁用复杂的图标动画以提高性能
            if not (self.platform_manager.is_linux() and optimize_linux):
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
        """设置内容区域"""
        # 创建内容部件
        self.content_widget = QWidget()
        self.content_widget.setObjectName("content_widget")
        
        # 创建内容布局
        content_layout = QHBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 添加侧边栏
        self.sidebar = self.setup_sidebar()
        content_layout.addWidget(self.sidebar)
        
        # 添加内容区域
        self.setup_content_area_internal()
        content_layout.addWidget(self.content_area)
        
        # 设置内容部件的样式
        if not self.platform_manager.is_linux():
            # 只在非Linux平台上设置圆角和阴影
            self.content_widget.setStyleSheet("""
                QWidget#content_widget {
                    background-color: #252525;
                    border-radius: 10px;
                }
            """)
            
            # 为窗口设置阴影效果
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 180))
            shadow.setOffset(0, 0)
            self.content_widget.setGraphicsEffect(shadow)
        else:
            # Linux上使用简单的背景色
            self.content_widget.setStyleSheet("""
                QWidget#content_widget {
                    background-color: #252525;
                }
            """)

    def setup_content_area_internal(self):
        """设置内部内容区域"""
        # 创建堆叠窗口部件用于页面切换
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("content_area")
        
        # 创建各个页面组件
        self.dashboard_widget = DashboardWidget()
        self.system_cleaner_widget = SystemCleanerWidget()
        self.disk_check_widget = DiskCheckWidget()
        self.boot_tools_widget = BootToolsWidget()
        self.virus_scan_widget = VirusScanWidget()
        self.system_repair_widget = SystemRepairWidget()
        self.dism_tool_widget = DismToolWidget()
        self.network_reset_widget = NetworkResetWidget()
        self.system_info_widget = SystemInfoWidget()
        self.settings_widget = SettingsWidget(self.settings)
        
        # 添加页面到堆叠窗口部件
        self.content_area.addWidget(self.dashboard_widget)
        self.content_area.addWidget(self.system_cleaner_widget)
        self.content_area.addWidget(self.disk_check_widget)
        self.content_area.addWidget(self.boot_tools_widget)
        self.content_area.addWidget(self.virus_scan_widget)
        self.content_area.addWidget(self.system_repair_widget)
        self.content_area.addWidget(self.dism_tool_widget)
        self.content_area.addWidget(self.network_reset_widget)
        self.content_area.addWidget(self.system_info_widget)
        self.content_area.addWidget(self.settings_widget)
        
        # 设置内容区域样式
        self.content_area.setStyleSheet("""
            QStackedWidget#content_area {
                background-color: transparent;
                border: none;
            }
        """)
    
    def apply_theme(self):
        """应用当前主题"""
        theme_name = self.settings.get_setting("theme", "dark")
        
        # 加载主题数据
        theme_data = self.settings.load_theme(theme_name)
        
        if theme_data and "colors" in theme_data:
            bg_color = theme_data["colors"].get("bg_color", "#2d2d2d")
            text_color = theme_data["colors"].get("text_color", "#dcdcdc")
            accent_color = theme_data["colors"].get("accent_color", "#007acc")
            border_color = theme_data["colors"].get("border_color", "#444444")
            
            # 更新复选框样式
            checkbox_style = f"""
                QCheckBox {{
                    color: {text_color};
                    background-color: transparent;
                    spacing: 5px;
                    padding: 5px;
                    font-size: 13px;
                    min-height: 20px;
                    margin: 2px 0;
                }}
                
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 2px solid {accent_color};
                    border-radius: 3px;
                    background-color: {bg_color};
                }}
                
                QCheckBox::indicator:unchecked {{
                    background-color: {bg_color};
                }}
                
                QCheckBox::indicator:checked {{
                    background-color: {accent_color};
                    border: 2px solid {accent_color};
                    image: url(resources/icons/check.png);  /* 可选：添加勾选图标 */
                }}
                
                QCheckBox::indicator:unchecked:hover {{
                    border-color: {self.lighten_color(accent_color, 20)};
                    background-color: {self.lighten_color(bg_color, 10)};
                }}
                
                QCheckBox::indicator:checked:hover {{
                    background-color: {self.lighten_color(accent_color, 10)};
                    border-color: {self.lighten_color(accent_color, 10)};
                }}
                
                QCheckBox:disabled {{
                    color: {self.lighten_color(text_color, -30)};
                }}
                
                QCheckBox::indicator:disabled {{
                    border-color: {self.lighten_color(accent_color, -30)};
                    background-color: {self.lighten_color(bg_color, -10)};
                }}
            """
            
            # 将复选框样式添加到主样式表中
            self.setStyleSheet(self.styleSheet() + checkbox_style)
            
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
                self.logger.error(f"Error applying custom theme to {component_name}: {str(e)}")
        
        # 对于其他标准组件，应用通用的apply_theme方法
        try:
            if hasattr(widget, 'apply_theme') and callable(widget.apply_theme):
                widget.apply_theme()
        except Exception as e:
            self.logger.error(f"Error applying theme to widget: {str(e)}")
            
        # Process children
        for child in widget.findChildren(QWidget):
            self.refresh_component_theme(child)

    def apply_window_icon(self):
        """Set window icon"""
        try:
            # Use icon file in root directory
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons", "icon.png")
            if not os.path.exists(icon_path):
                self.logger.warning(f"Warning: Window icon file does not exist: {icon_path}")
                return
                
            self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            self.logger.error(f"Error setting window icon: {str(e)}")
    
    def set_active_page(self, page_name):
        """Set active page
        
        Args:
            page_name (str): Page name
        """
        # Page name to index mapping
        page_indices = {
            "Dashboard": 0,
            "System Cleaner": 1,
            "Disk Tools": 2,
            "Boot Tools": 3,
            "Security Tools": 4,
            "System Tools": 5,
            "Network Tools": 6,
            "DISM Tool": 7,
            "System Information": 8,
            "Settings": 9
        }
        
        if page_name in page_indices:
            index = page_indices[page_name]
            self.content_area.setCurrentIndex(index)
            self.current_page = page_name
            
            # Update active button state
            self._update_active_button(page_name)
            
            # Update window title
            self.setWindowTitle(f"Glary Utilities - {page_name}")
            
            # Log page switch
            self.logger.debug(f"Switched to page: {page_name}")
        else:
            self.logger.warning(f"Unknown page: {page_name}")
    
    def _update_page_content(self, page_name):
        """Update content area based on page name"""
        self.logger.info(f"Switched to page: {page_name}")
        
        # Get localized display name for the page
        page_display_name = self.settings.get_translation("general", page_name.lower().replace(' ', '_'))
        
        # Update window title and toolbar title
        self.setWindowTitle(f"Glary Utilities - {page_display_name}")
        if hasattr(self, 'title_label'):
            self.title_label.setText(f"Glary Utilities - {page_display_name}")
        
        # Update active button state
        self._update_active_button(page_name)
        
        # Clear search if search box exists
        if hasattr(self, 'search_box'):
            self.search_box.clear()
            
        try:
            # If page index exists, directly switch to that page
            if page_name in self.page_indices:
                self.content_area.setCurrentIndex(self.page_indices[page_name])
                
                # Get current page widget
                current_widget = self.content_area.currentWidget()
                
                # After switching to this page, let the page widget automatically update data
                if hasattr(current_widget, 'update_data') and callable(getattr(current_widget, 'update_data')):
                    current_widget.update_data()
                    
                # Save current page name
                self.current_page = page_name
                
                # Emit page change signal
                self.page_changed.emit(page_name)
            else:
                # If page doesn't exist, show an error message
                self.logger.warning(f"Index not found for page '{page_name}'")
                self.show_status_message(f"Page '{page_name}' does not exist", 3000)
                
        except Exception as e:
            # Handle exception cases
            self.logger.error(f"Error switching to page '{page_name}': {e}")
            error_widget = QLabel(f"Error loading page: {e}")
            error_widget.setStyleSheet("color: red;")
            error_widget.setAlignment(Qt.AlignCenter)
            
            # Create a temporary page to display error
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
            # 关闭当前打开的帮助对话框（如果有）
            for dialog in self.findChildren(QDialog):
                if dialog.objectName() == "HelpDialog":
                    dialog.reject()
                    
            # Update language setting and refresh translation cache
            self.settings.set_language(language)
            self.settings.sync()
            
            # 直接更新UI文本，而不是触发信号
            self._update_ui_texts_directly(language)
            
            # Show a message indicating language was changed
            language_display = "English" if language == "en" else "中文"
            self.show_status_message(f"Language changed to {language_display}")
            
        except Exception as e:
            self.logger.error(f"Error changing language: {str(e)}")

    def _update_ui_texts_directly(self, language):
        """直接更新UI文本，避免递归
        
        Args:
            language: 当前语言代码
        """
        try:
            # 获取当前活动页面
            active_page = self.current_page
            
            # 直接从翻译字典获取翻译
            translations = self.settings.translations.get(language, {})
            main_window_translations = translations.get("main_window", {})
            general_translations = translations.get("general", {})
            
            # 更新按钮文本
            for button_name, button in self.page_buttons.items():
                translation_key = button_name.lower().replace(' ', '_')
                translated_name = main_window_translations.get(translation_key) or general_translations.get(translation_key) or button_name
                button.setText(translated_name)
            
            # 更新标题
            page_translation_key = active_page.lower().replace(' ', '_')
            page_display_name = main_window_translations.get(page_translation_key) or general_translations.get(page_translation_key) or active_page
            
            window_title = f"Glary Utilities - {page_display_name}"
            self.setWindowTitle(window_title)
            if hasattr(self, 'title_label'):
                self.title_label.setText(window_title)
            
            # 更新所有组件的语言
            for i in range(self.content_area.count()):
                widget = self.content_area.widget(i)
                if hasattr(widget, 'refresh_language') and callable(widget.refresh_language):
                    widget.refresh_language()
            
            # 更新状态栏
            if hasattr(self, 'status_label'):
                ready_text = general_translations.get("ready", "Ready")
                self.status_label.setText(ready_text)
                
        except Exception as e:
            self.logger.error(f"Error updating UI texts: {str(e)}")
    
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
                    self.logger.error(f"Error updating button text: {e}")
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
                            self.logger.warning(f"Missing translation for '{section}.{key}' in language '{current_lang}'")
            return True
        except Exception as e:
            self.logger.error(f"Error checking translations: {e}")
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
                    self.logger.info(f"Applied window transparency: {transparency}%")
                except Exception as e:
                    # Log the error but continue
                    self.logger.error(f"Error applying window transparency: {str(e)}")
                    # Reset to fully opaque
                    self.settings.set_setting("window_transparency", 100)
            else:
                # Fully opaque
                self.setWindowOpacity(1.0)
        except Exception as e:
            self.logger.error(f"Error in apply_transparency: {str(e)}")
            # Reset to default
            self.setWindowOpacity(1.0)
    
    def show_status_message(self, message, timeout=2000):
        """显示状态栏消息"""
        # 在控制台记录消息
        self.logger.debug(f"状态消息: {message}")
        
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

    def show_about_dialog(self):
        """显示关于界面（作为主窗口内的页面，而不是弹出对话框）"""
        
        # 创建内联关于页面（如果不存在）
        if not hasattr(self, 'about_page'):
            # 创建关于页面
            self.about_page = QWidget()
            self.about_page.setObjectName("About")
            
            # 创建页面布局
            about_layout = QVBoxLayout(self.about_page)
            about_layout.setContentsMargins(20, 20, 20, 20)
            about_layout.setSpacing(20)
            
            # 标题
            title = QLabel(self.get_translation("about_title", "About"))
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
            about_layout.addWidget(title)
            
            # 应用图标和标题
            icon_title_layout = QHBoxLayout()
            
            # 添加应用图标
            app_icon_label = QLabel()
            app_icon_label.setFixedSize(80, 80)
            if os.path.exists(Icon.Icon.Path):
                app_icon = QPixmap(Icon.Icon.Path)
                app_icon_label.setPixmap(app_icon.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            app_icon_label.setStyleSheet("background-color: transparent;")
            
            # 添加标题和版本布局
            title_version_layout = QVBoxLayout()
            title_version_layout.setSpacing(10)
            
            app_title = QLabel("Glary Utilities")
            app_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
            
            version_label = QLabel(f"{self.get_translation('version', 'Version')}: {App.version}")
            version_label.setStyleSheet("font-size: 16px; color: #cccccc;")
            
            title_version_layout.addWidget(app_title)
            title_version_layout.addWidget(version_label)
            title_version_layout.addStretch()
            
            icon_title_layout.addWidget(app_icon_label)
            icon_title_layout.addLayout(title_version_layout)
            icon_title_layout.addStretch()
            
            about_layout.addLayout(icon_title_layout)
            
            # 添加分割线
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setStyleSheet("background-color: #444444; max-height: 1px;")
            about_layout.addWidget(line)
            
            # 添加内容区域
            content_widget = QWidget()
            content_widget.setStyleSheet("background-color: #2a2a2a; border-radius: 8px;")
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(20, 20, 20, 20)
            content_layout.setSpacing(15)
            
            # 应用描述
            description_label = QLabel(self.get_translation("app_description", "A powerful system optimization tool."))
            description_label.setWordWrap(True)
            description_label.setStyleSheet("font-size: 16px; color: #e0e0e0;")
            content_layout.addWidget(description_label)
            
            # 添加主要功能
            features_label = QLabel(self.get_translation("features", "Main Features"))
            features_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; margin-top: 10px;")
            content_layout.addWidget(features_label)
            
            # 功能列表
            features_layout = QVBoxLayout()
            features_layout.setContentsMargins(15, 0, 0, 0)
            features_layout.setSpacing(8)
            
            feature_items = [
                self.get_translation("feature_clean", "System cleaning"),
                self.get_translation("feature_repair", "System repair"),
                self.get_translation("feature_security", "Security protection"),
                self.get_translation("feature_disk", "Disk optimization")
            ]
            
            for feature in feature_items:
                feature_label = QLabel(f"• {feature}")
                feature_label.setStyleSheet("font-size: 15px; color: #e0e0e0;")
                features_layout.addWidget(feature_label)
            
            content_layout.addLayout(features_layout)
            
            # 添加系统要求
            sys_req_label = QLabel(self.get_translation("system_requirements", "System Requirements"))
            sys_req_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; margin-top: 15px;")
            content_layout.addWidget(sys_req_label)
            
            sys_req_details = QLabel(self.get_translation("requirements_details", "Windows 10/11, 4GB RAM, 200MB disk space"))
            sys_req_details.setWordWrap(True)
            sys_req_details.setStyleSheet("font-size: 15px; color: #e0e0e0; margin-left: 15px;")
            content_layout.addWidget(sys_req_details)
            
            # 添加分割线
            inner_line = QFrame()
            inner_line.setFrameShape(QFrame.HLine)
            inner_line.setStyleSheet("background-color: #444444; max-height: 1px; margin-top: 10px;")
            content_layout.addWidget(inner_line)
            
            # 添加版权信息
            copyright_label = QLabel(f"© 2025 Glarysoft Ltd. All rights reserved.")
            copyright_label.setStyleSheet("font-size: 14px; color: #999999; margin-top: 10px;")
            content_layout.addWidget(copyright_label)
            
            # 添加开发者信息
            dev_label = QLabel(self.get_translation("developed_by", "Developed by Chen Runsen"))
            dev_label.setStyleSheet("font-size: 14px; color: #999999;")
            content_layout.addWidget(dev_label)
            
            # 添加网站链接
            website_label = QLabel("<a href='https://www.chenrunsen.com' style='color: #5b9bd5;'>www.chenrunsen.com</a>")
            website_label.setOpenExternalLinks(True)
            website_label.setStyleSheet("font-size: 14px; color: #5b9bd5;")
            content_layout.addWidget(website_label)
            
            # 添加内容区域到主布局
            about_layout.addWidget(content_widget)
            
            # 按钮布局
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            # 添加帮助按钮
            help_button = QPushButton(self.get_translation("help_button", "Help"))
            help_button.setFixedSize(120, 36)
            help_button.setStyleSheet("""
                QPushButton {
                    background-color: #555555;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 5px 15px;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
                QPushButton:pressed {
                    background-color: #444444;
                }
            """)
            help_button.clicked.connect(self.show_help_dialog)
            button_layout.addWidget(help_button)
            
            # 添加按钮布局到主布局
            about_layout.addLayout(button_layout)
            
            # 添加弹性空间
            about_layout.addStretch()
            
            # 添加关于页面到内容区域
            self.content_area.addWidget(self.about_page)
            
            # 更新页面索引字典
            self.page_indices["About"] = self.content_area.count() - 1
            
            # 创建侧边栏按钮（如果需要）
            if "About" not in self.page_buttons:
                # 添加关于按钮到侧边栏
                about_btn = self.create_sidebar_button(
                    self.get_translation("about_title", "About"),
                    Icon.About.Path, 
                    "About",
                    self.get_translation("about_tooltip", "About Glary Utilities")
                )
                # 暂时不显示在侧边栏，只在需要时显示
                about_btn.hide()
                self.page_buttons["About"] = about_btn
        
        # 切换到关于页面
        self.set_active_page("About")

    def lighten_color(self, color, amount=0):
        """使颜色变亮或变暗
        
        Args:
            color: 十六进制颜色代码
            amount: 变化量，正数变亮，负数变暗（范围：-100 到 100）
                
        Returns:
            新的十六进制颜色代码
        """
        try:
            # 移除井号并转换为RGB
            c = color.lstrip('#')
            c = tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
            
            # 调整每个颜色通道
            r = int(max(0, min(255, c[0] + (amount * 2.55))))
            g = int(max(0, min(255, c[1] + (amount * 2.55))))
            b = int(max(0, min(255, c[2] + (amount * 2.55))))
            
            # 转换回十六进制格式
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception as e:
            self.logger.error(f"Color adjustment error: {str(e)}")
            return color  # Return original color if error occurs

    def show_help_dialog(self):
        """Show help content (as a page within the main window, not a popup dialog)"""
        
        # Create inline help page (if it doesn't exist)
        if not hasattr(self, 'help_page'):
            # Create help page
            self.help_page = QWidget()
            self.help_page.setObjectName("Help")
            
            # Create page layout
            help_layout = QVBoxLayout(self.help_page)
            help_layout.setContentsMargins(20, 20, 20, 20)
            help_layout.setSpacing(15)
            
            # Title
            title = QLabel(self.get_translation("help_title", "Help Documentation"))
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
            help_layout.addWidget(title)
            
            # Description
            description = QLabel(self.get_translation("help_description", "Find answers and learn how to use Glary Utilities effectively"))
            description.setStyleSheet("font-size: 14px; color: #a0a0a0;")
            help_layout.addWidget(description)
            
            # 帮助内容
            help_text = QTextBrowser()
            help_text.setOpenExternalLinks(True)
            help_text.setStyleSheet("""
                QTextBrowser {
                    background-color: #252525;
                    color: #e0e0e0;
                    border: 1px solid #3a3a3a;
                    border-radius: 5px;
                    padding: 15px;
                    font-size: 14px;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #2d2d2d;
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #555555;
                    min-height: 20px;
                    border-radius: 5px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)
            
            # 使用翻译条目构建帮助内容HTML
            t = lambda key, default="": self.get_translation(key, default)
            
            help_html = f"""
            <h2>{t('help_content_title', 'Glary Utilities Help Documentation')}</h2>
            <p>{t('help_content_welcome', 'Welcome to Glary Utilities')}</p>
            
            <h3>{t('help_dashboard_title', 'Dashboard')}</h3>
            <p>{t('help_dashboard_desc', 'The Dashboard provides an overview of your system status and quick access to common tasks.')}</p>
            
            <h3>{t('help_cleaner_title', 'System Cleaner')}</h3>
            <p>{t('help_cleaner_desc', 'The System Cleaner tool helps you:')}</p>
            <ul>
                <li>{t('help_cleaner_item1', 'Clean temporary files')}</li>
                <li>{t('help_cleaner_item2', 'Free up disk space')}</li>
                <li>{t('help_cleaner_item3', 'Improve system performance')}</li>
            </ul>
            <p>{t('help_cleaner_usage', 'How to use: Click Scan to analyze your system, then select items to clean and click Clean button.')}</p>
            
            <h3>{t('help_repair_title', 'System Repair')}</h3>
            <p>{t('help_repair_desc', 'System Repair can fix common Windows issues:')}</p>
            <ul>
                <li>{t('help_repair_item1', 'Registry errors')}</li>
                <li>{t('help_repair_item2', 'System settings problems')}</li>
                <li>{t('help_repair_item3', 'Windows service issues')}</li>
            </ul>
            <p>{t('help_repair_usage', 'How to use: Select issues to scan for, review results, then apply repairs.')}</p>
            
            <h3>{t('help_disk_title', 'Disk Check')}</h3>
            <p>{t('help_disk_desc', 'The Disk Check tool can:')}</p>
            <ul>
                <li>{t('help_disk_item1', 'Detect disk errors')}</li>
                <li>{t('help_disk_item2', 'Find bad sectors')}</li>
                <li>{t('help_disk_item3', 'Optimize disk performance')}</li>
            </ul>
            <p>{t('help_disk_usage', 'How to use: Select a disk, choose check options, and click Check Disk button.')}</p>
            
            <h3>{t('help_boot_title', 'Boot Repair')}</h3>
            <p>{t('help_boot_desc', 'The Boot Repair tool can:')}</p>
            <ul>
                <li>{t('help_boot_item1', 'Fix startup problems')}</li>
                <li>{t('help_boot_item2', 'Restore boot records')}</li>
                <li>{t('help_boot_item3', 'Repair boot configuration')}</li>
            </ul>
            <p>{t('help_boot_note', 'Note: Administrator privileges are required for this tool.')}</p>
            
            <h3>{t('help_virus_title', 'Virus Scan')}</h3>
            <p>{t('help_virus_desc', 'The Virus Scan tool helps you:')}</p>
            <ul>
                <li>{t('help_virus_item1', 'Detect malware')}</li>
                <li>{t('help_virus_item2', 'Remove harmful files')}</li>
                <li>{t('help_virus_item3', 'Protect your system')}</li>
            </ul>
            <p>{t('help_virus_usage', 'How to use: Select areas to scan, click Scan button, and review results.')}</p>
            
            <h3>{t('help_network_title', 'Network Reset')}</h3>
            <p>{t('help_network_desc', 'Network Reset helps with connection issues:')}</p>
            <ul>
                <li>{t('help_network_item1', 'Reset DNS cache')}</li>
                <li>{t('help_network_item2', 'Reset Winsock catalog')}</li>
                <li>{t('help_network_item3', 'Reset TCP/IP stack')}</li>
                <li>{t('help_network_item4', 'Fix network adapters')}</li>
            </ul>
            <p>{t('help_network_usage', 'How to use: Select operations to perform and click Reset button.')}</p>
            
            <h3>{t('help_dism_title', 'DISM Tool')}</h3>
            <p>{t('help_dism_desc', 'The DISM tool can:')}</p>
            <ul>
                <li>{t('help_dism_item1', 'Repair Windows system image')}</li>
                <li>{t('help_dism_item2', 'Scan system health')}</li>
                <li>{t('help_dism_item3', 'Clean up component store')}</li>
            </ul>
            <p>{t('help_dism_usage', 'How to use: Select DISM operation and click Execute button.')}</p>
            
            <h3>{t('help_sysinfo_title', 'System Information')}</h3>
            <p>{t('help_sysinfo_desc', 'System Information provides details about:')}</p>
            <ul>
                <li>{t('help_sysinfo_item1', 'CPU and memory specifications')}</li>
                <li>{t('help_sysinfo_item2', 'Operating system details')}</li>
                <li>{t('help_sysinfo_item3', 'Network configuration')}</li>
                <li>{t('help_sysinfo_item4', 'Graphics hardware')}</li>
            </ul>
            <p>{t('help_sysinfo_usage', 'How to use: Switch between tabs to view different categories of information.')}</p>
            
            <h3>{t('help_settings_title', 'Settings')}</h3>
            <p>{t('help_settings_desc', 'In Settings you can:')}</p>
            <ul>
                <li>{t('help_settings_item1', 'Change language')}</li>
                <li>{t('help_settings_item2', 'Adjust theme and appearance')}</li>
                <li>{t('help_settings_item3', 'Configure cleaning options')}</li>
                <li>{t('help_settings_item4', 'Set application preferences')}</li>
            </ul>
            
            <h3>{t('help_contact_title', 'Contact & Support')}</h3>
            <p>{t('help_contact_desc', 'For additional help, visit our website or contact support.')}</p>
            """
            
            help_text.setHtml(help_html)
            help_layout.addWidget(help_text)
            
            # 添加帮助页面到内容区域
            self.content_area.addWidget(self.help_page)
            
            # 更新页面索引字典
            self.page_indices["Help"] = self.content_area.count() - 1
            
            # 创建侧边栏按钮（如果需要）
            if "Help" not in self.page_buttons:
                # 添加帮助按钮到侧边栏
                help_btn = self.create_sidebar_button(
                    self.get_translation("help_title", "Help"),
                    Icon.Help.Path, 
                    "Help",
                    self.get_translation("help_tooltip", "View help documentation")
                )
                # 暂时不显示在侧边栏，只在需要时显示
                help_btn.hide()
                self.page_buttons["Help"] = help_btn
        
        # 切换到帮助页面
        self.set_active_page("Help")
        
    def setup_tooltips(self):
        """设置所有主要组件的工具提示，提供内联帮助"""
        # Dashboard
        if hasattr(self, 'dashboard_btn'):
            self.dashboard_btn.setToolTip(self.get_translation("dashboard_tooltip", "View system overview and quick access to common tasks"))
            
        # System Cleaner
        if hasattr(self, 'system_cleaner_btn'):
            self.system_cleaner_btn.setToolTip(self.get_translation("system_cleaner_tooltip", "Clean temporary files and free up disk space"))
            
        # System Repair
        if hasattr(self, 'registry_btn'):
            self.registry_btn.setToolTip(self.get_translation("system_repair_tooltip", "Fix common Windows issues and optimize system settings"))
            
        # Disk Check
        if hasattr(self, 'disk_tools_btn'):
            self.disk_tools_btn.setToolTip(self.get_translation("disk_check_tooltip", "Check disk for errors and optimize performance"))
            
        # Boot Repair
        if hasattr(self, 'startup_btn'):
            self.startup_btn.setToolTip(self.get_translation("boot_repair_tooltip", "Fix startup issues and repair boot configuration"))
            
        # Virus Scan
        if hasattr(self, 'uninstaller_btn'):
            self.uninstaller_btn.setToolTip(self.get_translation("virus_scan_tooltip", "Scan for malware and protect your system"))
            
        # Network Reset
        if hasattr(self, 'privacy_btn'):
            self.privacy_btn.setToolTip(self.get_translation("network_reset_tooltip", "Fix network issues and reset connections"))
            
        # DISM Tool
        if hasattr(self, 'driver_btn'):
            self.driver_btn.setToolTip(self.get_translation("dism_tool_tooltip", "Repair Windows system image and check system health"))
            
        # System Information
        if hasattr(self, 'optimizer_btn'):
            self.optimizer_btn.setToolTip(self.get_translation("system_information_tooltip", "View detailed information about your hardware and software"))
            
        # Settings
        if hasattr(self, 'settings_btn'):
            self.settings_btn.setToolTip(self.get_translation("settings_tooltip", "Configure application settings and preferences"))

    def closeEvent(self, event):
        """确保关闭窗口时终止所有后台线程/定时器，防止进程挂起"""
        try:
            # 停止所有 QTimer
            for timer in self.findChildren(QTimer):
                try:
                    timer.stop()
                except Exception:
                    pass

            # 终止所有 QThread
            for thread in self.findChildren(QThread):
                try:
                    thread.requestInterruption()
                    thread.quit()
                    thread.wait(1000)
                except Exception:
                    pass
        except Exception as e:
            self.logger.error(f"Error while shutting down threads: {e}")

        # 继续默认处理，最终退出应用
        super().closeEvent(event)
 