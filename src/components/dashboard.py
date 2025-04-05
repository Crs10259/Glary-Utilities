import os
import sys
import psutil
import platform
import shutil
from collections import deque
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QSizePolicy, QSpacerItem,
                            QProgressBar, QGridLayout)
from PyQt5.QtCore import Qt, QSize, QTimer, QMargins
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QPainter, QPen
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from components.base_component import BaseComponent
from components.icons import Icon

# 最大数据点数量
MAX_DATA_POINTS = 60  # 60个数据点 = 2分钟，每2秒一个数据点

class ChartTile(QFrame):
    """自定义图表小部件，用于系统指标"""
    def __init__(self, title, icon_path=None, chart_color="#00a8ff", parent=None):
        super().__init__(parent)
        self.setObjectName("chartTile")
        self.setStyleSheet("""
            #chartTile {
                background-color: #2d2d2d;
                border-radius: 8px;
                border: 1px solid #3a3a3a;
            }
        """)
        self.setMinimumHeight(200)
        self.chart_color = chart_color
        
        # 设置尺寸策略，确保在窗口调整大小时正常伸展
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 数据存储（使用deque以提高append/pop效率）
        self.data_points = deque(maxlen=MAX_DATA_POINTS)
        
        # 创建布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题容器
        title_container = QHBoxLayout()
        
        # 标题标签
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {chart_color}; font-size: 14px; font-weight: bold;")
        title_container.addWidget(self.title_label)
        
        # 当前值标签（右对齐）
        self.value_label = QLabel("0%")
        self.value_label.setStyleSheet(f"color: {chart_color}; font-size: 18px; font-weight: bold;")
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        title_container.addWidget(self.value_label)
        
        # 将标题容器添加到主布局
        self.layout.addLayout(title_container)
        
        # 创建图表
        self.chart = QChart()
        self.chart.setBackgroundVisible(False)
        self.chart.setMargins(QMargins(0, 0, 0, 0))
        self.chart.legend().hide()
        
        # 创建图表系列
        self.series = QLineSeries()
        self.series.setColor(QColor(chart_color))
        self.chart.addSeries(self.series)
        
        # 创建X轴（时间）
        self.axis_x = QValueAxis()
        self.axis_x.setRange(0, MAX_DATA_POINTS - 1)
        self.axis_x.setVisible(False)
        
        # 创建Y轴（值）
        self.axis_y = QValueAxis()
        self.axis_y.setRange(0, 100)
        self.axis_y.setVisible(False)
        
        # 将轴附加到图表
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
        
        # 创建图表视图
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setStyleSheet("background-color: transparent;")
        self.chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 将图表视图添加到布局
        self.layout.addWidget(self.chart_view, 1)  # 设置伸展因子
        
        # 初始化为零数据
        for i in range(MAX_DATA_POINTS):
            self.data_points.append(0)
            self.series.append(i, 0)
            
        # 如果提供了图标路径且存在，则添加图标
        if icon_path and os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if not icon.isNull():
                self.icon_label = QLabel()
                self.icon_label.setPixmap(icon.pixmap(QSize(24, 24)))
                title_container.insertWidget(0, self.icon_label)
    
    def update_value(self, value):
        """更新显示的值和图表"""
        # 更新文本显示
        if isinstance(value, float):
            self.value_label.setText(f"{value:.1f}%")
        else:
            self.value_label.setText(str(value))
        
        # 添加新数据点
        if isinstance(value, str) and value != "N/A":
            # 尝试从字符串解析数值
            try:
                numeric_value = float(value.replace("%", "").replace("°C", ""))
                self.data_points.append(numeric_value)
            except (ValueError, AttributeError):
                self.data_points.append(0)
        else:
            # 如果值已经是数值或N/A
            try:
                numeric_value = float(value) if value != "N/A" else 0
                self.data_points.append(numeric_value)
            except (ValueError, TypeError):
                self.data_points.append(0)
        
        # 更新图表数据
        self.series.clear()
        for i, point in enumerate(self.data_points):
            self.series.append(i, point)
            
        # 如果需要，调整Y轴范围
        max_value = max(self.data_points)
        if max_value > 0:
            # 将上限设置为最大值的下一个25的倍数
            upper_limit = ((int(max_value) // 25) + 1) * 25
            self.axis_y.setRange(0, max(100, upper_limit))
        
class ActionTile(QFrame):
    """自定义样式的操作块小部件"""
    def __init__(self, title, description, icon_path=None, parent=None):
        super().__init__(parent)
        self.setObjectName("actionTile")
        self.setStyleSheet("""
            #actionTile {
                background-color: #2d2d2d;
                border-radius: 8px;
                border: none;
            }
            #actionTile:hover {
                background-color: #353535;
                border: none;
            }
        """)
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(Qt.PointingHandCursor)
        
        # 创建布局
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # 如果提供了图标路径且存在，则添加图标
        if icon_path and os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.icon_label = QLabel()
                    pixmap = icon.pixmap(QSize(32, 32))
                    if not pixmap.isNull():
                        self.icon_label.setPixmap(pixmap)
                        self.layout.addWidget(self.icon_label)
                    else:
                        print(f"Warning: Could not load pixmap for icon {icon_path}")  # 警告：无法加载图标像素图
                else:
                    print(f"Warning: Could not load icon {icon_path}")  # 警告：无法加载图标
            except Exception as e:
                print(f"Error loading icon {icon_path}: {str(e)}")  # 加载图标时出错
        
        # 文本容器
        self.text_container = QVBoxLayout()
        
        # 标题标签
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #e0e0e0; font-size: 16px; font-weight: bold;")
        
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        self.desc_label.setWordWrap(True)
        
        self.text_container.addWidget(self.title_label)
        self.text_container.addWidget(self.desc_label)
        
        self.layout.addLayout(self.text_container, 1)  # 添加伸展因子
        
        # 修复箭头图标显示
        try:
            if hasattr(Icon.Arrow, 'Path') and os.path.exists(Icon.Arrow.Path):
                arrow_icon = QIcon(Icon.Arrow.Path)
                if not arrow_icon.isNull():
                    self.arrow_label = QLabel()
                    arrow_pixmap = arrow_icon.pixmap(QSize(16, 16))
                    if not arrow_pixmap.isNull():
                        self.arrow_label.setPixmap(arrow_pixmap)
                        self.layout.addWidget(self.arrow_label, 0, Qt.AlignRight)
        except Exception as e:
            print(f"Error loading arrow icon: {str(e)}")  # 加载箭头图标时出错

class DashboardWidget(BaseComponent):
    def __init__(self, parent=None):
        # 初始化属性
        self.update_timer = None
        
        # 调用父类构造函数
        super().__init__(parent)
        
        # 检查缺失翻译（仅在开发模式下）
        missing_keys = self.check_all_translations()
        if missing_keys:
            print(f"Warning: Missing translations in DashboardWidget:")  # 警告：DashboardWidget 中缺少翻译
            for language, keys in missing_keys.items():
                print(f"  Language: {language}, Missing keys: {', '.join(keys)}")  # 语言和缺少的键
        
        # 设置定时器以更新系统信息
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_system_info)
        self.update_timer.start(2000)
    
    def get_translation(self, key, default=None):
        return self.settings.get_translation("dashboard", key, default)
    
    def setup_ui(self):
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # 仪表板标题
        self.title = QLabel(self.get_translation("system_status"))
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        self.main_layout.addWidget(self.title)
        
        # 系统统计部分
        self.create_system_stats_section()
        
        # 快速访问部分
        self.create_quick_access_section()
        
        # 添加伸缩项，确保内容垂直居中且组件合理分布空间
        self.main_layout.addStretch(1)
    
    def create_system_stats_section(self):
        # 统计容器
        self.stats_frame = QFrame()
        self.stats_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stats_layout = QGridLayout(self.stats_frame)
        self.stats_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_layout.setSpacing(15)
        
        # CPU 使用情况图表
        self.cpu_chart = ChartTile(
            self.get_translation("cpu_usage"), 
            Icon.CPU.Path,
            chart_color="#E74856"  # 红色，模拟Windows Task Manager CPU图表
        )
        self.stats_layout.addWidget(self.cpu_chart, 0, 0)
        
        # 内存使用情况图表
        self.memory_chart = ChartTile(
            self.get_translation("memory_usage"), 
            Icon.Memory.Path,
            chart_color="#00B7C3"  # 青色，模拟Windows Task Manager内存图表
        )
        self.stats_layout.addWidget(self.memory_chart, 0, 1)
        
        # 磁盘使用情况图表
        self.disk_chart = ChartTile(
            self.get_translation("disk_usage"), 
            Icon.Disk.Path,
            chart_color="#FFB900"  # 黄色，模拟Windows Task Manager磁盘图表
        )
        self.stats_layout.addWidget(self.disk_chart, 1, 0)
        
        # 温度图表
        self.temp_chart = ChartTile(
            self.get_translation("system_temperature"), 
            Icon.Temperature.Path,
            chart_color="#10893E"  # 绿色，模拟Windows Task Manager温度图表
        )
        self.stats_layout.addWidget(self.temp_chart, 1, 1)
        
        # 将统计框架添加到主布局，并设置为可扩展
        self.main_layout.addWidget(self.stats_frame, 4)  # 图表部分占据更多空间
    
    def create_quick_access_section(self):
        # 快速访问标题
        self.quick_title = QLabel(self.get_translation("quick_access"))
        self.quick_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e0e0e0;")
        self.main_layout.addWidget(self.quick_title)
        
        # 快速访问容器
        self.quick_frame = QFrame()
        self.quick_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.quick_layout = QGridLayout(self.quick_frame)
        self.quick_layout.setContentsMargins(0, 0, 0, 0)
        self.quick_layout.setSpacing(15)
        
        # 优化系统块
        self.optimize_tile = ActionTile(
            self.get_translation("optimize_system"),
            "Speed up your system by fixing issues",  # 通过修复问题加速系统
            None if not Icon.Optimize.Exist else Icon.Optimize.Path
        )
        self.quick_layout.addWidget(self.optimize_tile, 0, 0)
        
        # 清理垃圾块
        self.clean_tile = ActionTile(
            self.get_translation("clean_junk"),
            "Free up disk space by removing unnecessary files",  # 通过删除不必要的文件释放磁盘空间
            None if not Icon.Clean.Exist else Icon.Clean.Path
        )
        self.quick_layout.addWidget(self.clean_tile, 0, 1)
        
        # 病毒扫描块
        self.virus_tile = ActionTile(
            self.get_translation("scan_system"),
            "Scan your system for viruses and malware",  # 扫描系统中的病毒和恶意软件
            None if not Icon.Virus.Exist else Icon.Virus.Path
        )
        self.quick_layout.addWidget(self.virus_tile, 1, 0)
        
        # 获取系统信息块
        self.info_tile = ActionTile(
            self.get_translation("get_system_info"),
            "Get system information",  # 获取系统信息
            None if not Icon.Info.Exist else Icon.Info.Path
        )
        self.quick_layout.addWidget(self.info_tile, 1, 1)
        
        # 将快速访问框架添加到主布局，设置为可扩展但比图表部分分配少一些空间
        self.main_layout.addWidget(self.quick_frame, 3)
        
        # 连接操作块到各自的功能
        self.optimize_tile.mousePressEvent = lambda event: self.navigate_to_page(3)  # 系统修复
        self.clean_tile.mousePressEvent = lambda event: self.navigate_to_page(1)     # 系统清理
        self.virus_tile.mousePressEvent = lambda event: self.navigate_to_page(8)     # 病毒扫描
        self.info_tile.mousePressEvent = lambda event: self.navigate_to_page(9)     # 系统信息
    
    def update_system_info(self):
        """更新系统统计信息"""
        # CPU 使用情况
        cpu_percent = psutil.cpu_percent()
        self.cpu_chart.update_value(cpu_percent)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        self.memory_chart.update_value(memory_percent)
        
        # 磁盘使用情况（系统驱动器）
        try:
            if platform.system() == 'Windows':
                # 在Windows上，获取C:驱动器的使用情况
                total, used, free = shutil.disk_usage('C:')
                disk_percent = (used / total) * 100
            else:
                # 在Unix/Linux/Mac上，获取根目录的使用情况
                total, used, free = shutil.disk_usage('/')
                disk_percent = (used / total) * 100
            
            self.disk_chart.update_value(disk_percent)
        except Exception as e:
            self.disk_chart.update_value("Error")  # 错误
            print(f"Error getting disk usage: {e}")  # 获取磁盘使用情况时出错
        
        # 温度（如果可用）
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current > 0:
                                self.temp_chart.update_value(entry.current)
                                return
            self.temp_chart.update_value("N/A")
        except:
            self.temp_chart.update_value("N/A")
    
    def navigate_to_page(self, page_index):
        """在主窗口中导航到特定页面"""
        # 页面索引与页面名称的映射
        page_names = {
            0: "Dashboard",
            1: "System Cleaner",
            2: "GPU Information",
            3: "System Repair",
            4: "DISM Tool",
            5: "Network Reset",
            6: "Disk Check",
            7: "Boot Repair",
            8: "Virus Scan",
            9: "System Information",
            10: "Settings"
        }
        
        # 查找主窗口以更改页面
        main_window = self.window()
        if main_window and page_index in page_names:
            main_window.set_active_page(page_names[page_index])

    def refresh_language(self):
        # 更新UI文本元素
        self.title.setText(self.get_translation("system_status"))
        self.quick_title.setText(self.get_translation("quick_access"))
        
        # 更新图表标题
        self.cpu_chart.title_label.setText(self.get_translation("cpu_usage"))
        self.memory_chart.title_label.setText(self.get_translation("memory_usage"))
        self.disk_chart.title_label.setText(self.get_translation("disk_usage"))
        self.temp_chart.title_label.setText(self.get_translation("system_temperature"))
        
        # 更新操作块
        self.optimize_tile.title_label.setText(self.get_translation("optimize_system"))
        self.clean_tile.title_label.setText(self.get_translation("clean_junk"))
        self.virus_tile.title_label.setText(self.get_translation("scan_system"))
        self.info_tile.title_label.setText(self.get_translation("get_system_info"))
        
        # 添加动画以突出显示更改
        super().refresh_language()

    def check_all_translations(self):
        """检查此组件中使用的所有翻译键是否存在
        
        引发:
            KeyError: 如果缺少任何翻译键
        """
        # 尝试获取此组件中使用的所有翻译
        keys = [
            "system_status", "cpu_usage", "memory_usage", "disk_usage",
            "system_temperature", "quick_access", "optimize_system", 
            "clean_junk", "scan_system", "get_system_info"
        ]
        
        for key in keys:
            # 如果键不存在，将引发KeyError
            self.get_translation(key, None) 