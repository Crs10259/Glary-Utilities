import os
import sys
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QPushButton, 
                          QComboBox, QCheckBox, QGroupBox, QFormLayout, QSlider, QLineEdit,
                          QColorDialog, QFileDialog, QDialog, QScrollArea, QSpinBox, QStatusBar,
                          QApplication)
from PyQt5.QtCore import Qt, QSize, QSettings, QTranslator, QCoreApplication, QTimer
from PyQt5.QtGui import QColor, QIcon, QMovie
from utils.animations import AnimationUtils
from utils.theme_manager import ThemeManager

class SettingsWidget(QWidget):
    """应用程序设置的窗口小部件"""
    
    def __init__(self, settings, parent=None) -> None:
        """初始化设置组件"""
        super().__init__(parent)
        self.settings = settings
        self.main_window = parent
        self.background_image_path = ""
        self.theme_manager = ThemeManager()
        self.animations = AnimationUtils()
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self) -> None:
        """设置UI界面"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标签页
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                min-width: 100px;
                padding: 8px 16px;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 4px;
                padding: 10px;
            }
            QLabel {
                background-color: transparent;
            }
        """)
        
        # 设置标签页
        self.general_tab = QWidget()
        self.scan_tab = QWidget()
        self.advanced_tab = QWidget()
        self.appearance_tab = QWidget()
        
        # 创建各个选项卡
        self.setup_general_tab()
        self.setup_scan_tab()
        self.setup_advanced_tab()
        self.setup_appearance_tab()  # 设置外观选项卡
        
        # 添加选项卡到 QTabWidget
        self.tabs.addTab(self.general_tab, self.get_translation("general", "常规"))
        self.tabs.addTab(self.scan_tab, self.get_translation("scan", "扫描"))
        self.tabs.addTab(self.advanced_tab, self.get_translation("advanced", "高级"))
        self.tabs.addTab(self.appearance_tab, self.get_translation("appearance", "外观"))  # 添加外观选项卡
        
        self.main_layout.addWidget(self.tabs)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.save_button = QPushButton("保存设置")
        self.save_button.setObjectName("save_button")
        self.save_button.setMinimumWidth(120)
        self.save_button.setStyleSheet(""" 
            QPushButton {
                background-color: #00a8ff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0096e0;
            }
            QPushButton:pressed {
                background-color: #0085c7;
            }
        """)
        buttons_layout.addWidget(self.save_button)
        
        self.apply_button = QPushButton(self.get_translation("apply_settings"))
        self.apply_button.setObjectName("apply_button")
        self.apply_button.setMinimumWidth(120)
        self.apply_button.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
            QPushButton:pressed {
                background-color: #3e8f3e;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
            }
        """)
        buttons_layout.addWidget(self.apply_button)
        
        self.restore_defaults_button = QPushButton("恢复默认")
        self.restore_defaults_button.setObjectName("restore_defaults_button")
        self.restore_defaults_button.setMinimumWidth(140)
        self.restore_defaults_button.setStyleSheet(""" 
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        buttons_layout.addWidget(self.restore_defaults_button)
        
        self.main_layout.addLayout(buttons_layout)
        
        # 连接信号
        self.save_button.clicked.connect(self.save_settings)
        self.apply_button.clicked.connect(self.apply_settings)
        self.restore_defaults_button.clicked.connect(self.reset_settings)
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
    
    def setup_general_tab(self) -> None:
        """设置常规选项卡"""
        # 创建常规选项卡内容
        general_layout = QVBoxLayout(self.general_tab)
        general_layout.setContentsMargins(15, 15, 15, 15)
        general_layout.setSpacing(20)  # 增加间距
        
        # 语言设置组
        language_group = QGroupBox(self.get_translation("language"))
        language_group.setStyleSheet(""" 
            QGroupBox {
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
        language_layout = QVBoxLayout(language_group)
        language_layout.setContentsMargins(15, 15, 15, 15)  # 增加内边距
        
        language_select_layout = QHBoxLayout()
        language_label = QLabel(self.get_translation("language"))
        language_label.setMinimumWidth(120)  # 设置最小宽度确保标签不会重叠
        language_label.setMaximumWidth(120)  # 设置最大宽度
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("简体中文", "zh")
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        
        language_select_layout.addWidget(language_label)
        language_select_layout.addWidget(self.language_combo, 1)  # 设置伸展因子
        
        language_layout.addLayout(language_select_layout)
        
        # 启动设置
        startup_layout = QHBoxLayout()
        startup_label = QLabel(self.get_translation("start_with_windows", "开机启动:"))
        startup_label.setMinimumWidth(120)
        startup_label.setMaximumWidth(120)
        
        self.startup_checkbox = QCheckBox(self.get_translation("auto_start", "自动启动"))
        self.startup_checkbox.setObjectName("startup_checkbox")
        
        startup_layout.addWidget(startup_label)
        startup_layout.addWidget(self.startup_checkbox)
        
        language_layout.addLayout(startup_layout)
        
        # Add language group to general layout
        general_layout.addWidget(language_group)
        
        # 主题设置组
        theme_group = QGroupBox(self.get_translation("theme_selection", "主题选择"))
        theme_layout = QVBoxLayout()
        
        theme_label = QLabel(self.get_translation("select_theme", "选择主题:"))
        self.theme_combo = QComboBox()
        
        # 加载主题名称和显示名称
        theme_names = self.theme_manager.get_theme_names()
        display_names = self.theme_manager.get_theme_display_names(
            "zh" if self.settings.get_setting("language", "English") == "简体中文" else "en"
        )
        
        # 添加主题选项
        for theme_name in theme_names:
            display_name = display_names.get(theme_name, theme_name.capitalize())
            self.theme_combo.addItem(display_name, theme_name)
        
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        
        # 窗口透明度
        transparency_label = QLabel(self.get_translation("window_transparency", "窗口透明度:"))
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(30, 100)  # 30% 到 100%
        self.transparency_slider.setValue(100)
        self.transparency_slider.setTickPosition(QSlider.TicksBelow)
        self.transparency_slider.setTickInterval(10)
        self.transparency_value = QLabel("100%")
        self.transparency_slider.valueChanged.connect(self.on_transparency_changed)
        
        transparency_layout = QHBoxLayout()
        transparency_layout.addWidget(self.transparency_slider)
        transparency_layout.addWidget(self.transparency_value)
        
        # 自定义颜色选项
        self.custom_colors_widget = QWidget()
        custom_colors_layout = QVBoxLayout()
        self.custom_colors_widget.setLayout(custom_colors_layout)
        
        # 背景颜色
        bg_color_layout = QHBoxLayout()
        bg_color_label = QLabel(self.get_translation("background_color", "背景颜色:"))
        self.bg_color_button = QPushButton()
        self.bg_color_button.setFixedSize(80, 24)
        self.bg_color_button.clicked.connect(lambda: self.choose_color("custom_bg_color", self.bg_color_button))
        bg_color_layout.addWidget(bg_color_label)
        bg_color_layout.addWidget(self.bg_color_button)
        bg_color_layout.addStretch()
        
        # 文本颜色
        text_color_layout = QHBoxLayout()
        text_color_label = QLabel(self.get_translation("text_color", "文本颜色:"))
        self.text_color_button = QPushButton()
        self.text_color_button.setFixedSize(80, 24)
        self.text_color_button.clicked.connect(lambda: self.choose_color("custom_text_color", self.text_color_button))
        text_color_layout.addWidget(text_color_label)
        text_color_layout.addWidget(self.text_color_button)
        text_color_layout.addStretch()
        
        # 强调颜色
        accent_color_layout = QHBoxLayout()
        accent_color_label = QLabel(self.get_translation("accent_color", "强调颜色:"))
        self.accent_color_button = QPushButton()
        self.accent_color_button.setFixedSize(80, 24)
        self.accent_color_button.clicked.connect(lambda: self.choose_color("custom_accent_color", self.accent_color_button))
        accent_color_layout.addWidget(accent_color_label)
        accent_color_layout.addWidget(self.accent_color_button)
        accent_color_layout.addStretch()
        
        # 保存自定义主题按钮
        save_theme_button = QPushButton(self.get_translation("save_custom_theme", "保存自定义主题"))
        save_theme_button.clicked.connect(self.save_custom_theme)
        
        # 添加所有颜色选择器到自定义布局
        custom_colors_layout.addLayout(bg_color_layout)
        custom_colors_layout.addLayout(text_color_layout)
        custom_colors_layout.addLayout(accent_color_layout)
        custom_colors_layout.addWidget(save_theme_button)
        
        # 组装主题布局
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addWidget(transparency_label)
        theme_layout.addLayout(transparency_layout)
        theme_layout.addWidget(self.custom_colors_widget)
        theme_group.setLayout(theme_layout)
        
        # 将主题组添加到主布局
        general_layout.addWidget(theme_group)
        
        # 通知组
        notifications_group = QGroupBox(self.get_translation("notifications", "通知"))
        notifications_group.setStyleSheet(""" 
            QGroupBox {
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
        notifications_layout = QVBoxLayout(notifications_group)
        notifications_layout.setContentsMargins(15, 15, 15, 15)
        
        self.enable_notifications_checkbox = QCheckBox(self.get_translation("enable_notifications", "启用通知"))
        self.enable_notifications_checkbox.setObjectName("enable_notifications_checkbox")
        self.enable_notifications_checkbox.setChecked(True)
        self.enable_notifications_checkbox.setStyleSheet("color: #e0e0e0;")
        notifications_layout.addWidget(self.enable_notifications_checkbox)
        
        self.show_tips_checkbox = QCheckBox(self.get_translation("show_tips", "显示提示"))
        self.show_tips_checkbox.setObjectName("show_tips_checkbox")
        self.show_tips_checkbox.setChecked(True)
        self.show_tips_checkbox.setStyleSheet("color: #e0e0e0;")
        notifications_layout.addWidget(self.show_tips_checkbox)
        
        self.enable_animations_checkbox = QCheckBox(self.get_translation("enable_animations", "启用动画效果"))
        self.enable_animations_checkbox.setObjectName("enable_animations_checkbox")
        self.enable_animations_checkbox.setChecked(True)
        self.enable_animations_checkbox.setStyleSheet("color: #e0e0e0;")
        notifications_layout.addWidget(self.enable_animations_checkbox)
        
        self.maintenance_reminder_checkbox = QCheckBox(self.get_translation("maintenance_reminder", "维护提醒"))
        self.maintenance_reminder_checkbox.setObjectName("maintenance_reminder_checkbox")
        self.maintenance_reminder_checkbox.setChecked(True)
        self.maintenance_reminder_checkbox.setStyleSheet("color: #e0e0e0;")
        notifications_layout.addWidget(self.maintenance_reminder_checkbox)
        
        general_layout.addWidget(notifications_group)
    
    def setup_scan_tab(self) -> None:
        """设置扫描选项卡"""
        layout = QVBoxLayout(self.scan_tab)
        
        # 系统清理设置
        cleaner_group = QGroupBox("系统清理")
        cleaner_group.setStyleSheet("color: #e0e0e0;")
        cleaner_layout = QVBoxLayout(cleaner_group)
        
        self.check_clean_temp = QCheckBox("清理临时文件")
        self.check_clean_temp.setChecked(True)
        self.check_clean_temp.setStyleSheet("color: #e0e0e0;")
        cleaner_layout.addWidget(self.check_clean_temp)
        
        self.check_clean_recycle = QCheckBox("清空回收站")
        self.check_clean_recycle.setChecked(True)
        self.check_clean_recycle.setStyleSheet("color: #e0e0e0;")
        cleaner_layout.addWidget(self.check_clean_recycle)
        
        self.check_clean_browser = QCheckBox("清理浏览器缓存")
        self.check_clean_browser.setChecked(True)
        self.check_clean_browser.setStyleSheet("color: #e0e0e0;")
        cleaner_layout.addWidget(self.check_clean_browser)
        
        self.check_clean_prefetch = QCheckBox("清理Windows预取")
        self.check_clean_prefetch.setChecked(True)
        self.check_clean_prefetch.setStyleSheet("color: #e0e0e0;")
        cleaner_layout.addWidget(self.check_clean_prefetch)
        
        self.check_clean_logs = QCheckBox("清理系统日志")
        self.check_clean_logs.setChecked(False)
        self.check_clean_logs.setStyleSheet("color: #e0e0e0;")
        cleaner_layout.addWidget(self.check_clean_logs)
        
        layout.addWidget(cleaner_group)
        
        # 磁盘检查设置
        disk_check_group = QGroupBox("磁盘检查")
        disk_check_group.setStyleSheet("color: #e0e0e0;")
        disk_check_layout = QVBoxLayout(disk_check_group)
        
        self.check_disk_readonly = QCheckBox("默认以只读模式运行磁盘检查")
        self.check_disk_readonly.setChecked(True)
        self.check_disk_readonly.setStyleSheet("color: #e0e0e0;")
        disk_check_layout.addWidget(self.check_disk_readonly)
        
        layout.addWidget(disk_check_group)
        
        # 病毒扫描设置
        virus_group = QGroupBox("病毒扫描")
        virus_group.setStyleSheet("color: #e0e0e0;")
        virus_layout = QVBoxLayout(virus_group)
        
        self.check_scan_archives = QCheckBox("扫描压缩文件")
        self.check_scan_archives.setChecked(True)
        self.check_scan_archives.setStyleSheet("color: #e0e0e0;")
        virus_layout.addWidget(self.check_scan_archives)
        
        self.check_scan_rootkits = QCheckBox("扫描根套件")
        self.check_scan_rootkits.setChecked(True)
        self.check_scan_rootkits.setStyleSheet("color: #e0e0e0;")
        virus_layout.addWidget(self.check_scan_rootkits)
        
        self.check_scan_autofix = QCheckBox("自动修复检测到的问题")
        self.check_scan_autofix.setChecked(False)
        self.check_scan_autofix.setStyleSheet("color: #e0e0e0;")
        virus_layout.addWidget(self.check_scan_autofix)
        
        scan_level_layout = QHBoxLayout()
        scan_level_label = QLabel("扫描彻底程度：")
        scan_level_label.setStyleSheet("color: #e0e0e0;")
        scan_level_layout.addWidget(scan_level_label)
        
        self.slider_scan_level = QSlider(Qt.Horizontal)
        self.slider_scan_level.setRange(1, 3)
        self.slider_scan_level.setValue(2)
        self.slider_scan_level.setTickPosition(QSlider.TicksBelow)
        self.slider_scan_level.setTickInterval(1)
        scan_level_layout.addWidget(self.slider_scan_level)
        
        virus_layout.addLayout(scan_level_layout)
        layout.addWidget(virus_group)
    
    def setup_advanced_tab(self):
        """设置高级设置选项卡"""
        layout = QVBoxLayout(self.advanced_tab)
        
        # 备份设置
        backup_group = QGroupBox("备份设置")
        backup_group.setStyleSheet("color: #e0e0e0;")
        backup_group_layout = QVBoxLayout(backup_group)
        
        self.check_backup_before_repair = QCheckBox("修复问题前创建备份")
        self.check_backup_before_repair.setChecked(True)
        self.check_backup_before_repair.setStyleSheet("color: #e0e0e0;")
        backup_group_layout.addWidget(self.check_backup_before_repair)
        
        backup_location_layout = QHBoxLayout()
        backup_location_label = QLabel("备份位置：")
        backup_location_label.setStyleSheet("color: #e0e0e0;")
        backup_location_layout.addWidget(backup_location_label)
        
        self.edit_backup_location = QLineEdit()
        self.edit_backup_location.setText(os.path.join(os.environ.get("USERPROFILE", ""), "GlaryBackups"))
        self.edit_backup_location.setStyleSheet("color: #e0e0e0; background-color: #2a2a2a;")
        backup_location_layout.addWidget(self.edit_backup_location)
        
        self.btn_browse_backup = QPushButton("浏览...")
        self.btn_browse_backup.clicked.connect(self.browse_backup_location)
        self.btn_browse_backup.setStyleSheet("color: #e0e0e0; background-color: #2a2a2a;")
        backup_location_layout.addWidget(self.btn_browse_backup)
        
        backup_group_layout.addLayout(backup_location_layout)
        layout.addWidget(backup_group)
        
        # 日志设置
        log_group = QGroupBox("日志设置")
        log_group.setStyleSheet("color: #e0e0e0;")
        log_group_layout = QVBoxLayout(log_group)
        
        self.check_enable_logging = QCheckBox("启用日志记录")
        self.check_enable_logging.setChecked(True)
        self.check_enable_logging.setStyleSheet("color: #e0e0e0;")
        log_group_layout.addWidget(self.check_enable_logging)
        
        layout.addWidget(log_group)
        
        # 性能设置
        performance_group = QGroupBox(self.get_translation("performance_settings", "性能设置"))
        performance_group.setStyleSheet("color: #e0e0e0;")
        performance_layout = QVBoxLayout(performance_group)
        
        # 添加启用动画设置选项
        self.enable_animations_checkbox = QCheckBox(self.get_translation("enable_animations", "启用界面动画效果"))
        self.enable_animations_checkbox.setChecked(self.settings.get_setting("enable_animations", True))
        self.enable_animations_checkbox.setStyleSheet("color: #e0e0e0;")
        self.enable_animations_checkbox.stateChanged.connect(lambda state: self.settings.set_setting("enable_animations", state == Qt.Checked))
        performance_layout.addWidget(self.enable_animations_checkbox)
        
        # 使用多线程选项
        self.check_use_multithreading = QCheckBox(self.get_translation("use_multithreading", "使用多线程以加快扫描速度"))
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.check_use_multithreading.setStyleSheet("color: #e0e0e0;")
        performance_layout.addWidget(self.check_use_multithreading)
        
        # 线程数量设置
        thread_layout = QHBoxLayout()
        thread_label = QLabel("最大线程数：")
        thread_label.setStyleSheet("color: #e0e0e0;")
        thread_layout.addWidget(thread_label)
        
        self.spin_max_threads = QSpinBox()
        self.spin_max_threads.setRange(1, 16)
        self.spin_max_threads.setValue(4)
        self.spin_max_threads.setStyleSheet("color: #e0e0e0; background-color: #2a2a2a;")
        thread_layout.addWidget(self.spin_max_threads)
        
        performance_layout.addLayout(thread_layout)
        layout.addWidget(performance_group)
    
    def setup_appearance_tab(self):
        """设置外观选项卡"""
        layout = QVBoxLayout(self.appearance_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 主题设置
        theme_group = QGroupBox(self.get_translation("theme_settings", "主题设置"))
        theme_layout = QFormLayout(theme_group)
        theme_layout.setContentsMargins(15, 15, 15, 15)
        theme_layout.setSpacing(15)
        
        # 主题选择器
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumWidth(200)
        self.theme_combo.setObjectName("theme_combo")
        
        # 获取所有主题
        theme_names = self.theme_manager.get_theme_names()
        theme_display_names = self.theme_manager.get_theme_display_names()
        
        # 添加主题到下拉列表
        for theme_name in theme_names:
            display_name = theme_display_names.get(theme_name, theme_name.capitalize())
            self.theme_combo.addItem(display_name, theme_name)
        
        # 设置当前选中的主题
        current_theme = self.theme_manager.current_theme
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_theme:
                self.theme_combo.setCurrentIndex(i)
                break
        
        # 应用主题按钮
        self.apply_theme_button = QPushButton(self.get_translation("apply_theme", "应用主题"))
        self.apply_theme_button.setObjectName("apply_theme_button")
        self.apply_theme_button.clicked.connect(self.apply_theme)
        
        # 添加到布局
        theme_layout.addRow(self.get_translation("select_theme", "选择主题:"), self.theme_combo)
        theme_layout.addRow("", self.apply_theme_button)
        
        # 界面调整设置
        ui_group = QGroupBox(self.get_translation("ui_settings", "界面设置"))
        ui_layout = QVBoxLayout(ui_group)
        ui_layout.setContentsMargins(15, 15, 15, 15)
        ui_layout.setSpacing(10)
        
        # 启用动画复选框
        self.enable_animations_checkbox = QCheckBox(self.get_translation("enable_animations", "启用动画效果"))
        self.enable_animations_checkbox.setObjectName("enable_animations_checkbox")
        self.enable_animations_checkbox.setChecked(True)
        
        # 添加到布局
        ui_layout.addWidget(self.enable_animations_checkbox)
        
        # 添加组到主布局
        layout.addWidget(theme_group)
        layout.addWidget(ui_group)
        layout.addStretch(1)
    
    def browse_backup_location(self):
        """打开对话框以选择备份位置"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择备份位置", self.edit_backup_location.text()
        )
        if folder:
            self.edit_backup_location.setText(folder)
    
    def choose_color(self, color_type, button):
        """打开颜色选择对话框"""
        current_color = None
        
        try:
            # 获取当前颜色设置
            if color_type == "custom_bg_color":
                current_color = self.settings.get_setting("custom_bg_color", "#1e1e1e")
            elif color_type == "custom_text_color":
                current_color = self.settings.get_setting("custom_text_color", "#e0e0e0")
            elif color_type == "custom_accent_color":
                current_color = self.settings.get_setting("custom_accent_color", "#555555")
            
            # 创建颜色对话框
            color = QColorDialog.getColor(QColor(current_color), self, "选择颜色")
            
            if color.isValid():
                # 保存新颜色设置
                hex_color = color.name()
                self.settings.set_setting(color_type, hex_color)
                
                # 更新按钮颜色
                button.setStyleSheet(f"background-color: {hex_color}; min-width: 80px; min-height: 24px;")
                
                # 更新并应用自定义主题
                self.update_custom_theme()
        except Exception as e:
            print(f"选择颜色时出错: {str(e)}")
    
    def update_custom_theme(self):
        """更新自定义主题"""
        # 获取自定义颜色
        bg_color = self.settings.get_setting("custom_bg_color", "#1e1e1e")
        text_color = self.settings.get_setting("custom_text_color", "#e0e0e0")
        accent_color = self.settings.get_setting("custom_accent_color", "#555555")
        
        # 更新主题管理器中的自定义主题
        self.theme_manager.update_custom_theme({
            "bg_color": bg_color,
            "text_color": text_color,
            "accent_color": accent_color
        })
        
        # 更新主题
        if self.settings.get_setting("theme", "dark") == "custom":
            main_window = self.window()
            if main_window and hasattr(main_window, 'apply_theme'):
                main_window.apply_theme()
    
    def on_theme_changed(self, index):
        """处理主题变化"""
        # 只有当选择"自定义"时才显示自定义颜色选项
        selected_theme = self.theme_combo.currentData()
        self.custom_colors_widget.setVisible(selected_theme == "custom")
        
        # 实时应用主题更改
        self.settings.set_setting("theme", selected_theme)
        
        # 设置主题管理器当前主题
        self.theme_manager.set_current_theme(selected_theme)
        
        # 尝试通知主窗口应用新主题
        main_window = self.window()
        if main_window and hasattr(main_window, 'apply_theme'):
            main_window.apply_theme()
    
    def load_settings(self):
        """从设置管理器加载设置"""
        # 加载语言设置
        current_language = self.settings.get_setting("language", "English")
        index = self.language_combo.findText(current_language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        # 加载主题设置
        current_theme = self.settings.get_setting("theme", "dark")
        theme_index = -1
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_theme:
                theme_index = i
                break
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
        else:
            self.theme_combo.setCurrentIndex(0)  # 默认dark主题
        
        # 加载透明度设置
        transparency = self.settings.get_setting("transparency", 100)
        self.transparency_slider.setValue(transparency)
        self.transparency_value.setText(f"{transparency}%")
        
        # 设置自定义颜色按钮的初始颜色
        self.update_color_buttons()
        
        # 加载通知设置
        enable_notifications = self.settings.get_setting("enable_notifications", True)
        self.enable_notifications_checkbox.setChecked(enable_notifications)
        
        show_tips = self.settings.get_setting("show_tips", True)
        self.show_tips_checkbox.setChecked(show_tips)
        
        # 加载动画设置
        enable_animations = self.settings.get_setting("enable_animations", True)
        self.enable_animations_checkbox.setChecked(enable_animations)
        
        maintenance_reminder = self.settings.get_setting("maintenance_reminder", True)
        self.maintenance_reminder_checkbox.setChecked(maintenance_reminder)
        
        # 加载自启动设置
        start_with_windows = self.settings.get_setting("start_with_windows", False)
        self.startup_checkbox.setChecked(start_with_windows)
        
        # 加载高级设置
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", 
                                                                 os.path.join(os.environ.get("USERPROFILE", ""), "GlaryBackups")))
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
        
        # 更新扫描设置
        self.check_clean_temp.setChecked(self.settings.get_setting("clean_temp", True))
        self.check_clean_recycle.setChecked(self.settings.get_setting("clean_recycle", True))
        self.check_clean_browser.setChecked(self.settings.get_setting("clean_browser", True))
        self.check_clean_prefetch.setChecked(self.settings.get_setting("clean_prefetch", True))
        self.check_clean_logs.setChecked(self.settings.get_setting("clean_logs", True))
        
        # 更新备份设置
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", os.path.join(os.environ.get("USERPROFILE", ""), "GlaryBackups")))
        
        # 更新日志设置
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        
        # 更新性能设置
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
        self.spin_max_threads.setValue(self.settings.get_setting("max_threads", 4))
    
    def save_settings(self):
        """保存设置"""
        # 主题设置
        self.settings.set_setting("theme", self.theme_combo.currentText())
        accent_color = self.accent_color_button.property("current_color")
        if accent_color:
            self.settings.set_setting("accent_color", accent_color)
        self.settings.set_setting("background_image", self.background_image_path)
        
        # 窗口设置
        self.settings.set_setting("use_system_title_bar", self.system_titlebar_check.isChecked())
        self.settings.set_setting("window_blur", self.window_blur_check.isChecked())
        self.settings.set_setting("start_minimized", self.start_minimized_check.isChecked())
        self.settings.set_setting("close_to_tray", self.close_to_tray_check.isChecked())
        
        # 语言设置
        self.settings.set_setting("language", self.language_combo.currentText())
        
        # 性能设置
        self.settings.set_setting("startup_scan", self.startup_scan_check.isChecked())
        
        # 清理设置
        self.settings.set_setting("deep_scan", self.deep_scan_check.isChecked())
        self.settings.set_setting("auto_clean", self.auto_clean_check.isChecked())
        
        # 更新设置
        self.settings.set_setting("check_updates", self.check_updates_check.isChecked())
        self.settings.set_setting("auto_update", self.auto_update_check.isChecked())
        
        # 备份设置
        self.settings.set_setting("auto_backup", self.auto_backup_check.isChecked())
        self.settings.set_setting("backup_location", self.backup_location_edit.text())
        
        # 通知设置
        self.settings.set_setting("show_notifications", self.show_notifications_check.isChecked())
        self.settings.set_setting("notification_sound", self.notification_sound_check.isChecked())
        
        # 重启时间表设置
        self.settings.set_setting("schedule_restarts", self.schedule_restarts_check.isChecked())
        
        # 保存到文件
        self.settings.save_settings()
        
        # 更新应用主题
        self.main_window.apply_theme()
    
    def reset_settings(self):
        """重置设置为默认值"""
        # 重置常规设置
        self.language_combo.setCurrentText("English")
        self.startup_checkbox.setChecked(False)
        self.enable_notifications_checkbox.setChecked(True)
        self.show_tips_checkbox.setChecked(True)
        self.maintenance_reminder_checkbox.setChecked(True)
        
        # 重置主题设置
        self.theme_combo.setCurrentText("dark")
        
        # 重置自定义颜色
        self.update_color_buttons()
        
        # 重置高级设置
        self.check_backup_before_repair.setChecked(True)
        self.edit_backup_location.setText(os.path.join(os.environ.get("USERPROFILE", ""), "GlaryBackups"))
        self.check_enable_logging.setChecked(True)
        self.check_use_multithreading.setChecked(True)
        self.spin_max_threads.setValue(4)
        
        # 重置扫描设置
        self.check_clean_temp.setChecked(True)
        self.check_clean_recycle.setChecked(True)
        self.check_clean_browser.setChecked(True)
        self.check_clean_prefetch.setChecked(True)
        self.check_clean_logs.setChecked(False)
        self.check_scan_archives.setChecked(True)
        self.check_scan_rootkits.setChecked(True)
        self.check_scan_autofix.setChecked(False)
        self.slider_scan_level.setValue(2)
    
    def get_translation(self, key, default=None):
        """获取键的翻译"""
        return self.settings.get_translation("settings", key, default)
        
    def on_language_changed(self, index):
        """处理语言更改"""
        # 获取所选语言
        language = self.language_combo.currentText()
        
        # 更新设置
        self.settings.set_setting("language", language)
        
        # 使用新语言刷新UI
        self.refresh_language()
        
        # 如果可能，通知父级（主窗口）语言更改
        parent = self.parent()
        while parent:
            if hasattr(parent, 'language_changed') and callable(getattr(parent, 'language_changed')):
                parent.language_changed.emit(language)
                break
            parent = parent.parent()
        
    def refresh_language(self):
        """根据当前语言更新界面文本"""
        # 更新标签页标题
        self.tabs.setTabText(0, self.get_translation("general_tab", "常规"))
        self.tabs.setTabText(1, self.get_translation("scan_tab", "扫描"))
        self.tabs.setTabText(2, self.get_translation("advanced_tab", "高级"))
        self.tabs.setTabText(3, self.get_translation("appearance_tab", "外观"))
        
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
            
        self.startup_checkbox.setText(self.get_translation("auto_start", "自动启动"))
        
        # 更新主题设置
        theme_group = self.findChild(QGroupBox, "theme_group")
        if theme_group:
            theme_group.setTitle(self.get_translation("theme_settings", "主题设置"))
            
        theme_label = self.findChild(QLabel, "theme_label")
        if theme_label:
            theme_label.setText(self.get_translation("theme", "主题："))
            
        # 更新主题选项
        if self.theme_combo.count() >= 6:
            self.theme_combo.setItemText(0, self.get_translation("dark", "深色"))
            self.theme_combo.setItemText(1, self.get_translation("light", "浅色"))
            self.theme_combo.setItemText(2, self.get_translation("blue", "蓝色主题"))
            self.theme_combo.setItemText(3, self.get_translation("green", "绿色主题"))
            self.theme_combo.setItemText(4, self.get_translation("purple", "紫色主题"))
            self.theme_combo.setItemText(5, self.get_translation("custom", "自定义"))
            
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
            print(f"更新自定义颜色标签出错: {str(e)}")
                
        # 更新颜色选择按钮
        for button in self.findChildren(QPushButton):
            if "选择颜色" in button.text():
                button.setText(self.get_translation("choose_color", "选择颜色"))
        
        # 更新通知组
        notifications_group = self.findChild(QGroupBox, "notifications_group")
        if notifications_group:
            notifications_group.setTitle(self.get_translation("notifications", "通知"))
            
        self.enable_notifications_checkbox.setText(self.get_translation("enable_notifications", "启用通知"))
        self.show_tips_checkbox.setText(self.get_translation("show_tips", "显示提示"))
        self.maintenance_reminder_checkbox.setText(self.get_translation("maintenance_reminder", "维护提醒"))
        
        # 更新按钮
        self.save_button.setText(self.get_translation("save_settings", "保存设置"))
        self.apply_button.setText(self.get_translation("apply_settings", "应用设置"))
        self.restore_defaults_button.setText(self.get_translation("restore_defaults", "恢复默认"))
    
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
        """处理透明度变化"""
        self.transparency_value.setText(f"{value}%")
        self.settings.set_setting("window_transparency", value)
        
        # 如果直接连接到主窗口，应用透明度变化
        main_window = self.window()
        if main_window and hasattr(main_window, 'apply_transparency'):
            main_window.apply_transparency()

    def apply_settings(self):
        """应用当前设置并重新加载UI"""
        self.save_settings()  # 复用保存逻辑
        
        # 获取主窗口实例
        main_window = self.window()
        
        # 如果当前在独立设置窗口
        if isinstance(main_window, QDialog):
            main_window = main_window.parent()
        
        # 禁用应用按钮，避免重复点击
        self.apply_button.setEnabled(False)
        self.apply_button.setText(self.get_translation("applying", "正在应用..."))
        
        # 清除之前的状态栏（如果存在）
        if hasattr(self, 'status_bar') and self.status_bar:
            try:
                self.layout().removeWidget(self.status_bar)
                self.status_bar.deleteLater()
                self.status_bar = None
            except Exception as e:
                print(f"移除状态栏出错: {str(e)}")
        
        # 添加加载动画
        movie = QMovie("resources/images/loading.gif")
        loading_label = None
        if movie.isValid() and self.settings.get_setting("enable_animations", True):
            loading_label = QLabel(self)
            loading_label.setAlignment(Qt.AlignCenter)
            loading_label.setMovie(movie)
            movie.start()
            
            # 将加载动画覆盖在设置界面上，但不影响原来的布局
            loading_label.setGeometry(self.rect())
            loading_label.setFixedSize(self.size())  # 确保大小固定
            loading_label.setStyleSheet("background-color: rgba(0, 0, 0, 150); border: none;")
            loading_label.raise_()  # 确保显示在最上层
            loading_label.show()
            
            # 确保处理事件以显示加载界面
            QApplication.processEvents()
        
        if main_window and hasattr(main_window, 'apply_theme'):
            # 应用主题变化
            main_window.apply_theme()
            
            # 应用透明度
            main_window.apply_transparency()
            
            # 刷新所有组件
            if hasattr(main_window, 'refresh_all_components'):
                main_window.refresh_all_components()
                
            # 应用语言变化并重新加载UI
            QTimer.singleShot(100, lambda: main_window.change_language(
                self.settings.get_setting("language", "en")
            ))
        
        # 延迟一段时间后恢复按钮状态，确保用户看到反馈
        QTimer.singleShot(1500, lambda: self._finish_applying(loading_label if movie.isValid() else None, movie))
            
        # 添加视觉反馈
        AnimationUtils.highlight(self.apply_button, duration=800)
        
        # 创建新的状态栏用于显示反馈信息
        self.status_bar = QStatusBar(self)
        self.status_bar.setStyleSheet("color: #4CAF50;")
        self.layout().addWidget(self.status_bar)
        self.status_bar.showMessage(self.get_translation("settings_applied", "设置已应用"), 3000)
        
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
            print(f"清理应用设置界面出错: {str(e)}")

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
            print(f"计算颜色变化出错: {str(e)}")
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
