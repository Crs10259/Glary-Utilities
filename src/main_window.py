import os
import sys
import platform
import subprocess
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QToolTip, QApplication
import logging
import weakref
import json

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
        super().__init__()
        
        self.settings = settings
        self.theme_manager = ThemeManager()
        
        # Initialize dictionaries
        self.page_indices = {}
        self.page_buttons = {}
        
        # 动画
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(500)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 连接语言更改信号
        self.language_changed.connect(self.change_language)
        
        # 初始化UI
        self.init_ui()
        
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
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Glary Utilities")
        self.setMinimumSize(1000, 700)
        
        # 设置窗口样式 - 移除具体样式，将在apply_theme中设置
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.create_toolbar()
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setChildrenCollapsible(False)
        
        self.setup_sidebar()
        
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("contentArea")
        
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.content_area)
        
        # 修复：确保 splitter 比例正确，内容区域伸展填充
        self.splitter.setStretchFactor(0, 0)  # 侧边栏不会伸展
        self.splitter.setStretchFactor(1, 1)  # 内容区域会伸展
        
        # 设置分隔条初始位置
        self.splitter.setSizes([220, self.width() - 220])
        
        # 添加到主布局，确保填满整个窗口
        self.main_layout.addWidget(self.splitter, 1)  # 设置伸展因子
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 添加状态栏指示器
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(12, 12)
        self.status_indicator.setStyleSheet("background-color: #4CAF50; border-radius: 6px;")
        
        self.status_text = QLabel()
        self.status_text.setStyleSheet("color: white; margin-left: 5px;")
        
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(5, 2, 5, 2)
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        self.status_bar.addWidget(status_widget, 1)
        
        self.setup_content_area()
        self.setup_menu_bar()
        self.apply_theme()
        self.apply_transparency()
        
        default_tab = self.settings.get_setting("default_tab", "Dashboard")
        self.set_active_page(default_tab)

        self.show_status_message(self.settings.get_translation("general", "welcome"), 5000)
        
        # 应用窗口阴影效果
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(20)
        shadow_effect.setXOffset(5)
        shadow_effect.setYOffset(5)
        shadow_effect.setColor(QColor(0, 0, 0, 160))  # 半透明黑色阴影
        self.setGraphicsEffect(shadow_effect)
        
        # 使用淡入动画显示窗口
        self.setWindowOpacity(0.0)
        self.fade_in_effect = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_effect.setDuration(800)
        self.fade_in_effect.setStartValue(0.0)
        self.fade_in_effect.setEndValue(1.0)
        self.fade_in_effect.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_in_effect.start()

    def create_toolbar(self):
        """创建顶部工具栏"""
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(22, 22))
        
        # 创建标题标签
        self.title_label = QLabel("Dashboard")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-left: 10px;")
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # 创建工具栏图标和添加动画效果
        if Icon.Home.Exist:    
            self.home_action = self.create_animated_action(
                QIcon(Icon.Home.Path), 
                self.settings.get_translation("general", "dashboard"), 
                lambda: self.set_active_page("Dashboard")
            )
            self.toolbar.addAction(self.home_action)
        
        if Icon.Cleaner.Exist:
            self.clean_action = self.create_animated_action(
                QIcon(Icon.Cleaner.Path), 
                self.settings.get_translation("general", "system_cleaner"), 
                lambda: self.set_active_page("System Cleaner")
            )
            self.toolbar.addAction(self.clean_action)
        
        if Icon.Disk.Exist:
            self.disk_action = self.create_animated_action(
                QIcon(Icon.Disk.Path), 
                self.settings.get_translation("general", "disk_check"), 
                lambda: self.set_active_page("Disk Check")
            )
            self.toolbar.addAction(self.disk_action)
        
        if Icon.Boot.Exist:
            self.boot_action = self.create_animated_action(
                QIcon(Icon.Boot.Path), 
                self.settings.get_translation("general", "boot_repair"), 
                lambda: self.set_active_page("Boot Repair")
            )
            self.toolbar.addAction(self.boot_action)
        
        if Icon.Virus.Exist:
            self.virus_action = self.create_animated_action(
                QIcon(Icon.Virus.Path), 
                self.settings.get_translation("general", "virus_scan"), 
                lambda: self.set_active_page("Virus Scan")
            )
            self.toolbar.addAction(self.virus_action)

        # 添加标题到中间
        self.toolbar.addWidget(spacer)
        self.toolbar.addWidget(self.title_label)
        
        # 添加右侧空白和设置按钮
        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer2)
        
        if Icon.Settings.Exist:
            self.settings_action = self.create_animated_action(
                QIcon(Icon.Settings.Path), 
                self.settings.get_translation("general", "settings"), 
                lambda: self.set_active_page("Settings")
            )
            self.toolbar.addAction(self.settings_action)
        
        self.addToolBar(self.toolbar)
    
    def create_animated_action(self, icon, text, callback):
        """创建带有动画效果的工具栏操作"""
        action = QAction(icon, text, self)
        action.triggered.connect(callback)
        
        # 获取该操作对应的QToolButton
        action.button = None
        
        # 在下一个事件循环中查找按钮
        QTimer.singleShot(0, lambda: self.find_action_button(action))
        
        return action
    
    def find_action_button(self, action):
        """查找与特定操作关联的工具栏按钮"""
        for button in self.toolbar.findChildren(QToolButton):
            if button.defaultAction() == action:
                action.button = button
                
                # 添加悬停效果
                original_style = button.styleSheet()
                original_icon_size = button.iconSize()  # 保存初始图标大小
                
                # 保存动画引用以便能够停止之前的动画
                if not hasattr(button, '_hover_animation'):
                    button._hover_animation = None
                
                def enter_event(e, btn=button):
                    # 如果存在运行中的动画，先停止它
                    if hasattr(btn, '_hover_animation') and btn._hover_animation is not None:
                        try:
                            if btn._hover_animation().state() == QAbstractAnimation.Running:
                                btn._hover_animation().stop()
                        except (RuntimeError, ReferenceError):
                            # 如果动画对象已经被删除，清空引用
                            btn._hover_animation = None
                    
                    # 创建缩放动画
                    anim = QPropertyAnimation(btn, b"iconSize")
                    # 使用弱引用存储动画对象
                    btn._hover_animation = weakref.ref(anim)
                    anim.setDuration(150)  # 减少动画时间以避免延迟感
                    anim.setStartValue(btn.iconSize())
                    anim.setEndValue(QSize(28, 28))  # 稍微放大图标
                    anim.setEasingCurve(QEasingCurve.OutCubic)  # 使用更平滑的缓动曲线
                    anim.start(QAbstractAnimation.DeleteWhenStopped)
                    
                    # 设置悬停样式
                    accent_color = self.palette().color(QPalette.Highlight).name()
                    btn.setStyleSheet(f"""
                        QToolButton {{
                            border-radius: 5px;
                            padding: 5px;
                            border-bottom: 2px solid {accent_color};
                        }}
                    """)
                    
                    QToolTip.showText(
                        btn.mapToGlobal(QPoint(btn.width()/2, btn.height())), 
                        btn.defaultAction().text()
                    )
                
                def leave_event(e, btn=button):
                    # 如果存在运行中的动画，先停止它
                    if hasattr(btn, '_hover_animation') and btn._hover_animation is not None:
                        try:
                            if btn._hover_animation() and btn._hover_animation().state() == QAbstractAnimation.Running:
                                btn._hover_animation().stop()
                        except (RuntimeError, ReferenceError):
                            # 如果动画对象已经被删除，清空引用
                            btn._hover_animation = None
                    
                    # 创建缩放动画（恢复原始大小）
                    anim = QPropertyAnimation(btn, b"iconSize")
                    # 使用弱引用存储动画对象
                    btn._hover_animation = weakref.ref(anim)
                    anim.setDuration(150)  # 减少动画时间
                    anim.setStartValue(btn.iconSize())
                    anim.setEndValue(original_icon_size)  # 使用保存的初始大小
                    anim.setEasingCurve(QEasingCurve.OutCubic)  # 使用更平滑的缓动曲线
                    anim.start(QAbstractAnimation.DeleteWhenStopped)
                    
                    # 恢复原始样式
                    btn.setStyleSheet(original_style)
                    
                    # 确保移除底部边框
                    QTimer.singleShot(50, lambda: btn.setStyleSheet(original_style))
                
                # 替换原始的悬停事件处理
                button.enterEvent = enter_event
                button.leaveEvent = leave_event
                
                # 添加点击动画
                original_mouse_press = button.mousePressEvent
                
                def press_animation(e, btn=button):
                    # 创建按下动画
                    anim = QPropertyAnimation(btn, b"iconSize")
                    anim.setDuration(100)
                    anim.setStartValue(btn.iconSize())
                    anim.setEndValue(QSize(20, 20))  # 稍微缩小图标
                    anim.start(QAbstractAnimation.DeleteWhenStopped)
                    
                    # 调用原始的鼠标按下事件
                    original_mouse_press(e)
                
                button.mousePressEvent = press_animation
                
                # 替换原始的鼠标释放事件
                original_mouse_release = button.mouseReleaseEvent
                
                def release_animation(e, btn=button):
                    # 创建释放动画 - 恢复到原始大小而不是固定值
                    anim = QPropertyAnimation(btn, b"iconSize")
                    anim.setDuration(200)
                    anim.setStartValue(btn.iconSize())
                    anim.setEndValue(original_icon_size)  # 使用保存的初始大小
                    anim.setEasingCurve(QEasingCurve.OutBack)
                    anim.start(QAbstractAnimation.DeleteWhenStopped)
                    
                    # 调用原始的鼠标释放事件
                    original_mouse_release(e)
                
                button.mouseReleaseEvent = release_animation
                break
    
    def setup_sidebar(self):
        """设置应用程序侧边栏"""
        # 创建侧边栏容器
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        
        # 侧边栏布局
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(8)
        
        # 工具列表组
        self.sidebar_group = QFrame()
        self.sidebar_group.setObjectName("sidebarGroup")
        
        # 创建布局
        sidebar_group_layout = QVBoxLayout(self.sidebar_group)
        sidebar_group_layout.setContentsMargins(0, 10, 0, 10)
        sidebar_group_layout.setSpacing(8)
        
        # 添加侧边栏标题
        title_label = QLabel("Glary Utilities")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px; padding: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title_label)
        
        # 应用程序功能类别标题
        # common_tools_label = QLabel(self.settings.get_translation("general", "common_tools"))
        # common_tools_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #aaaaaa; padding: 5px;")
        # sidebar_layout.addWidget(common_tools_label)
        
        # 添加主要功能按钮
        self.page_buttons["Dashboard"] = self.create_sidebar_button("Dashboard", "Home", sidebar_group_layout)
        self.page_buttons["System Cleaner"] = self.create_sidebar_button("System Cleaner", "Cleaner", sidebar_group_layout)
        self.page_buttons["Disk Check"] = self.create_sidebar_button("Disk Check", "Disk", sidebar_group_layout)
        self.page_buttons["Virus Scan"] = self.create_sidebar_button("Virus Scan", "Virus", sidebar_group_layout)
        
        # 系统工具类别标题
        # system_tools_label = QLabel(self.settings.get_translation("general", "system_tools"))
        # system_tools_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #aaaaaa; margin-top: 15px; padding: 5px;")
        # sidebar_layout.addWidget(system_tools_label)
        
        # 添加系统工具按钮
        self.page_buttons["Boot Repair"] = self.create_sidebar_button("Boot Repair", "Boot", sidebar_group_layout)
        self.page_buttons["System Repair"] = self.create_sidebar_button("System Repair", "Repair", sidebar_group_layout)
        self.page_buttons["DISM Tool"] = self.create_sidebar_button("DISM Tool", "Dism", sidebar_group_layout)
        self.page_buttons["Network Reset"] = self.create_sidebar_button("Network Reset", "Network", sidebar_group_layout)
        
        # 信息与设置类别标题
        # info_settings_label = QLabel(self.settings.get_translation("general", "info_settings"))
        # info_settings_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #aaaaaa; margin-top: 15px; padding: 5px;")
        # sidebar_layout.addWidget(info_settings_label)
        
        # 添加信息与设置按钮
        self.page_buttons["System Info"] = self.create_sidebar_button("System Info", "SystemInfo", sidebar_group_layout)
        # self.page_buttons["Settings"] = self.create_sidebar_button("Settings", "Settings", sidebar_group_layout)
        
        sidebar_layout.addWidget(self.sidebar_group)
        
        # 底部版本信息
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("color: #888888; font-size: 12px;")
        version_label.setAlignment(Qt.AlignCenter)
        
        sidebar_layout.addStretch(1)  # 添加可拉伸的空间，推送版本标签到底部
        sidebar_layout.addWidget(version_label)

    def create_sidebar_button(self, text, icon_name, parent_layout):
        """创建侧边栏按钮"""
        button = QPushButton(self.settings.get_translation("general", text.lower().replace(' ', '_')))
        button.setCheckable(True)
        button.setObjectName(f"sidebar_btn_{text.lower().replace(' ', '_')}")
        button.setProperty("page", text)  # 用于识别对应的页面
        button.setMinimumHeight(40)
        button.setCursor(Qt.PointingHandCursor)
        
        # 增加圆角和样式
        base_style = """
            QPushButton {
                text-align: left;
                padding-left: 15px;
                border: none;
                border-radius: 8px;
                color: #bbbbbb;
                font-size: 14px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
            }
            QPushButton:checked {
                background-color: palette(highlight);
                color: white;
                font-weight: bold;
            }
        """
        button.setStyleSheet(base_style)
        
        # 尝试设置图标
        icon_attr = getattr(Icon, icon_name, None)
        if icon_attr and hasattr(icon_attr, 'Exist') and icon_attr.Exist:
            button.setIcon(QIcon(getattr(icon_attr, 'Path')))
            button.setIconSize(QSize(20, 20))
            # 保存原始样式并添加带有图标的样式
            button.setStyleSheet(base_style + """
                QPushButton {
                    padding-left: 10px;
            }
        """)
        
        # 保存原始样式和动画引用
        button._base_style = button.styleSheet()
        button._hover_animation = None
        
        # 创建悬停进入动画
        def on_hover_enter(event):
            if not button.isChecked():
                # 停止任何正在运行的动画
                if hasattr(button, '_hover_animation') and button._hover_animation is not None:
                    try:
                        if button._hover_animation() and button._hover_animation().state() == QAbstractAnimation.Running:
                            button._hover_animation().stop()
                    except (RuntimeError, ReferenceError):
                        # 如果动画对象已经被删除，清空引用
                        button._hover_animation = None
                
                # 创建样式字符串
                hover_style = base_style
                if icon_attr and hasattr(icon_attr, 'Exist') and icon_attr.Exist:
                    hover_style += """
                        QPushButton {
                            padding-left: 10px;
                            color: white;
                            background-color: rgba(255, 255, 255, 0.1);
                        }
                    """
                else:
                    hover_style += """
                        QPushButton {
                            color: white;
                            background-color: rgba(255, 255, 255, 0.1);
                        }
                    """
                
                # 直接设置样式，减少不必要的动画
                button.setStyleSheet(hover_style)
                
        # 创建悬停离开动画
        def on_hover_leave(event):
            if not button.isChecked():
                # 停止任何正在运行的动画
                if hasattr(button, '_hover_animation') and button._hover_animation is not None:
                    try:
                        if button._hover_animation() and button._hover_animation().state() == QAbstractAnimation.Running:
                            button._hover_animation().stop()
                    except (RuntimeError, ReferenceError):
                        # 如果动画对象已经被删除，清空引用
                        button._hover_animation = None
                
                # 创建样式字符串
                leave_style = base_style
                if icon_attr and hasattr(icon_attr, 'Exist') and icon_attr.Exist:
                    leave_style += """
                        QPushButton {
                            padding-left: 10px;
                        }
                    """
                
                # 直接设置样式，减少不必要的动画
                button.setStyleSheet(leave_style)
                
        # 连接悬停事件
        button.enterEvent = on_hover_enter
        button.leaveEvent = on_hover_leave
        
        # 页面切换处理
        def on_clicked(checked, page=text):
            # 停止任何正在运行的动画
            if hasattr(button, '_hover_animation') and button._hover_animation is not None:
                try:
                    if button._hover_animation() and button._hover_animation().state() == QAbstractAnimation.Running:
                        button._hover_animation().stop()
                except (RuntimeError, ReferenceError):
                    # 如果动画对象已经被删除，清空引用
                    button._hover_animation = None
            # 设置活动页面
            self.set_active_page(page)
        
        # 连接按钮点击事件
        button.clicked.connect(on_clicked)
        
        # 添加到布局
        parent_layout.addWidget(button)
        
        return button

    def setup_content_area(self):
        """Set up the content area"""
        self.content_area.setStyleSheet("""
            background-color: #1e1e1e;
            border: none;
        """)
        
        # Initialize page indices dictionary and buttons dictionary
        self.page_indices = {}
        self.page_buttons = {}
        
        # Setup content pages
        self.setup_content_pages()

    def setup_content_pages(self):
        """设置内容页面"""
        # 创建所有页面
        self.dashboard = DashboardWidget()
        self.content_area.addWidget(self.dashboard)
        self.page_indices["Dashboard"] = self.content_area.count() - 1
        
        # System Cleaner
        self.system_cleaner = SystemCleanerWidget()
        self.content_area.addWidget(self.system_cleaner)
        self.page_indices["System Cleaner"] = self.content_area.count() - 1
        
        # GPU Information
        # self.gpu_info = GPUInfoWidget()
        # self.content_area.addWidget(self.gpu_info)
        # self.page_indices["GPU Information"] = self.content_area.count() - 1
        
        # System Repair
        self.system_repair = SystemRepairWidget()
        self.content_area.addWidget(self.system_repair)
        self.page_indices["System Repair"] = self.content_area.count() - 1
        
        # DISM Tool
        self.dism_tool = DismToolWidget()
        self.content_area.addWidget(self.dism_tool)
        self.page_indices["DISM Tool"] = self.content_area.count() - 1
        
        # Network Reset
        self.network_reset = NetworkResetWidget()
        self.content_area.addWidget(self.network_reset)
        self.page_indices["Network Reset"] = self.content_area.count() - 1
        
        # Disk Check
        self.disk_check = DiskCheckWidget()
        self.content_area.addWidget(self.disk_check)
        self.page_indices["Disk Check"] = self.content_area.count() - 1
        
        # Boot Repair
        self.boot_repair = BootRepairWidget()
        self.content_area.addWidget(self.boot_repair)
        self.page_indices["Boot Repair"] = self.content_area.count() - 1
        
        # Virus Scan
        self.virus_scan = VirusScanWidget()
        self.content_area.addWidget(self.virus_scan)
        self.page_indices["Virus Scan"] = self.content_area.count() - 1
        
        # System Information
        self.system_info = SystemInfoWidget()
        self.content_area.addWidget(self.system_info)
        self.page_indices["System Info"] = self.content_area.count() - 1
        
        # Settings - 注意：SettingsWidget不是BaseComponent的子类
        self.settings_page = SettingsWidget(self.settings)
        self.content_area.addWidget(self.settings_page)
        self.page_indices["Settings"] = self.content_area.count() - 1
        
        # Set Dashboard as active page
        self.set_active_page("Dashboard")
        
        self.fade_in_animation = QPropertyAnimation(self.content_area, b"windowOpacity")
        self.fade_in_animation.setDuration(150)
        self.fade_in_animation.setStartValue(0.7)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.OutCubic)

    def setup_menu_bar(self):
        """设置菜单栏"""
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #2d2d30;
                color: #cccccc;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #3a3a3a;
            }
            QMenu {
                background-color: #2d2d30;
                border: 1px solid #3a3a3a;
                color: #cccccc;
            }
            QMenu::item {
                padding: 5px 30px 5px 20px;
                border: none;
            }
            QMenu::item:selected {
                background-color: #3a3a3a;
            }
        """)
        
        self.file_menu = self.menu_bar.addMenu(self.settings.get_translation("menu", "file"))
        
        self.exit_action = QAction(self.settings.get_translation("menu", "exit"), self)
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)
        
        self.help_menu = self.menu_bar.addMenu(self.settings.get_translation("menu", "help"))
        
        self.help_action = QAction(self.settings.get_translation("menu", "help"), self)
        self.help_action.triggered.connect(self.show_help_dialog)
        self.help_menu.addAction(self.help_action)
        
        self.system_info_action = QAction(self.settings.get_translation("menu", "system_info"), self)
        self.system_info_action.triggered.connect(self.show_system_info)
        self.help_menu.addAction(self.system_info_action)
        
        self.about_action = QAction(self.settings.get_translation("menu", "about"), self)
        self.about_action.triggered.connect(self.show_about_dialog)
        self.menu_bar.addAction(self.about_action)
        
        self.setMenuBar(self.menu_bar)
    
    def apply_theme(self):
        """应用主题设置"""
        # 获取当前主题名称
        theme_name = self.settings.get_setting("theme", "dark")
        
        # 设置主题管理器当前主题
        self.theme_manager.set_current_theme(theme_name)
        
        # 应用样式表
        self.setStyleSheet(self.theme_manager.generate_style_sheet())
        
        # 应用透明度
        self.apply_transparency()
        
        # 更新组件的主题
        self.update_component_themes()
            
    def update_component_themes(self):
        """Update the theme for all components"""
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
                        if button._hover_animation() and button._hover_animation().state() == QAbstractAnimation.Running:
                            button._hover_animation().stop()
                    except (RuntimeError, ReferenceError):
                        # 如果动画对象已经被删除，清空引用
                        button._hover_animation = None
            elif hasattr(button, 'property') and button.property("page"):
                button.setChecked(False)
                
        # 停止所有正在运行的页面切换动画
        if hasattr(self, '_page_animation') and self._page_animation is not None:
            try:
                if isinstance(self._page_animation, QParallelAnimationGroup) and self._page_animation.state() == QAbstractAnimation.Running:
                    self._page_animation.stop()
            except (RuntimeError, ReferenceError):
                # 如果动画对象已经被删除，清空引用
                self._page_animation = None
        
        # 检查页面是否存在于页面索引中
        if page_name not in self.page_indices:
            logging.error(f"页面 '{page_name}' 不存在")
            return
            
        # 记录当前可见页面的索引和目标索引  
        current_index = self.content_area.currentIndex()
        target_index = self.page_indices[page_name]
        
        # 更新状态栏提示
        self.status_bar.showMessage(f"{self.settings.get_translation('general', 'switched_to', 'Switched to')} {page_name}", 2000)
        
        # 如果当前没有活动页面或点击的是当前页面，直接设置
        if current_index == -1 or current_index == target_index:
            self.content_area.setCurrentIndex(target_index)
            self._update_page_content(page_name, target_index)
            return
            
        # 创建页面切换动画
        self._page_animation = QParallelAnimationGroup()
        
        # 当前页面和目标页面
        current_widget = self.content_area.widget(current_index)
        target_widget = self.content_area.widget(target_index)
        
        # 确定动画方向（左或右）
        direction = 1 if target_index > current_index else -1
        
        # 当前页面淡出动画
        fade_out = QPropertyAnimation(current_widget, b"geometry")
        fade_out.setDuration(200)
        current_geo = current_widget.geometry()
        fade_out.setStartValue(current_geo)
        fade_out.setEndValue(QRect(
            current_geo.x() - direction * current_geo.width(),
            current_geo.y(),
            current_geo.width(),
            current_geo.height()
        ))
        fade_out.setEasingCurve(QEasingCurve.OutCubic)
        
        # 目标页面淡入动画
        fade_in = QPropertyAnimation(target_widget, b"geometry")
        fade_in.setDuration(200)
        target_geo = target_widget.geometry()
        fade_in.setStartValue(QRect(
            target_geo.x() + direction * target_geo.width(),
            target_geo.y(),
            target_geo.width(),
            target_geo.height()
        ))
        fade_in.setEndValue(target_geo)
        fade_in.setEasingCurve(QEasingCurve.OutCubic)
        
        # 添加动画到组
        self._page_animation.addAnimation(fade_out)
        self._page_animation.addAnimation(fade_in)
        
        # 准备目标页面
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
        
        self.file_menu.setTitle(self.settings.get_translation("menu", "file"))
        self.help_menu.setTitle(self.settings.get_translation("menu", "help"))
        
        self.exit_action.setText(self.settings.get_translation("menu", "exit"))
        self.help_action.setText(self.settings.get_translation("menu", "help"))
        self.system_info_action.setText(self.settings.get_translation("menu", "system_info"))
        self.about_action.setText(self.settings.get_translation("menu", "about"))
        
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
        menu_keys = ["file", "exit", "help", "about", "system_info", "language"]
        for key in menu_keys:
            self.settings.get_translation("menu", key)
        
        self.dashboard_widget.check_all_translations()
        self.system_cleaner_widget.check_all_translations()
        self.gpu_info_widget.check_all_translations()
        self.system_repair_widget.check_all_translations()
        self.dism_tool_widget.check_all_translations()
        self.network_reset_widget.check_all_translations()
        self.disk_check_widget.check_all_translations()
        self.boot_repair_widget.check_all_translations()
        self.virus_scan_widget.check_all_translations()
        self.system_info_widget.check_all_translations()
        self.settings_widget.check_all_translations()
    
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
        logo_pixmap = QPixmap("assets/images/icon.png")
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
    
    def show_status_message(self, message, timeout=0):
        """在状态栏显示消息，带有动画效果"""
        # 设置状态文本
        self.status_text.setText(message)
        
        # 创建状态指示器的动画
        pulse_anim = QPropertyAnimation(self.status_indicator, b"styleSheet")
        pulse_anim.setDuration(500)
        pulse_anim.setLoopCount(2)
        
        # 设置起始颜色
        pulse_anim.setStartValue("background-color: #4CAF50; border-radius: 6px;")
        # 设置结束颜色
        pulse_anim.setEndValue("background-color: #4CAF50; border-radius: 6px; border: 2px solid white;")
        
        # 创建文本标签的动画
        text_anim = QPropertyAnimation(self.status_text, b"styleSheet")
        text_anim.setDuration(500)
        text_anim.setStartValue("color: white; margin-left: 5px; font-weight: bold;")
        text_anim.setEndValue("color: white; margin-left: 5px;")
        
        # 创建并行动画组
        anim_group = QParallelAnimationGroup()
        anim_group.addAnimation(pulse_anim)
        anim_group.addAnimation(text_anim)
        anim_group.start(QAbstractAnimation.DeleteWhenStopped)
        
        # 如果设置了超时，则在超时后清除消息
        if timeout > 0:
            QTimer.singleShot(timeout, lambda: self.status_text.setText(""))
            
            # 创建淡出动画
            fade_out = QPropertyAnimation(self.status_text, b"styleSheet")
            fade_out.setDuration(500)
            fade_out.setStartValue("color: white; margin-left: 5px;")
            fade_out.setEndValue("color: rgba(255, 255, 255, 0); margin-left: 5px;")
            
            # 在超时前稍微延迟执行淡出动画
            QTimer.singleShot(timeout - 500, lambda: fade_out.start(QAbstractAnimation.DeleteWhenStopped)) 