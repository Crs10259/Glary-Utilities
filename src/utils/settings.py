import os
import json
import platform
from PyQt5.QtCore import QObject, QSettings
from .exception_handler import SettingsError, TranslationError

class Settings(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("GlaryUtilities", "GlaryUtilities")
        self.translations = {}
        self.load_translations()
        
    def load_translations(self):
        """加载所有可用的翻译"""
        translations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "translations")
        
        # 确保目录存在
        if not os.path.exists(translations_dir):
            os.makedirs(translations_dir)
        
        # 加载所有翻译文件
        for file in os.listdir(translations_dir):
            if file.endswith(".json"):
                lang_code = file.split(".")[0]
                try:
                    with open(os.path.join(translations_dir, file), 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                except Exception as e:
                    print(f"Error loading translation {file}: {e}")
    
    def load_theme(self, theme_name):
        """加载指定主题的配置"""
        themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "themes")
        theme_file = os.path.join(themes_dir, f"{theme_name}.json")
        
        # 确保目录存在
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)
        
        # 尝试加载主题文件
        try:
            if os.path.exists(theme_file):
                with open(theme_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Theme file not found: {theme_file}")
                return None
        except Exception as e:
            print(f"Error loading theme {theme_name}: {e}")
            return None
        
    def save_custom_theme(self, theme_data):
        """保存自定义主题配置"""
        themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "themes")
        theme_file = os.path.join(themes_dir, "custom.json")
        
        # 确保目录存在
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)
        
        # 确保主题数据包含必要字段
        if not theme_data.get("name"):
            theme_data["name"] = "custom"
        if not theme_data.get("display_name"):
            theme_data["display_name"] = {"en": "Custom", "zh": "自定义"}
        
        # 保存主题文件
        try:
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving custom theme: {e}")
            return False

    def get_available_themes(self):
        """获取所有可用的主题"""
        themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "themes")
        themes = []
        
        # 确保目录存在
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)
            return themes
        
        # 加载所有主题文件
        for file in os.listdir(themes_dir):
            if file.endswith(".json"):
                theme_name = file.split(".")[0]
                theme_data = self.load_theme(theme_name)
                if theme_data:
                    display_name = "Unknown"
                    if "display_name" in theme_data:
                        # 获取当前语言的显示名称
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
        """获取设置值，带默认回退"""
        return self.settings.value(key, default_value)
    
    def set_setting(self, key, value):
        """设置设置值"""
        self.settings.setValue(key, value)
        self.settings.sync()
    
    def reset_settings(self):
        """重置所有设置为默认值"""
        self.settings.clear()
        self.settings.sync()
        print("所有设置已重置为默认值")
        
        # 设置基本默认值
        self.set_setting("theme", "dark")
        self.set_setting("language", "English")
        self.set_setting("window_transparency", 100)
    
    def get_translation(self, section, key, language=None):
        """获取给定键的翻译文本"""
        if not language:
            language = self.get_setting("language", "en")
            
        # 如果语言不可用，则回退到英语
        if language not in self.translations:
            language = "en"
            
        # 如果找不到翻译，则返回键
        if section not in self.translations[language] or key not in self.translations[language][section]:
            # 尝试在英语中查找作为回退
            if section in self.translations["en"] and key in self.translations["en"][section]:
                return self.translations["en"][section][key]
            return key
            
        return self.translations[language][section][key]