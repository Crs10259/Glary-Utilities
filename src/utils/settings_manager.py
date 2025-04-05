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
    # 运行模式常量
    MODE_PRODUCTION = "production"
    MODE_DEVELOPMENT = "development"
    MODE_DEBUG = "debug"
    MODE_TEST = "test"
    
    def __init__(self, app_name="Glary-Utilities", mode=None):
        self.app_name = app_name
        self.settings = {
            "language": "English",  # 默认使用英语
            "theme": "dark",
            "font_size": 12,
            "transparency": 100,
            "enable_notifications": True,
            "show_tips": True,
            "maintenance_reminder": True
        }
        self.translations = {}
        self.current_language = "English"
        self.mode = mode or self.MODE_PRODUCTION
        self.error_handlers = {}
        
        # 初始化错误处理器
        self._init_error_handlers()
        
        # Create config directory if it doesn't exist
        self.config_dir = self._get_config_dir()
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Settings file path
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        
        # Load settings
        self.load_settings()
        
        # Load translations
        self.load_translations()
    
    def _init_error_handlers(self):
        """初始化错误处理器"""
        self.error_handlers = {
            "file_not_found": self._handle_file_not_found,
            "permission_denied": self._handle_permission_denied,
            "invalid_json": self._handle_invalid_json,
            "missing_translation": self._handle_missing_translation,
            "disk_full": self._handle_disk_full,
            "network_error": self._handle_network_error
        }
    
    def _handle_error(self, error_type, error_details):
        """通用错误处理方法"""
        handler = self.error_handlers.get(error_type)
        if handler:
            return handler(error_details)
        return self._handle_unknown_error(error_type, error_details)
    
    def _handle_file_not_found(self, details):
        """处理文件未找到错误"""
        error_msg = f"File not found: {details}"  # 输出使用英语
        if self.mode in [self.MODE_DEVELOPMENT, self.MODE_DEBUG]:
            error_msg += f"\n调试信息: 当前工作目录: {os.getcwd()}"  # 注释保持中文
        return error_msg
    
    def _handle_permission_denied(self, details):
        """处理权限错误"""
        error_msg = f"Permission denied: {details}"  # 输出使用英语
        if self.mode in [self.MODE_DEVELOPMENT, self.MODE_DEBUG]:
            error_msg += f"\n调试信息: 当前用户: {os.getenv('USERNAME') or os.getenv('USER')}"  # 注释保持中文
        return error_msg
    
    def _handle_invalid_json(self, details):
        """处理JSON解析错误"""
        error_msg = f"Invalid JSON format: {details}"  # 输出使用英语
        if self.mode in [self.MODE_DEVELOPMENT, self.MODE_DEBUG]:
            error_msg += "\n调试信息: 请检查JSON语法"  # 注释保持中文
        return error_msg
    
    def _handle_missing_translation(self, details):
        """处理缺失翻译错误"""
        error_msg = f"Missing translation: {details}"  # 输出使用英语
        if self.mode in [self.MODE_DEVELOPMENT, self.MODE_DEBUG]:
            error_msg += f"\n调试信息: 当前语言: {self.current_language}"  # 注释保持中文
        return error_msg
    
    def _handle_disk_full(self, details):
        """处理磁盘空间不足错误"""
        error_msg = f"Disk space insufficient: {details}"  # 输出使用英语
        if self.mode in [self.MODE_DEVELOPMENT, self.MODE_DEBUG]:
            try:
                disk = os.path.dirname(self.settings_file)
                usage = shutil.disk_usage(disk)
                error_msg += f"\n调试信息: 可用空间: {self._format_bytes(usage.free)}"
            except Exception:
                pass
        return error_msg
    
    def _handle_network_error(self, details):
        """处理网络错误"""
        error_msg = f"Network error: {details}"  # 输出使用英语
        if self.mode in [self.MODE_DEVELOPMENT, self.MODE_DEBUG]:
            error_msg += "\n调试信息: 请检查网络连接"  # 注释保持中文
        return error_msg
    
    def _handle_unknown_error(self, error_type, details):
        """处理未知错误"""
        error_msg = f"Unknown error ({error_type}): {details}"  # 输出使用英语
        if self.mode in [self.MODE_DEVELOPMENT, self.MODE_DEBUG]:
            import traceback
            error_msg += f"\n调试信息: \n{traceback.format_exc()}"
        return error_msg
    
    def is_development_mode(self):
        """检查是否为开发模式"""
        return self.mode in [self.MODE_DEVELOPMENT, self.MODE_DEBUG]
    
    def is_debug_mode(self):
        """检查是否为调试模式"""
        return self.mode == self.MODE_DEBUG
    
    def is_test_mode(self):
        """检查是否为测试模式"""
        return self.mode == self.MODE_TEST
    
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
            if not os.path.exists(self.settings_file):
                raise FileNotFoundError(self.settings_file)
            
            if not os.access(self.settings_file, os.R_OK):
                raise PermissionError(f"Cannot read configuration file: {self.settings_file}")
            
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        raise ValueError("Configuration file is empty")
                    self.settings = json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Configuration file format error: {str(e)}")
            except UnicodeDecodeError:
                raise ValueError("Configuration file encoding error, please use UTF-8 encoding")
            
            # Set current language
            self.current_language = self.get_setting("language", "English")
            
            # 验证必要的配置项
            self._validate_settings()
            
        except FileNotFoundError:
            error_msg = self._handle_error("file_not_found", self.settings_file)
            print(error_msg)
            self.settings = self.get_default_settings()
            self.save_settings()
            self._notify_user("Settings file not found, default settings have been created.")
        
        except PermissionError as e:
            error_msg = self._handle_error("permission_denied", str(e))
            print(error_msg)
            self.settings = self.get_default_settings()
            self._notify_user("Cannot access settings file, default settings loaded. Please check file permissions.")
        
        except ValueError as e:
            error_msg = self._handle_error("invalid_json", str(e))
            print(error_msg)
            self.settings = self.get_default_settings()
            self._notify_user("Settings file format error, default settings loaded. Please check file content.")
        
        except Exception as e:
            error_msg = self._handle_error("unknown_error", str(e))
            print(error_msg)
            self.settings = self.get_default_settings()
            self._notify_user("Unknown error occurred while loading settings, default settings loaded.")
        
        finally:
            if not self.settings:
                self.settings = self.get_default_settings()
                self._notify_user("Failed to load settings, using default settings.")
    
    def _validate_settings(self):
        """验证设置的有效性"""
        required_settings = [
            "language",
            "theme",
            "font_size",
            "icon_size"
        ]
        
        missing_settings = []
        invalid_settings = []
        
        for setting in required_settings:
            if setting not in self.settings:
                missing_settings.append(setting)
            elif not self._is_valid_setting(setting, self.settings[setting]):
                invalid_settings.append(setting)
        
        if missing_settings or invalid_settings:
            error_msg = ""
            if missing_settings:
                error_msg += f"Missing required settings: {', '.join(missing_settings)}. "
            if invalid_settings:
                error_msg += f"Invalid settings: {', '.join(invalid_settings)}. "
            
            self._notify_user(error_msg + "Using default values.")
            
            # 使用默认值填充缺失或无效的设置
            for setting in missing_settings + invalid_settings:
                self.settings[setting] = self.get_default_settings()[setting]
        
    def _is_valid_setting(self, setting, value):
        """检查设置值是否有效"""
        if setting == "language":
            return value in ["English", "中文"]  # 添加更多支持的语言
        elif setting == "theme":
            return value in ["light", "dark", "blue", "green", "purple", "custom"]
        elif setting == "font_size":
            return isinstance(value, int) and 8 <= value <= 24
        elif setting == "icon_size":
            return isinstance(value, int) and 16 <= value <= 64
        return True  # 对于其他设置，默认为有效
    
    def save_settings(self):
        """Save settings to the settings file"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            
            print("Settings saved successfully.")
        except PermissionError:
            error_msg = self._handle_error("permission_denied", self.settings_file)
            print(error_msg)
            self._notify_user("Cannot save settings, permission denied. Please check file permissions.")
        except IOError as e:
            error_msg = self._handle_error("io_error", str(e))
            print(error_msg)
            self._notify_user("IO error occurred while saving settings. Please check disk space and file system.")
        except Exception as e:
            error_msg = self._handle_error("unknown_error", str(e))
            print(error_msg)
            self._notify_user("Unknown error occurred while saving settings.")
    
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
            
    def reset_settings(self):
        """重置所有设置为默认值"""
        self.settings = self.get_default_settings()
        # 保存默认设置
        self.save_settings()
        print("所有设置已重置为默认值")
    
    def load_translations(self):
        """Load translations from language files"""
        try:
            # Clear existing translations
            self.translations = {}
            
            # List of supported languages
            languages = ["English", "简体中文"]
            
            # Map language names to file names
            language_files = {
                "English": "en.json",
                "简体中文": "zh.json"
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
        
        # If still not found, log the missing translation and return default or key
        self._log_missing_translation(section, key)
        return default if default is not None else key

    def _log_missing_translation(self, section, key):
        """记录缺失的翻译"""
        log_message = f"Missing translation: '{section}.{key}' (Language: {self.current_language})"
        print(log_message)  # 可以替换为更复杂的日志记录机制
        if self.is_development_mode():
            self._notify_user(f"Developer note: {log_message}")

    def _notify_user(self, message):
        """通知用户（可以根据实际情况实现，如显示对话框或状态栏消息）"""
        print(f"User notification: {message}")
        # TODO: 实现实际的用户通知机制，例如：
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.show_notification(message)
    
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
            if info_type is None:
                return "Invalid parameter"
            
            if info_type == "cpu":
                return platform.processor()
            
            elif info_type == "memory":
                mem = psutil.virtual_memory()
                return f"Total: {self._format_bytes(mem.total)}, Available: {self._format_bytes(mem.available)}, Used: {mem.percent}%"
            
            elif info_type == "disk":
                
                disk_info = []
                try:
                    # 获取所有磁盘分区
                    partitions = psutil.disk_partitions(all=False)  # 只获取实际挂载的分区
              
                    for partition in partitions:
                        try:
                            # 检查路径是否存在
                            if not os.path.exists(partition.mountpoint):
                                disk_info.append(f"{partition.device} - Mount point does not exist")
                                continue
                       
                            # 检查是否可访问
                            if not os.access(partition.mountpoint, os.R_OK):
                                disk_info.append(f"{partition.device} ({partition.mountpoint}) - No access permission")
                                continue
                   
                            # 获取磁盘使用情况
                            usage = psutil.disk_usage(partition.mountpoint)
                            
                            disk_info.append(f"{partition.device} ({partition.mountpoint}) - Total: {self._format_bytes(usage.total)}, Used: {self._format_bytes(usage.used)} ({usage.percent}%)")
                        except PermissionError:
                            disk_info.append(f"{partition.device} ({partition.mountpoint}) - Permission error")
                        except FileNotFoundError:
                            disk_info.append(f"{partition.device} ({partition.mountpoint}) - Path does not exist")
                        except OSError as e:
                            disk_info.append(f"{partition.device} ({partition.mountpoint}) - 操作系统错误: {str(e)}")
                        except Exception as e:
                            disk_info.append(f"{partition.device} ({partition.mountpoint}) - 错误: {str(e)}")
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
    
    