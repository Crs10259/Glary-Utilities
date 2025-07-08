import os
import sys
import psutil
import shutil
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QSpacerItem, QSizePolicy, QFrame, QProgressBar,
    QToolButton, QApplication, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, QSize, QRectF, QPropertyAnimation, QEasingCurve, QMargins
from PyQt5.QtGui import (
    QColor, QPainter, QPainterPath, QIcon, QBrush, QPen, QFont, QCursor,
    QLinearGradient, QPalette
)
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis

from .base_component import BaseComponent
from config import Icon
from collections import deque

# 最大数据点数量
MAX_DATA_POINTS = 60  # 60个数据点 = 2分钟，每2秒一个数据点

class ChartTile(QFrame):
    """自定义图表小部件，用于系统指标"""
    def __init__(self, title, icon_path=None, chart_color="#00a8ff", parent=None):
        super().__init__(parent)
        self.setObjectName("chartTile")
        self.setStyleSheet(f"""
            #chartTile {{
                background-color: #2d2d2d;
                border-radius: 12px;
                border: 1px solid #3a3a3a;
            }}
        """)
        self.setMinimumHeight(200)
        self.chart_color = chart_color
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # 设置尺寸策略，确保在窗口调整大小时正常伸展
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 数据存储（使用deque以提高append/pop效率）
        self.data_points = deque(maxlen=MAX_DATA_POINTS)
        
        # 创建布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题容器
        title_container = QHBoxLayout()
        
        # 如果提供了图标路径且存在，则添加图标
        if icon_path and os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if not icon.isNull():
                self.icon_label = QLabel()
                self.icon_label.setPixmap(icon.pixmap(QSize(24, 24)))
                title_container.addWidget(self.icon_label)
        
        # 标题标签
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {chart_color}; font-size: 16px; font-weight: bold; background-color: transparent;")
        title_container.addWidget(self.title_label)
        
        # 当前值标签（右对齐）
        self.value_label = QLabel("0%")
        self.value_label.setStyleSheet(f"color: {chart_color}; font-size: 24px; font-weight: bold; background-color: transparent;")
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
        pen = QPen(QColor(chart_color))
        pen.setWidth(3)  # 增加线宽
        self.series.setPen(pen)
        self.chart.addSeries(self.series)
        
        # 添加渐变填充
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0, QColor(chart_color).lighter(150))
        gradient.setColorAt(1, QColor(chart_color).darker(150))
        self.series.setBrush(QBrush(gradient))
        
        # 创建X轴（时间）
        self.axis_x = QValueAxis()
        self.axis_x.setRange(0, MAX_DATA_POINTS - 1)
        self.axis_x.setVisible(True)
        self.axis_x.setLabelsVisible(False)  # 隐藏标签但显示网格线
        self.axis_x.setGridLineVisible(True)
        self.axis_x.setGridLineColor(QColor(60, 60, 60))  # 暗色网格线
        self.axis_x.setMinorGridLineVisible(False)  # 不显示次网格线
        
        # 创建Y轴（值）
        self.axis_y = QValueAxis()
        self.axis_y.setRange(0, 100)
        self.axis_y.setVisible(True)
        self.axis_y.setLabelsVisible(False)  # 隐藏标签但显示网格线
        self.axis_y.setGridLineVisible(True)
        self.axis_y.setGridLineColor(QColor(60, 60, 60))  # 暗色网格线
        self.axis_y.setMinorGridLineVisible(False)  # 不显示次网格线
        
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
    
    def update_value(self, value):
        """更新图表的数值，处理多种输入格式和错误状态"""
        if isinstance(value, (int, float)):
            # 是数字，显示为百分比
            percent_text = f"{value:.1f}%"
            self._update_percent_display(value, percent_text)
        elif isinstance(value, str):
            if value.endswith("°C"):
                # 温度值，特殊处理（先移除°C）
                try:
                    temp = float(value.replace("°C", ""))
                    self._update_temp_display(temp, value)
                except ValueError:
                    # 显示原始字符串
                    self.value_label.setText(value)
                    self._update_history_with_error()
            elif value.startswith("Retry in"):
                # 显示重试倒计时，使用特殊样式
                self.value_label.setText(value)
                self.value_label.setStyleSheet("color: #FFA500; font-size: 15px; font-weight: bold;")
                # 使用警告色的虚线边框表示等待状态
                # self.setStyleSheet(f"""
                #     QFrame {{
                #         background-color: #2d2d2d;
                #         border: 2px dashed #FFA500;
                #         border-radius: 8px;
                #     }}
                # """)
                self._update_history_with_error()
            elif value == "N/A":
                # 显示N/A
                self.value_label.setText("N/A")
                self.value_label.setStyleSheet("color: #a0a0a0; font-size: 18px; font-weight: bold;")
                # 设置灰色边框
                self.setStyleSheet(f"""
                    QFrame {{
                        background-color: #2d2d2d;
                        border: 2px solid #4d4d4d;
                        border-radius: 8px;
                    }}
                """)
                self._update_history_with_error()
            elif value == "Error":
                # 显示错误状态
                self.value_label.setText("Error")
                self.value_label.setStyleSheet("color: #ff5555; font-size: 18px; font-weight: bold;")
                # 设置红色边框
                self.setStyleSheet(f"""
                    QFrame {{
                        background-color: #2d2d2d;
                        border: 2px solid #ff5555;
                        border-radius: 8px;
                    }}
                """)
                self._update_history_with_error()
            else:
                # 尝试解析为数字
                try:
                    num_value = float(value.replace("%", ""))
                    self._update_percent_display(num_value, value)
                except ValueError:
                    # 显示原始字符串
                    self.value_label.setText(value)
                    self._update_history_with_error()
        else:
            # 未知类型，显示为字符串
            self.value_label.setText(str(value))
            self._update_history_with_error()
    
    def _smooth_data(self, data_points, window_size=3):
        """简单的移动平均平滑算法
        
        Args:
            data_points: 要平滑的数据点列表
            window_size: 移动窗口大小
            
        Returns:
            平滑后的数据点列表
        """
        if window_size < 2:
            return data_points
            
        result = []
        for i in range(len(data_points)):
            # 计算窗口的起始和结束位置
            start = max(0, i - window_size // 2)
            end = min(len(data_points), i + window_size // 2 + 1)
            # 计算窗口内的平均值
            window = data_points[start:end]
            result.append(sum(window) / len(window))
            
        return result
        
    def _update_percent_display(self, value_num, text):
        """更新百分比类型数据的显示"""
        self.value_label.setText(text)
        self.value_label.setStyleSheet("color: #e0e0e0; font-size: 18px; font-weight: bold;")
        
        # # 根据值设置边框颜色
        # border_color = "#00a8ff"  # 默认
        # if value_num >= 90:
        #     border_color = "#ff5555"  # 高负载时为红色
        # elif value_num >= 70:
        #     border_color = "#ffaa00"  # 中等负载时为黄色
        
        # 设置灰色边框
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2d2d2d;
                border: 2px solid #4d4d4d;
                border-radius: 8px;
            }}
        """)
        
        # 更新图表数据
        self._update_chart_data(value_num)
        
    def _update_temp_display(self, temp_value, text):
        """更新温度类型数据的显示"""
        self.value_label.setText(text)
        self.value_label.setStyleSheet("color: #e0e0e0; font-size: 18px; font-weight: bold;")
        
        # 根据温度值设置边框颜色
        border_color = "#10893E"  # 默认绿色
        if temp_value >= 80:
            border_color = "#ff5555"  # 高温为红色
        elif temp_value >= 60:
            border_color = "#ffaa00"  # 中等温度为黄色
        
        # 设置边框
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2d2d2d;
                border: 2px solid {border_color};
                border-radius: 8px;
            }}
        """)
        
        # 更新图表数据
        self._update_chart_data(temp_value)
        
    def _update_history_with_error(self):
        """处理图表历史记录，当出现错误或特殊状态时"""
        # 保持当前的图表状态不变，只添加一个零值点
        # 这样可以在图表上显示出有问题的时间段
        self.data_points.append(0)
        
        # 只保留最近的MAX_DATA_POINTS个数据点
        while len(self.data_points) > 60:  # 假设MAX_DATA_POINTS是60
            self.data_points.pop(0)
        
        # 更新图表
        self.series.clear()
        
        # 平滑数据点（简单平均）以使图表看起来更平滑
        smoothed_points = self._smooth_data(list(self.data_points), 3)
        
        for i, point in enumerate(smoothed_points):
            self.series.append(i, point)
            
    def _update_chart_data(self, value):
        """更新图表数据"""
        # 添加新数据点
        self.data_points.append(value)
        
        # 只保留最近的MAX_DATA_POINTS个数据点
        while len(self.data_points) > 60:  # 假设MAX_DATA_POINTS是60
            self.data_points.pop(0)
            
        # 更新图表数据
        self.series.clear()
        
        # 平滑数据点（简单平均）以使图表看起来更平滑
        smoothed_points = self._smooth_data(list(self.data_points), 3)
        
        for i, point in enumerate(smoothed_points):
            self.series.append(i, point)
            
        # 如果需要，调整Y轴范围
        max_value = max(self.data_points) if self.data_points else 0
        if max_value > 0:
            # 将上限设置为最大值的下一个25的倍数，并添加一点额外空间
            upper_limit = ((int(max_value) // 25) + 1) * 25
            self.axis_y.setRange(0, max(100, upper_limit))

class ActionTile(QFrame):
    """自定义样式的操作块小部件"""
    def __init__(self, title, description, icon_path=None, parent=None, color="#4285F4"):
        super().__init__(parent)
        self.setObjectName("actionTile")
        self.color = color
        
        self.setStyleSheet(f"""
            #actionTile {{
                background-color: #2d2d2d;
                border-radius: 12px;
                border: none;
            }}
            #actionTile:hover {{
                background-color: #353535;
                border-left: 4px solid {color};
            }}
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(Qt.PointingHandCursor)
        
        # 创建布局
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(18, 18, 18, 18)
        
        # 如果提供了图标路径且存在，则添加图标
        if icon_path and os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.icon_label = QLabel()
                    pixmap = icon.pixmap(QSize(42, 42))
                    if not pixmap.isNull():
                        self.icon_label.setPixmap(pixmap)
                        self.layout.addWidget(self.icon_label)
                    else:
                        self.logger.warning(f"Warning: Could not load pixmap for icon {icon_path}")  # 警告：无法加载图标像素图
                else:
                    self.logger.error(f"Warning: Could not load icon {icon_path}")  # 警告：无法加载图标
            except Exception as e:
                self.logger.error(f"Error loading icon {icon_path}: {str(e)}")  # 加载图标时出错
        
        # 文本容器
        self.text_container = QVBoxLayout()
        
        # 标题标签
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold; background-color: transparent;")
        
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("color: #a0a0a0; font-size: 13px; background-color: transparent;")
        self.desc_label.setWordWrap(True)
        
        self.text_container.addWidget(self.title_label)
        self.text_container.addWidget(self.desc_label)
        
        self.layout.addLayout(self.text_container, 1)  # 添加伸展因子
        
        # Fix arrow icon loading
        try:
            # Explicitly use the path from the Icon class
            arrow_icon_path = Icon.DownArrow.Path 
            if arrow_icon_path and os.path.exists(arrow_icon_path):
                arrow_icon = QIcon(arrow_icon_path)
                if not arrow_icon.isNull():
                    self.arrow_label = QLabel()
                    arrow_pixmap = arrow_icon.pixmap(QSize(18, 18))
                    if not arrow_pixmap.isNull():
                        self.arrow_label.setPixmap(arrow_pixmap)
                        self.layout.addWidget(self.arrow_label, 0, Qt.AlignRight)
        except Exception as e:
            self.logger.error(f"Error loading arrow icon: {str(e)}")

class DashboardWidget(BaseComponent):
    def __init__(self, parent=None):
        # 初始化属性
        self.update_timer = None
        
        # 调用父类构造函数
        super().__init__(parent)
        
        # 检查缺失翻译（仅在开发模式下）
        missing_keys = self.check_all_translations()
        if missing_keys:
            self.logger.warning(f"Warning: Missing translations in DashboardWidget:")  # 警告：DashboardWidget 中缺少翻译
            for language, keys in missing_keys.items():
                self.logger.warning(f"  Language: {language}, Missing keys: {', '.join(keys)}")  # 语言和缺少的键
        
        # 设置定时器以更新系统信息
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_system_info)
        self.update_timer.start(2000)
    
    def get_translation(self, key, default=None):
        return self.settings.get_translation("dashboard", key, default)
    
    def setup_ui(self):
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(25)
        
        # 仪表板标题和欢迎消息
        title_container = QHBoxLayout()
        
        # 仪表板标题
        self.title = QLabel(self.get_translation("system_status"))
        self.title.setStyleSheet("font-size: 28px; font-weight: bold; color: #e0e0e0; background-color: transparent;")
        title_container.addWidget(self.title)
        
        # 欢迎消息，右对齐
        self.welcome_label = QLabel(self.get_translation("welcome_message", "Welcome to Glary Utilities"))
        self.welcome_label.setStyleSheet("color: #a0a0a0; font-size: 16px; background-color: transparent;")
        self.welcome_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        title_container.addWidget(self.welcome_label)
        
        self.main_layout.addLayout(title_container)
        
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
        self.stats_layout.setSpacing(20)
        
        # CPU 使用情况图表
        cpu_icon_path = Icon.CPU.Path
        self.cpu_chart = ChartTile(
            self.get_translation("cpu_usage"), 
            cpu_icon_path if os.path.exists(cpu_icon_path) else Icon.CPU.Path,
            chart_color="#E74856"  # 红色，模拟Windows Task Manager CPU图表
        )
        self.stats_layout.addWidget(self.cpu_chart, 0, 0)
        
        # 内存使用情况图表
        memory_icon_path = Icon.Memory.Path
        self.memory_chart = ChartTile(
            self.get_translation("memory_usage"), 
            memory_icon_path if os.path.exists(memory_icon_path) else Icon.Memory.Path,
            chart_color="#00B7C3"  # 青色，模拟Windows Task Manager内存图表
        )
        self.stats_layout.addWidget(self.memory_chart, 0, 1)
        
        # 磁盘使用情况图表
        disk_icon_path = Icon.Disk.Path
        self.disk_chart = ChartTile(
            self.get_translation("disk_usage"), 
            disk_icon_path if os.path.exists(disk_icon_path) else Icon.Disk.Path,
            chart_color="#FFB900"  # 黄色，模拟Windows Task Manager磁盘图表
        )
        self.stats_layout.addWidget(self.disk_chart, 1, 0)
        
        # 温度图表
        temp_icon_path = Icon.Temperature.Path
        self.temp_chart = ChartTile(
            self.get_translation("system_temperature"), 
            temp_icon_path if os.path.exists(temp_icon_path) else Icon.Temperature.Path,
            chart_color="#10893E"  # 绿色，模拟Windows Task Manager温度图表
        )
        self.stats_layout.addWidget(self.temp_chart, 1, 1)
        
        # 将统计框架添加到主布局，并设置为可扩展
        self.main_layout.addWidget(self.stats_frame, 4)  # 图表部分占据更多空间
    
    def create_quick_access_section(self):
        # 快速访问标题
        self.quick_title = QLabel(self.get_translation("quick_access"))
        self.quick_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #e0e0e0; margin-top: 10px; background-color: transparent;")
        self.main_layout.addWidget(self.quick_title)
        
        # 快速访问容器
        self.quick_frame = QFrame()
        self.quick_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.quick_layout = QGridLayout(self.quick_frame)
        self.quick_layout.setContentsMargins(0, 0, 0, 0)
        self.quick_layout.setSpacing(20)
        
        # System Repair tile (Corrected)
        repair_icon_path = Icon.Repair.Path
        self.repair_tile = ActionTile(
            self.get_translation("system_repair"), # Use correct translation key
            self.get_translation("system_repair_desc"), # Use correct description key
            repair_icon_path if os.path.exists(repair_icon_path) else Icon.Repair.Path,
            color="#4285F4" # Keep color or adjust as needed
        )
        self.quick_layout.addWidget(self.repair_tile, 0, 0)
        
        # Clean Junk tile
        clean_icon_path = Icon.Clean.Path
        self.clean_tile = ActionTile(
            self.get_translation("clean_junk"),
            self.get_translation("clean_junk_desc", "Free up disk space by removing unnecessary files"),
            clean_icon_path if os.path.exists(clean_icon_path) else (None if not Icon.Clean.Exist else Icon.Clean.Path),
            color="#EA4335"  # Google Red
        )
        self.quick_layout.addWidget(self.clean_tile, 0, 1)
        
        # Virus Scan tile
        virus_icon_path = Icon.Virus.Path
        self.virus_tile = ActionTile(
            self.get_translation("scan_system"),
            self.get_translation("scan_system_desc", "Scan your system for viruses and malware"),
            virus_icon_path if os.path.exists(virus_icon_path) else (None if not Icon.Virus.Exist else Icon.Virus.Path),
            color="#FBBC05"  # Google Yellow
        )
        self.quick_layout.addWidget(self.virus_tile, 1, 0)
        
        # Get System Info tile
        info_icon_path = Icon.Info.Path
        self.info_tile = ActionTile(
            self.get_translation("get_system_info"),
            self.get_translation("get_system_info_desc", "Get system information"),
            info_icon_path if os.path.exists(info_icon_path) else (None if not Icon.Info.Exist else Icon.Info.Path),
            color="#34A853"  # Google Green
        )
        self.quick_layout.addWidget(self.info_tile, 1, 1)
        
        # Connect tiles to correct pages
        self.repair_tile.mousePressEvent = lambda event: self.navigate_to_page(3)  # System Tools
        self.clean_tile.mousePressEvent = lambda event: self.navigate_to_page(1)  # System Cleaner
        self.virus_tile.mousePressEvent = lambda event: self.navigate_to_page(5)  # Security Tools
        self.info_tile.mousePressEvent = lambda event: self.window().set_active_page("System Information") if self.window() else None

        self.main_layout.addWidget(self.quick_frame, 3)
    
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
            if self.platform_manager == 'Windows':
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
            self.logger.error(f"Error getting disk usage: {e}")  # 获取磁盘使用情况时出错
        
        # 温度检测 - 增强版
        self._update_temperature()
    
    def _update_temperature(self):
        """更新温度显示，使用 SystemInformation 来获取温度数据"""
        try:
            # 使用 SystemInformation 类的 get_temperature 方法获取温度
            temperature_data = self.system_information.get_temperature()
            
            # 检查是否处于重试延迟中
            if len(temperature_data) == 2 and "CPU" in temperature_data and "System" in temperature_data:
                if temperature_data["CPU"] == "N/A" and temperature_data["System"] == "N/A":
                    # 如果处于延迟重试状态，显示特殊状态指示
                    if self.system_information._temp_failure_count > 1:
                        # 计算下次尝试剩余时间
                        import time
                        time_elapsed = time.time() - self.system_information._temp_last_attempt
                        remaining = max(0, self.system_information._temp_retry_delay - time_elapsed)
                        
                        if remaining > 60:
                            # 如果剩余时间超过1分钟，显示分钟
                            self.temp_chart.update_value(f"Retry in {int(remaining/60)}m")
                        else:
                            # 否则显示秒数
                            self.temp_chart.update_value(f"Retry in {int(remaining)}s")
                        return
            
            # 如果有 CPU 温度，优先显示它
            if "CPU" in temperature_data:
                self.temp_chart.update_value(temperature_data["CPU"])
                return
            
            # 如果没有 CPU 温度，但有其他温度数据，显示第一个
            if temperature_data:
                first_temp = next(iter(temperature_data.values()))
                self.temp_chart.update_value(first_temp)
                return
                
            # 如果没有找到温度数据，显示 N/A
            self.temp_chart.update_value("N/A")
        except Exception as e:
            self.temp_chart.update_value("N/A")
            self.logger.error(f"Error getting temperature: {e}")  # 获取温度时出错
    
    def navigate_to_page(self, page_index):
        """在主窗口中导航到特定页面"""
        # 页面索引与页面名称的映射
        page_names = {
            0: "Dashboard",
            1: "System Cleaner",
            2: "System Tools",
            3: "Disk Tools",
            4: "Boot Tools",
            5: "Security Tools",
            6: "Network Tools",
            7: "DISM Tool",
            8: "System Information",
            9: "Settings"
        }
        
        # 查找主窗口以更改页面
        main_window = self.window()
        if main_window and page_index in page_names:
            main_window.set_active_page(page_names[page_index])

    def refresh_language(self):
        # 更新UI文本元素
        self.title.setText(self.get_translation("system_status"))
        self.welcome_label.setText(self.get_translation("welcome_message", "Welcome to Glary Utilities"))
        self.quick_title.setText(self.get_translation("quick_access"))
        
        # 更新图表标题
        self.cpu_chart.title_label.setText(self.get_translation("cpu_usage"))
        self.memory_chart.title_label.setText(self.get_translation("memory_usage"))
        self.disk_chart.title_label.setText(self.get_translation("disk_usage"))
        self.temp_chart.title_label.setText(self.get_translation("system_temperature"))
        
        # 更新操作块
        self.repair_tile.title_label.setText(self.get_translation("system_repair"))
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
            "clean_junk", "scan_system", "get_system_info", 
            "system_resources", "welcome_message"
        ]
        
        for key in keys:
            # 如果键不存在，将引发KeyError
            self.get_translation(key, None) 
            