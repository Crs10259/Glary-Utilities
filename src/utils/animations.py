from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect, QGraphicsColorizeEffect
from PyQt5.QtCore import QPropertyAnimation, QSequentialAnimationGroup, QParallelAnimationGroup
from PyQt5.QtCore import QEasingCurve, Qt, QSize, QPoint, QRect, QAbstractAnimation
from PyQt5.QtGui import QColor
from utils.settings import Settings

class AnimationUtils:
    """提供UI动画效果的工具类"""
    
    @classmethod
    def is_animations_enabled(cls):
        """检查是否启用动画效果"""
        try:
            settings = Settings()
            # 明确将值转换为布尔值，避免可能的类型问题
            # 默认为 True (启用动画)
            enabled = settings.get_setting("enable_animations", True)
            
            # 字符串类型转换
            if isinstance(enabled, str):
                return enabled.lower() in ('true', 'yes', '1', 'on')
            # 整数类型转换
            elif isinstance(enabled, int):
                return enabled != 0
            # 直接作为布尔值处理
            elif isinstance(enabled, bool):
                return enabled
            # 其他类型返回默认值True
            return True
        except Exception as e:
            raise Exception(f"获取动画设置时出错: {str(e)}")
    
    @classmethod
    def fade(cls, widget, duration=200, start=1.0, end=0.0, direction="out", callback=None):
        """淡入淡出动画
        
        Args:
            widget: 要动画的部件
            duration: 持续时间(毫秒)
            start: 开始不透明度
            end: 结束不透明度
            direction: "in" 淡入, "out" 淡出, "inout" 淡入后淡出
            callback: 动画完成后的回调函数
        """
        # 检查是否启用动画
        if not cls.is_animations_enabled():
            # 如果动画禁用，直接设置最终效果并调用回调
            widget.setWindowOpacity(end)
            if callback:
                callback()
            return None
            
        # 先停止当前可能正在运行的动画
        if hasattr(widget, "_current_anim") and widget._current_anim is not None:
            try:
                widget._current_anim.stop()
                widget._current_anim = None
            except Exception:
                pass
                
        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(int(duration * 0.6))  # 进一步减少动画时间以使其感觉更快速
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.OutQuint)  # 使用更平滑的缓动曲线
        
        if callback:
            anim.finished.connect(callback)
        
        # 保存当前动画引用，以便后续可以停止
        widget._current_anim = anim
        
        anim.start(QAbstractAnimation.DeleteWhenStopped)
        return anim
    
    @classmethod
    def slide(cls, widget, duration=200, direction="left", distance=50, callback=None):
        """滑动动画
        
        Args:
            widget: 要动画的部件
            duration: 持续时间(毫秒)
            direction: "left", "right", "up", "down"
            distance: 滑动距离(像素)
            callback: 动画完成后的回调函数
        """
        # 检查是否启用动画
        if not cls.is_animations_enabled():
            # 如果动画禁用，直接设置最终位置并调用回调
            start_pos = widget.pos()
            end_pos = None
            if direction == "left":
                end_pos = start_pos - QPoint(distance, 0)
            elif direction == "right":
                end_pos = start_pos + QPoint(distance, 0)
            elif direction == "up":
                end_pos = start_pos - QPoint(0, distance)
            elif direction == "down":
                end_pos = start_pos + QPoint(0, distance)
            widget.move(end_pos)
            if callback:
                callback()
            return None
            
        start_pos = widget.pos()
        end_pos = None
        
        if direction == "left":
            end_pos = start_pos - QPoint(distance, 0)
        elif direction == "right":
            end_pos = start_pos + QPoint(distance, 0)
        elif direction == "up":
            end_pos = start_pos - QPoint(0, distance)
        elif direction == "down":
            end_pos = start_pos + QPoint(0, distance)
        
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(start_pos)
        anim.setEndValue(end_pos)
        anim.setEasingCurve(QEasingCurve.OutQuad)
        
        if callback:
            anim.finished.connect(callback)
        
        anim.start(QAbstractAnimation.DeleteWhenStopped)
        return anim
    
    @classmethod
    def highlight(cls, widget, duration=250, color="#3498db", fade_out=True):
        """突出显示widget，通常用于指示更改"""
        if not widget:
            return
            
        # 创建颜色动画
        color_anim = QPropertyAnimation(widget, b"styleSheet")
        color_anim.setDuration(duration // 2)  # 淡入时间
        
        # 获取当前样式
        current_style = widget.styleSheet()
        
        # 创建高亮样式
        highlight_style = current_style + f"background-color: {color};"
        
        # 设置动画
        color_anim.setStartValue(current_style)
        color_anim.setEndValue(highlight_style)
        color_anim.setEasingCurve(QEasingCurve.OutQuad)
        
        # 如果需要淡出效果
        if fade_out:
            fade_anim = QPropertyAnimation(widget, b"styleSheet")
            fade_anim.setDuration(duration // 2)  # 淡出时间
            fade_anim.setStartValue(highlight_style)
            fade_anim.setEndValue(current_style)
            fade_anim.setEasingCurve(QEasingCurve.OutQuad)
            
            # 创建序列动画组
            sequence = QSequentialAnimationGroup()
            sequence.addAnimation(color_anim)
            sequence.addAnimation(fade_anim)
            sequence.start(QAbstractAnimation.DeleteWhenStopped)
        else:
            color_anim.start(QAbstractAnimation.DeleteWhenStopped)
    
    @classmethod
    def pulse(cls, widget, duration=1000, scale=1.05):
        """脉冲动画
        
        Args:
            widget: 要动画的部件
            duration: 持续时间(毫秒)
            scale: 缩放比例
        """
        # 检查是否启用动画
        if not cls.is_animations_enabled():
            return None
            
        orig_geo = widget.geometry()
        
        # 计算放大的几何形状
        center_x = orig_geo.x() + orig_geo.width() / 2
        center_y = orig_geo.y() + orig_geo.height() / 2
        scaled_width = orig_geo.width() * scale
        scaled_height = orig_geo.height() * scale
        scaled_x = center_x - scaled_width / 2
        scaled_y = center_y - scaled_height / 2
        scaled_geo = QRect(int(scaled_x), int(scaled_y), int(scaled_width), int(scaled_height))
        
        # 创建几何动画
        anim = QPropertyAnimation(widget, b"geometry")
        anim.setDuration(duration)
        anim.setStartValue(orig_geo)
        anim.setKeyValueAt(0.5, scaled_geo)
        anim.setEndValue(orig_geo)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        anim.start(QAbstractAnimation.DeleteWhenStopped)
        return anim
    
    @classmethod
    def highlight_button(cls, button, duration=400):
        """按钮高亮动画"""
        # 检查是否启用动画
        if not cls.is_animations_enabled():
            return None
            
        # 保存原始样式
        orig_style = button.styleSheet()
        
        # 颜色动画
        anim = QPropertyAnimation(button, b"styleSheet")
        anim.setDuration(duration)
        
        # 提取背景色
        bg_color = "#5cb85c"  # 默认为绿色
        for style in orig_style.split(";"):
            if "background-color" in style:
                try:
                    bg_color = style.split(":")[1].strip()
                except:
                    pass
        
        # 设置动画关键帧
        highlight_style = f"background-color: {bg_color}; color: white; border: 2px solid white;"
        anim.setStartValue(highlight_style)
        anim.setKeyValueAt(0.5, orig_style)
        anim.setEndValue(orig_style)
        
        # 创建缩放动画
        scale_anim = QPropertyAnimation(button, b"geometry")
        scale_anim.setDuration(duration)
        orig_geo = button.geometry()
        scale_anim.setKeyValueAt(0, orig_geo)
        scale_anim.setKeyValueAt(0.3, orig_geo.adjusted(-3, -2, 3, 2))  # 减小缩放幅度
        scale_anim.setKeyValueAt(0.6, orig_geo.adjusted(1, 1, -1, -1))
        scale_anim.setEndValue(orig_geo)
        
        # 创建动画组
        group = QParallelAnimationGroup()
        group.addAnimation(anim)
        group.addAnimation(scale_anim)
        
        # 完成后恢复样式
        def restore_style():
            button.setStyleSheet(orig_style)
        
        group.finished.connect(restore_style)
        group.start(QAbstractAnimation.DeleteWhenStopped)
        return group
    
    @classmethod
    def page_transition(cls, old_page, new_page, duration=200, direction="left"):
        """页面过渡动画
        
        Args:
            old_page: 当前页面
            new_page: 新页面
            duration: 持续时间(毫秒)
            direction: "left", "right"
        """
        # 检查是否启用动画
        if not cls.is_animations_enabled():
            # 如果动画禁用，直接切换页面
            new_page.show()
            old_page.hide()
            # 恢复位置确保正确显示
            new_page.move(old_page.pos())
            return None
            
        # 优化动画性能 - 更快的动画
        duration = int(duration * 0.5)  # 进一步减少动画时间
        
        # 确保新页面可见
        new_page.show()
        
        # 获取页面宽度
        width = old_page.width()
        
        # 设置新页面初始位置
        old_pos = old_page.pos()
        if direction == "left":
            new_page.move(old_pos.x() + width, old_pos.y())
        else:
            new_page.move(old_pos.x() - width, old_pos.y())
        
        # 创建动画组
        anim_group = QParallelAnimationGroup()
        
        # 旧页面动画
        old_anim = QPropertyAnimation(old_page, b"pos")
        old_anim.setDuration(duration)
        old_anim.setStartValue(old_pos)
        if direction == "left":
            old_anim.setEndValue(old_pos - QPoint(width, 0))
        else:
            old_anim.setEndValue(old_pos + QPoint(width, 0))
        old_anim.setEasingCurve(QEasingCurve.OutQuart)  # 更快的缓动曲线
        
        # 新页面动画
        new_anim = QPropertyAnimation(new_page, b"pos")
        new_anim.setDuration(duration)
        if direction == "left":
            new_anim.setStartValue(old_pos + QPoint(width, 0))
        else:
            new_anim.setStartValue(old_pos - QPoint(width, 0))
        new_anim.setEndValue(old_pos)
        new_anim.setEasingCurve(QEasingCurve.OutQuart)  # 更快的缓动曲线
        
        # 添加到动画组
        anim_group.addAnimation(old_anim)
        anim_group.addAnimation(new_anim)
        
        # 完成后隐藏旧页面
        def on_finished():
            old_page.hide()
        
        anim_group.finished.connect(on_finished)
        anim_group.start(QAbstractAnimation.DeleteWhenStopped)
        return anim_group

    @classmethod
    def text_flow(cls, label, duration=800):
        """文字流动动画"""
        anim = QPropertyAnimation(label, b"pos")
        anim.setEasingCurve(QEasingCurve.InOutSine)
        anim.setDuration(duration)
        start_pos = label.pos()
        anim.setKeyValueAt(0, start_pos)
        anim.setKeyValueAt(0.5, start_pos + QPoint(10, 0))  # 减小位移
        anim.setKeyValueAt(1, start_pos)
        anim.setLoopCount(1)  # 减少循环次数
        anim.start() 