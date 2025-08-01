from PyQt5.QtCore import QPropertyAnimation, QSequentialAnimationGroup, QParallelAnimationGroup
from PyQt5.QtCore import QEasingCurve, Qt, QSize, QPoint, QRect, QAbstractAnimation, QTimer
from utils.settings import Settings

class AnimationUtils:
    """Provide UI animation effect tools"""
    
    @classmethod
    def is_animations_enabled(cls):
        """Check if animations are enabled"""
        try:
            settings = Settings()
            # Explicitly convert the value to a boolean to avoid type issues
            # Default is True (enable animations)
            enabled = settings.get_setting("enable_animations", True)
            
            # String type conversion
            if isinstance(enabled, str):
                return enabled.lower() in ('true', 'yes', '1', 'on')
            # Integer type conversion
            elif isinstance(enabled, int):
                return enabled != 0
            # Directly handle as boolean
            elif isinstance(enabled, bool):
                return enabled
            # Other types return default value True
            return True
        except Exception as e:
            raise Exception(f"Error getting animation settings: {str(e)}")
    
    @classmethod
    def fade(cls, widget, duration=200, start=1.0, end=0.0, direction="out", callback=None):
        """Fade in and fade out animation
        
        Args:
            widget: The widget to animate
            duration: Duration (milliseconds)
            start: Start opacity
            end: End opacity
            direction: "in" fade in, "out" fade out, "inout" fade in then fade out
            callback: Callback function after animation is finished
        """
        # Check if animations are enabled
        if not cls.is_animations_enabled():
            # If animations are disabled, set the final effect and call the callback
            widget.setWindowOpacity(end)
            if callback:
                callback()
            return None
            
        # Stop the current animation that may be running
        if hasattr(widget, "_current_anim") and widget._current_anim is not None:
            try:
                widget._current_anim.stop()
                widget._current_anim = None
            except Exception:
                pass
                
        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(int(duration * 0.4))  # Further reduce animation time to make it feel faster
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.OutQuad)  # Use smooth easing curve
        
        if callback:
            anim.finished.connect(callback)
        
        # Save the current animation reference, so it can be stopped later
        widget._current_anim = anim
        
        anim.start(QAbstractAnimation.DeleteWhenStopped)
        return anim
    
    @classmethod
    def slide(cls, widget, duration=200, direction="left", distance=50, callback=None):
        """Slide animation
        
        Args:
            widget: The widget to animate
            duration: Duration (milliseconds)
            direction: "left", "right", "up", "down"
            distance: Slide distance (pixels)
            callback: Callback function after animation is finished
        """
        # Check if animations are enabled
        if not cls.is_animations_enabled():
            # If animations are disabled, set the final position and call the callback
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
        """Highlight widget, usually used to indicate changes"""
        if not widget:
            return
            
        # Create color animation
        color_anim = QPropertyAnimation(widget, b"styleSheet")
        color_anim.setDuration(duration // 2)  # Fade in time
        
        # Get current style
        current_style = widget.styleSheet()
        
        # Create highlight style
        highlight_style = current_style + f"background-color: {color};"
        
        # Set animation
        color_anim.setStartValue(current_style)
        color_anim.setEndValue(highlight_style)
        color_anim.setEasingCurve(QEasingCurve.OutQuad)
        
        # If fade out effect is needed
        if fade_out:
            fade_anim = QPropertyAnimation(widget, b"styleSheet")
            fade_anim.setDuration(duration // 2)  # Fade out time
            fade_anim.setStartValue(highlight_style)
            fade_anim.setEndValue(current_style)
            fade_anim.setEasingCurve(QEasingCurve.OutQuad)
            
            # Create sequence animation group
            sequence = QSequentialAnimationGroup()
            sequence.addAnimation(color_anim)
            sequence.addAnimation(fade_anim)
            sequence.start(QAbstractAnimation.DeleteWhenStopped)
        else:
            color_anim.start(QAbstractAnimation.DeleteWhenStopped)
    
    @classmethod
    def pulse(cls, widget, duration=1000, scale=1.05):
        """Pulse animation
        
        Args:
            widget: The widget to animate
            duration: Duration (milliseconds)
            scale: Scale ratio
        """
        # Check if animations are enabled
        if not cls.is_animations_enabled():
            return None
            
        orig_geo = widget.geometry()
        
        # Calculate enlarged geometry
        center_x = orig_geo.x() + orig_geo.width() / 2
        center_y = orig_geo.y() + orig_geo.height() / 2
        scaled_width = orig_geo.width() * scale
        scaled_height = orig_geo.height() * scale
        scaled_x = center_x - scaled_width / 2
        scaled_y = center_y - scaled_height / 2
        scaled_geo = QRect(int(scaled_x), int(scaled_y), int(scaled_width), int(scaled_height))
        
        # Create geometry animation
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
        """Button highlight animation"""
        # Check if animations are enabled
        if not cls.is_animations_enabled():
            return None
            
        # Save original style
        orig_style = button.styleSheet()
        
        # Color animation
        anim = QPropertyAnimation(button, b"styleSheet")
        anim.setDuration(duration)
        
        # Extract background color
        bg_color = "#5cb85c"  # Default is green
        for style in orig_style.split(";"):
            if "background-color" in style:
                try:
                    bg_color = style.split(":")[1].strip()
                except:
                    pass
        
        # Set animation keyframes
        highlight_style = f"background-color: {bg_color}; color: white; border: 2px solid white;"
        anim.setStartValue(highlight_style)
        anim.setKeyValueAt(0.5, orig_style)
        anim.setEndValue(orig_style)
        
        # Create scale animation
        scale_anim = QPropertyAnimation(button, b"geometry")
        scale_anim.setDuration(duration)
        orig_geo = button.geometry()
        scale_anim.setKeyValueAt(0, orig_geo)
        scale_anim.setKeyValueAt(0.3, orig_geo.adjusted(-3, -2, 3, 2))  # Reduce scale amplitude
        scale_anim.setKeyValueAt(0.6, orig_geo.adjusted(1, 1, -1, -1))
        scale_anim.setEndValue(orig_geo)
        
        # Create animation group
        group = QParallelAnimationGroup()
        group.addAnimation(anim)
        group.addAnimation(scale_anim)
        
        # Restore style after completion
        def restore_style():
            button.setStyleSheet(orig_style)
        
        group.finished.connect(restore_style)
        group.start(QAbstractAnimation.DeleteWhenStopped)
        return group
    
    @classmethod
    def page_transition(cls, old_page, new_page, duration=200, direction="left"):
        """Page transition animation
        
        Args:
            old_page: Current page
            new_page: New page
            duration: Duration (milliseconds)
            direction: "left", "right"
        """
        # Check if animations are enabled
        if not cls.is_animations_enabled():
            # If animations are disabled, switch pages immediately
            new_page.show()
            old_page.hide()
            # Restore position to ensure correct display
            new_page.move(old_page.pos())
            return None

        # Prevent rapid consecutive switching causing interface disappearance
        # If any page has _transition_preventing_timer property and is active,
        # skip animation and switch immediately
        for page in [old_page, new_page]:
            if hasattr(page, "_transition_preventing_timer") and page._transition_preventing_timer:
                # Switch immediately, without animation
                new_page.move(old_page.pos())
                new_page.show()
                old_page.hide()
                return None

        # If the old page is animating, stop it
        if hasattr(old_page, "_transition_anim") and old_page._transition_anim is not None:
            try:
                old_page._transition_anim.stop()
                old_page._transition_anim = None
            except Exception:
                pass
        
        # If the new page is animating, stop it
        if hasattr(new_page, "_transition_anim") and new_page._transition_anim is not None:
            try:
                new_page._transition_anim.stop()
                new_page._transition_anim = None
            except Exception:
                pass
            
        # Optimize animation performance - faster animation
        duration = int(duration * 0.15)  # Significantly reduce animation time, making switching faster
        
        # Ensure new page is visible
        new_page.show()
        
        # Get page width
        width = old_page.width()
        
        # Set new page initial position
        old_pos = old_page.pos()
        if direction == "left":
            new_page.move(old_pos.x() + width, old_pos.y())
        else:
            new_page.move(old_pos.x() - width, old_pos.y())
        
        # Create animation group
        anim_group = QParallelAnimationGroup()
        
        # Old page animation
        old_anim = QPropertyAnimation(old_page, b"pos")
        old_anim.setDuration(duration)
        old_anim.setStartValue(old_pos)
        if direction == "left":
            old_anim.setEndValue(old_pos - QPoint(width, 0))
        else:
            old_anim.setEndValue(old_pos + QPoint(width, 0))
        old_anim.setEasingCurve(QEasingCurve.OutQuad)  # More smooth easing curve
        
        # New page animation
        new_anim = QPropertyAnimation(new_page, b"pos")
        new_anim.setDuration(duration)
        if direction == "left":
            new_anim.setStartValue(old_pos + QPoint(width, 0))
        else:
            new_anim.setStartValue(old_pos - QPoint(width, 0))
        new_anim.setEndValue(old_pos)
        new_anim.setEasingCurve(QEasingCurve.OutQuad)  # More smooth easing curve
        
        # Add to animation group
        anim_group.addAnimation(old_anim)
        anim_group.addAnimation(new_anim)
        
        # Save animation reference
        old_page._transition_anim = anim_group
        new_page._transition_anim = anim_group
        
        # Clean up and prevent rapid switching after completion
        def on_finished():
            # Hide old page
            old_page.hide()
            
            # Clear animation reference
            old_page._transition_anim = None
            new_page._transition_anim = None
            
            # Ensure new page is in the correct position
            new_page.move(old_pos)
            
            # Set a short debounce timer to prevent rapid switching
            for page in [old_page, new_page]:
                page._transition_preventing_timer = True
                # Allow new switch animation after 100ms
                QTimer.singleShot(100, lambda p=page: cls._reset_transition_timer(p))
        
        anim_group.finished.connect(on_finished)
        anim_group.start(QAbstractAnimation.DeleteWhenStopped)
        return anim_group
        
    @classmethod
    def _reset_transition_timer(cls, page):
        """Reset page switch debounce timer"""
        if hasattr(page, "_transition_preventing_timer"):
            page._transition_preventing_timer = False

    @classmethod
    def text_flow(cls, label, duration=800):
        """Text flow animation"""
        anim = QPropertyAnimation(label, b"pos")
        anim.setEasingCurve(QEasingCurve.InOutSine)
        anim.setDuration(duration)
        start_pos = label.pos()
        anim.setKeyValueAt(0, start_pos)
        anim.setKeyValueAt(0.5, start_pos + QPoint(10, 0))  # Reduce displacement
        anim.setKeyValueAt(1, start_pos)
        anim.setLoopCount(1)  # Reduce loop count
        anim.start()

    @classmethod
    def fade_in(cls, widget, duration=200, callback=None):
        """Fade in animation
        
        Args:
            widget: The widget to animate
            duration: Duration (milliseconds)
            callback: Callback function after animation is finished
        """
        # Mark component as animating
        widget._animating_in = True
        
        # If there is a fade out animation in progress, stop it
        if hasattr(widget, "_fade_out_anim") and widget._fade_out_anim is not None:
            try:
                widget._fade_out_anim.stop()
                widget._fade_out_anim = None
            except Exception:
                pass
        
        # Create fade in animation
        anim = cls.fade(widget, duration, 0.0, 1.0, "in", callback=lambda: cls._on_fade_in_finished(widget, callback))
        
        # Save animation reference
        widget._fade_in_anim = anim
        return anim

    @classmethod
    def _on_fade_in_finished(cls, widget, callback=None):
        """Fade in animation completed processing"""
        # Remove animation marker
        widget._animating_in = False
        widget._fade_in_anim = None
        
        if callback:
            callback()

    @classmethod
    def fade_out(cls, widget, duration=200, finished_callback=None):
        """Fade out animation
        
        Args:
            widget: The widget to animate
            duration: Duration (milliseconds)
            finished_callback: Callback function after animation is finished
        """
        # Mark component as animating
        widget._animating_out = True
        
        # If there is a fade in animation in progress, stop it
        if hasattr(widget, "_fade_in_anim") and widget._fade_in_anim is not None:
            try:
                widget._fade_in_anim.stop()
                widget._fade_in_anim = None
            except Exception:
                pass
        
        # Create fade out animation
        anim = cls.fade(widget, duration, 1.0, 0.0, "out", callback=lambda: cls._on_fade_out_finished(widget, finished_callback))
        
        # Save animation reference
        widget._fade_out_anim = anim
        return anim

    @classmethod
    def _on_fade_out_finished(cls, widget, callback=None):
        """Fade out animation completed processing"""
        # Remove animation marker
        widget._animating_out = False
        widget._fade_out_anim = None
        
        if callback:
            callback() 