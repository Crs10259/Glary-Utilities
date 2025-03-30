import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QStackedWidget, QTabWidget,
                            QFrame, QSplitter, QToolButton, QStyleFactory,
                            QAction, QMenu, QMenuBar, QStatusBar, QToolBar,
                            QSizePolicy, QDialog, QTextBrowser, QDialogButtonBox)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPalette

from components.dashboard import DashboardWidget
from components.system_cleaner import SystemCleanerWidget
from components.gpu_info import GPUInfoWidget
from components.system_repair import SystemRepairWidget
from components.dism_tool import DISMToolWidget
from components.network_reset import NetworkResetWidget
from components.disk_check import DiskCheckWidget
from components.boot_repair import BootRepairWidget
from components.virus_scan import VirusScanWidget
from components.settings import SettingsWidget
from components.icons import Icon
from animations import AnimationUtils

class MainWindow(QMainWindow):
    """主应用程序窗口"""
    language_changed = pyqtSignal(str)
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        
        # 初始化属性
        self.nav_actions = {}
        self.sidebar_buttons = {}
        self.page_indices = {}
        
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
        
        self.init_ui()
        
        # 连接语言更改信号
        self.language_changed.connect(self.update_ui_language)
        
        # 应用窗口图标
        self.apply_window_icon()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Glary Utilities")
        self.setMinimumSize(1000, 700)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.create_toolbar()
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setChildrenCollapsible(False)
        
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setStyleSheet("""
            #sidebar {
                background-color: #252526;
                border-right: 1px solid #3a3a3a;
            }
        """)
        self.sidebar.setMinimumWidth(220)
        self.sidebar.setMaximumWidth(220)
        
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("contentArea")
        self.content_area.setStyleSheet("""
            #contentArea {
                background-color: #1e1e1e;
            }
        """)
        
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.content_area)
        self.splitter.setSizes([220, 780])
        
        self.main_layout.addWidget(self.splitter)
        
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
        """)
        self.setStatusBar(self.status_bar)
        
        self.setup_sidebar()
        self.setup_content_pages()
        self.setup_menu_bar()
        self.apply_theme()
        
        default_tab = self.settings.get_setting("default_tab", "Dashboard")
        self.set_active_page(default_tab)
        
        self.status_bar.showMessage("欢迎使用Glary Utilities", 5000)
    
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
        """设置侧边栏菜单"""
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(1)
        
        title_widget = QWidget()
        title_widget.setObjectName("sidebarTitle")
        title_widget.setStyleSheet("""
            #sidebarTitle {
                background-color: #007acc;
                min-height: 40px;
            }
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        title_icon = QLabel()
        title_icon.setPixmap(QPixmap("assets/images/icon.png").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_layout.addWidget(title_icon)
        
        self.title_label = QLabel(self.settings.get_translation("general", "dashboard"))
        title_layout.addWidget(self.title_label)
        
        sidebar_layout.addWidget(title_widget)
        
        self.create_sidebar_button("Dashboard", Icon.Home.Path, sidebar_layout)
        self.create_sidebar_button("System Cleaner", Icon.Clean.Path, sidebar_layout)
        self.create_sidebar_button("GPU Information", Icon.GPU.Path, sidebar_layout)
        self.create_sidebar_button("System Repair", Icon.Repair.Path, sidebar_layout)
        self.create_sidebar_button("DISM Tool", Icon.Dism.Path, sidebar_layout)
        self.create_sidebar_button("Network Reset", Icon.Network.Path, sidebar_layout)
        self.create_sidebar_button("Disk Check", Icon.Disk.Path, sidebar_layout)
        self.create_sidebar_button("Boot Repair", Icon.Boot.Path, sidebar_layout)
        self.create_sidebar_button("Virus Scan", Icon.Virus.Path, sidebar_layout)
        self.create_sidebar_button("Settings", Icon.Settings.Path, sidebar_layout)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sidebar_layout.addWidget(spacer)
    
    def create_sidebar_button(self, text, icon_name, parent_layout):
        """创建侧边栏菜单按钮"""
        button = QPushButton()
        button.setObjectName(f"sidebar_btn_{text.lower().replace(' ', '_')}")
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 0;
                color: #cccccc;
                font-size: 14px;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:checked {
                background-color: #007acc;
                color: white;
            }
        """)
        button.setCheckable(True)
        
        button_layout = QHBoxLayout(button)
        button_layout.setContentsMargins(10, 0, 10, 0)
        button_layout.setSpacing(10)
        
        icon_label = QLabel()
        icon_path = f"assets/images/{icon_name}"
        if os.path.exists(icon_path):
            icon_label.setPixmap(QPixmap(icon_path).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        button_layout.addWidget(icon_label)
        
        text_label = QLabel(self.settings.get_translation("general", text.lower().replace(' ', '_')))
        text_label.setObjectName(f"label_{text.lower().replace(' ', '_')}")
        button_layout.addWidget(text_label)
        
        button_layout.addStretch()
        
        button.clicked.connect(lambda: self.set_active_page(text))
        
        setattr(self, f"button_{text.lower().replace(' ', '_')}", button)
        setattr(self, f"label_{text.lower().replace(' ', '_')}", text_label)
        
        parent_layout.addWidget(button)
    
    def setup_content_pages(self):
        """设置内容页面"""
        self.dashboard_widget = DashboardWidget(self.settings)
        self.content_area.addWidget(self.dashboard_widget)
        
        self.system_cleaner_widget = SystemCleanerWidget(self.settings)
        self.content_area.addWidget(self.system_cleaner_widget)
        
        self.gpu_info_widget = GPUInfoWidget(self.settings)
        self.content_area.addWidget(self.gpu_info_widget)
        
        self.system_repair_widget = SystemRepairWidget(self.settings)
        self.content_area.addWidget(self.system_repair_widget)
        
        self.dism_tool_widget = DISMToolWidget(self.settings)
        self.content_area.addWidget(self.dism_tool_widget)
        
        self.network_reset_widget = NetworkResetWidget(self.settings)
        self.content_area.addWidget(self.network_reset_widget)
        
        self.disk_check_widget = DiskCheckWidget(self.settings)
        self.content_area.addWidget(self.disk_check_widget)
        
        self.boot_repair_widget = BootRepairWidget(self.settings)
        self.content_area.addWidget(self.boot_repair_widget)
        
        self.virus_scan_widget = VirusScanWidget(self.settings)
        self.content_area.addWidget(self.virus_scan_widget)
        
        self.settings_widget = SettingsWidget(self.settings)
        self.content_area.addWidget(self.settings_widget)
        
        self.page_indices = {
            "Dashboard": 0,
            "System Cleaner": 1,
            "GPU Information": 2,
            "System Repair": 3,
            "DISM Tool": 4,
            "Network Reset": 5,
            "Disk Check": 6,
            "Boot Repair": 7,
            "Virus Scan": 8,
            "Settings": 9
        }
        
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
        """应用当前主题"""
        theme = self.settings.get_setting("theme", "dark")
        
        if theme == "dark":
            self.apply_dark_theme()
        elif theme == "light":
            self.apply_light_theme()
        elif theme == "custom":
            self.apply_custom_theme()
        else:
            self.apply_system_theme()
    
    def apply_dark_theme(self):
        """应用黑暗主题"""
        self.setStyleSheet("""
            QMainWindow, QDialog, QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QLabel {
                background-color: transparent;
                border: none;
            }
            QPushButton {
                background-color: #444444;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #666666;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #252526;
                color: #e0e0e0;
                padding: 8px 16px;
                border: 1px solid #3a3a3a;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                border-bottom: 2px solid #007acc;
            }
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                margin-top: 1em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def apply_light_theme(self):
        """应用浅色主题"""
        self.setStyleSheet("""
            QMainWindow, QDialog, QWidget {
                background-color: #f8f8f8;
                color: #202020;
            }
            QLabel {
                background-color: transparent;
                border: none;
            }
            QPushButton {
                background-color: #e0e0e0;
                color: #202020;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: #f8f8f8;
            }
            QTabBar::tab {
                background-color: #e8e8e8;
                color: #202020;
                padding: 8px 16px;
                border: 1px solid #c0c0c0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #f8f8f8;
                border-bottom: 2px solid #0078d7;
            }
            QGroupBox {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                margin-top: 1em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def apply_custom_theme(self):
        """应用自定义主题"""
        bg_color = self.settings.get_setting("custom_bg_color", "#1e1e1e")
        text_color = self.settings.get_setting("custom_text_color", "#e0e0e0")
        accent_color = self.settings.get_setting("custom_accent_color", "#007acc")
        
        self.setStyleSheet(f"""
            QMainWindow, QDialog, QWidget {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QPushButton {{
                background-color: {QColor(bg_color).lighter(130).name()};
                color: {text_color};
                border: 1px solid {QColor(bg_color).lighter(150).name()};
                border-radius: 4px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background-color: {QColor(bg_color).lighter(150).name()};
            }}
            QPushButton:pressed {{
                background-color: {QColor(bg_color).lighter(170).name()};
            }}
            QTabWidget::pane {{
                border: 1px solid {QColor(bg_color).lighter(130).name()};
                background-color: {bg_color};
            }}
            QTabBar::tab {{
                background-color: {QColor(bg_color).lighter(110).name()};
                color: {text_color};
                padding: 8px 16px;
                border: 1px solid {QColor(bg_color).lighter(130).name()};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {bg_color};
                border-bottom: 2px solid {accent_color};
            }}
            QGroupBox {{
                border: 1px solid {QColor(bg_color).lighter(130).name()};
                border-radius: 4px;
                margin-top: 1em;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
    
    def apply_system_theme(self):
        """应用系统主题"""
        style = QStyleFactory.create("Fusion")
        self.setStyle(style)
        
        self.setStyleSheet("")
        
        palette = QPalette()
        self.setPalette(palette)
    
    def apply_window_icon(self):
        """为所有窗口应用窗口图标"""
        icon_path = "src/assets/images/icon.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            icon_path = "assets/images/icon.png"
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
    
    def set_active_page(self, page_name):
        """设置活动页面"""
        if page_name in self.page_indices:
            old_index = self.content_area.currentIndex()
            new_index = self.page_indices[page_name]
            
            if old_index == new_index:
                return
            
            for name, index in self.page_indices.items():
                button = getattr(self, f"button_{name.lower().replace(' ', '_')}", None)
                if button:
                    button.setChecked(name == page_name)
            
            self.title_label.setText(self.settings.get_translation("general", page_name.lower().replace(' ', '_')))
            
            old_widget = self.content_area.widget(old_index)
            new_widget = self.content_area.widget(new_index)
            
            direction = "left" if new_index > old_index else "right"
            
            new_widget.show()
            self.content_area.setCurrentIndex(new_index)
            
            AnimationUtils.slide_view_transition(old_widget, new_widget, direction)
            
            self.status_bar.showMessage(f"{page_name} 已加载", 2000)
    
    def change_language(self, language):
        """更改应用程序语言"""
        if language != self.settings.current_language:
            self.settings.set_setting("language", language)
            self.settings.save_settings()
            
            self.language_changed.emit(language)
            self.update_ui_language(language)
    
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