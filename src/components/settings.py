import os
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QPushButton, 
                          QComboBox, QCheckBox, QGroupBox, QFormLayout, QSlider, QLineEdit,
                          QColorDialog, QFileDialog, QDialog, QScrollArea, QSpinBox)
from PyQt5.QtCore import Qt, QSize, QSettings, QTranslator, QCoreApplication
from PyQt5.QtGui import QColor, QIcon

class SettingsWidget(QWidget):
    """应用程序设置的窗口小部件"""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """设置UI元素"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建选项卡
        self.tabs = QTabWidget()
        self.tabs.setObjectName("settings_tabs")
        
        # 创建选项卡
        self.general_tab = QWidget()
        self.scan_tab = QWidget()
        self.advanced_tab = QWidget()
        
        # 设置选项卡
        self.setup_general_tab()
        self.setup_scan_tab()
        self.setup_advanced_tab()
        
        # 将选项卡添加到小部件
        self.tabs.addTab(self.general_tab, "常规")
        self.tabs.addTab(self.scan_tab, "扫描")
        self.tabs.addTab(self.advanced_tab, "高级")
        
        layout.addWidget(self.tabs)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.save_button = QPushButton("保存设置")
        self.save_button.setObjectName("save_button")
        self.save_button.setMinimumWidth(120)
        self.save_button.setStyleSheet("color: #e0e0e0; background-color: #2a2a2a;")
        buttons_layout.addWidget(self.save_button)
        
        self.restore_defaults_button = QPushButton("恢复默认")
        self.restore_defaults_button.setObjectName("restore_defaults_button")
        self.restore_defaults_button.setMinimumWidth(140)
        self.restore_defaults_button.setStyleSheet("color: #e0e0e0; background-color: #2a2a2a;")
        buttons_layout.addWidget(self.restore_defaults_button)
        
        layout.addLayout(buttons_layout)
        
        # 连接信号
        self.save_button.clicked.connect(self.save_settings)
        self.restore_defaults_button.clicked.connect(self.reset_settings)
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
    
    def setup_general_tab(self):
        """设置常规设置选项卡"""
        layout = QVBoxLayout(self.general_tab)
        
        # 常规组
        general_group = QGroupBox("常规设置")
        general_group.setObjectName("general_group")
        general_group.setStyleSheet("color: #e0e0e0;")
        general_group_layout = QFormLayout(general_group)
        
        # 语言设置
        language_label = QLabel("语言：")
        language_label.setObjectName("language_label")
        language_label.setStyleSheet("color: #e0e0e0;")
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("language_combo")
        self.language_combo.addItems(["English", "中文"])
        self.language_combo.setStyleSheet("color: #e0e0e0; background-color: #2a2a2a;")
        general_group_layout.addRow(language_label, self.language_combo)
        
        # 启动设置
        startup_label = QLabel("开机启动：")
        startup_label.setObjectName("startup_label")
        startup_label.setStyleSheet("color: #e0e0e0;")
        self.startup_checkbox = QCheckBox("自动启动")
        self.startup_checkbox.setObjectName("startup_checkbox")
        self.startup_checkbox.setStyleSheet("color: #e0e0e0;")
        general_group_layout.addRow(startup_label, self.startup_checkbox)
        
        layout.addWidget(general_group)
        
        # 主题设置
        theme_group = QGroupBox("主题设置")
        theme_group.setObjectName("theme_group")
        theme_group.setStyleSheet("color: #e0e0e0;")
        theme_layout = QVBoxLayout(theme_group)
        
        # 主题选择
        theme_form_layout = QFormLayout()
        theme_label = QLabel("主题：")
        theme_label.setObjectName("theme_label")
        theme_label.setStyleSheet("color: #e0e0e0;")
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("theme_combo")
        self.theme_combo.addItems(["深色", "浅色", "蓝色主题", "绿色主题", "紫色主题", "自定义"])
        self.theme_combo.setStyleSheet("color: #e0e0e0; background-color: #2a2a2a;")
        theme_form_layout.addRow(theme_label, self.theme_combo)
        theme_layout.addLayout(theme_form_layout)
        
        # 透明度设置
        transparency_layout = QFormLayout()
        transparency_label = QLabel("窗口透明度：")
        transparency_label.setObjectName("transparency_label")
        transparency_label.setStyleSheet("color: #e0e0e0;")
        
        transparency_container = QWidget()
        transparency_container_layout = QHBoxLayout(transparency_container)
        transparency_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setObjectName("transparency_slider")
        self.transparency_slider.setRange(30, 100)  # 30% 到 100% 的透明度范围
        self.transparency_slider.setValue(100)  # 默认为不透明
        self.transparency_slider.setTickPosition(QSlider.TicksBelow)
        self.transparency_slider.setTickInterval(10)
        
        self.transparency_value = QLabel("100%")
        self.transparency_value.setStyleSheet("color: #e0e0e0;")
        
        transparency_container_layout.addWidget(self.transparency_slider)
        transparency_container_layout.addWidget(self.transparency_value)
        
        transparency_layout.addRow(transparency_label, transparency_container)
        theme_layout.addLayout(transparency_layout)
        
        # 连接透明度滑块的信号
        self.transparency_slider.valueChanged.connect(self.update_transparency_value)
        
        # 自定义颜色设置
        self.custom_colors_widget = QWidget()
        custom_colors_layout = QFormLayout(self.custom_colors_widget)
        
        # 背景颜色
        bg_color_label = QLabel("背景颜色：")
        bg_color_label.setStyleSheet("color: #e0e0e0;")
        bg_color_container = QWidget()
        bg_color_layout = QHBoxLayout(bg_color_container)
        bg_color_layout.setContentsMargins(0, 0, 0, 0)
        
        self.bg_color_preview = QLabel()
        self.bg_color_preview.setFixedSize(24, 24)
        self.bg_color_preview.setStyleSheet("background-color: #1e1e1e; border: 1px solid #3a3a3a;")
        bg_color_layout.addWidget(self.bg_color_preview)
        
        self.bg_color_button = QPushButton("选择颜色")
        self.bg_color_button.clicked.connect(lambda: self.choose_color("bg"))
        self.bg_color_button.setStyleSheet("color: #e0e0e0; background-color: #2a2a2a;")
        bg_color_layout.addWidget(self.bg_color_button)
        bg_color_layout.addStretch()
        
        custom_colors_layout.addRow(bg_color_label, bg_color_container)
        
        # 文本颜色
        text_color_label = QLabel("文本颜色：")
        text_color_label.setStyleSheet("color: #e0e0e0;")
        text_color_container = QWidget()
        text_color_layout = QHBoxLayout(text_color_container)
        text_color_layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_color_preview = QLabel()
        self.text_color_preview.setFixedSize(24, 24)
        self.text_color_preview.setStyleSheet("background-color: #e0e0e0; border: 1px solid #3a3a3a;")
        text_color_layout.addWidget(self.text_color_preview)
        
        self.text_color_button = QPushButton("选择颜色")
        self.text_color_button.clicked.connect(lambda: self.choose_color("text"))
        self.text_color_button.setStyleSheet("color: #e0e0e0; background-color: #2a2a2a;")
        text_color_layout.addWidget(self.text_color_button)
        text_color_layout.addStretch()
        
        custom_colors_layout.addRow(text_color_label, text_color_container)
        
        # 强调颜色
        accent_color_label = QLabel("强调颜色：")
        accent_color_label.setStyleSheet("color: #e0e0e0;")
        accent_color_container = QWidget()
        accent_color_layout = QHBoxLayout(accent_color_container)
        accent_color_layout.setContentsMargins(0, 0, 0, 0)
        
        self.accent_color_preview = QLabel()
        self.accent_color_preview.setFixedSize(24, 24)
        self.accent_color_preview.setStyleSheet("background-color: #00a8ff; border: 1px solid #3a3a3a;")
        accent_color_layout.addWidget(self.accent_color_preview)
        
        self.accent_color_button = QPushButton("选择颜色")
        self.accent_color_button.clicked.connect(lambda: self.choose_color("accent"))
        self.accent_color_button.setStyleSheet("color: #e0e0e0; background-color: #2a2a2a;")
        accent_color_layout.addWidget(self.accent_color_button)
        accent_color_layout.addStretch()
        
        custom_colors_layout.addRow(accent_color_label, accent_color_container)
        
        theme_layout.addWidget(self.custom_colors_widget)
        self.custom_colors_widget.setVisible(False)  # Initially hide custom colors
        
        # Connect theme combo box signal
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        
        layout.addWidget(theme_group)
        
        # 通知组
        notifications_group = QGroupBox("通知")
        notifications_group.setObjectName("notifications_group")
        notifications_group.setStyleSheet("color: #e0e0e0;")
        notifications_layout = QVBoxLayout(notifications_group)
        
        self.enable_notifications_checkbox = QCheckBox("启用通知")
        self.enable_notifications_checkbox.setObjectName("enable_notifications_checkbox")
        self.enable_notifications_checkbox.setChecked(True)
        self.enable_notifications_checkbox.setStyleSheet("color: #e0e0e0;")
        notifications_layout.addWidget(self.enable_notifications_checkbox)
        
        self.show_tips_checkbox = QCheckBox("显示提示")
        self.show_tips_checkbox.setObjectName("show_tips_checkbox")
        self.show_tips_checkbox.setChecked(True)
        self.show_tips_checkbox.setStyleSheet("color: #e0e0e0;")
        notifications_layout.addWidget(self.show_tips_checkbox)
        
        self.maintenance_reminder_checkbox = QCheckBox("维护提醒")
        self.maintenance_reminder_checkbox.setObjectName("maintenance_reminder_checkbox")
        self.maintenance_reminder_checkbox.setChecked(True)
        self.maintenance_reminder_checkbox.setStyleSheet("color: #e0e0e0;")
        notifications_layout.addWidget(self.maintenance_reminder_checkbox)
        
        layout.addWidget(notifications_group)
    
    def setup_scan_tab(self):
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
        performance_group = QGroupBox("性能")
        performance_group.setStyleSheet("color: #e0e0e0;")
        performance_group_layout = QVBoxLayout(performance_group)
        
        self.check_use_multithreading = QCheckBox("使用多线程以加快扫描速度")
        self.check_use_multithreading.setChecked(True)
        self.check_use_multithreading.setStyleSheet("color: #e0e0e0;")
        performance_group_layout.addWidget(self.check_use_multithreading)
        
        thread_layout = QHBoxLayout()
        thread_label = QLabel("最大线程数：")
        thread_label.setStyleSheet("color: #e0e0e0;")
        thread_layout.addWidget(thread_label)
        
        self.spin_max_threads = QSpinBox()
        self.spin_max_threads.setRange(1, 16)
        self.spin_max_threads.setValue(4)
        self.spin_max_threads.setStyleSheet("color: #e0e0e0; background-color: #2a2a2a;")
        thread_layout.addWidget(self.spin_max_threads)
        
        performance_group_layout.addLayout(thread_layout)
        layout.addWidget(performance_group)
    
    def browse_backup_location(self):
        """打开对话框以选择备份位置"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择备份位置", self.edit_backup_location.text()
        )
        if folder:
            self.edit_backup_location.setText(folder)
    
    def choose_color(self, color_type):
        """打开颜色选择对话框"""
        current_color = None
        preview_widget = None
        
        if color_type == "bg":
            current_color = QColor(self.settings.get_setting("custom_bg_color", "#1e1e1e"))
            preview_widget = self.bg_color_preview
        elif color_type == "text":
            current_color = QColor(self.settings.get_setting("custom_text_color", "#e0e0e0"))
            preview_widget = self.text_color_preview
        elif color_type == "accent":
            current_color = QColor(self.settings.get_setting("custom_accent_color", "#00a8ff"))
            preview_widget = self.accent_color_preview
        
        dialog = QColorDialog(current_color, self)
        if dialog.exec_():
            selected_color = dialog.selectedColor()
            if selected_color.isValid():
                color_hex = selected_color.name()
                
                # 更新预览
                preview_widget.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #3a3a3a;")
                
                # 存储颜色
                if color_type == "bg":
                    self.settings.set_setting("custom_bg_color", color_hex)
                elif color_type == "text":
                    self.settings.set_setting("custom_text_color", color_hex)
                elif color_type == "accent":
                    self.settings.set_setting("custom_accent_color", color_hex)
    
    def on_theme_changed(self, index):
        """处理主题变化"""
        # 只有当选择"自定义"时才显示自定义颜色选项
        self.custom_colors_widget.setVisible(index == 5)  # 5 = "自定义"
        
        # 实时应用主题更改
        selected_theme = self.theme_combo.currentText()
        self.settings.set_setting("theme", selected_theme)
        
        # 尝试通知主窗口应用新主题
        main_window = self.window()
        if main_window and hasattr(main_window, 'apply_theme'):
            main_window.apply_theme()
    
    def load_settings(self):
        """从设置管理器加载设置"""
        # 加载常规设置
        self.language_combo.setCurrentText(self.settings.get_setting("language", "English"))
        self.startup_checkbox.setChecked(self.settings.get_setting("start_with_windows", False))
        self.enable_notifications_checkbox.setChecked(self.settings.get_setting("enable_notifications", True))
        self.show_tips_checkbox.setChecked(self.settings.get_setting("show_tips", True))
        self.maintenance_reminder_checkbox.setChecked(self.settings.get_setting("maintenance_reminder", True))
        
        # 加载主题设置
        theme = self.settings.get_setting("theme", "深色")
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        else:
            self.theme_combo.setCurrentIndex(0)  # 默认深色主题
        
        # 加载透明度设置
        transparency = self.settings.get_setting("window_transparency", 100)
        self.transparency_slider.setValue(transparency)
        self.transparency_value.setText(f"{transparency}%")
            
        # 设置自定义颜色预览
        bg_color = self.settings.get_setting("custom_bg_color", "#1e1e1e")
        text_color = self.settings.get_setting("custom_text_color", "#e0e0e0")
        accent_color = self.settings.get_setting("custom_accent_color", "#00a8ff")
        
        self.bg_color_preview.setStyleSheet(f"background-color: {bg_color}; border: 1px solid #3a3a3a;")
        self.text_color_preview.setStyleSheet(f"background-color: {text_color}; border: 1px solid #3a3a3a;")
        self.accent_color_preview.setStyleSheet(f"background-color: {accent_color}; border: 1px solid #3a3a3a;")
        
        # 显示/隐藏自定义颜色设置
        self.custom_colors_widget.setVisible(self.theme_combo.currentText() == "自定义")
        
        # 加载高级设置
        self.check_backup_before_repair.setChecked(self.settings.get_setting("backup_before_repair", True))
        self.edit_backup_location.setText(self.settings.get_setting("backup_location", 
                                                                 os.path.join(os.environ.get("USERPROFILE", ""), "GlaryBackups")))
        self.check_enable_logging.setChecked(self.settings.get_setting("enable_logging", True))
        self.check_use_multithreading.setChecked(self.settings.get_setting("use_multithreading", True))
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
        """保存设置到设置管理器"""
        # 保存常规设置
        self.settings.set_setting("language", self.language_combo.currentText())
        self.settings.set_setting("start_with_windows", self.startup_checkbox.isChecked())
        self.settings.set_setting("enable_notifications", self.enable_notifications_checkbox.isChecked())
        self.settings.set_setting("show_tips", self.show_tips_checkbox.isChecked())
        self.settings.set_setting("maintenance_reminder", self.maintenance_reminder_checkbox.isChecked())
        
        # 保存主题设置
        self.settings.set_setting("theme", self.theme_combo.currentText())
        
        # 保存透明度设置
        self.settings.set_setting("window_transparency", self.transparency_slider.value())
        
        # 保存高级设置
        self.settings.set_setting("backup_before_repair", self.check_backup_before_repair.isChecked())
        self.settings.set_setting("backup_location", self.edit_backup_location.text())
        self.settings.set_setting("enable_logging", self.check_enable_logging.isChecked())
        self.settings.set_setting("use_multithreading", self.check_use_multithreading.isChecked())
        self.settings.set_setting("max_threads", self.spin_max_threads.value())
        
        # 保存扫描设置
        self.settings.set_setting("clean_temp", self.check_clean_temp.isChecked())
        self.settings.set_setting("clean_recycle", self.check_clean_recycle.isChecked())
        self.settings.set_setting("clean_browser", self.check_clean_browser.isChecked())
        self.settings.set_setting("clean_prefetch", self.check_clean_prefetch.isChecked())
        self.settings.set_setting("clean_logs", self.check_clean_logs.isChecked())
        self.settings.set_setting("scan_archives", self.check_scan_archives.isChecked())
        self.settings.set_setting("scan_rootkits", self.check_scan_rootkits.isChecked())
        self.settings.set_setting("scan_autofix", self.check_scan_autofix.isChecked())
        self.settings.set_setting("scan_level", self.slider_scan_level.value())
        
        # 保存到磁盘
        self.settings.save_settings()
        
    def reset_settings(self):
        """重置设置为默认值"""
        # 重置常规设置
        self.language_combo.setCurrentText("English")
        self.startup_checkbox.setChecked(False)
        self.enable_notifications_checkbox.setChecked(True)
        self.show_tips_checkbox.setChecked(True)
        self.maintenance_reminder_checkbox.setChecked(True)
        
        # 重置主题设置
        self.theme_combo.setCurrentText("深色")
        
        # 重置自定义颜色
        self.bg_color_preview.setStyleSheet("background-color: #1e1e1e; border: 1px solid #3a3a3a;")
        self.text_color_preview.setStyleSheet("background-color: #e0e0e0; border: 1px solid #3a3a3a;")
        self.accent_color_preview.setStyleSheet("background-color: #00a8ff; border: 1px solid #3a3a3a;")
        
        # 隐藏自定义颜色设置
        self.custom_colors_widget.setVisible(False)
        
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
        """使用新翻译更新UI元素"""
        # 更新选项卡标题
        self.tabs.setTabText(0, self.get_translation("general_tab", "常规"))
        self.tabs.setTabText(1, self.get_translation("scan_tab", "扫描"))
        self.tabs.setTabText(2, self.get_translation("advanced_tab", "高级"))
        
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
            
        # 找到自定义颜色部分的标签并更新
        for i in range(self.custom_colors_widget.layout().rowCount()):
            item = self.custom_colors_widget.layout().itemAt(i, 0)
            if item and item.widget():
                label = item.widget()
                if label.text() == "背景颜色：":
                    label.setText(self.get_translation("background_color", "背景颜色："))
                elif label.text() == "文本颜色：":
                    label.setText(self.get_translation("text_color", "文本颜色："))
                elif label.text() == "强调颜色：":
                    label.setText(self.get_translation("accent_color", "强调颜色："))
                    
        # 更新颜色选择按钮
        for button in self.findChildren(QPushButton):
            if button.text() == "选择颜色":
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
        
        # 按钮翻译
        self.get_translation("save_settings")
        self.get_translation("restore_defaults")

    def update_transparency_value(self):
        """处理透明度变化"""
        value = self.transparency_slider.value()
        self.transparency_value.setText(f"{value}%")
