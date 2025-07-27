import os
import sys
import platform
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QPushButton, 
                          QComboBox, QCheckBox, QGroupBox, QFormLayout, QSlider, QLineEdit,
                          QColorDialog, QFileDialog, QDialog, QScrollArea, QSpinBox, QStatusBar,
                          QApplication, QMessageBox, QFrame, QRadioButton)
from PyQt5.QtCore import Qt, QSize, QSettings, QTranslator, QCoreApplication, QTimer
from PyQt5.QtGui import QColor, QIcon, QMovie
from utils.animations import AnimationUtils
from utils.theme_manager import ThemeManager
from utils.logger import Logger
import logging

class SettingsWidget(QWidget):
    """应用程序设置的窗口小部件"""
    
    def __init__(self, settings, parent=None) -> None:
        """初始化设置组件"""
        self.settings = settings
        self.logger = Logger().get_logger()
        self.main_window = parent
        super().__init__(parent)
        self.background_image_path = ""
        self.theme_manager = ThemeManager()
        self.animations = AnimationUtils()
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self) -> None:
        """设置UI组件"""
        # 创建整体布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题和说明
        title_label = QLabel(self.get_translation("title", "Settings"))
        title_label.setObjectName("title_label")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 5px;")
        main_layout.addWidget(title_label)
        
        desc_label = QLabel(self.get_translation("description", "Customize Glary Utilities to suit your needs"))
        desc_label.setObjectName("desc_label")
        desc_label.setStyleSheet("font-size: 14px; color: #a0a0a0; margin-bottom: 15px;")
        main_layout.addWidget(desc_label)
        
        # 创建标签页
        self.settings_tabs = QTabWidget()
        self.settings_tabs.setObjectName("settings_tabs")
        self.settings_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: transparent;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #a0a0a0;
                border: 1px solid #3a3a3a;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #333333;
                color: #e0e0e0;
            }
            QTabBar::tab:hover {
                background-color: #303030;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
        """)
        
        # 常规选项卡
        general_tab = QWidget()
        self.setup_general_tab(general_tab)
        self.settings_tabs.addTab(general_tab, "")  # 空标题，在语言更新时添加
        
        # 扫描选项卡
        scan_tab = QWidget()
        self.setup_scan_tab(scan_tab)
        self.settings_tabs.addTab(scan_tab, "")
        
        # 高级选项卡
        advanced_tab = QWidget()
        self.setup_advanced_tab(advanced_tab)
        self.settings_tabs.addTab(advanced_tab, "")
        
        # 外观选项卡
        appearance_tab = QWidget()
        self.setup_appearance_tab(appearance_tab)
        self.settings_tabs.addTab(appearance_tab, "")
        
        # 添加标签页
        main_layout.addWidget(self.settings_tabs)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # 恢复默认按钮 - 左对齐
        self.restore_defaults_button = QPushButton(self.get_translation("restore_defaults", "Restore Defaults"))
        self.restore_defaults_button.setObjectName("restore_defaults_button")
        self.restore_defaults_button.clicked.connect(self.reset_settings)
        self.restore_defaults_button.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: #e0e0e0;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #383838;
            }
        """)
        button_layout.addWidget(self.restore_defaults_button)
        
        # 弹性空间
        button_layout.addStretch()
        
        # 保存按钮 - 右对齐
        self.save_button = QPushButton(self.get_translation("save_settings", "Save Settings"))
        self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self._on_save_settings_clicked)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #00a8ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0096e0;
            }
            QPushButton:pressed {
                background-color: #0085c7;
            }
        """)
        button_layout.addWidget(self.save_button)
        
        # 应用按钮
        self.apply_button = QPushButton(self.get_translation("apply_settings", "Apply"))
        self.apply_button.setObjectName("apply_button")
        self.apply_button.clicked.connect(self.apply_settings)
        self.apply_button.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: #e0e0e0;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #383838;
            }
        """)
        button_layout.addWidget(self.apply_button)

        # Restart button – prompt and relaunch application
        self.restart_button = QPushButton(self.get_translation("restart_now", "Restart Now"))
        self.restart_button.setObjectName("restart_button")
        self.restart_button.clicked.connect(self._on_restart_clicked)
        self.restart_button.setStyleSheet("""
            QPushButton {
                background-color: #d35400;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #ba4a00;
            }
        """)
        button_layout.addWidget(self.restart_button)
        
        # 添加按钮布局
        main_layout.addLayout(button_layout)
        
        # 加载设置
        self.load_settings()
        
        # 更新本地化
        self.refresh_language()
        
    
    def setup_general_tab(self, general_tab) -> None:
        """设置常规选项卡"""
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # 内容容器
        general_container = QWidget()
        
        # 创建常规选项卡内容
        general_layout = QVBoxLayout(general_container)
        general_layout.setContentsMargins(15, 15, 15, 15)
        general_layout.setSpacing(20)  # 增加间距
        
        # General settings title
        title_label = QLabel(self.get_translation("general_title", "General Settings"))
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e0e0e0; margin-bottom: 10px;")
        general_layout.addWidget(title_label)

        # Language selection
        language_frame = QFrame()
        language_frame.setStyleSheet("background-color: rgba(40, 40, 40, 0.7); border-radius: 6px; padding: 10px;")
        language_layout = QVBoxLayout(language_frame)
        language_layout.setContentsMargins(15, 15, 15, 15)
        
        language_title = QLabel(self.get_translation("language_title", "Language"))
        language_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        language_layout.addWidget(language_title)
        
        language_desc = QLabel(self.get_translation("language_desc", "Select your preferred language."))
        language_desc.setStyleSheet("color: #b0b0b0; margin-bottom: 10px;")
        language_layout.addWidget(language_desc)
        
        # Language dropdown
        language_select_layout = QHBoxLayout()
        language_label = QLabel(self.get_translation("language", "Language:"))
        language_label.setStyleSheet("color: #e0e0e0;")
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("中文", "zh")
        self.language_combo.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #555555;
                border-radius: 4px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: #e0e0e0;
                selection-background-color: #444444;
            }
        """)
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        
        language_select_layout.addWidget(language_label)
        language_select_layout.addWidget(self.language_combo)
        language_select_layout.addStretch()
        language_layout.addLayout(language_select_layout)
        
        # Add language frame to tab layout
        general_layout.addWidget(language_frame)
        
        # Behavior settings frame
        behavior_frame = QFrame()
        behavior_frame.setStyleSheet("background-color: rgba(40, 40, 40, 0.7); border-radius: 6px; padding: 10px;")
        behavior_layout = QVBoxLayout(behavior_frame)
        behavior_layout.setContentsMargins(15, 15, 15, 15)
        
        behavior_title = QLabel(self.get_translation("behavior_title", "Application Behavior"))
        behavior_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        behavior_layout.addWidget(behavior_title)
        
        # Startup settings
        self.start_minimized_check = QCheckBox(self.get_translation("start_minimized", "Start minimized"))
        self.start_minimized_check.setStyleSheet("color: #e0e0e0; margin-top: 5px;")
        self.start_minimized_check.setObjectName("start_minimized")
        
        self.close_to_tray_check = QCheckBox(self.get_translation("close_to_tray", "Close to system tray"))
        self.close_to_tray_check.setStyleSheet("color: #e0e0e0; margin-top: 5px;")
        self.close_to_tray_check.setObjectName("close_to_tray")
        
        self.enable_animations_check = QCheckBox(self.get_translation("enable_animations", "启用动画效果"))
        self.enable_animations_check.setStyleSheet("color: #e0e0e0; margin-top: 5px;")
        self.enable_animations_check.setObjectName("enable_animations")
        self.enable_animations_check.stateChanged.connect(self.on_animations_changed)
        
        # Linux性能优化选项
        from tools.base_tools import PlatformManager
        platform_manager = PlatformManager()
        if platform_manager.is_linux():
            self.optimize_linux_performance_check = QCheckBox(self.get_translation("optimize_linux_performance", "优化Linux性能（禁用复杂动画）"))
            self.optimize_linux_performance_check.setStyleSheet("color: #e0e0e0; margin-top: 5px;")
            self.optimize_linux_performance_check.setObjectName("optimize_linux_performance")
            self.optimize_linux_performance_check.setChecked(True)  # 默认启用
            behavior_layout.addWidget(self.optimize_linux_performance_check)
        
        behavior_layout.addWidget(self.start_minimized_check)
        behavior_layout.addWidget(self.close_to_tray_check)
        behavior_layout.addWidget(self.enable_animations_check)
        
        # Add behavior frame to tab layout
        general_layout.addWidget(behavior_frame)
        
        # Add spacer at bottom
        general_layout.addStretch()
        
        # 设置滚动区域的内容
        scroll_area.setWidget(general_container)
        
        # 设置标签页的布局
        tab_layout = QVBoxLayout(general_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
        
    def setup_appearance_tab(self, appearance_tab):
        """设置外观选项卡"""
        layout = QVBoxLayout(appearance_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 添加标题
        title_label = QLabel(self.get_translation("appearance_title", "Appearance Settings"))
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e0e0e0; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 主题设置框架
        theme_frame = QFrame()
        theme_frame.setStyleSheet("background-color: rgba(40, 40, 40, 0.7); border-radius: 6px; padding: 10px;")
        theme_layout = QVBoxLayout(theme_frame)
        theme_layout.setContentsMargins(15, 15, 15, 15)
        
        # 主题设置标题
        theme_title = QLabel(self.get_translation("theme_title", "Theme"))
        theme_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        theme_layout.addWidget(theme_title)
        
        # 主题说明
        theme_desc = QLabel(self.get_translation("theme_desc", "Select your preferred theme."))
        theme_desc.setStyleSheet("color: #b0b0b0; margin-bottom: 10px;")
        theme_layout.addWidget(theme_desc)
        
        # 主题选择
        theme_select_layout = QHBoxLayout()
        theme_label = QLabel(self.get_translation("theme", "Theme:"))
        theme_label.setStyleSheet("color: #e0e0e0;")
        
        self.theme_combo = QComboBox()
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #555555;
                border-radius: 4px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: #e0e0e0;
                selection-background-color: #444444;
            }
        """)
        
        # 加载可用主题并按预定义顺序插入，确保索引与语言刷新一致
        available_names = self.theme_manager.get_theme_names()
        theme_display = self.theme_manager.get_theme_display_names()

        preferred_order = ["dark", "light", "custom"]
        ordered_names = [n for n in preferred_order if n in available_names]
        # Append any additional themes not in the predefined list
        ordered_names.extend([n for n in available_names if n not in ordered_names])

        for theme_name in ordered_names:
            display_name = theme_display.get(theme_name, theme_name.capitalize())
            self.theme_combo.addItem(display_name, theme_name)
        
        # 连接信号
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        
        theme_select_layout.addWidget(theme_label)
        theme_select_layout.addWidget(self.theme_combo)
        theme_select_layout.addStretch()
        theme_layout.addLayout(theme_select_layout)
        
        # 添加主题设置框架
        layout.addWidget(theme_frame)
        
        # 界面设置框架
        ui_frame = QFrame()
        ui_frame.setStyleSheet("background-color: rgba(40, 40, 40, 0.7); border-radius: 6px; padding: 10px;")
        ui_layout = QVBoxLayout(ui_frame)
        ui_layout.setContentsMargins(15, 15, 15, 15)
        ui_layout.setSpacing(10)
        
        # UI设置标题
        ui_title = QLabel(self.get_translation("ui_title", "User Interface"))
        ui_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        ui_layout.addWidget(ui_title)
        
        # 窗口透明度设置
        transparency_layout = QVBoxLayout()
        transparency_title = QLabel(self.get_translation("transparency", "Window Transparency:"))
        transparency_title.setStyleSheet("color: #e0e0e0; margin-top: 5px;")
        
        # 创建透明度滑块
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(70, 100)  # 70%-100%透明度范围
        self.transparency_slider.setValue(100)  # 默认完全不透明
        self.transparency_slider.setTickPosition(QSlider.TicksBelow)
        self.transparency_slider.setTickInterval(5)
        self.transparency_slider.valueChanged.connect(self.on_transparency_changed)
        
        # 添加标签显示当前透明度
        transparency_value_layout = QHBoxLayout()
        transparency_value_layout.addWidget(QLabel("70%"))
        
        self.transparency_value_label = QLabel("100%")
        self.transparency_value_label.setAlignment(Qt.AlignRight)
        transparency_value_layout.addWidget(self.transparency_value_label)
        
        transparency_layout.addWidget(transparency_title)
        transparency_layout.addWidget(self.transparency_slider)
        transparency_layout.addLayout(transparency_value_layout)
        
        ui_layout.addLayout(transparency_layout)
        
        # 添加UI框架
        layout.addWidget(ui_frame)
        
        # 添加伸缩空间
        layout.addStretch()
        
        # 添加到选项卡
        self.settings_tabs.addTab(appearance_tab, self.get_translation("appearance", "Appearance"))
        
    def setup_scan_tab(self, scan_tab) -> None:
        """设置扫描选项卡"""
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # 内容容器
        scan_container = QWidget()
        
        # 创建扫描选项卡内容
        scan_layout = QVBoxLayout(scan_container)
        scan_layout.setContentsMargins(15, 15, 15, 15)
        scan_layout.setSpacing(20)
        
        # 扫描设置组
        scan_group = QGroupBox(self.get_translation("scan_settings"))
        scan_group.setStyleSheet(""" 
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        scan_settings_layout = QVBoxLayout(scan_group)
        scan_settings_layout.setContentsMargins(15, 15, 15, 15)
        
        # 自动扫描
        auto_scan_layout = QHBoxLayout()
        auto_scan_label = QLabel(self.get_translation("auto_scan"))
        auto_scan_label.setMinimumWidth(120)
        auto_scan_label.setMaximumWidth(120)
        
        self.auto_scan_checkbox = QCheckBox()
        self.auto_scan_checkbox.setObjectName("auto_scan_checkbox")
        
        auto_scan_layout.addWidget(auto_scan_label)
        auto_scan_layout.addWidget(self.auto_scan_checkbox)
        
        scan_settings_layout.addLayout(auto_scan_layout)
        
        # 扫描频率
        scan_freq_layout = QHBoxLayout()
        scan_freq_label = QLabel(self.get_translation("scan_frequency"))
        scan_freq_label.setMinimumWidth(120)
        scan_freq_label.setMaximumWidth(120)
        
        self.scan_freq_combo = QComboBox()
        self.scan_freq_combo.addItem(self.get_translation("daily"), "daily")
        self.scan_freq_combo.addItem(self.get_translation("weekly"), "weekly")
        self.scan_freq_combo.addItem(self.get_translation("monthly"), "monthly")
        
        scan_freq_layout.addWidget(scan_freq_label)
        scan_freq_layout.addWidget(self.scan_freq_combo, 1)
        
        scan_settings_layout.addLayout(scan_freq_layout)
        
        # 添加到主布局
        scan_layout.addWidget(scan_group)
        
        # 扫描选项组
        scan_options_group = QGroupBox(self.get_translation("scan_options"))
        scan_options_group.setStyleSheet(""" 
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        scan_options_layout = QVBoxLayout(scan_options_group)
        scan_options_layout.setContentsMargins(15, 15, 15, 15)
        
        # 扫描项目选项
        self.temp_files_checkbox = QCheckBox(self.get_translation("temp_files"))
        self.temp_files_checkbox.setObjectName("temp_files_checkbox")
        self.temp_files_checkbox.setChecked(True)
        scan_options_layout.addWidget(self.temp_files_checkbox)
        
        self.recycle_bin_checkbox = QCheckBox(self.get_translation("recycle_bin"))
        self.recycle_bin_checkbox.setObjectName("recycle_bin_checkbox")
        self.recycle_bin_checkbox.setChecked(True)
        scan_options_layout.addWidget(self.recycle_bin_checkbox)
        
        self.cache_files_checkbox = QCheckBox(self.get_translation("cache_files"))
        self.cache_files_checkbox.setObjectName("cache_files_checkbox")
        self.cache_files_checkbox.setChecked(True)
        scan_options_layout.addWidget(self.cache_files_checkbox)
        
        self.log_files_checkbox = QCheckBox(self.get_translation("log_files"))
        self.log_files_checkbox.setObjectName("log_files_checkbox")
        self.log_files_checkbox.setChecked(True)
        scan_options_layout.addWidget(self.log_files_checkbox)
        
        # 添加到主布局
        scan_layout.addWidget(scan_options_group)
        
        # 添加弹性空间
        scan_layout.addStretch(1)
        
        # 设置滚动区域的内容
        scroll_area.setWidget(scan_container)
        
        # 设置标签页的布局
        tab_layout = QVBoxLayout(scan_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
        
    def setup_advanced_tab(self, advanced_tab):
        """设置高级选项卡"""
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # 内容容器
        advanced_container = QWidget()
        
        # 创建高级选项卡内容
        advanced_layout = QVBoxLayout(advanced_container)
        advanced_layout.setContentsMargins(15, 15, 15, 15)
        advanced_layout.setSpacing(20)
        
        # 备份设置组
        backup_group = QGroupBox(self.get_translation("backup_settings"))
        backup_group.setStyleSheet(""" 
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        backup_layout = QVBoxLayout(backup_group)
        backup_layout.setContentsMargins(15, 15, 15, 15)
        
        # 修复前创建备份
        self.check_backup_before_repair = QCheckBox(self.get_translation("backup_before_repair", "修复前创建备份"))
        self.check_backup_before_repair.setObjectName("check_backup_before_repair")
        self.check_backup_before_repair.setChecked(True)
        backup_layout.addWidget(self.check_backup_before_repair)
        
        # 备份位置
        backup_location_layout = QHBoxLayout()
        backup_location_label = QLabel(self.get_translation("backup_location"))
        backup_location_label.setMinimumWidth(120)
        
        self.edit_backup_location = QLineEdit()
        self.edit_backup_location.setObjectName("edit_backup_location")
        self.edit_backup_location.setText(os.path.join(os.environ.get("USERPROFILE", ""), "GlaryBackups"))
        
        self.browse_backup_button = QPushButton(self.get_translation("browse"))
        self.browse_backup_button.setObjectName("browse_backup_button")
        self.browse_backup_button.clicked.connect(self.browse_backup_location)
        
        backup_location_layout.addWidget(backup_location_label)
        backup_location_layout.addWidget(self.edit_backup_location, 1)
        backup_location_layout.addWidget(self.browse_backup_button)
        
        backup_layout.addLayout(backup_location_layout)
        
        # 最大备份数量
        max_backups_layout = QHBoxLayout()
        max_backups_label = QLabel(self.get_translation("max_backups"))
        max_backups_label.setMinimumWidth(120)
        
        self.spinbox_max_backups = QSpinBox()
        self.spinbox_max_backups.setMinimum(1)
        self.spinbox_max_backups.setMaximum(20)
        self.spinbox_max_backups.setValue(5)
        
        max_backups_layout.addWidget(max_backups_label)
        max_backups_layout.addWidget(self.spinbox_max_backups)
        max_backups_layout.addStretch()
        
        backup_layout.addLayout(max_backups_layout)
        
        # 添加到主布局
        advanced_layout.addWidget(backup_group)
        
        # 日志设置组
        logs_group = QGroupBox(self.get_translation("logs"))
        logs_group.setStyleSheet(""" 
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        logs_layout = QVBoxLayout(logs_group)
        logs_layout.setContentsMargins(15, 15, 15, 15)
        
        # 启用日志记录
        self.check_enable_logging = QCheckBox(self.get_translation("logs", "日志记录"))
        self.check_enable_logging.setObjectName("check_enable_logging")
        self.check_enable_logging.setChecked(True)
        logs_layout.addWidget(self.check_enable_logging)
        
        # 保存日志时间
        logs_retention_layout = QHBoxLayout()
        logs_retention_label = QLabel(self.get_translation("keep_logs"))
        logs_retention_label.setMinimumWidth(120)
        
        self.spinbox_log_days = QSpinBox()
        self.spinbox_log_days.setMinimum(1)
        self.spinbox_log_days.setMaximum(90)
        self.spinbox_log_days.setValue(30)
        
        days_label = QLabel(self.get_translation("days"))
        
        logs_retention_layout.addWidget(logs_retention_label)
        logs_retention_layout.addWidget(self.spinbox_log_days)
        logs_retention_layout.addWidget(days_label)
        logs_retention_layout.addStretch()
        
        logs_layout.addLayout(logs_retention_layout)
        
        # 清除日志按钮
        clear_logs_button = QPushButton(self.get_translation("clear_logs"))
        clear_logs_button.setObjectName("clear_logs_button")
        logs_layout.addWidget(clear_logs_button)
        
        # 添加到主布局
        advanced_layout.addWidget(logs_group)
        
        # 添加弹性空间
        advanced_layout.addStretch(1)
        
        # 设置滚动区域的内容
        scroll_area.setWidget(advanced_container)
        
        # 设置标签页的布局
        tab_layout = QVBoxLayout(advanced_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

    def on_animations_changed(self, state):
        """Handle animations checkbox state change"""
        is_enabled = (state == Qt.Checked)
        # Save the setting
        self.settings.set_setting("enable_animations", is_enabled)
        self.settings.sync()
        
        # Apply the setting
        try:
            if self.main_window is not None:
                # Notify main window of animation setting change
                self.logger.info(f"Animation setting changed to: {is_enabled}")
        except AttributeError:
            pass

    def on_theme_changed(self, index):
        """Handle theme selection change"""
        try:
            if index >= 0:
                theme_id = self.theme_combo.itemData(index)
                if theme_id:
                    current_theme = self.settings.get_setting("theme", "dark")
                    if theme_id != current_theme:
                        # Save but don't apply – require restart
                        self.settings.set_setting("theme", theme_id)
                        self.settings.sync()

                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.information(self, self.get_translation("restart_required", "Restart Required"),
                                                self.get_translation("restart_theme_note", "The theme change will take effect after restarting the application."))
                        self.logger.info(f"Theme set to {theme_id}; restart required to apply.")
        except AttributeError:
            pass
    
    def load_settings(self):
        """从设置中加载界面选项"""
        try:
            # 应用设置到界面
            current_language = self.settings.get_setting("language", "en")
            
            # 确保语言下拉框显示正确
            try:
                language_index = 0  # 默认英语
                if self.language_combo:
                    for i in range(self.language_combo.count()):
                        if self.language_combo.itemData(i) == current_language:
                            language_index = i
                            break
                    self.language_combo.setCurrentIndex(language_index)
            except AttributeError:
                pass
            
            # 设置主题选择器的值
            current_theme = self.settings.get_setting("theme", "dark")
            try:
                theme_index = 0  # 默认深色主题
                for i in range(self.theme_combo.count()):
                    if self.theme_combo.itemData(i) == current_theme:
                        theme_index = i
                        break
                self.theme_combo.setCurrentIndex(theme_index)
            except AttributeError:
                pass
            
            # 加载自定义颜色
            try:
                self.update_color_buttons()
            except AttributeError:
                pass
            
            # 加载开机启动设置
            try:
                if hasattr(self, 'startup_check'):
                    self.startup_check.setChecked(self.settings.get_setting("start_with_windows", False))
            except AttributeError:
                pass
            
            # 加载开机最小化设置
            try:
                if hasattr(self, 'start_minimized_check'):
                    self.start_minimized_check.setChecked(self.settings.get_setting("start_minimized", False))
            except AttributeError:
                pass
            
            # 加载动画启用设置
            try:
                if hasattr(self, 'enable_animations_check'):
                    animation_enabled = self.settings.get_setting("enable_animations", True)
                    # Convert to proper boolean value
                    if isinstance(animation_enabled, str):
                        animation_enabled = animation_enabled.lower() in ('true', 'yes', '1', 'on')
                    elif isinstance(animation_enabled, int):
                        animation_enabled = animation_enabled != 0
                    else:
                        animation_enabled = bool(animation_enabled)
                        
                    self.enable_animations_check.setChecked(animation_enabled)
            except AttributeError:
                pass
            
            # 加载透明度设置
            try:
                transparency = int(self.settings.get_setting("window_transparency", 100))
                if hasattr(self, 'transparency_slider'):
                    self.transparency_slider.setValue(transparency)
                if hasattr(self, 'transparency_value_label'):
                    self.transparency_value_label.setText(f"{transparency}%")
            except (AttributeError, ValueError):
                pass
            
            # 加载所有自定义复选框设置
            for checkbox in self.findChildren(QCheckBox):
                setting_key = checkbox.objectName()
                if setting_key:
                    try:
                        value = self.settings.get_setting(setting_key, False)
                        # 将值转换为布尔类型
                        if isinstance(value, str):
                            value = value.lower() in ('true', 'yes', '1', 'on')
                        checkbox.setChecked(bool(value))
                    except Exception as e:
                        self.logger.error(f"Error loading setting for {setting_key}: {e}")
            
            self.logger.info("设置加载完成")
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
    
    def reset_settings(self):
        """重置设置为默认值"""
        # 重置常规设置
        try:
            self.language_combo.setCurrentText("English")
        except AttributeError:
            self.logger.error("无法重置语言设置")
        
        try:
            self.start_minimized_check.setChecked(False)
        except AttributeError:
            self.logger.error("无法重置最小化设置")
        
        try:
            self.close_to_tray_check.setChecked(False)
        except AttributeError:
            self.logger.error("无法重置托盘设置")
        
        try:
            self.enable_animations_check.setChecked(False)
        except AttributeError:
            self.logger.error("无法重置动画设置")
        
        # 重置主题设置
        try:
            # 找到 "dark" 主题的索引
            dark_index = -1
            for i in range(self.theme_combo.count()):
                if self.theme_combo.itemData(i) == "dark":
                    dark_index = i
                    break
            
            if dark_index >= 0:
                self.theme_combo.setCurrentIndex(dark_index)
        except AttributeError:
            self.logger.error("无法重置主题设置")
        
        # 重置自定义颜色
        try:
            self.update_color_buttons()
        except AttributeError:
            self.logger.error("无法重置自定义颜色")
        
        # 重置高级设置
        try:
            self.check_backup_before_repair.setChecked(True)
        except AttributeError:
            self.logger.error("无法重置备份设置")
        
        try:
            self.edit_backup_location.setText(os.path.join(os.environ.get("USERPROFILE", ""), "GlaryBackups"))
        except AttributeError:
            self.logger.error("无法重置备份位置")
        
        try:
            self.check_enable_logging.setChecked(True)
        except AttributeError:
            self.logger.error("无法重置日志设置")
        
        try:
            self.spinbox_max_backups.setValue(5)
        except AttributeError:
            self.logger.error("无法重置最大备份数量")
        
        # 重置扫描设置
        try:
            self.auto_scan_checkbox.setChecked(True)
        except AttributeError:
            self.logger.error("无法重置自动扫描设置")
        
        try:
            self.scan_freq_combo.setCurrentText("daily")
        except AttributeError:
            self.logger.error("无法重置扫描频率")
        
        try:
            self.temp_files_checkbox.setChecked(True)
        except AttributeError:
            self.logger.error("无法重置临时文件设置")
        
        try:
            self.recycle_bin_checkbox.setChecked(True)
        except AttributeError:
            self.logger.error("无法重置回收站设置")
        
        try:
            self.cache_files_checkbox.setChecked(True)
        except AttributeError:
            self.logger.error("无法重置缓存文件设置")
        
        try:
            self.log_files_checkbox.setChecked(True)
        except AttributeError:
            self.logger.error("无法重置日志文件设置")
        
        # 重置扫描选项
        try:
            self.check_scan_archives.setChecked(True)
        except AttributeError:
            self.logger.error("无法重置扫描归档设置")
        
        try:
            self.check_scan_rootkits.setChecked(True)
        except AttributeError:
            self.logger.error("无法重置扫描rootkits设置")
        
        try:
            self.check_scan_autofix.setChecked(False)
        except AttributeError:
            self.logger.error("无法重置扫描自动修复设置")
        
        try:
            self.slider_scan_level.setValue(2)
        except AttributeError:
            self.logger.error("无法重置扫描级别设置")
            
        # 重置其他设置
        for attr_name in ['deep_scan_check', 'auto_clean_check', 'auto_backup_check', 
                         'check_updates_check', 'auto_update_check', 'show_notifications_check',
                         'notification_sound_check', 'schedule_restarts_check', 
                         'startup_scan_check', 'system_titlebar_check', 'window_blur_check',
                         'start_minimized_check', 'close_to_tray_check']:
            try:
                getattr(self, attr_name).setChecked(False)
            except (AttributeError, TypeError):
                self.logger.error(f"无法重置{attr_name}设置")
                
        # 重置主窗口透明度
        try:
            self.transparency_slider.setValue(100)
            self.transparency_value_label.setText("100%")
        except AttributeError:
            self.logger.error("无法重置主窗口透明度")
            
        # 通知用户设置已重置
        try:
            # 显示状态消息
            if self.main_window is not None:
                self.main_window.show_status_message("设置已重置为默认值", 3000)
        except AttributeError:
            self.logger.error("无法显示状态消息 - main_window不可用")
    
    def get_translation(self, key, default=None):
        """获取键的翻译"""
        return self.settings.get_translation("settings", key, default)
        
    def on_language_changed(self, index):
        """Handle language selection change"""
        try:
            if index >= 0:
                # Get language code from the combobox
                language_code = self.language_combo.itemData(index)
                if language_code:
                    current_lang = self.settings.get_setting("language", "en")
                    # Only proceed if language actually changed
                    if language_code != current_lang:
                        self.settings.set_language(language_code)
                        self.settings.sync()
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.information(self, self.get_translation("restart_required", "Restart Required"),
                                                self.get_translation("restart_language_note", "The language change will take effect after restarting the application."))
                        self.logger.info(f"Language changed from {current_lang} to {language_code}; restart required.")
        except AttributeError:
            pass
    
    def refresh_language(self):
        """根据当前语言更新界面文本"""
        # 更新标签页标题
        self.settings_tabs.setTabText(0, self.get_translation("general_tab", "常规"))
        self.settings_tabs.setTabText(1, self.get_translation("scan_tab", "扫描"))
        self.settings_tabs.setTabText(2, self.get_translation("advanced_tab", "高级"))
        self.settings_tabs.setTabText(3, self.get_translation("appearance_tab", "外观"))
        
        # 更新常规选项卡
        general_group = self.findChild(QGroupBox, "general_group")
        if general_group:
            general_group.setTitle(self.get_translation("general_settings", "常规设置"))
            
        language_label = self.findChild(QLabel, "language_label")
        if language_label:
            language_label.setText(self.get_translation("language", "语言："))
            
        startup_label = self.findChild(QLabel, "startup_label")
        if startup_label:
            startup_label.setText(self.get_translation("start_with_windows", "开机启动："))
            
        self.start_minimized_check.setText(self.get_translation("start_minimized", "Start minimized"))
        
        # 更新主题设置
        theme_group = self.findChild(QGroupBox, "theme_group")
        if theme_group:
            theme_group.setTitle(self.get_translation("theme_settings", "主题设置"))
            
        theme_label = self.findChild(QLabel, "theme_label")
        if theme_label:
            theme_label.setText(self.get_translation("theme", "主题："))
            
        # 更新主题选项
        if self.theme_combo.count() >= 3:
            self.theme_combo.setItemText(0, self.get_translation("dark", "深色"))
            self.theme_combo.setItemText(1, self.get_translation("light", "浅色"))
            self.theme_combo.setItemText(2, self.get_translation("custom", "自定义"))
            
        # 更新自定义颜色部分 - 考虑布局变更为QVBoxLayout
        try:
            bg_color_label = None
            text_color_label = None
            accent_color_label = None
            
            # 遍历所有标签，查找自定义颜色的标签
            for label in self.findChildren(QLabel):
                if "背景颜色" in label.text():
                    label.setText(self.get_translation("background_color", "背景颜色："))
                elif "文本颜色" in label.text():
                    label.setText(self.get_translation("text_color", "文本颜色："))
                elif "强调颜色" in label.text():
                    label.setText(self.get_translation("accent_color", "强调颜色："))
        except Exception as e:
            self.logger.error(f"更新自定义颜色标签出错: {str(e)}")
                
        # 更新颜色选择按钮
        for button in self.findChildren(QPushButton):
            if "选择颜色" in button.text():
                button.setText(self.get_translation("choose_color", "选择颜色"))
        
        # 更新通知组
        notifications_group = self.findChild(QGroupBox, "notifications_group")
        if notifications_group:
            notifications_group.setTitle(self.get_translation("notifications", "通知"))
            
        self.enable_animations_check.setText(self.get_translation("enable_animations", "启用动画效果"))
        
        # 更新按钮
        self.save_button.setText(self.get_translation("save_settings", "保存设置"))
        self.apply_button.setText(self.get_translation("apply_settings", "应用设置"))
        self.restore_defaults_button.setText(self.get_translation("restore_defaults", "恢复默认"))
        if hasattr(self, "restart_button"):
            self.restart_button.setText(self.get_translation("restart_now", "立即重启"))
    
    def check_all_translations(self):
        """检查所有必需的翻译是否存在"""
        # 常规选项卡翻译
        self.get_translation("general_tab")
        self.get_translation("general_settings")
        self.get_translation("language")
        self.get_translation("start_with_windows")
        self.get_translation("auto_start")
        self.get_translation("notifications")
        self.get_translation("enable_notifications")
        self.get_translation("show_tips")
        self.get_translation("maintenance_reminder")
        
        # 扫描选项卡翻译
        self.get_translation("scan_tab")
        
        # 高级选项卡翻译
        self.get_translation("advanced_tab")
        
        # 外观选项卡翻译
        self.get_translation("appearance_tab")
        
        # 按钮翻译
        self.get_translation("save_settings")
        self.get_translation("restore_defaults")

    def on_transparency_changed(self, value):
        """处理透明度滑块值变化"""
        self.transparency_value_label.setText(f"{value}%")
        self.settings.set_setting("window_transparency", value)
        
        # 尝试应用透明度
        main_window = self.window()
        if main_window and hasattr(main_window, 'apply_transparency'):
            main_window.apply_transparency()
    
    def browse_backup_location(self):
        """打开对话框选择备份文件夹"""
        from PyQt5.QtWidgets import QFileDialog
        
        current_path = self.edit_backup_location.text()
        folder = QFileDialog.getExistingDirectory(
            self, self.get_translation("select_backup_folder", "选择备份文件夹"), 
            current_path if os.path.exists(current_path) else os.environ.get("USERPROFILE", "")
        )
        
        if folder:
            self.edit_backup_location.setText(folder)
            self.settings.set_setting("backup_location", folder)
    
    def apply_settings(self):
        """Apply settings changes"""
        # Handle any remaining old-style checkbox references
        try:
            # Language setting
            try:
                current_idx = self.language_combo.currentIndex()
                language_code = self.language_combo.itemData(current_idx)
                current_lang = self.settings.get_setting("language", "en")
                if language_code != current_lang:
                    self.settings.set_language(language_code)
                    # Prompt user restart; do not update UI immediately
                    from PyQt5.QtWidgets import QMessageBox
                    try:
                        if self.main_window:
                            QMessageBox.information(self, self.get_translation("restart_required", "Restart Required"),
                                                    self.get_translation("restart_language_note", "The language change will take effect after restarting the application."))
                    except AttributeError:
                        pass
            except AttributeError:
                pass
            
            # Theme setting
            try:
                current_idx = self.theme_combo.currentIndex()
                theme_id = self.theme_combo.itemData(current_idx)
                current_theme = self.settings.get_setting("theme", "dark")
                if theme_id != current_theme:
                    self.settings.set_setting("theme", theme_id)
                    # Prompt user restart
                    from PyQt5.QtWidgets import QMessageBox
                    try:
                        if self.main_window:
                            QMessageBox.information(self, self.get_translation("restart_required", "Restart Required"),
                                                    self.get_translation("restart_theme_note", "The theme change will take effect after restarting the application."))
                    except AttributeError:
                        pass
            except AttributeError:
                pass
            
            # Window transparency
            try:
                transparency = self.transparency_slider.value()
                self.settings.set_setting("window_transparency", transparency)
                # Apply transparency if window available
                try:
                    if self.main_window:
                        self.main_window.apply_transparency()
                except AttributeError:
                    pass
            except AttributeError:
                pass
            
            # Process all checkboxes automatically
            for checkbox in self.findChildren(QCheckBox):
                setting_key = checkbox.objectName()
                if setting_key:
                    is_checked = checkbox.isChecked()
                    self.settings.set_setting(setting_key, is_checked)
            
            # Save settings to disk
            self.settings.sync()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                self.get_translation("settings_applied_title", "Settings Applied"),
                self.get_translation("settings_applied", "Settings applied successfully.")
            )
            self.logger.info("Settings saved successfully")
            # Emit signal that settings were saved (if it exists)
            try:
                self.settings_saved.emit()
            except AttributeError:
                pass
            # Show status message in main window if available
            try:
                if self.main_window is not None and hasattr(self.main_window, 'show_status_message'):
                    self.main_window.show_status_message(self.get_translation("settings_saved", "Settings saved successfully."))
            except AttributeError:
                pass
            return True
        except Exception as e:
            self.logger.error(f"Error applying settings: {str(e)}")
            return False

    def _finish_applying(self, loading_label=None, movie=None):
        """完成应用设置过程"""
        try:
            # 恢复按钮状态
            self.apply_button.setEnabled(True)
            self.apply_button.setText(self.get_translation("apply_settings", "应用设置"))
            
            # 移除加载动画
            if loading_label:
                if movie:
                    movie.stop()
                loading_label.hide()
                loading_label.deleteLater()
            
            # 确保布局更新
            self.updateGeometry()
            self.update()
        except Exception as e:
            self.logger.error(f"清理应用设置界面出错: {str(e)}")

    def save_custom_theme(self):
        """保存当前自定义主题设置到主题文件"""
        # 获取当前自定义颜色
        bg_color = self.settings.get_setting("custom_bg_color", "#1e1e1e")
        text_color = self.settings.get_setting("custom_text_color", "#e0e0e0")
        accent_color = self.settings.get_setting("custom_accent_color", "#555555")
        
        # 创建主题数据结构
        theme_data = {
            "name": "custom",
            "display_name": {
                "en": "Custom",
                "zh": "自定义"
            },
            "colors": {
                "bg_color": bg_color,
                "text_color": text_color,
                "accent_color": accent_color,
                "bg_lighter": self.lighten_color(bg_color, 10),
                "bg_darker": self.lighten_color(bg_color, -10)
            },
            "component_specific": {
                "button": {
                    "primary_bg": accent_color,
                    "primary_text": "#ffffff",
                    "primary_hover": self.lighten_color(accent_color, 10),
                    "primary_pressed": self.lighten_color(accent_color, -10)
                },
                "progressbar": {
                    "chunk_color": accent_color
                }
            }
        }
        
        # 保存主题到文件
        try:
            theme_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "themes")
            if not os.path.exists(theme_dir):
                os.makedirs(theme_dir)
            
            theme_file = os.path.join(theme_dir, "custom.json")
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=4, ensure_ascii=False)
            
            # 显示成功消息
            self.status_bar = QStatusBar(self)
            self.status_bar.setStyleSheet("color: #4CAF50;")
            self.layout().addWidget(self.status_bar)
            self.status_bar.showMessage(self.get_translation("custom_theme_saved", "自定义主题已保存"), 3000)
        except Exception as e:
            # 显示错误消息
            self.status_bar = QStatusBar(self)
            self.status_bar.setStyleSheet("color: #F44336;")
            self.layout().addWidget(self.status_bar)
            self.status_bar.showMessage(self.get_translation("custom_theme_save_error", f"保存自定义主题时出错: {str(e)}"), 3000)

    def lighten_color(self, color, amount=0):
        """使颜色变亮或变暗
        
        Args:
            color: 十六进制颜色代码
            amount: 变化量，正数变亮，负数变暗
            
        Returns:
            新的十六进制颜色代码
        """
        try:
            c = color.lstrip('#')
            c = tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
            
            r, g, b = c
            
            r = min(255, max(0, r + amount * 2.55))
            g = min(255, max(0, g + amount * 2.55))
            b = min(255, max(0, b + amount * 2.55))
            
            return '#{:02x}{:02x}{:02x}'.format(int(r), int(g), int(b))
        except Exception as e:
            self.logger.error(f"计算颜色变化出错: {str(e)}")
            return color

    def update_color_buttons(self):
        """更新自定义颜色按钮的显示"""
        bg_color = self.settings.get_setting("custom_bg_color", "#1e1e1e")
        text_color = self.settings.get_setting("custom_text_color", "#e0e0e0")
        accent_color = self.settings.get_setting("custom_accent_color", "#555555")
        
        self.bg_color_button.setStyleSheet(f"background-color: {bg_color}; min-width: 80px; min-height: 24px;")
        self.text_color_button.setStyleSheet(f"background-color: {text_color}; min-width: 80px; min-height: 24px;")
        self.accent_color_button.setStyleSheet(f"background-color: {accent_color}; min-width: 80px; min-height: 24px;")

    def apply_theme(self):
        """应用所选主题"""
        index = self.theme_combo.currentIndex()
        if index >= 0:
            theme_name = self.theme_combo.itemData(index)
            self.theme_manager.apply_theme(theme_name)

    def save_settings(self):
        """Save all settings"""
        try:
            # Save language setting
            try:
                lang_idx = self.language_combo.currentIndex()
                lang_data = self.language_combo.itemData(lang_idx)
                current_lang = self.settings.get_setting("language", "en")
                if lang_data != current_lang:
                    self.settings.set_language(lang_data)
            except AttributeError:
                pass
            
            # Save theme setting
            try:  
                theme_idx = self.theme_combo.currentIndex()
                theme_id = self.theme_combo.itemData(theme_idx)
                self.settings.set_setting("theme", theme_id)
            except AttributeError:
                pass
            
            # Save checkbox settings directly from their state
            for checkbox in self.findChildren(QCheckBox):
                setting_key = checkbox.objectName()
                if setting_key:
                    self.settings.set_setting(setting_key, checkbox.isChecked())
            
            # Save window transparency
            try:
                self.settings.set_setting("window_transparency", self.transparency_slider.value())
            except AttributeError:
                pass
            
            # Sync settings to save them immediately
            self.settings.sync()
            
            # Apply theme if main window is available
            try:
                if self.main_window is not None:
                    self.main_window.apply_theme()
            except AttributeError:
                pass
                
            return True
        except Exception as e:
            self.logger.error(f"Error saving settings: {str(e)}")
            return False

    # 添加save_settings按钮的点击处理函数
    def _on_save_settings_clicked(self):
        """Save settings and close settings window"""
        # Save all settings
        success = self.save_settings()
        
        if success:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                self.get_translation("settings_saved_title", "Settings Saved"),
                self.get_translation("settings_saved", "Settings saved successfully.")
            )
            self.logger.info("Settings saved successfully")
            # Emit signal that settings were saved (if it exists)
            try:
                self.settings_saved.emit()
            except AttributeError:
                pass
            # Show status message in main window if available
            try:
                if self.main_window is not None and hasattr(self.main_window, 'show_status_message'):
                    self.main_window.show_status_message(self.get_translation("settings_saved", "Settings saved successfully."))
            except AttributeError:
                pass
        else:
            # Show error message
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error",
                "Failed to save settings. Please try again."
            )

    def on_checkbox_changed(self, setting_key, state):
        """处理复选框状态改变
        
        Args:
            setting_key: 设置键名
            state: 复选框状态 (Qt.Checked 或 Qt.Unchecked)
        """
        try:
            # 将Qt.Checked/Qt.Unchecked转换为布尔值
            checked = (state == Qt.Checked)
            
            # 保存设置
            self.settings.set_setting(setting_key, checked)
            self.settings.sync()
            
            # 记录设置变更
            self.logger.info(f"设置已更改: {setting_key} = {checked}")
            
            # 根据设置键执行特定操作
            if setting_key == "enable_animations":
                # 更新动画设置
                self.apply_animation_settings(checked)
            elif setting_key == "use_system_title_bar":
                # 更新标题栏设置
                self.apply_titlebar_settings(checked)
            elif setting_key == "show_tooltips":
                # 更新工具提示设置
                self.apply_tooltip_settings(checked)
            elif setting_key == "enable_logging":
                # 更新日志设置
                self.apply_logging_settings(checked)
            
            # 应用设置更改
            self.apply_settings()
            
        except Exception as e:
            self.logger.error(f"更改设置时出错: {str(e)}")
            # 恢复复选框状态
            sender = self.sender()
            if sender:
                sender.setChecked(not checked)
                
    def apply_animation_settings(self, enabled):
        """应用动画设置
        
        Args:
            enabled: 是否启用动画
        """
        try:
            # 更新所有支持动画的组件
            main_window = self.window()
            if main_window:
                main_window.refresh_all_components()
        except Exception as e:
            self.logger.error(f"应用动画设置时出错: {str(e)}")
            
    def apply_titlebar_settings(self, use_system):
        """应用标题栏设置
        
        Args:
            use_system: 是否使用系统标题栏
        """
        try:
            # 通知主窗口更新标题栏
            main_window = self.window()
            if main_window and hasattr(main_window, 'update_titlebar'):
                main_window.update_titlebar(use_system)
        except Exception as e:
            self.logger.error(f"应用标题栏设置时出错: {str(e)}")
            
    def apply_tooltip_settings(self, show):
        """应用工具提示设置
        
        Args:
            show: 是否显示工具提示
        """
        try:
            # 更新所有工具提示
            main_window = self.window()
            if main_window:
                for widget in main_window.findChildren(QWidget):
                    if widget.toolTip():
                        widget.setToolTipDuration(-1 if show else 0)
        except Exception as e:
            self.logger.error(f"应用工具提示设置时出错: {str(e)}")
            
    def apply_logging_settings(self, enabled):
        """应用日志设置
        
        Args:
            enabled: 是否启用日志
        """
        try:
            # 更新日志级别
            log_level = logging.DEBUG if enabled else logging.WARNING
            logging.getLogger().setLevel(log_level)
        except Exception as e:
            self.logger.error(f"应用日志设置时出错: {str(e)}")

    def _on_restart_clicked(self):
        """Save settings and restart the application"""
        try:
            from PyQt5.QtWidgets import QMessageBox, QApplication
            import subprocess, sys, os
 
            # Confirm restart
            reply = QMessageBox.question(
                self,
                self.get_translation("restart_required", "Restart Required"),
                self.get_translation("restart_confirm", "The application needs to restart to apply changes. Restart now?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.No:
                return
 
            # Save any pending settings
            self.save_settings()
 
            # Relaunch
            python = sys.executable
            args = sys.argv
            self.logger.info("Restarting application with: %s %s", python, " ".join(args))
            try:
                subprocess.Popen([python] + args)
            except Exception as e:
                self.logger.error(f"Failed to relaunch application: {e}")
 
            # Quit current instance
            QApplication.instance().quit()
        except Exception as e:
            self.logger.error(f"Error during restart: {e}")

   