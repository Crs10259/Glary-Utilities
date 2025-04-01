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

# Maximum number of data points to store for charts
MAX_DATA_POINTS = 60  # 60 data points = 2 minutes at 2-second intervals

class ChartTile(QFrame):
    """Custom chart widget for system metrics"""
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
        
        # Data storage (deque for efficient append/pop)
        self.data_points = deque(maxlen=MAX_DATA_POINTS)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Title container
        title_container = QHBoxLayout()
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {chart_color}; font-size: 14px; font-weight: bold;")
        title_container.addWidget(self.title_label)
        
        # Current value label (right-aligned)
        self.value_label = QLabel("0%")
        self.value_label.setStyleSheet(f"color: {chart_color}; font-size: 18px; font-weight: bold;")
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        title_container.addWidget(self.value_label)
        
        # Add title container to main layout
        self.layout.addLayout(title_container)
        
        # Create chart
        self.chart = QChart()
        self.chart.setBackgroundVisible(False)
        self.chart.setMargins(QMargins(0, 0, 0, 0))
        self.chart.legend().hide()
        
        # Create chart series
        self.series = QLineSeries()
        self.series.setColor(QColor(chart_color))
        self.chart.addSeries(self.series)
        
        # Create X axis (time)
        self.axis_x = QValueAxis()
        self.axis_x.setRange(0, MAX_DATA_POINTS - 1)
        self.axis_x.setVisible(False)
        
        # Create Y axis (value)
        self.axis_y = QValueAxis()
        self.axis_y.setRange(0, 100)
        self.axis_y.setVisible(False)
        
        # Attach axes to chart
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
        
        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setStyleSheet("background-color: transparent;")
        self.chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Add chart view to layout
        self.layout.addWidget(self.chart_view, 1)  # 设置伸展因子
        
        # Initialize with zero data
        for i in range(MAX_DATA_POINTS):
            self.data_points.append(0)
            self.series.append(i, 0)
            
        # If icon path provided and exists, add icon
        if icon_path and os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if not icon.isNull():
                self.icon_label = QLabel()
                self.icon_label.setPixmap(icon.pixmap(QSize(24, 24)))
                title_container.insertWidget(0, self.icon_label)
    
    def update_value(self, value):
        """Update the displayed value and chart"""
        # Update text display
        if isinstance(value, float):
            self.value_label.setText(f"{value:.1f}%")
        else:
            self.value_label.setText(str(value))
        
        # Add new data point
        if isinstance(value, str) and value != "N/A":
            # Try to parse numeric value from string
            try:
                numeric_value = float(value.replace("%", "").replace("°C", ""))
                self.data_points.append(numeric_value)
            except (ValueError, AttributeError):
                self.data_points.append(0)
        else:
            # If value is already numeric or N/A
            try:
                numeric_value = float(value) if value != "N/A" else 0
                self.data_points.append(numeric_value)
            except (ValueError, TypeError):
                self.data_points.append(0)
        
        # Update chart data
        self.series.clear()
        for i, point in enumerate(self.data_points):
            self.series.append(i, point)
            
        # Adjust Y axis range if needed
        max_value = max(self.data_points)
        if max_value > 0:
            # Set upper limit to the next multiple of 25 above max value
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
                        print(f"警告: 无法加载图标 {icon_path} 的像素图")
                else:
                    print(f"警告: 无法加载图标 {icon_path}")
            except Exception as e:
                print(f"加载图标时出错 {icon_path}: {str(e)}")
        
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
            print(f"加载箭头图标时出错: {str(e)}")

class DashboardWidget(BaseComponent):
    def __init__(self, settings, parent=None):
        # 初始化属性
        self.update_timer = None
        
        # 调用父类构造函数
        super().__init__(settings, parent)
        
        # 检查缺失翻译（仅在开发模式下）
        missing_keys = self.check_all_translations()
        if missing_keys:
            print(f"警告: 在 DashboardWidget 中缺少翻译:")
            for language, keys in missing_keys.items():
                print(f"  语言: {language}, 缺少的键: {', '.join(keys)}")
        
        # 设置定时器以更新系统信息
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_system_info)
        self.update_timer.start(2000) 
    
    def get_translation(self, key, default=None):
        """重写 get_translation 以使用正确的部分名称"""
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
            "通过修复问题来加速您的系统",
            None if not Icon.Optimize.Exist else Icon.Optimize.Path
        )
        self.quick_layout.addWidget(self.optimize_tile, 0, 0)
        
        # 清理垃圾块
        self.clean_tile = ActionTile(
            self.get_translation("clean_junk"),
            "通过删除不必要的文件来释放磁盘空间",
            None if not Icon.Clean.Exist else Icon.Clean.Path
        )
        self.quick_layout.addWidget(self.clean_tile, 0, 1)
        
        # 病毒扫描块
        self.virus_tile = ActionTile(
            self.get_translation("scan_system"),
            "扫描您的系统以查找病毒和恶意软件",
            None if not Icon.Virus.Exist else Icon.Virus.Path
        )
        self.quick_layout.addWidget(self.virus_tile, 1, 0)
        
        # 获取系统信息块
        self.info_tile = ActionTile(
            self.get_translation("get_system_info"),
            "获取系统信息",
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
            self.disk_chart.update_value("错误")
            print(f"获取磁盘使用情况时出错: {e}")
        
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