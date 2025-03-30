import os
import json
import platform
from PyQt5.QtCore import QObject, QSettings

class Settings(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("GlaryUtilities", "GlaryUtilities")
        self.translations = {}
        self.load_translations()
        
    def load_translations(self):
        """Load all available translations"""
        translations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "translations")
        
        # Ensure directory exists
        if not os.path.exists(translations_dir):
            os.makedirs(translations_dir)
            
            # Create default English translation
            # self._create_default_translations()
        
        # Load all translation files
        for file in os.listdir(translations_dir):
            if file.endswith(".json"):
                lang_code = file.split(".")[0]
                try:
                    with open(os.path.join(translations_dir, file), 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                except Exception as e:
                    print(f"Error loading translation {file}: {e}")
    
    # def _create_default_translations(self):
    #     """Create default translations if they don't exist"""
    #     translations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "translations")
        
    #     # English translations
    #     en_translations = {
    #         "general": {
    #             "dashboard": "Dashboard",
    #             "system_cleaner": "System Cleaner",
    #             "gpu_info": "GPU Information",
    #             "system_repair": "System Repair",
    #             "dism_tool": "DISM Tool",
    #             "network_reset": "Network Reset",
    #             "disk_check": "Disk Check",
    #             "boot_repair": "Boot Repair",
    #             "virus_scan": "Virus Scan",
    #             "settings": "Settings",
    #             "save": "Save",
    #             "cancel": "Cancel",
    #             "back": "Back",
    #             "next": "Next",
    #             "finish": "Finish",
    #             "scan": "Scan",
    #             "clean": "Clean",
    #             "repair": "Repair",
    #             "check": "Check",
    #             "reset": "Reset"
    #         },
    #         "dashboard": {
    #             "system_status": "System Status",
    #             "cpu_usage": "CPU Usage",
    #             "memory_usage": "Memory Usage",
    #             "disk_usage": "Disk Usage",
    #             "system_temperature": "System Temperature",
    #             "quick_access": "Quick Access",
    #             "optimize_system": "Optimize System",
    #             "clean_junk": "Clean Junk Files",
    #             "scan_virus": "Scan for Viruses",
    #             "check_updates": "Check for Updates"
    #         },
    #         "system_cleaner": {
    #             "title": "System Cleaner",
    #             "description": "Clean unnecessary files to free up disk space",
    #             "scan_for": "Scan for:",
    #             "temp_files": "Temporary Files",
    #             "recycle_bin": "Recycle Bin",
    #             "cache_files": "Cache Files",
    #             "log_files": "Log Files",
    #             "exclude_files": "Exclude Files",
    #             "add_exclusion": "Add Exclusion",
    #             "remove_exclusion": "Remove Exclusion",
    #             "file_extensions": "File Extensions",
    #             "add_extension": "Add Extension",
    #             "remove_extension": "Remove Extension",
    #             "scan_button": "Scan Now",
    #             "clean_button": "Clean Selected",
    #             "scanning": "Scanning...",
    #             "cleaning": "Cleaning...",
    #             "scan_complete": "Scan Complete",
    #             "clean_complete": "Clean Complete",
    #             "items_found": "Items Found",
    #             "space_to_free": "Space to Free"
    #         },
    #         "gpu_info": {
    #             "title": "GPU Information",
    #             "description": "View basic information about your GPU",
    #             "gpu_name": "GPU Name",
    #             "driver_version": "Driver Version",
    #             "memory_total": "Total Memory",
    #             "memory_used": "Memory Used",
    #             "temperature": "Temperature",
    #             "refresh": "Refresh Information"
    #         },
    #         "system_repair": {
    #             "title": "System Repair",
    #             "description": "Check and repair system issues",
    #             "scan_for": "Scan for:",
    #             "registry_issues": "Registry Issues",
    #             "system_files": "System Files",
    #             "startup_items": "Startup Items",
    #             "services": "Services",
    #             "scan_button": "Scan Now",
    #             "repair_button": "Repair Selected",
    #             "scanning": "Scanning...",
    #             "repairing": "Repairing...",
    #             "scan_complete": "Scan Complete",
    #             "repair_complete": "Repair Complete",
    #             "issues_found": "Issues Found",
    #             "fixed_issues": "Fixed Issues"
    #         },
    #         "dism_tool": {
    #             "title": "DISM Tool",
    #             "description": "Deployment Image Servicing and Management tool",
    #             "operations": "Operations:",
    #             "check_health": "Check Health",
    #             "scan_health": "Scan Health",
    #             "restore_health": "Restore Health",
    #             "cleanup_image": "Cleanup Image",
    #             "start_button": "Start Operation",
    #             "log_output": "Operation Log"
    #         },
    #         "network_reset": {
    #             "title": "Network Reset",
    #             "description": "Reset network settings to resolve connectivity issues",
    #             "warning": "Warning: This will reset all network adapters and settings",
    #             "operations": "Operations:",
    #             "flush_dns": "Flush DNS Cache",
    #             "reset_winsock": "Reset Winsock",
    #             "reset_tcp_ip": "Reset TCP/IP Stack",
    #             "reset_firewall": "Reset Firewall Settings",
    #             "reset_button": "Reset Network",
    #             "log_output": "Operation Log"
    #         },
    #         "disk_check": {
    #             "title": "Disk Check",
    #             "description": "Check disk for errors and repair them",
    #             "select_drive": "Select Drive:",
    #             "check_types": "Check Types:",
    #             "file_system": "File System Errors",
    #             "bad_sectors": "Bad Sectors",
    #             "check_button": "Check Disk",
    #             "repair_button": "Repair Disk",
    #             "warning": "Warning: Disk check may require a system restart",
    #             "log_output": "Operation Log"
    #         },
    #         "boot_repair": {
    #             "title": "Boot Repair",
    #             "description": "Repair Windows boot issues",
    #             "operations": "Operations:",
    #             "rebuild_bcd": "Rebuild BCD",
    #             "fix_mbr": "Fix MBR",
    #             "fix_boot": "Fix Boot Sector",
    #             "repair_button": "Repair Boot",
    #             "warning": "Warning: Boot repair may require a system restart",
    #             "log_output": "Operation Log"
    #         },
    #         "virus_scan": {
    #             "title": "Virus Scan",
    #             "description": "Scan for viruses and malware",
    #             "scan_locations": "Scan Locations:",
    #             "system_drive": "System Drive",
    #             "all_drives": "All Drives",
    #             "specific_folder": "Specific Folder",
    #             "select_folder": "Select Folder",
    #             "scan_types": "Scan Types:",
    #             "quick_scan": "Quick Scan",
    #             "full_scan": "Full Scan",
    #             "custom_scan": "Custom Scan",
    #             "scan_button": "Start Scan",
    #             "stop_button": "Stop Scan",
    #             "scanning": "Scanning...",
    #             "scan_complete": "Scan Complete",
    #             "threats_found": "Threats Found",
    #             "clean_threats": "Clean Threats",
    #             "log_output": "Scan Log"
    #         },
    #         "settings": {
    #             "title": "Settings",
    #             "description": "Configure application settings",
    #             "general": "General",
    #             "language": "Language:",
    #             "theme": "Theme:",
    #             "light": "Light",
    #             "dark": "Dark",
    #             "system": "System",
    #             "startup": "Start with Windows",
    #             "updates": "Check for updates automatically",
    #             "advanced": "Advanced",
    #             "disk_space": "Minimum free disk space to maintain (GB):",
    #             "logs": "Keep logs for (days):",
    #             "exclusions": "Exclusions",
    #             "files_folders": "Excluded Files and Folders:",
    #             "add": "Add",
    #             "remove": "Remove",
    #             "save_button": "Save Settings",
    #             "reset_button": "Reset to Default"
    #         }
    #     }
        
    #     # Save English translations
    #     with open(os.path.join(translations_dir, "en.json"), 'w', encoding='utf-8') as f:
    #         json.dump(en_translations, f, indent=4, ensure_ascii=False)
            
    #     # Create a simple Chinese translation
    #     zh_translations = {
    #         "general": {
    #             "dashboard": "仪表板",
    #             "system_cleaner": "系统清理",
    #             "gpu_info": "GPU信息",
    #             "system_repair": "系统修复",
    #             "dism_tool": "DISM工具",
    #             "network_reset": "网络重置",
    #             "disk_check": "磁盘检查",
    #             "boot_repair": "启动修复",
    #             "virus_scan": "病毒扫描",
    #             "settings": "设置",
    #             "save": "保存",
    #             "cancel": "取消",
    #             "back": "返回",
    #             "next": "下一步",
    #             "finish": "完成",
    #             "scan": "扫描",
    #             "clean": "清理",
    #             "repair": "修复",
    #             "check": "检查",
    #             "reset": "重置"
    #         },
    #         "dashboard": {
    #             "system_status": "系统状态",
    #             "cpu_usage": "CPU使用率",
    #             "memory_usage": "内存使用率",
    #             "disk_usage": "磁盘使用率",
    #             "system_temperature": "系统温度",
    #             "quick_access": "快速访问",
    #             "optimize_system": "系统优化",
    #             "clean_junk": "清理垃圾文件",
    #             "scan_virus": "病毒扫描",
    #             "check_updates": "检查更新"
    #         }
    #         # Add other sections similarly to English but with Chinese translations
    #     }
        
    #     # Save Chinese translations
    #     with open(os.path.join(translations_dir, "zh.json"), 'w', encoding='utf-8') as f:
    #         json.dump(zh_translations, f, indent=4, ensure_ascii=False)
    
    def get_setting(self, key, default_value=None):
        """Get a setting value with default fallback"""
        return self.settings.value(key, default_value)
    
    def set_setting(self, key, value):
        """Set a setting value"""
        self.settings.setValue(key, value)
        self.settings.sync()
    
    def get_translation(self, section, key, language=None):
        """Get translated text for a given key"""
        if not language:
            language = self.get_setting("language", "en")
            
        # Fallback to English if the language is not available
        if language not in self.translations:
            language = "en"
            
        # Return key if translation not found
        if section not in self.translations[language] or key not in self.translations[language][section]:
            # Try to find in English as fallback
            if section in self.translations["en"] and key in self.translations["en"][section]:
                return self.translations["en"][section][key]
            return key
            
        return self.translations[language][section][key]
    
    def get_system_info(self):
        """Get basic system information"""
        system_info = {
            "os": platform.system() + " " + platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version()
        }
        return system_info 