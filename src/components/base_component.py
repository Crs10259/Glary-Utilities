from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QPoint, Qt
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from animations import AnimationUtils

class BaseComponent(QWidget):
    """Base component class for all application components"""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        
        # 确保组件填充整个可用空间
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 初始化UI
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Setup component UI - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement setup_ui()")
    
    def apply_theme(self):
        """应用主题样式到组件"""
        # 确保组件背景透明
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # 获取当前主题
        theme = self.settings.get_setting("theme", "深色")
        
        # 根据主题名称获取相应的颜色
        if theme == "深色" or theme == "Dark":
            bg_color = "#1e1e1e"
            text_color = "#e0e0e0"
            accent_color = "#00a8ff"
        elif theme == "浅色" or theme == "Light":
            bg_color = "#f0f0f0"
            text_color = "#333333"
            accent_color = "#007acc"
        elif theme == "蓝色主题" or theme == "Blue Theme":
            bg_color = "#0d1117"
            text_color = "#e6edf3"
            accent_color = "#58a6ff"
        elif theme == "绿色主题" or theme == "Green Theme":
            bg_color = "#0f1610"
            text_color = "#e6edf3"
            accent_color = "#4caf50"
        elif theme == "紫色主题" or theme == "Purple Theme":
            bg_color = "#13111d"
            text_color = "#e6edf3"
            accent_color = "#9c27b0"
        elif theme == "自定义" or theme == "Custom":
            # 自定义主题使用用户定义的颜色
            bg_color = self.settings.get_setting("custom_bg_color", "#1e1e1e")
            text_color = self.settings.get_setting("custom_text_color", "#e0e0e0")
            accent_color = self.settings.get_setting("custom_accent_color", "#00a8ff")
        else:
            # 默认为深色主题
            bg_color = "#1e1e1e"
            text_color = "#e0e0e0"
            accent_color = "#00a8ff"
        
        # 生成辅助颜色
        bg_lighter = self._lighten_color(bg_color, 10)
        bg_darker = self._lighten_color(bg_color, -10)
        
        # 应用基础样式表
        self.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QPushButton {{
                background-color: {bg_lighter};
                color: {text_color};
                border: 1px solid {accent_color};
                border-radius: 6px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(bg_lighter, 10)};
                border: 1px solid {self._lighten_color(accent_color, 10)};
            }}
            QPushButton:pressed {{
                background-color: {self._lighten_color(bg_lighter, -5)};
            }}
            QPushButton:disabled {{
                background-color: {bg_darker};
                color: {self._lighten_color(bg_color, 30)};
                border: 1px solid {self._lighten_color(bg_color, 20)};
            }}
            QGroupBox {{
                color: {self._lighten_color(text_color, -10)};
                font-weight: bold;
                border: 1px solid {accent_color};
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 10px;
                background-color: {bg_color};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: {bg_color};
            }}
            QCheckBox, QRadioButton {{
                color: {text_color};
            }}
            QCheckBox::indicator, QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                background-color: {bg_lighter};
                border: 1px solid {accent_color};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                background-color: {accent_color};
            }}
            QLineEdit, QTextEdit, QListWidget, QTableWidget, QComboBox {{
                background-color: {bg_lighter};
                color: {text_color};
                border: 1px solid {accent_color};
                border-radius: 6px;
                padding: 3px;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border: 1px solid {self._lighten_color(accent_color, 15)};
            }}
            QTextEdit {{
                background-color: {bg_lighter};
                color: {text_color};
            }}
            QTableWidget {{
                background-color: {bg_lighter};
                alternate-background-color: {self._lighten_color(bg_lighter, 5)};
                gridline-color: {self._lighten_color(accent_color, -20)};
                border: 1px solid {accent_color};
                border-radius: 6px;
            }}
            QTableWidget QHeaderView::section {{
                background-color: {bg_darker};
                color: {text_color};
                border: 1px solid {accent_color};
                padding: 4px;
            }}
            QProgressBar {{
                border: 1px solid {accent_color};
                border-radius: 6px;
                background-color: {bg_lighter};
                text-align: center;
                color: {text_color};
            }}
            QProgressBar::chunk {{
                background-color: {accent_color};
                border-radius: 5px;
            }}
            QTabWidget::pane {{
                border: 1px solid {accent_color};
                background-color: {bg_color};
                border-radius: 6px;
            }}
            QTabBar::tab {{
                background-color: {bg_lighter};
                color: {self._lighten_color(text_color, -10)};
                border: 1px solid {accent_color};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 12px;
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QTabBar::tab:hover {{
                background-color: {self._lighten_color(bg_lighter, 10)};
            }}
            QScrollBar {{
                background-color: {bg_color};
                width: 12px;
                height: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle {{
                background-color: {self._lighten_color(bg_color, 30)};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:hover {{
                background-color: {accent_color};
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                width: 0px;
                height: 0px;
            }}
            QScrollBar::add-page, QScrollBar::sub-page {{
                background-color: {bg_color};
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
            from PyQt5.QtGui import QColor
            
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