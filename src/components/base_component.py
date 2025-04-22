from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QPoint, Qt
import sys
import os
import json
from PyQt5.QtGui import QColor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.animations import AnimationUtils
from utils.settings_manager import Settings
from utils.theme_manager import ThemeManager

class BaseComponent(QWidget):
    """Base component class for all application components"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.theme_manager = ThemeManager()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.apply_theme()
        
        # 确保组件填充整个可用空间
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 初始化UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup component UI - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement setup_ui()")
    
    def apply_theme(self):
        """应用主题样式到组件"""
        # 确保组件背景透明
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # 获取当前主题
        theme_name = self.settings.get_setting("theme", "dark")
        
        # 确保主题管理器使用同样的主题
        self.theme_manager.set_current_theme(theme_name)
        
        # 获取主题颜色
        colors = self.theme_manager.get_theme_colors()
        
        # 获取基本颜色
        bg_color = colors.get("bg_color", "#1e1e1e")
        text_color = colors.get("text_color", "#e0e0e0")
        accent_color = colors.get("accent_color", "#555555")
        bg_lighter = colors.get("bg_lighter", self.theme_manager.lighten_color(bg_color, 10))
        bg_darker = colors.get("bg_darker", self.theme_manager.lighten_color(bg_color, -10))
        
        # 获取组件特定颜色
        button_colors = self.theme_manager.get_component_colors("button")
        button_bg = button_colors.get("primary_bg", accent_color)
        button_text = button_colors.get("primary_text", "#ffffff")
        button_hover = button_colors.get("primary_hover", self.theme_manager.lighten_color(accent_color, 10))
        button_pressed = button_colors.get("primary_pressed", self.theme_manager.lighten_color(accent_color, -10))
        
        # 应用基本样式
        self.setStyleSheet(f"""
            BaseComponent {{
                /* 使用透明背景，防止出现蓝色叠加 */
                background-color: transparent;
                color: {text_color};
                border-radius: 8px;
            }}
            
            QLabel {{
                color: {text_color};
                border: none;
                background-color: transparent;
            }}
            
            QPushButton {{
                background-color: {button_bg};
                color: {button_text};
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {button_hover};
            }}
            
            QPushButton:pressed {{
                background-color: {button_pressed};
            }}
            
            QLineEdit, QTextEdit {{
                background-color: {bg_lighter};
                color: {text_color};
                border: 1px solid {accent_color};
                border-radius: 4px;
                padding: 4px;
            }}
            
            QComboBox {{
                background-color: {bg_lighter};
                color: {text_color};
                border: 1px solid {accent_color};
                border-radius: 4px;
                padding: 4px;
                min-height: 20px;
            }}
            
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                border: none;
                width: 20px;
                height: 20px;
                image: url(resources/images/down_arrow.png);
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {accent_color};
                selection-background-color: {bg_lighter};
            }}
            
            QProgressBar {{
                border: 1px solid {accent_color};
                border-radius: 5px;
                background-color: {bg_darker};
                text-align: center;
                color: {text_color};
            }}
            
            QProgressBar::chunk {{
                background-color: {accent_color};
                border-radius: 4px;
            }}
            
            QCheckBox {{
                color: {text_color};
                spacing: 5px;
            }}
            
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {accent_color};
                border-radius: 3px;
                background-color: {bg_lighter};
            }}
            
            QCheckBox::indicator:checked {{
                image: url(resources/images/checkbox_checked.png);
            }}
        """)
    
    def _lighten_color(self, color, amount=20):
        """调亮或调暗十六进制颜色
        
        Args:
            color: 十六进制颜色代码 (如 "#1e1e1e")
            amount: 亮度调整量 (-100到100)
        
        Returns:
            新的十六进制颜色代码
        """
        try:
            c = QColor(color)
            h, s, l, a = c.getHslF()
            
            # 调整亮度
            l = max(0, min(1, l + amount / 100.0))
            
            c.setHslF(h, s, l, a)
            return c.name()
        except:
            return color
    
    def refresh_language(self):
        """Refresh all text elements after language change"""
        # Default implementation does animation to indicate refresh
        # Subclasses should override this to properly update text elements
        self._animate_refresh()
    
    def _animate_refresh(self):
        """Animate the component to indicate refresh"""
        AnimationUtils.highlight(self)
    
    def show_with_animation(self):
        """Show the component with animation"""
        self.setVisible(True)
        AnimationUtils.fade_in(self)
    
    def hide_with_animation(self, on_complete=None):
        """Hide the component with animation"""
        AnimationUtils.fade_out(self, finished_callback=lambda: self._handle_hide_complete(on_complete))
    
    def _handle_hide_complete(self, callback=None):
        """Handle hide animation completion"""
        self.setVisible(False)
        if callback:
            callback()
    
    def get_translation(self, key, default=None):
        """Get translation for the current component
        
        Args:
            key: Translation key
            default: Default text if translation not found
        
        Returns:
            Translated text
            
        Raises:
            KeyError: If the translation key is missing and no default is provided
        """
        # Get component name from class name
        component_name = self.__class__.__name__.lower()
        if component_name.endswith('widget'):
            component_name = component_name[:-6]  # Remove 'widget' suffix
        
        try:
            # Components should correspond to sections in the translation files
            return self.settings.get_translation(component_name, key, default)
        except KeyError as e:
            # Re-raise with component context for easier debugging
            raise KeyError(f"Missing translation key in component {component_name}: {str(e)}") from e
    
    def check_all_translations(self):
        """Check if all translation keys are available for this component
        
        Returns:
            A list of missing translation keys
        """
        # Get component name from class name
        component_name = self.__class__.__name__.lower()
        if component_name.endswith('widget'):
            component_name = component_name[:-6]  # Remove 'widget' suffix
        
        # Get all languages
        languages = list(self.settings.translations.keys())
        
        # Collect all keys used by this component
        used_keys = set()
        # First, get all available keys in all languages
        for language in languages:
            lang_translations = self.settings.translations.get(language, {})
            section_translations = lang_translations.get(component_name, {})
            used_keys.update(section_translations.keys())
        
        # Check missing keys for each language
        missing_keys = {}
        for language in languages:
            lang_translations = self.settings.translations.get(language, {})
            section_translations = lang_translations.get(component_name, {})
            
            # Find keys missing in this language
            missing_in_language = []
            for key in used_keys:
                if key not in section_translations:
                    missing_in_language.append(key)
            
            if missing_in_language:
                missing_keys[language] = missing_in_language
        
        return missing_keys
    
    def getComponentName(self):
        """Get component name for identification"""
        return self.__class__.__name__ 