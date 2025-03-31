import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QStackedWidget, QTabWidget,
                            QFrame, QSplitter, QToolButton, QStyleFactory,
                            QAction, QMenu, QMenuBar, QStatusBar, QToolBar,
                            QSizePolicy, QDialog, QTextBrowser, QDialogButtonBox,
                            QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPalette, QCursor

from components.dashboard import DashboardWidget
from components.system_cleaner import SystemCleanerWidget
from components.gpu_info import GPUInfoWidget
from components.system_repair import SystemRepairWidget
from components.dism_tool import DISMToolWidget
from components.network_reset import NetworkResetWidget
from components.disk_check import DiskCheckWidget
from components.boot_repair import BootRepairWidget
from components.virus_scan import VirusScanWidget
from components.system_info import SystemInfoWidget
from components.settings import SettingsWidget
from components.icons import Icon
from animations import AnimationUtils

class MainWindow(QMainWindow):
    """主应用程序窗口"""
    
    # 语言更改信号
    language_changed = pyqtSignal(str)
    
    def __init__(self, settings):
        super().__init__()
        
        self.settings = settings
        
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
            print("警告: 找到缺失的翻译!")
            for language, sections in missing_translations.items():
                print(f"\n语言: {language}")
                for section, keys in sections.items():
                    print(f"  部分: {section}")
                    for key in keys:
                        print(f"    - {key}")
        
        # 应用窗口图标
        self.apply_window_icon()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Glary Utilities")
        self.setMinimumSize(1000, 700)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;  /* 背景颜色 */
                border: 2px solid #00a8ff;  /* 边框颜色 */
                border-radius: 10px;         /* 边框圆角 */
            }
        """)
        
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
        self.content_area.setStyleSheet("""
            #contentArea {
                background-color: #1e1e1e;
            }
        """)
        
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.content_area)
        
        # 修复：确保 splitter 比例正确，内容区域伸展填充
        self.splitter.setStretchFactor(0, 0)  # 侧边栏不会伸展
        self.splitter.setStretchFactor(1, 1)  # 内容区域会伸展
        
        # 设置分隔条初始位置
        self.splitter.setSizes([220, self.width() - 220])
        
        # 添加到主布局，确保填满整个窗口
        self.main_layout.addWidget(self.splitter, 1)  # 设置伸展因子
        
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
        """)
        self.setStatusBar(self.status_bar)
        
        self.setup_content_area()
        self.setup_menu_bar()
        self.apply_theme()
        self.apply_transparency()
        
        default_tab = self.settings.get_setting("default_tab", "Dashboard")
        self.set_active_page(default_tab)
        
        self.status_bar.showMessage("欢迎使用 Glary Utilities", 5000)
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(20)
        shadow_effect.setXOffset(5)
        shadow_effect.setYOffset(5)
        shadow_effect.setColor(QColor(0, 0, 0, 160))  # 半透明黑色阴影
        self.setGraphicsEffect(shadow_effect)

    def create_toolbar(self):
        """创建顶部工具栏"""
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(22, 22))
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #2d2d30;
                border-bottom: 1px solid #3a3a3a;
                spacing: 5px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 2px;
                color: #cccccc;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #3a3a3a;
            }
            QToolButton:pressed {
                background-color: #007acc;
            }
        """)
        if Icon.Home.Exist:    
            self.home_action = QAction(QIcon(Icon.Home.Path), "主页", self)
            self.home_action.triggered.connect(lambda: self.set_active_page("Dashboard"))
            self.toolbar.addAction(self.home_action)
        
        if Icon.Cleaner.Exist:
            self.clean_action = QAction(QIcon(Icon.Cleaner.Path), "系统清理", self)
            self.clean_action.triggered.connect(lambda: self.set_active_page("System Cleaner"))
            self.toolbar.addAction(self.clean_action)
        
        if Icon.Disk.Exist:
            self.disk_action = QAction(QIcon(Icon.Disk.Path), "磁盘检查", self)
            self.disk_action.triggered.connect(lambda: self.set_active_page("Disk Check"))
            self.toolbar.addAction(self.disk_action)
        
        if Icon.Virus.Exist:
            self.virus_action = QAction(QIcon(Icon.Virus.Path), "病毒扫描", self)
            self.virus_action.triggered.connect(lambda: self.set_active_page("Virus Scan"))
            self.toolbar.addAction(self.virus_action)
        
        if Icon.Settings.Exist:
            self.settings_action = QAction(QIcon(Icon.Settings.Path), "设置", self)
            self.settings_action.triggered.connect(lambda: self.set_active_page("Settings"))
            self.toolbar.addAction(self.settings_action)
        
        self.addToolBar(self.toolbar)
    
    def setup_sidebar(self):
        """设置应用程序侧边栏"""
        # 创建侧边栏容器
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("""
            #sidebar {
                background-color: #252525;
                border-right: 1px solid #3a3a3a;
                border-radius: 0px;
            }
        """)
        
        # 侧边栏布局
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(8)
        
        # 工具列表组
        self.sidebar_group = QFrame()
        self.sidebar_group.setObjectName("sidebarGroup")
        self.sidebar_group.setStyleSheet("""
            #sidebarGroup {
                background-color: transparent;
                border: none;
            }
        """)
        
        # 工具列表布局
        sidebar_group_layout = QVBoxLayout(self.sidebar_group)
        sidebar_group_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_group_layout.setSpacing(5)
        
        # 添加按钮 - 使用布局而不是硬编码位置
        self.create_sidebar_button(self.tr("Dashboard"), "Home", sidebar_group_layout)
        self.create_sidebar_button(self.tr("System Cleaner"), "Cleaner", sidebar_group_layout)
        self.create_sidebar_button(self.tr("GPU Information"), "GPU", sidebar_group_layout)
        self.create_sidebar_button(self.tr("System Repair"), "Repair", sidebar_group_layout)
        self.create_sidebar_button(self.tr("DISM Tool"), "Dism", sidebar_group_layout)
        self.create_sidebar_button(self.tr("Network Reset"), "Network", sidebar_group_layout)
        self.create_sidebar_button(self.tr("Disk Check"), "Disk", sidebar_group_layout)
        self.create_sidebar_button(self.tr("Boot Repair"), "Boot", sidebar_group_layout)
        self.create_sidebar_button(self.tr("Virus Scan"), "Virus", sidebar_group_layout)
        self.create_sidebar_button(self.tr("System Information"), "SystemInfo", sidebar_group_layout)
        
        # 添加工具列表到侧边栏
        sidebar_layout.addWidget(self.sidebar_group)
        
        # 标题（App名称）- 移至底部
        app_title = QLabel("Glary Utilities")
        app_title.setStyleSheet("color: #e0e0e0; font-size: 18px; font-weight: bold;")
        
        # 添加伸缩项将设置按钮推到底部
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(app_title)
        
        # 在侧边栏底部添加设置按钮
        self.settings_button = QPushButton(self.tr("Settings"))
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.settings_button.setStyleSheet("""
            #settingsButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: none;
                border-radius: 6px;
                text-align: left;
                padding: 10px 15px;
                font-size: 14px;
                margin-bottom: 10px;
            }
            #settingsButton:hover {
                background-color: #454545;
            }
            #settingsButton:pressed {
                background-color: #505050;
            }
        """)
        
        # Add settings icon if available
        if Icon.Settings.Exist:
            settings_icon = QIcon(Icon.Settings.Path)
            if not settings_icon.isNull():
                self.settings_button.setIcon(settings_icon)
                self.settings_button.setIconSize(QSize(18, 18))
        
        # Connect settings button
        self.settings_button.clicked.connect(lambda: self.set_active_page("Settings"))
        
        # Add settings button to bottom of sidebar
        sidebar_layout.addWidget(self.settings_button)
        
        # 将侧边栏添加到主布局
        self.main_layout.addWidget(self.sidebar)

    def create_sidebar_button(self, text, icon_name, parent_layout):
        """创建侧边栏按钮"""
        button = QPushButton(text)
        button.setObjectName(f"{text.lower().replace(' ', '_')}_btn")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #a0a0a0;
                border: none;
                border-radius: 6px;
                text-align: left;
                padding: 10px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #353535;
                color: #e0e0e0;
            }
            QPushButton:checked {
                background-color: #454545;
                color: #ffffff;
                font-weight: bold;
            }
        """)
        button.setCheckable(True)
        button.setAutoExclusive(True)
        
        # 添加图标（如果可用）
        icon_path = None
        if icon_name == "Home":
            icon_path = Icon.Home.Path if Icon.Home.Exist else None
        elif icon_name == "Cleaner":
            icon_path = Icon.Cleaner.Path if Icon.Cleaner.Exist else None
        elif icon_name == "GPU":
            icon_path = Icon.GPU.Path if Icon.GPU.Exist else None
        elif icon_name == "Repair":
            icon_path = Icon.Repair.Path if Icon.Repair.Exist else None
        elif icon_name == "Dism":
            icon_path = Icon.Dism.Path if Icon.Dism.Exist else None
        elif icon_name == "Network":
            icon_path = Icon.Network.Path if Icon.Network.Exist else None
        elif icon_name == "Disk":
            icon_path = Icon.Disk.Path if Icon.Disk.Exist else None
        elif icon_name == "Boot":
            icon_path = Icon.Boot.Path if Icon.Boot.Exist else None
        elif icon_name == "Virus":
            icon_path = Icon.Virus.Path if Icon.Virus.Exist else None
        elif icon_name == "SystemInfo":
            icon_path = Icon.SystemInfo.Path if Icon.SystemInfo.Exist else None
        
        if icon_path:
            icon = QIcon(icon_path)
            if not icon.isNull():
                button.setIcon(icon)
                button.setIconSize(QSize(18, 18))
        
        # 添加到布局
        parent_layout.addWidget(button)
        
        # 将按钮添加到页面名称到按钮的映射
        self.page_buttons[text] = button
        
        # 连接点击事件
        button.clicked.connect(lambda: self.set_active_page(text))
        
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
        """Setup content pages for each menu option"""
        # Dashboard
        self.dashboard = DashboardWidget(self.settings)
        self.content_area.addWidget(self.dashboard)
        self.page_indices["Dashboard"] = self.content_area.count() - 1
        
        # System Cleaner
        self.system_cleaner = SystemCleanerWidget(self.settings)
        self.content_area.addWidget(self.system_cleaner)
        self.page_indices["System Cleaner"] = self.content_area.count() - 1
        
        # GPU Information
        self.gpu_info = GPUInfoWidget(self.settings)
        self.content_area.addWidget(self.gpu_info)
        self.page_indices["GPU Information"] = self.content_area.count() - 1
        
        # System Repair
        self.system_repair = SystemRepairWidget(self.settings)
        self.content_area.addWidget(self.system_repair)
        self.page_indices["System Repair"] = self.content_area.count() - 1
        
        # DISM Tool
        self.dism_tool = DISMToolWidget(self.settings)
        self.content_area.addWidget(self.dism_tool)
        self.page_indices["DISM Tool"] = self.content_area.count() - 1
        
        # Network Reset
        self.network_reset = NetworkResetWidget(self.settings)
        self.content_area.addWidget(self.network_reset)
        self.page_indices["Network Reset"] = self.content_area.count() - 1
        
        # Disk Check
        self.disk_check = DiskCheckWidget(self.settings)
        self.content_area.addWidget(self.disk_check)
        self.page_indices["Disk Check"] = self.content_area.count() - 1
        
        # Boot Repair
        self.boot_repair = BootRepairWidget(self.settings)
        self.content_area.addWidget(self.boot_repair)
        self.page_indices["Boot Repair"] = self.content_area.count() - 1
        
        # Virus Scan
        self.virus_scan = VirusScanWidget(self.settings)
        self.content_area.addWidget(self.virus_scan)
        self.page_indices["Virus Scan"] = self.content_area.count() - 1
        
        # System Information
        self.system_info = SystemInfoWidget(self.settings)
        self.content_area.addWidget(self.system_info)
        self.page_indices["System Information"] = self.content_area.count() - 1
        
        # Settings
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
        theme = self.settings.get_setting("theme", "深色")
        
        # 应用主题
        if theme == "深色":
            self.apply_dark_theme()
        elif theme == "浅色":
            self.apply_light_theme()
        elif theme == "蓝色主题":
            self.apply_blue_theme()
        elif theme == "绿色主题":
            self.apply_green_theme()
        elif theme == "紫色主题":
            self.apply_purple_theme()
        elif theme == "自定义":
            self.apply_custom_theme()
        else:
            self.apply_dark_theme()  # 默认为深色主题
            
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

    def lighten_color(self, color, amount=20):
        """调亮或调暗十六进制颜色
        
        Args:
            color: 十六进制颜色代码 (如 "#1e1e1e")
            amount: 亮度调整量 (-100到100)
        
        Returns:
            新的十六进制颜色代码
        """
        try:
            c = QColor(color)
            h, s, l, a = c.getHslF()
            
            # 调整亮度
            l = max(0, min(1, l + amount / 100.0))
            
            c.setHslF(h, s, l, a)
            return c.name()
        except:
            return color

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
        """Set the active page in the content area"""
        # Ensure page_name is in the page_indices dictionary
        if page_name in self.page_indices:
            # Show the selected page
            self.content_area.setCurrentIndex(self.page_indices[page_name])
            
            # Update button states if page_buttons is available
            if hasattr(self, 'page_buttons'):
                for name, index in self.page_indices.items():
                    button = self.page_buttons.get(name, None)
                    if button:
                        button.setChecked(name == page_name)
            
            # Fade in animation
            self.fade_in_animation.setDuration(300)
            self.fade_in_animation.setStartValue(0.5)
            self.fade_in_animation.setEndValue(1.0)
            self.fade_in_animation.setEasingCurve(QEasingCurve.OutQuad)
            self.fade_in_animation.start()
    
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
        """刷新所有组件以反映语言更改"""
        for i in range(self.content_area.count()):
            widget = self.content_area.widget(i)
            if i == self.content_area.currentIndex():
                AnimationUtils.pulse(widget, duration=300)
                if hasattr(widget, 'refresh_language') and callable(getattr(widget, 'refresh_language')):
                    widget.refresh_language()
    
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

    def apply_dark_theme(self):
        """应用深色主题"""
        bg_color = "#1e1e1e"
        text_color = "#e0e0e0"
        accent_color = "#00a8ff"
        self._apply_theme_colors(bg_color, text_color, accent_color)
    
    def apply_light_theme(self):
        """应用浅色主题"""
        bg_color = "#f0f0f0"
        text_color = "#333333"
        accent_color = "#007acc"
        self._apply_theme_colors(bg_color, text_color, accent_color)
    
    def apply_blue_theme(self):
        """应用蓝色主题"""
        bg_color = "#0d1117"
        text_color = "#e6edf3"
        accent_color = "#58a6ff"
        self._apply_theme_colors(bg_color, text_color, accent_color)
    
    def apply_green_theme(self):
        """应用绿色主题"""
        bg_color = "#0f1610"
        text_color = "#e6edf3"
        accent_color = "#4caf50"
        self._apply_theme_colors(bg_color, text_color, accent_color)
    
    def apply_purple_theme(self):
        """应用紫色主题"""
        bg_color = "#13111d"
        text_color = "#e6edf3"
        accent_color = "#9c27b0"
        self._apply_theme_colors(bg_color, text_color, accent_color)
    
    def apply_custom_theme(self):
        """应用自定义主题"""
        bg_color = self.settings.get_setting("custom_bg_color", "#1e1e1e")
        text_color = self.settings.get_setting("custom_text_color", "#e0e0e0")
        accent_color = self.settings.get_setting("custom_accent_color", "#00a8ff")
        self._apply_theme_colors(bg_color, text_color, accent_color)
    
    def _apply_theme_colors(self, bg_color, text_color, accent_color):
        """应用主题颜色"""
        # 生成辅助颜色
        bg_lighter = self.lighten_color(bg_color, 10)
        bg_darker = self.lighten_color(bg_color, -10)
        
        # 为整个应用程序设置样式表
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QWidget {{
                background-color: transparent;
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QPushButton {{
                background-color: {bg_lighter};
                color: {text_color};
                border: 1px solid {accent_color};
                border-radius: 6px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(bg_lighter, 10)};
                border: 1px solid {self.lighten_color(accent_color, 10)};
            }}
            QPushButton:pressed {{
                background-color: {self.lighten_color(bg_lighter, -5)};
            }}
            QPushButton:disabled {{
                background-color: {bg_darker};
                color: {self.lighten_color(bg_color, 30)};
                border: 1px solid {self.lighten_color(bg_color, 20)};
            }}
            QGroupBox {{
                color: {self.lighten_color(text_color, -10)};
                font-weight: bold;
                border: 1px solid {accent_color};
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: {bg_color};
            }}
            QCheckBox, QRadioButton {{
                color: {text_color};
            }}
            QCheckBox::indicator, QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                background-color: {bg_lighter};
                border: 1px solid {accent_color};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                background-color: {accent_color};
            }}
            QLineEdit, QTextEdit, QListWidget, QTableWidget, QComboBox {{
                background-color: {bg_lighter};
                color: {text_color};
                border: 1px solid {accent_color};
                border-radius: 6px;
                padding: 3px;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border: 1px solid {self.lighten_color(accent_color, 15)};
            }}
            QTextEdit {{
                background-color: {bg_lighter};
                color: {text_color};
            }}
            QTableWidget {{
                background-color: {bg_lighter};
                alternate-background-color: {self.lighten_color(bg_lighter, 5)};
                gridline-color: {self.lighten_color(accent_color, -20)};
                border: 1px solid {accent_color};
                border-radius: 6px;
            }}
            QTableWidget QHeaderView::section {{
                background-color: {bg_darker};
                color: {text_color};
                border: 1px solid {accent_color};
                padding: 4px;
            }}
            QProgressBar {{
                border: 1px solid {accent_color};
                border-radius: 6px;
                background-color: {bg_lighter};
                text-align: center;
                color: {text_color};
            }}
            QProgressBar::chunk {{
                background-color: {accent_color};
                border-radius: 5px;
            }}
            QTabWidget::pane {{
                border: 1px solid {accent_color};
                background-color: {bg_color};
                border-radius: 6px;
            }}
            QTabBar::tab {{
                background-color: {bg_lighter};
                color: {self.lighten_color(text_color, -10)};
                border: 1px solid {accent_color};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 12px;
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QTabBar::tab:hover {{
                background-color: {self.lighten_color(bg_lighter, 10)};
            }}
            QScrollBar {{
                background-color: {bg_color};
                width: 12px;
                height: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle {{
                background-color: {self.lighten_color(bg_color, 30)};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:hover {{
                background-color: {accent_color};
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                width: 0px;
                height: 0px;
            }}
            QScrollBar::add-page, QScrollBar::sub-page {{
                background-color: {bg_color};
            }}
            QStatusBar {{
                background-color: {accent_color};
                color: white;
            }}
        """) 