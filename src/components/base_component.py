from PyQt5.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QLabel, QCheckBox, QRadioButton, QButtonGroup
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QPoint, Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QFont
from src.utils.animations import AnimationUtils
from src.utils.settings import Settings
from src.utils.theme_manager import ThemeManager
from src.utils.logger import Logger
from src.tools.base_tools import PlatformManager
from src.tools.base_tools import SystemInformation

class BaseComponent(QWidget):
    """Base component class for all application components"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.logger = Logger().get_logger()
        self.theme_manager = ThemeManager()
        self.platform_manager = PlatformManager()
        self.system_information = SystemInformation()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.apply_theme()
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setup_ui()

    def setup_ui(self):
        """Setup component UI - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement setup_ui()")
    
    def apply_theme(self):
        """Apply theme styles to component"""
        self.setAttribute(Qt.WA_StyledBackground, True)
        theme_name = self.settings.get_setting("theme", "dark")
        self.theme_manager.set_current_theme(theme_name)
        colors = self.theme_manager.get_theme_colors()
        
        # Get basic colors
        bg_color = colors.get("bg_color", "#1e1e1e")
        text_color = colors.get("text_color", "#e0e0e0")
        accent_color = colors.get("accent_color", "#555555")
        bg_lighter = colors.get("bg_lighter", self.theme_manager.lighten_color(bg_color, 10))
        bg_darker = colors.get("bg_darker", self.theme_manager.lighten_color(bg_color, -10))
        
        # Get component specific colors
        button_colors = self.theme_manager.get_component_colors("button")
        button_bg = button_colors.get("primary_bg", accent_color)
        button_text = button_colors.get("primary_text", "#ffffff")
        button_hover = button_colors.get("primary_hover", self.theme_manager.lighten_color(accent_color, 10))
        button_pressed = button_colors.get("primary_pressed", self.theme_manager.lighten_color(accent_color, -10))
        
        # Apply basic styles
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
        """Lighten or darken hex color
        
        Args:
            color: Hex color code (e.g. "#1e1e1e")
            amount: Brightness adjustment (-100 to 100)
        
        Returns:
            New hex color code
        """
        try:
            c = QColor(color)
            h, s, l, a = c.getHslF()
            
            # Adjust brightness
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
        # If component is already animating in, do nothing
        if hasattr(self, "_animating_in") and self._animating_in:
            return
        
        # Stop any ongoing fade out animation
        if hasattr(self, "_animating_out") and self._animating_out:
            if hasattr(self, "_fade_out_anim") and self._fade_out_anim is not None:
                self._fade_out_anim.stop()
                self._fade_out_anim = None
            self._animating_out = False
        
        # Ensure component is visible but transparent
        self.setWindowOpacity(0.0)
        self.setVisible(True)
        
        # Start fade in animation
        AnimationUtils.fade_in(self)
        
        # Safety check: Ensure component is visible even if animation fails
        QTimer.singleShot(500, self._ensure_visibility)

    def _ensure_visibility(self):
        """Ensure component is visible to prevent animation issues"""
        if self.isVisible() and self.windowOpacity() < 0.5:
            # If component should be visible but opacity is too low, force to fully opaque
            self.setWindowOpacity(1.0)
            if hasattr(self, "_animating_in"):
                self._animating_in = False
            if hasattr(self, "_fade_in_anim") and self._fade_in_anim is not None:
                try:
                    self._fade_in_anim.stop()
                    self._fade_in_anim = None
                except:
                    pass

    def hide_with_animation(self, on_complete=None):
        """Hide the component with animation"""
        # If component is already animating out, do nothing
        if hasattr(self, "_animating_out") and self._animating_out:
            # If there's a new callback, connect it to the existing animation
            if on_complete and hasattr(self, "_fade_out_anim") and self._fade_out_anim is not None:
                # Add additional callback
                original_callback = getattr(self._fade_out_anim, "finished_callback", None)
                def combined_callback():
                    if original_callback:
                        original_callback()
                    on_complete()
                self._fade_out_anim.finished.disconnect()
                self._fade_out_anim.finished.connect(combined_callback)
            return
        
        # Stop any ongoing fade in animation
        if hasattr(self, "_animating_in") and self._animating_in:
            if hasattr(self, "_fade_in_anim") and self._fade_in_anim is not None:
                self._fade_in_anim.stop()
                self._fade_in_anim = None
            self._animating_in = False
        
        # Start fade out animation
        AnimationUtils.fade_out(self, finished_callback=lambda: self._handle_hide_complete(on_complete))

    def _handle_hide_complete(self, callback=None):
        """Handle hide animation completion"""
        # Ensure component is transparent and hidden
        self.setWindowOpacity(0.0)
        self.setVisible(False)
        
        # Clear animation state
        self._animating_out = False
        if hasattr(self, "_fade_out_anim"):
            self._fade_out_anim = None
        
        # Execute callback
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
        """Update checkbox state and apply related settings
        
        Args:
            checkbox (QCheckBox): Checkbox object
            state (Qt.CheckState): Checkbox state
        """
        # Get checkbox object name as setting key
        setting_key = checkbox.objectName()
        
        # Convert Qt.CheckState to boolean
        is_checked = (state == Qt.Checked)
        
        # Debug output for troubleshooting
        self.logger.info(f"Checkbox state changed: {checkbox.text()} -> {is_checked}")
        
        # If setting_key is empty, try to use checkbox text as fallback
        if not setting_key and checkbox.text():
            # Create a valid setting key from checkbox text
            setting_key = f"checkbox_{checkbox.text().lower().replace(' ', '_')}"
            
        if setting_key:
            # Save state to settings
            self.settings.set_setting(setting_key, is_checked)
            self.settings.sync()  # Ensure settings are saved immediately
    
            
    def update_radiobutton_state(self, radio_button, checked):
        """Update radio button state and apply related settings"""
        if not checked:
            return  # Only handle checked state to avoid duplicate processing
            
        # Get radio button object name as setting key
        setting_key = radio_button.objectName()
        
        # Debug output
        self.logger.info.info(f"Radio button state changed: {radio_button.text()} -> {checked}")
        
        # If setting_key is empty, try to use radio button text as fallback
        if not setting_key and radio_button.text():
            # Create a valid setting key from radio button text
            setting_key = f"radio_{radio_button.text().lower().replace(' ', '_')}"
            
        if setting_key:
            # Save state to settings - for radio buttons, save button text as value
            self.settings.set_setting(setting_key, radio_button.text())
            
    def update_buttongroup_selection(self, button_group, selected_button):
        """Handle selection changes in button group"""
        # Get button group object name as setting key
        setting_key = button_group.objectName()
        
        # Debug output
        self.logger.info.info(f"Button group selection changed: {setting_key} -> {selected_button.text()}")
        
        if setting_key:
            # Save selected button ID or text
            button_id = button_group.id(selected_button)
            button_text = selected_button.text()
            button_obj_name = selected_button.objectName()
            
            # Save button ID and text
            self.settings.set_setting(f"{setting_key}_id", button_id)
            self.settings.set_setting(f"{setting_key}_text", button_text)
            if button_obj_name:
                self.settings.set_setting(f"{setting_key}_selected", button_obj_name) 