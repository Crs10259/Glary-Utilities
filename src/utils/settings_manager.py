import os
import json
import shutil
import platform
import psutil
import socket
import uuid
import subprocess

class Settings:
    """
    Settings manager class that stores settings in a JSON file
    """
    def __init__(self, app_name="Glary-Utilities"):
        self.app_name = app_name
        self.settings = {}
        self.translations = {}
        self.current_language = "English"
        
        # Create config directory if it doesn't exist
        self.config_dir = self._get_config_dir()
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Settings file path
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        
        # Load settings
        self.load_settings()
        
        # Load translations
        self.load_translations()
    
    def _get_config_dir(self):
        """Get the configuration directory for the application"""
        if os.name == 'nt':  # Windows
            appdata = os.environ.get('APPDATA')
            if appdata:
                return os.path.join(appdata, self.app_name)
            else:
                return os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', self.app_name)
        else:  # Unix/Linux/Mac
            config_home = os.environ.get('XDG_CONFIG_HOME')
            if config_home:
                return os.path.join(config_home, self.app_name)
            else:
                return os.path.join(os.path.expanduser('~'), '.config', self.app_name)
    
    def load_settings(self):
        """Load settings from the settings file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                
                # Set current language
                self.current_language = self.get_setting("language", "English")
            else:
                # Default settings
                self.settings = self.get_default_settings()
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            # If there's an error, use default settings
            self.settings = self.get_default_settings()
    
    def save_settings(self):
        """Save settings to the settings file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_default_settings(self):
        """Get default settings for the application"""
        return {
            "language": "English",
            "theme": "dark",
            "custom_theme_name": "My Custom Theme",
            "custom_bg_color": "#1e1e1e",
            "custom_text_color": "#e0e0e0",
            "custom_accent_color": "#00a8ff",
            "accent_color": "Blue",
            "font_family": "System Default",
            "font_size": 10,
            "icon_size": 24,
            "start_minimized": False,
            "start_with_windows": False,
            "check_updates": True,
            "minimize_to_tray": True,
            "show_notifications": True,
            "default_tab": "Dashboard",
            "clean_temp": True,
            "clean_recycle": True,
            "clean_browser": True,
            "clean_prefetch": True,
            "clean_logs": False,
            "disk_check_readonly": True,
            "scan_archives": True,
            "scan_rootkits": True,
            "scan_autofix": False,
            "scan_level": 2,
            "backup_before_repair": True,
            "backup_location": os.path.join(os.environ.get('USERPROFILE', ''), "GlaryBackups"),
            "enable_logging": True,
            "log_level": "Info",
            "log_retention": 30,
            "use_multithreading": True,
            "max_threads": 4
        }
    
    def get_setting(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set_setting(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        if key == "language":
            self.current_language = value
            # Reload translations
            self.load_translations()
    
    def load_translations(self):
        """Load translations from language files"""
        try:
            # Clear existing translations
            self.translations = {}
            
            # List of supported languages
            languages = ["English", "中文"]
            
            # Map language names to file names
            language_files = {
                "English": "en.json",
                "中文": "zh.json"
            }
            
            # Base directory for translations
            base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "translations")
            
            # Load translations for all supported languages
            for language in languages:
                file_name = language_files.get(language)
                if file_name:
                    file_path = os.path.join(base_dir, file_name)
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            self.translations[language] = json.load(f)
        except Exception as e:
            print(f"Error loading translations: {e}")
    
    def get_translation(self, section, key, default=None):
        """Get a translation for the current language
        
        Args:
            section: Translation section
            key: Translation key
            default: Default value if translation not found
            
        Returns:
            Translated text
            
        Raises:
            KeyError: If translation key is missing and no default provided
        """
        # Get translations for the current language
        lang_translations = self.translations.get(self.current_language, {})
        
        # Get the translation for the section and key
        section_translations = lang_translations.get(section, {})
        translation = section_translations.get(key)
        
        if translation:
            return translation
        
        # If not found, try English
        if self.current_language != "English":
            eng_translations = self.translations.get("English", {})
            section_translations = eng_translations.get(section, {})
            translation = section_translations.get(key)
            
            if translation:
                return translation
        
        # If still not found and no default is provided, raise KeyError
        if default is None:
            # Only print an error in console instead of raising exception if debugging
            if self.get_setting("debug_mode", False):
                print(f"Missing translation key: '{section}.{key}'")
                return key
            else:
                raise KeyError(f"Missing translation: '{section}.{key}'")
        
        # Return the default
        return default
    
    def check_missing_translations(self):
        """Check for missing translations across all components
        
        Returns:
            A dictionary of missing translations by language and section
        """
        missing = {}
        
        # Get all sections and keys from all languages
        all_sections = set()
        sections_to_keys = {}
        
        for language, translations in self.translations.items():
            for section, keys in translations.items():
                all_sections.add(section)
                if section not in sections_to_keys:
                    sections_to_keys[section] = set()
                sections_to_keys[section].update(keys.keys())
        
        # Check for missing keys in each language
        for language, translations in self.translations.items():
            language_missing = {}
            
            for section in all_sections:
                section_translations = translations.get(section, {})
                section_keys = sections_to_keys.get(section, set())
                
                # Find keys missing in this section
                missing_keys = []
                for key in section_keys:
                    if key not in section_translations:
                        missing_keys.append(key)
                
                if missing_keys:
                    language_missing[section] = missing_keys
            
            if language_missing:
                missing[language] = language_missing
        
        return missing
    
    def validate_translations(self, raise_error=True):
        """Validate all translations and report missing keys
        
        Args:
            raise_error: If True, raise an error if missing translations are found
            
        Returns:
            A dictionary of missing translations by language and section
            
        Raises:
            ValueError: If missing translations are found and raise_error is True
        """
        missing = self.check_missing_translations()
        
        if missing and raise_error:
            error_msg = "Missing translations found:\n"
            for language, sections in missing.items():
                error_msg += f"\nLanguage: {language}\n"
                for section, keys in sections.items():
                    error_msg += f"  Section: {section}\n"
                    for key in keys:
                        error_msg += f"    - {key}\n"
            
            raise ValueError(error_msg)
        
        return missing
    
    def get_system_info(self, info_type):
        """获取系统信息
        
        Args:
            info_type: 要检索的信息类型 (cpu, memory, disk, os, app_list, env_vars, ip_address, mac_address)
            
        Returns:
            包含请求信息的字符串
        """
        try:
            # 检查参数有效性
            if info_type is None or info_type == "impossible":
                return "参数无效"
            
            if info_type == "cpu":
                return platform.processor()
            
            elif info_type == "memory":
                mem = psutil.virtual_memory()
                return f"总计: {self._format_bytes(mem.total)}, 可用: {self._format_bytes(mem.available)}, 已使用: {mem.percent}%"
            
            elif info_type == "disk":
                disk_info = []
                try:
                    # 获取所有磁盘分区
                    partitions = psutil.disk_partitions(all=False)  # 只获取实际挂载的分区
                    
                    for partition in partitions:
                        try:
                            # 过滤掉光驱和特殊分区
                            if platform.system() == "Windows":
                                # 检查驱动器类型
                                from ctypes import windll
                                drive_path = f"{partition.device}\\"
                                drive_type = windll.kernel32.GetDriveTypeW(drive_path)
                                
                                # 跳过光驱(5)和可移动设备(2)
                                if drive_type in [2, 5]:
                                    disk_info.append(f"{partition.device} - 可移动驱动器或光驱")
                                    continue
                            
                            # 检查路径是否存在
                            if not os.path.exists(partition.mountpoint):
                                disk_info.append(f"{partition.device} - 挂载点不存在")
                                continue
                                
                            # 检查是否可访问
                            if not os.access(partition.mountpoint, os.R_OK):
                                disk_info.append(f"{partition.device} ({partition.mountpoint}) - 无访问权限")
                                continue
                                
                            # 获取磁盘使用情况
                            usage = psutil.disk_usage(partition.mountpoint)
                            disk_info.append(f"{partition.device} ({partition.mountpoint}) - 总计: {self._format_bytes(usage.total)}, 已使用: {self._format_bytes(usage.used)} ({usage.percent}%)")
                        except PermissionError:
                            disk_info.append(f"{partition.device} ({partition.mountpoint}) - 权限错误")
                        except FileNotFoundError:
                            disk_info.append(f"{partition.device} ({partition.mountpoint}) - 路径不存在")
                        except OSError as e:
                            disk_info.append(f"{partition.device} ({partition.mountpoint}) - 操作系统错误: {str(e)}")
                        except Exception as e:
                            disk_info.append(f"{partition.device} ({partition.mountpoint}) - 未知错误: {str(e)}")
                except Exception as e:
                    disk_info.append(f"获取磁盘信息时出错: {str(e)}")
                    
                if not disk_info:
                    return "未能获取磁盘信息"
                return "<br>".join(disk_info)
            
            elif info_type == "os":
                return f"{platform.system()} {platform.version()} ({platform.architecture()[0]})"
            
            elif info_type == "app_list":
                apps = []
                if os.name == 'nt':  # Windows
                    try:
                        cmd = 'powershell "Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion | Sort-Object DisplayName"'
                        output = subprocess.check_output(cmd, shell=True, text=True)
                        
                        # Parse output for display names and versions
                        for line in output.strip().split('\n'):
                            if line and not line.startswith('-') and not line.startswith('DisplayName'):
                                parts = line.strip().split()
                                if len(parts) >= 2:
                                    name = ' '.join(parts[:-1])
                                    version = parts[-1]
                                    apps.append(f"<li>{name} - {version}</li>")
                    except:
                        apps.append("<li>Error retrieving installed applications</li>")
                else:  # Linux/Mac
                    apps.append("<li>Application listing not supported on this OS</li>")
                
                # Return only first 15 apps to avoid overwhelming the UI
                if len(apps) > 15:
                    return ''.join(apps[:15]) + f"<li>... and {len(apps) - 15} more</li>"
                return ''.join(apps) if apps else "<li>No applications found</li>"
            
            elif info_type == "env_vars":
                env_vars = []
                for key, value in os.environ.items():
                    if key.lower() not in ['path', 'pathext', 'temp', 'tmp']:  # Skip long variables
                        env_vars.append(f"<li><b>{key}</b>: {value}</li>")
                
                # Return only first 10 environment variables
                if len(env_vars) > 10:
                    return ''.join(env_vars[:10]) + f"<li>... and {len(env_vars) - 10} more</li>"
                return ''.join(env_vars)
            
            elif info_type == "ip_address":
                try:
                    hostname = socket.gethostname()
                    ip_address = socket.gethostbyname(hostname)
                    return ip_address
                except:
                    return "Unable to retrieve IP address"
            
            elif info_type == "mac_address":
                try:
                    mac_num = hex(uuid.getnode()).replace('0x', '')
                    mac = ':'.join(mac_num[i:i+2] for i in range(0, len(mac_num), 2))
                    return mac
                except:
                    return "Unable to retrieve MAC address"
            
            else:
                return f"未知的信息类型: {info_type}"
        
        except Exception as e:
            return f"获取信息时出错: {str(e)}"
    
    def _format_bytes(self, bytes):
        """Format bytes to a human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} PB" 