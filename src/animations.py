from PyQt5.QtCore import (QPropertyAnimation, QParallelAnimationGroup, QSequentialAnimationGroup,
                        QEasingCurve, QPoint, QSize, Qt, QTimer, QRect)
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QWidget
from PyQt5.QtGui import QColor

class AnimationUtils:
    """Utility class for common animations in the application"""
    
    @staticmethod
    def fade_in(widget, duration=300, finished_callback=None):
        """Create and start a fade-in animation for a widget
        
        Args:
            widget: The widget to animate
            duration: Animation duration in milliseconds
            finished_callback: Function to call when animation finishes
        """
        # Create opacity effect
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        # Create animation
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        
        if finished_callback:
            anim.finished.connect(finished_callback)
        
        # Start animation
        anim.start()
        
        return anim
    
    @staticmethod
    def fade_out(widget, duration=300, finished_callback=None):
        """Create and start a fade-out animation for a widget
        
        Args:
            widget: The widget to animate
            duration: Animation duration in milliseconds
            finished_callback: Function to call when animation finishes
        """
        # Create opacity effect
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        effect.setOpacity(1.0)
        
        # Create animation
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        
        if finished_callback:
            anim.finished.connect(finished_callback)
        
        # Start animation
        anim.start()
        
        return anim
    
    @staticmethod
    def slide_in_from_right(widget, duration=300, distance=100, finished_callback=None):
        """Create and start a slide-in animation from the right
        
        Args:
            widget: The widget to animate
            duration: Animation duration in milliseconds
            distance: Distance to slide in pixels
            finished_callback: Function to call when animation finishes
        """
        # Save original position
        original_pos = widget.pos()
        
        # Set starting position (off to the right)
        widget.move(original_pos.x() + distance, original_pos.y())
        
        # Create animation
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(widget.pos())
        anim.setEndValue(original_pos)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        
        if finished_callback:
            anim.finished.connect(finished_callback)
        
        # Start animation
        anim.start()
        
        return anim
    
    @staticmethod
    def slide_in_from_left(widget, duration=300, distance=100, finished_callback=None):
        """Create and start a slide-in animation from the left
        
        Args:
            widget: The widget to animate
            duration: Animation duration in milliseconds
            distance: Distance to slide in pixels
            finished_callback: Function to call when animation finishes
        """
        # Save original position
        original_pos = widget.pos()
        
        # Set starting position (off to the left)
        widget.move(original_pos.x() - distance, original_pos.y())
        
        # Create animation
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(widget.pos())
        anim.setEndValue(original_pos)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        
        if finished_callback:
            anim.finished.connect(finished_callback)
        
        # Start animation
        anim.start()
        
        return anim
    
    @staticmethod
    def slide_out_to_left(widget, duration=300, distance=100, finished_callback=None):
        """Create and start a slide-out animation to the left
        
        Args:
            widget: The widget to animate
            duration: Animation duration in milliseconds
            distance: Distance to slide in pixels
            finished_callback: Function to call when animation finishes
        """
        # Save original position
        original_pos = widget.pos()
        
        # Create animation
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(original_pos)
        anim.setEndValue(QPoint(original_pos.x() - distance, original_pos.y()))
        anim.setEasingCurve(QEasingCurve.OutCubic)
        
        if finished_callback:
            anim.finished.connect(finished_callback)
        
        # Start animation
        anim.start()
        
        return anim
    
    @staticmethod
    def slide_out_to_right(widget, duration=300, distance=100, finished_callback=None):
        """Create and start a slide-out animation to the right
        
        Args:
            widget: The widget to animate
            duration: Animation duration in milliseconds
            distance: Distance to slide in pixels
            finished_callback: Function to call when animation finishes
        """
        # Save original position
        original_pos = widget.pos()
        
        # Create animation
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(original_pos)
        anim.setEndValue(QPoint(original_pos.x() + distance, original_pos.y()))
        anim.setEasingCurve(QEasingCurve.OutCubic)
        
        if finished_callback:
            anim.finished.connect(finished_callback)
        
        # Start animation
        anim.start()
        
        return anim
    
    @staticmethod
    def pulse(widget, duration=300, scale_factor=1.05, finished_callback=None):
        """Create and start a pulse animation (grow and shrink)
        
        Args:
            widget: The widget to animate
            duration: Animation duration in milliseconds
            scale_factor: Maximum scale factor
            finished_callback: Function to call when animation finishes
        """
        # Original size
        original_size = widget.size()
        
        # Target size
        target_size = QSize(int(original_size.width() * scale_factor), 
                            int(original_size.height() * scale_factor))
        
        # Create animation group
        group = QSequentialAnimationGroup()
        
        # Scale up
        anim1 = QPropertyAnimation(widget, b"size")
        anim1.setDuration(duration // 2)
        anim1.setStartValue(original_size)
        anim1.setEndValue(target_size)
        anim1.setEasingCurve(QEasingCurve.OutQuad)
        group.addAnimation(anim1)
        
        # Scale down
        anim2 = QPropertyAnimation(widget, b"size")
        anim2.setDuration(duration // 2)
        anim2.setStartValue(target_size)
        anim2.setEndValue(original_size)
        anim2.setEasingCurve(QEasingCurve.InQuad)
        group.addAnimation(anim2)
        
        if finished_callback:
            group.finished.connect(finished_callback)
        
        # Start animation
        group.start()
        
        return group
    
    @staticmethod
    def highlight(widget, color=QColor(255, 255, 0, 100), duration=500, finished_callback=None):
        """Temporarily highlight a widget with a color overlay
        
        Args:
            widget: The widget to animate
            color: The highlight color (with alpha)
            duration: Animation duration in milliseconds
            finished_callback: Function to call when animation finishes
        """
        # Original stylesheet
        original_stylesheet = widget.styleSheet()
        
        # Apply highlight
        widget.setStyleSheet(f"{original_stylesheet}; background-color: {color.name(QColor.HexArgb)};")
        
        # Create timer to restore original
        timer = QTimer()
        timer.setSingleShot(True)
        timer.setInterval(duration)
        
        def restore_style():
            widget.setStyleSheet(original_stylesheet)
            if finished_callback:
                finished_callback()
        
        timer.timeout.connect(restore_style)
        timer.start()
        
        return timer
    
    @staticmethod
    def slide_view_transition(old_widget, new_widget, direction="left", duration=300, finished_callback=None):
        """Create a slide transition between two widgets
        
        Args:
            old_widget: The widget being replaced
            new_widget: The widget being shown
            direction: Direction of transition ("left", "right")
            duration: Animation duration in milliseconds
            finished_callback: Function to call when animation finishes
        """
        if direction == "left":
            # Old widget slides out to left, new widget slides in from right
            old_anim = AnimationUtils.slide_out_to_left(old_widget, duration)
            new_anim = AnimationUtils.slide_in_from_right(new_widget, duration)
        else:  # right
            # Old widget slides out to right, new widget slides in from left
            old_anim = AnimationUtils.slide_out_to_right(old_widget, duration)
            new_anim = AnimationUtils.slide_in_from_left(new_widget, duration)
            
        # Create animation group
        group = QParallelAnimationGroup()
        group.addAnimation(old_anim)
        group.addAnimation(new_anim)
        
        if finished_callback:
            group.finished.connect(finished_callback)
        
        # Start animation
        group.start()
        
        return group 