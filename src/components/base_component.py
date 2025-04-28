from PyQt5.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QLabel, QCheckBox, QRadioButton, QButtonGroup
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from utils.animations import AnimationUtils
from utils.settings import Settings
from utils.theme_manager import ThemeManager
from utils.logger import Logger

class BaseComponent(QWidget):
    """Base component class for all application components"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.logger = Logger().get_logger()
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
                border: 2px solid {accent_color};
                border-radius: 3px;
                background-color: {bg_lighter};
            }}
            
            QCheckBox::indicator:unchecked {{
                background-color: {bg_lighter};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {accent_color};
            }}
            
            QCheckBox::indicator:unchecked:hover {{
                border-color: {button_hover};
                background-color: {self._lighten_color(bg_lighter, 5)};
            }}
            
            QCheckBox::indicator:checked:hover {{
                background-color: {button_hover};
            }}
            
            QRadioButton {{
                color: {text_color};
                spacing: 5px;
            }}
            
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {accent_color};
                border-radius: 8px;
                background-color: {bg_lighter};
            }}
            
            QRadioButton::indicator:unchecked {{
                background-color: {bg_lighter};
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {bg_lighter};
                width: 6px;
                height: 6px;
                border: 5px solid {accent_color};
            }}
            
            QRadioButton::indicator:unchecked:hover {{
                border-color: {button_hover};
            }}
            
            QRadioButton::indicator:checked:hover {{
                border-color: {button_hover};
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
    
    
    def update_checkbox_state(self, checkbox, state):
        """更新复选框状态并应用相关设置
        
        Args:
            checkbox (QCheckBox): 复选框对象
            state (Qt.CheckState): 复选框状态
        """
        # 获取复选框的对象名称，作为设置键
        setting_key = checkbox.objectName()
        
        # 将 Qt.CheckState 转换为布尔值
        is_checked = (state == Qt.Checked)
        
        # Debug output for troubleshooting
        self.logger.info(f"Checkbox state changed: {checkbox.text()} -> {is_checked}")
        
        # If setting_key is empty, try to use checkbox text as fallback
        if not setting_key and checkbox.text():
            # Create a valid setting key from checkbox text
            setting_key = f"checkbox_{checkbox.text().lower().replace(' ', '_')}"
            
        if setting_key:
            # 将状态保存到设置
            self.settings.set_setting(setting_key, is_checked)
            self.settings.sync()  # 确保立即保存设置
    
            
    def update_radiobutton_state(self, radio_button, checked):
        """更新单选按钮状态并应用相关设置"""
        if not checked:
            return  # 只处理选中状态，避免重复处理
            
        # 获取单选按钮的对象名称，作为设置键
        setting_key = radio_button.objectName()
        
        # Debug output
        self.logger.info.info(f"Radio button state changed: {radio_button.text()} -> {checked}")
        
        # If setting_key is empty, try to use radio button text as fallback
        if not setting_key and radio_button.text():
            # Create a valid setting key from radio button text
            setting_key = f"radio_{radio_button.text().lower().replace(' ', '_')}"
            
        if setting_key:
            # 将状态保存到设置 - 对于单选按钮，保存按钮文本作为值
            self.settings.set_setting(setting_key, radio_button.text())
            
    def update_buttongroup_selection(self, button_group, selected_button):
        """处理按钮组中的选择变化"""
        # 获取按钮组的对象名称，作为设置键
        setting_key = button_group.objectName()
        
        # Debug output
        self.logger.info.info(f"Button group selection changed: {setting_key} -> {selected_button.text()}")
        
        if setting_key:
            # 保存所选按钮的ID或文本
            button_id = button_group.id(selected_button)
            button_text = selected_button.text()
            button_obj_name = selected_button.objectName()
            
            # 保存按钮ID和文本
            self.settings.set_setting(f"{setting_key}_id", button_id)
            self.settings.set_setting(f"{setting_key}_text", button_text)
            if button_obj_name:
                self.settings.set_setting(f"{setting_key}_selected", button_obj_name) 