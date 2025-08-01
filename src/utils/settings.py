import os
import json
import platform
from PyQt5.QtCore import QObject, QSettings
from config import Path
from .logger import Logger

class Settings(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger().get_logger()
        self.settings = QSettings("GlaryUtilities", "GlaryUtilities")
        self.translations = {}

        # Determine default language from system locale if user hasn't set one
        import locale
        if self.settings.value("language", None) is None:
            sys_locale = locale.getdefaultlocale()[0] or "en"
            default_lang = "zh" if sys_locale.lower().startswith("zh") else "en"
            self.settings.setValue("language", default_lang)
            self.logger.info(f"Language not set – defaulting to system locale: {default_lang}")

        self._current_language = self.settings.value("language", "en")  # cache current language
        self.load_translations()
        
    def load_translations(self):
        """Load all available translations"""

        # Ensure directory exists
        if not os.path.exists(Path.TRANSLATIONS_DIR):
            os.makedirs(Path.TRANSLATIONS_DIR)
        
        # Language code mapping
        language_mapping = {
            "en.json": "en",    # English
            "zh.json": "zh"     # Chinese
        }
        
        # Clear existing translations
        self.translations = {
            "en": {},  # Default English translations
            "zh": {}   # Default Chinese translations
        }
        
        for file in os.listdir(Path.TRANSLATIONS_DIR):
            if file.endswith(".json"):
                lang_code = language_mapping.get(file, file.split(".")[0])
                try:
                    with open(os.path.join(Path.TRANSLATIONS_DIR, file), 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                except Exception as e:
                    self.logger.error(f"Error loading translation {file}: {e}")
    
    def get_config_dir(self):
        """Get configuration directory path"""
        if platform.system() == "Windows":
            return os.path.join(os.environ.get("APPDATA"), "GlaryUtilities")
        elif platform.system() == "Darwin":  # macOS
            return os.path.join(os.path.expanduser("~/Library/Application Support"), "GlaryUtilities")
        else:  # Linux and others
            return os.path.join(os.path.expanduser("~/.config"), "GlaryUtilities")
            
    def load_theme(self, theme_name):
        """Load configuration data for specified theme
        
        Args:
            theme_name (str): Theme name
            
        Returns:
            dict: Theme configuration data, returns None if theme doesn't exist
        """
        # Theme file path - first check user custom theme
        themes_dir = Path.THEMES_DIR
        theme_file = os.path.join(themes_dir, f"{theme_name}.json")
                     
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading theme {theme_name}: {e}")
            return None
        
    def save_custom_theme(self, theme_data):
        """Save custom theme configuration"""
        themes_dir = Path.THEMES_DIR
        theme_file = os.path.join(themes_dir, "custom.json")
        
        # Ensure directory exists
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)
        
        # Ensure theme data contains required fields
        if not theme_data.get("name"):
            theme_data["name"] = "custom"
        if not theme_data.get("display_name"):
            theme_data["display_name"] = {"en": "Custom", "zh": "Custom"}
        
        # Save theme file
        try:
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error saving custom theme: {e}")
            return False

    def get_available_themes(self):
        """Get all available themes"""
        themes_dir = Path.THEMES_DIR
        themes = []
        
        # Ensure directory exists
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)
            return themes
        
        # Load all theme files
        for file in os.listdir(themes_dir):
            if file.endswith(".json"):
                theme_name = file.split(".")[0]
                theme_data = self.load_theme(theme_name)
                if theme_data:
                    display_name = "Unknown"
                    if "display_name" in theme_data:
                        # Get display name in current language
                        current_lang = self.get_setting("language", "en")
                        if current_lang.lower() in ["中文", "chinese", "zh"]:
                            display_name = theme_data["display_name"].get("zh", theme_name)
                        else:
                            display_name = theme_data["display_name"].get("en", theme_name)
                    elif "name" in theme_data:
                        display_name = theme_data["name"]
                    
                    themes.append({
                        "id": theme_name,
                        "name": display_name
                    })
        
        return themes
    
    def get_setting(self, key, default_value=None):
        """Get setting value with default fallback
        
        Args:
            key (str): Setting key name
            default_value: Default value
        
        Returns:
            Setting value, if the setting is related to boolean values, it will ensure to return bool type
        """
        value = self.settings.value(key, default_value)
        
        # If the default value is a boolean type, ensure to return boolean value
        if isinstance(default_value, bool) or key.startswith(('enable_', 'show_', 'use_', 'is_')):
            if isinstance(value, str):
                return value.lower() in ('true', 'yes', '1', 'on')
            elif isinstance(value, int):
                return bool(value)
            return bool(value)
        
        return value
    
    def set_setting(self, key, value):
        """Set setting value
        
        Args:
            key (str): Setting key name
            value: Value to set
        """
        # For boolean values, ensure to store as string 'true' or 'false'
        if isinstance(value, bool):
            value = 'true' if value else 'false'
        
        self.settings.setValue(key, value)
    
    def sync(self):
        """Sync settings to disk"""
        self.settings.sync()
    
    def reset_settings(self):
        """Reset all settings to default values"""
        self.settings.clear()
        self.logger.info("All settings have been reset to default values")
        
        # Set basic default values
        self.set_setting("theme", "dark")
        self.set_setting("language", "English")
        self.set_setting("window_transparency", 100)
    
    def get_translation(self, section, key, default=None, language=None):
        """Get translation text for given key"""
        # Use cached language setting to avoid recursion
        if not language:
            if not self._current_language:
                self._current_language = self.settings.value("language", "en")
            language = self._current_language
            
        # Process language code mapping
        language_map = {
            "en": "en",
            "english": "en",
            "zh": "zh",
            "中文": "zh",
            "chinese": "zh"
        }
        
        lang_code = language_map.get(language.lower(), language)
            
        # If language is not available or translation dictionary is empty, create a default structure
        if not self.translations or lang_code not in self.translations:
            # Try to reload translations
            self.load_translations()
            # If still not exists, create an empty structure
            if lang_code not in self.translations:
                self.translations[lang_code] = {}
        
        # Check if section exists
        if section not in self.translations[lang_code]:
            self.translations[lang_code][section] = {}
        
        # If translation is not found, return key or default value
        if key not in self.translations[lang_code][section]:
            # Try to find in English as fallback
            if "en" in self.translations and section in self.translations["en"] and key in self.translations["en"][section]:
                return self.translations["en"][section][key]
            return default if default is not None else key
        
        return self.translations[lang_code][section][key]

    def set_language(self, language):
        """Set application language
        
        Args:
            language: Language to set
        """
        self.set_setting("language", language)
        self._current_language = language  # Update cached language setting
        # Reload translations
        self.load_translations()
        
    def set_current_language(self, language):
        """Set current language and reload translations
        
        Args:
            language: Language code or name to set
        """
        # Process language code mapping
        language_map = {
            "en": "en",
            "english": "en",
            "English": "en",
            "zh": "zh",
            "中文": "zh",
            "chinese": "zh",
            "Chinese": "zh"
        }
        
        lang_code = language_map.get(language.lower(), language)
        self.set_setting("language", language)
        
        # Ensure translations are loaded
        if not self.translations or lang_code not in self.translations:
            self.load_translations()
            
    def validate_translations(self, raise_error=False):
        """Validate all translations exist
        
        Args:
            raise_error: Whether to raise an exception when missing translations are found
            
        Returns:
            dict: Missing translations grouped by language, returns empty dictionary if no missing translations
        """
        missing_translations = {}
        
        try:
            # Get list of all translation keys
            # This method does not use get_translation to avoid potential recursion
            all_keys = {}
            
            # Collect all keys in all sections for all languages
            for language, sections in self.translations.items():
                if language not in all_keys:
                    all_keys[language] = {}
                    
                for section, keys in sections.items():
                    if section not in all_keys[language]:
                        all_keys[language][section] = set()
                    
                    for key in keys:
                        all_keys[language][section].add(key)
            
            # Check each language's each section, ensure each key exists
            for language, sections in all_keys.items():
                language_missing = {}
                
                for section, keys in sections.items():
                    section_missing = []
                    
                    # Check each key in this language's this section
                    for key in keys:
                        if section not in self.translations[language] or key not in self.translations[language][section]:
                            section_missing.append(key)
                    
                    if section_missing:
                        language_missing[section] = section_missing
                
                if language_missing:
                    missing_translations[language] = language_missing
            
            if missing_translations and raise_error:
                raise ValueError("Missing translations detected")
            
            return missing_translations
        except Exception as e:
            self.logger.error(f"Error validating translations: {e}")
            if raise_error:
                raise
            return {}