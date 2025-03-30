from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QPoint
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from animations import AnimationUtils

class BaseComponent(QWidget):
    """Base component class for all application components"""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setup_ui()
    
    def setup_ui(self):
        """Setup component UI - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement setup_ui()")
    
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