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
        themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "themes")
        theme_file = os.path.join(themes_dir, f"{theme_name}.json")
        
        # If custom theme doesn't exist, try to load built-in theme
        # if not os.path.exists(theme_file):
        #     builtin_themes_dir = os.path.join(
        #         os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        #         "resources", "themes"
        #     )
        # builtin_theme_file = os.path.join(builtin_themes_dir, f"{theme_name}.json")
            
        #     if os.path.exists(builtin_theme_file):
        #         theme_file = builtin_theme_file
        #     else:
        #         return None
                
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading theme {theme_name}: {e}")
            return None
        
    def save_custom_theme(self, theme_data):
        """Save custom theme configuration"""
        themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "themes")
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
        themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "themes")
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
            设置值，如果是布尔值相关的设置会确保返回bool类型
        """
        value = self.settings.value(key, default_value)
        
        # 如果默认值是布尔类型，确保返回布尔值
        if isinstance(default_value, bool) or key.startswith(('enable_', 'show_', 'use_', 'is_')):
            if isinstance(value, str):
                return value.lower() in ('true', 'yes', '1', 'on')
            elif isinstance(value, int):
                return bool(value)
            return bool(value)
        
        return value
    
    def set_setting(self, key, value):
        """设置设置值
        
        Args:
            key (str): 设置键名
            value: 要设置的值
        """
        # 对于布尔值，确保存储为字符串 'true' 或 'false'
        if isinstance(value, bool):
            value = 'true' if value else 'false'
        
        self.settings.setValue(key, value)
    
    def sync(self):
        """同步设置到磁盘"""
        self.settings.sync()
    
    def reset_settings(self):
        """重置所有设置为默认值"""
        self.settings.clear()
        self.logger.info("All settings have been reset to default values")
        
        # 设置基本默认值
        self.set_setting("theme", "dark")
        self.set_setting("language", "English")
        self.set_setting("window_transparency", 100)
    
    def get_translation(self, section, key, default=None, language=None):
        """获取给定键的翻译文本"""
        # 使用缓存的语言设置，避免递归
        if not language:
            if not self._current_language:
                self._current_language = self.settings.value("language", "en")
            language = self._current_language
            
        # 处理语言代码映射
        language_map = {
            "en": "en",
            "english": "en",
            "zh": "zh",
            "中文": "zh",
            "chinese": "zh"
        }
        
        lang_code = language_map.get(language.lower(), language)
            
        # 如果语言不可用或者翻译字典为空，则创建一个默认结构
        if not self.translations or lang_code not in self.translations:
            # 尝试重新加载翻译
            self.load_translations()
            # 如果还是不存在，创建一个空的结构
            if lang_code not in self.translations:
                self.translations[lang_code] = {}
        
        # 检查section是否存在
        if section not in self.translations[lang_code]:
            self.translations[lang_code][section] = {}
        
        # 如果找不到翻译，则返回键或默认值
        if key not in self.translations[lang_code][section]:
            # 尝试在英语中查找作为回退
            if "en" in self.translations and section in self.translations["en"] and key in self.translations["en"][section]:
                return self.translations["en"][section][key]
            return default if default is not None else key
        
        return self.translations[lang_code][section][key]

    def set_language(self, language):
        """设置应用程序语言
        
        Args:
            language: 要设置的语言
        """
        self.set_setting("language", language)
        self._current_language = language  # 更新缓存的语言设置
        # 重新加载翻译
        self.load_translations()
        
    def set_current_language(self, language):
        """设置当前语言并重新加载翻译
        
        Args:
            language: 要设置的语言代码或名称
        """
        # 处理语言代码映射
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
        
        # 确保翻译已加载
        if not self.translations or lang_code not in self.translations:
            self.load_translations()
            
    def validate_translations(self, raise_error=False):
        """验证所有翻译是否存在
        
        Args:
            raise_error: 当发现缺失翻译时是否抛出异常
            
        Returns:
            dict: 按语言分组的缺失翻译映射，如果没有缺失则返回空字典
        """
        missing_translations = {}
        
        try:
            # 获取所有翻译键的列表
            # 这个方法不会使用get_translation，避免潜在的递归
            all_keys = {}
            
            # 收集所有语言中所有部分的所有键
            for language, sections in self.translations.items():
                if language not in all_keys:
                    all_keys[language] = {}
                    
                for section, keys in sections.items():
                    if section not in all_keys[language]:
                        all_keys[language][section] = set()
                    
                    for key in keys:
                        all_keys[language][section].add(key)
            
            # 检查每种语言的每个部分，确保每个键都存在
            for language, sections in all_keys.items():
                language_missing = {}
                
                for section, keys in sections.items():
                    section_missing = []
                    
                    # 在这个语言的这个部分检查每个键
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