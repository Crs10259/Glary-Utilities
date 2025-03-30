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
        buttons_layout.addWidget(self.save_button)
        
        self.restore_defaults_button = QPushButton("恢复默认")
        self.restore_defaults_button.setObjectName("restore_defaults_button")
        self.restore_defaults_button.setMinimumWidth(140)
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
        general_group_layout = QFormLayout(general_group)
        
        # 语言设置
        language_label = QLabel("语言：")
        language_label.setObjectName("language_label")
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("language_combo")
        self.language_combo.addItems(["English", "中文"])
        general_group_layout.addRow(language_label, self.language_combo)
        
        # 启动设置
        startup_label = QLabel("开机启动：")
        startup_label.setObjectName("startup_label")
        self.startup_checkbox = QCheckBox("自动启动")
        self.startup_checkbox.setObjectName("startup_checkbox")
        general_group_layout.addRow(startup_label, self.startup_checkbox)
        
        layout.addWidget(general_group)
        
        # 通知组
        notifications_group = QGroupBox("通知")
        notifications_group.setObjectName("notifications_group")
        notifications_layout = QVBoxLayout(notifications_group)
        
        self.enable_notifications_checkbox = QCheckBox("启用通知")
        self.enable_notifications_checkbox.setObjectName("enable_notifications_checkbox")
        self.enable_notifications_checkbox.setChecked(True)
        notifications_layout.addWidget(self.enable_notifications_checkbox)
        
        self.show_tips_checkbox = QCheckBox("显示提示")
        self.show_tips_checkbox.setObjectName("show_tips_checkbox")
        self.show_tips_checkbox.setChecked(True)
        notifications_layout.addWidget(self.show_tips_checkbox)
        
        self.maintenance_reminder_checkbox = QCheckBox("维护提醒")
        self.maintenance_reminder_checkbox.setObjectName("maintenance_reminder_checkbox")
        self.maintenance_reminder_checkbox.setChecked(True)
        notifications_layout.addWidget(self.maintenance_reminder_checkbox)
        
        layout.addWidget(notifications_group)
        
    def setup_scan_tab(self):
        """设置扫描选项卡"""
        layout = QVBoxLayout(self.scan_tab)
        
        # 系统清理设置
        cleaner_group = QGroupBox("系统清理")
        cleaner_layout = QVBoxLayout(cleaner_group)
        
        self.check_clean_temp = QCheckBox("清理临时文件")
        self.check_clean_temp.setChecked(True)
        cleaner_layout.addWidget(self.check_clean_temp)
        
        self.check_clean_recycle = QCheckBox("清空回收站")
        self.check_clean_recycle.setChecked(True)
        cleaner_layout.addWidget(self.check_clean_recycle)
        
        self.check_clean_browser = QCheckBox("清理浏览器缓存")
        self.check_clean_browser.setChecked(True)
        cleaner_layout.addWidget(self.check_clean_browser)
        
        self.check_clean_prefetch = QCheckBox("清理Windows预取")
        self.check_clean_prefetch.setChecked(True)
        cleaner_layout.addWidget(self.check_clean_prefetch)
        
        self.check_clean_logs = QCheckBox("清理系统日志")
        self.check_clean_logs.setChecked(False)
        cleaner_layout.addWidget(self.check_clean_logs)
        
        layout.addWidget(cleaner_group)
        
        # 磁盘检查设置
        disk_check_group = QGroupBox("磁盘检查")
        disk_check_layout = QVBoxLayout(disk_check_group)
        
        self.check_disk_readonly = QCheckBox("默认以只读模式运行磁盘检查")
        self.check_disk_readonly.setChecked(True)
        disk_check_layout.addWidget(self.check_disk_readonly)
        
        layout.addWidget(disk_check_group)
        
        # 病毒扫描设置
        virus_group = QGroupBox("病毒扫描")
        virus_layout = QVBoxLayout(virus_group)
        
        self.check_scan_archives = QCheckBox("扫描压缩文件")
        self.check_scan_archives.setChecked(True)
        virus_layout.addWidget(self.check_scan_archives)
        
        self.check_scan_rootkits = QCheckBox("扫描根套件")
        self.check_scan_rootkits.setChecked(True)
        virus_layout.addWidget(self.check_scan_rootkits)
        
        self.check_scan_autofix = QCheckBox("自动修复检测到的问题")
        self.check_scan_autofix.setChecked(False)
        virus_layout.addWidget(self.check_scan_autofix)
        
        scan_level_layout = QHBoxLayout()
        scan_level_layout.addWidget(QLabel("扫描彻底程度："))
        
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
        backup_group_layout = QVBoxLayout(backup_group)
        
        self.check_backup_before_repair = QCheckBox("修复问题前创建备份")
        self.check_backup_before_repair.setChecked(True)
        backup_group_layout.addWidget(self.check_backup_before_repair)
        
        backup_location_layout = QHBoxLayout()
        backup_location_layout.addWidget(QLabel("备份位置："))
        
        self.edit_backup_location = QLineEdit()
        self.edit_backup_location.setText(os.path.join(os.environ.get("USERPROFILE", ""), "GlaryBackups"))
        backup_location_layout.addWidget(self.edit_backup_location)
        
        self.btn_browse_backup = QPushButton("浏览...")
        self.btn_browse_backup.clicked.connect(self.browse_backup_location)
        backup_location_layout.addWidget(self.btn_browse_backup)
        
        backup_group_layout.addLayout(backup_location_layout)
        layout.addWidget(backup_group)
        
        # 日志设置
        log_group = QGroupBox("日志设置")
        log_group_layout = QVBoxLayout(log_group)
        
        self.check_enable_logging = QCheckBox("启用日志记录")
        self.check_enable_logging.setChecked(True)
        log_group_layout.addWidget(self.check_enable_logging)
        
        layout.addWidget(log_group)
        
        # 性能设置
        performance_group = QGroupBox("性能")
        performance_group_layout = QVBoxLayout(performance_group)
        
        self.check_use_multithreading = QCheckBox("使用多线程以加快扫描速度")
        self.check_use_multithreading.setChecked(True)
        performance_group_layout.addWidget(self.check_use_multithreading)
        
        thread_layout = QHBoxLayout()
        thread_layout.addWidget(QLabel("最大线程数："))
        
        self.spin_max_threads = QSpinBox()
        self.spin_max_threads.setRange(1, 16)
        self.spin_max_threads.setValue(4)
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
    
    def load_settings(self):
        """从设置管理器加载设置"""
        # 加载常规设置
        self.language_combo.setCurrentText(self.settings.get_setting("language", "English"))
        self.startup_checkbox.setChecked(self.settings.get_setting("start_with_windows", False))
        self.enable_notifications_checkbox.setChecked(self.settings.get_setting("enable_notifications", True))
        self.show_tips_checkbox.setChecked(self.settings.get_setting("show_tips", True))
        self.maintenance_reminder_checkbox.setChecked(self.settings.get_setting("maintenance_reminder", True))
        
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
        """使用当前语言翻译刷新所有UI元素"""
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
