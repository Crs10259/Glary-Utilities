from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect, QGraphicsColorizeEffect
from PyQt5.QtCore import QPropertyAnimation, QSequentialAnimationGroup, QParallelAnimationGroup
from PyQt5.QtCore import QEasingCurve, Qt, QSize, QPoint, QRect, QAbstractAnimation
from PyQt5.QtGui import QColor

class AnimationUtils:
    """提供UI动画效果的工具类"""
    
    @classmethod
    def fade(cls, widget, duration=300, start=1.0, end=0.0, direction="out", callback=None):
        """淡入淡出动画
        
        Args:
            widget: 要动画的部件
            duration: 持续时间(毫秒)
            start: 开始不透明度
            end: 结束不透明度
            direction: "in" 淡入, "out" 淡出, "inout" 淡入后淡出
            callback: 动画完成后的回调函数
        """
        # 创建不透明度效果
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        if direction == "inout":
            # 创建序列动画组
            anim_group = QSequentialAnimationGroup()
            
            # 淡出
            fade_out = QPropertyAnimation(effect, b"opacity")
            fade_out.setDuration(duration // 2)
            fade_out.setStartValue(start)
            fade_out.setEndValue(end)
            fade_out.setEasingCurve(QEasingCurve.OutQuad)
            
            # 淡入
            fade_in = QPropertyAnimation(effect, b"opacity")
            fade_in.setDuration(duration // 2)
            fade_in.setStartValue(end)
            fade_in.setEndValue(start)
            fade_in.setEasingCurve(QEasingCurve.InQuad)
            
            anim_group.addAnimation(fade_out)
            anim_group.addAnimation(fade_in)
            
            if callback:
                fade_out.finished.connect(callback)
            
            anim_group.start(QAbstractAnimation.DeleteWhenStopped)
            return anim_group
        else:
            # 创建单个动画
            fade_anim = QPropertyAnimation(effect, b"opacity")
            fade_anim.setDuration(duration)
            fade_anim.setStartValue(start if direction == "out" else end)
            fade_anim.setEndValue(end if direction == "out" else start)
            fade_anim.setEasingCurve(QEasingCurve.OutQuad if direction == "out" else QEasingCurve.InQuad)
            
            if callback:
                fade_anim.finished.connect(callback)
            
            fade_anim.start(QAbstractAnimation.DeleteWhenStopped)
            return fade_anim
    
    @classmethod
    def slide(cls, widget, duration=300, direction="left", distance=50, callback=None):
        """滑动动画
        
        Args:
            widget: 要动画的部件
            duration: 持续时间(毫秒)
            direction: "left", "right", "up", "down"
            distance: 滑动距离(像素)
            callback: 动画完成后的回调函数
        """
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
    def highlight(cls, widget, duration=800, color="#00a8ff"):
        """高亮动画
        
        Args:
            widget: 要动画的部件
            duration: 持续时间(毫秒)
            color: 高亮颜色
        """
        effect = QGraphicsColorizeEffect(widget)
        widget.setGraphicsEffect(effect)
        
        highlight_color = QColor(color)
        highlight_color.setAlphaF(0.3)  # 设置透明度
        
        # 创建颜色动画
        color_anim = QPropertyAnimation(effect, b"color")
        color_anim.setDuration(duration)
        color_anim.setStartValue(highlight_color)
        color_anim.setEndValue(QColor(0, 0, 0, 0))  # 完全透明
        color_anim.setEasingCurve(QEasingCurve.OutQuad)
        
        color_anim.start(QAbstractAnimation.DeleteWhenStopped)
        return color_anim
    
    @classmethod
    def pulse(cls, widget, duration=1000, scale=1.05):
        """脉冲动画
        
        Args:
            widget: 要动画的部件
            duration: 持续时间(毫秒)
            scale: 缩放比例
        """
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
    def highlight_button(cls, button, duration=800):
        """按钮高亮动画"""
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
        scale_anim.setKeyValueAt(0.3, orig_geo.adjusted(-5, -3, 5, 3))
        scale_anim.setKeyValueAt(0.6, orig_geo.adjusted(2, 1, -2, -1))
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
    def page_transition(cls, old_page, new_page, duration=400, direction="left"):
        """页面过渡动画
        
        Args:
            old_page: 当前页面
            new_page: 新页面
            duration: 持续时间(毫秒)
            direction: "left", "right"
        """
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
        old_anim.setEasingCurve(QEasingCurve.OutQuad)
        
        # 新页面动画
        new_anim = QPropertyAnimation(new_page, b"pos")
        new_anim.setDuration(duration)
        if direction == "left":
            new_anim.setStartValue(old_pos + QPoint(width, 0))
        else:
            new_anim.setStartValue(old_pos - QPoint(width, 0))
        new_anim.setEndValue(old_pos)
        new_anim.setEasingCurve(QEasingCurve.OutQuad)
        
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
    def text_flow(cls, label, duration=1200):
        """文字流动动画"""
        anim = QPropertyAnimation(label, b"pos")
        anim.setEasingCurve(QEasingCurve.InOutSine)
        anim.setDuration(duration)
        start_pos = label.pos()
        anim.setKeyValueAt(0, start_pos)
        anim.setKeyValueAt(0.5, start_pos + QPoint(20, 0))
        anim.setKeyValueAt(1, start_pos)
        anim.setLoopCount(2)
        anim.start() 