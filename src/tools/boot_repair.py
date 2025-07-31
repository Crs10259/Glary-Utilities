
import os
import sys
import logging
from typing import List, Dict, Tuple

# Platform adaptation imports
if sys.platform.startswith("win"):
    import winreg
    import win32com.client
    from win32com.shell import shell, shellcon
else:
    winreg = None
    win32com = None
    shell = None
    shellcon = None

from .base_tools import BaseThread
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

class StartupManager:
    """Tool class for managing Windows startup items"""
    logger = logging.getLogger(__name__)

    if sys.platform.startswith("win"):
        STARTUP_LOCATIONS = {
            "HKCU_RUN": (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            "HKLM_RUN": (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            "STARTUP_FOLDER": shell.SHGetFolderPath(0, shellcon.CSIDL_STARTUP, 0, 0),
            "COMMON_STARTUP": shell.SHGetFolderPath(0, shellcon.CSIDL_COMMON_STARTUP, 0, 0)
        }
    else:
        STARTUP_LOCATIONS = {}
    
    @staticmethod
    def get_startup_items() -> List[Dict]:
        """Get all startup items
        
        Returns:
            List[Dict]: List of startup items, each containing name, path, status, type
        """
        items = []
        
        if not sys.platform.startswith("win"):
            StartupManager.logger.info("Startup items only available on Windows.")
            return []

        try:
            # Get registry startup items
            items.extend(StartupManager._get_registry_items())
            
            # Get startup folder items
            items.extend(StartupManager._get_folder_items())
            
            # Get scheduled task startup items
            items.extend(StartupManager._get_scheduled_tasks())
            
            return items
        except Exception as e:
            StartupManager.logger.error(f"Error getting startup items: {e}")
            return []
    
    @staticmethod
    def _get_registry_items() -> List[Dict]:
        """Get startup items from registry"""
        items = []
        
        if not sys.platform.startswith("win"):
            return []

        for location_name, location_value in StartupManager.STARTUP_LOCATIONS.items():
            # Only process tuple-type registry locations, skip string paths
            if not isinstance(location_value, tuple) or len(location_value) != 2:
                continue
                
            hkey, subkey = location_value
            try:
                with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            # Check if disabled
                            is_enabled = not StartupManager._is_registry_item_disabled(name)
                            
                            items.append({
                                "name": name,
                                "path": value,
                                "status": "Enabled" if is_enabled else "Disabled",
                                "type": "Registry"
                            })
                            i += 1
                        except OSError:
                            break
            except Exception as e:
                StartupManager.logger.error(f"Error reading registry startup items ({location_name}): {e}")
        
        return items
    
    @staticmethod
    def _get_folder_items() -> List[Dict]:
        """Get startup items from startup folders"""
        items = []
        
        if not sys.platform.startswith("win"):
            return []

        for location_name, location_value in StartupManager.STARTUP_LOCATIONS.items():
            # Only process string-type paths, skip registry key-value pairs
            if not isinstance(location_value, str):
                continue
                
            try:
                folder_path = location_value
                if os.path.exists(folder_path):
                    for filename in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, filename)
                        if os.path.isfile(file_path) and (filename.endswith('.lnk') or filename.endswith('.url')):
                            # Get shortcut target
                            shell_obj = win32com.client.Dispatch("WScript.Shell")
                            shortcut = shell_obj.CreateShortCut(file_path)
                            target_path = shortcut.Targetpath
                            
                            items.append({
                                "name": os.path.splitext(filename)[0],
                                "path": target_path,
                                "status": "Enabled",  # Items in folders are always enabled
                                "type": "Startup Folder"
                            })
            except Exception as e:
                StartupManager.logger.error(f"Error reading startup folder items ({location_name}): {e}")
        
        return items
    
    @staticmethod
    def _get_scheduled_tasks() -> List[Dict]:
        """Get startup items from scheduled tasks"""
        items = []
        
        if not sys.platform.startswith("win"):
            return []

        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            root_folder = scheduler.GetFolder("\\")
            tasks = root_folder.GetTasks(0)
            
            for task in tasks:
                try:
                    if task.Enabled and "OnLogon" in [trigger.Type for trigger in task.Definition.Triggers]:
                        items.append({
                            "name": task.Name,
                            "path": task.Path,
                            "status": "Enabled" if task.Enabled else "Disabled",
                            "type": "Task Scheduler"
                        })
                except Exception as e:
                    StartupManager.logger.error(f"Error reading scheduled task {task.Name}: {e}")
                    continue
        except Exception as e:
            StartupManager.logger.error(f"Error reading scheduled task startup items: {e}")
        
        return items
    
    @staticmethod
    def _is_registry_item_disabled(name: str) -> bool:
        """Check if registry startup item is disabled"""
        if not sys.platform.startswith("win"):
            return False
        try:
            disabled_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
                0,
                winreg.KEY_READ
            )
            
            try:
                value, _ = winreg.QueryValueEx(disabled_key, name)
                # First byte 0x02 indicates disabled
                return value[0] == 0x02
            except OSError:
                return False
            finally:
                winreg.CloseKey(disabled_key)
        except OSError:
            return False
    
    @staticmethod
    def enable_startup_item(name: str, item_type: str) -> bool:
        """Enable startup item
        
        Args:
            name: Startup item name
            item_type: Startup item type ("Registry", "Startup Folder", "Task Scheduler")
            
        Returns:
            bool: Whether successful
        """
        if not sys.platform.startswith("win"):
            return False
        try:
            if item_type == "Registry":
                return StartupManager._enable_registry_item(name)
            elif item_type == "Task Scheduler":
                return StartupManager._enable_scheduled_task(name)
            else:
                StartupManager.logger.warning(f"Unsupported startup item type for enabling: {item_type}")
                return False
        except Exception as e:
            StartupManager.logger.error(f"Error enabling startup item {name}: {e}")
            return False
    
    @staticmethod
    def disable_startup_item(name: str, item_type: str) -> bool:
        """Disable startup item
        
        Args:
            name: Startup item name
            item_type: Startup item type ("Registry", "Startup Folder", "Task Scheduler")
            
        Returns:
            bool: Whether successful
        """
        if not sys.platform.startswith("win"):
            return False
        try:
            if item_type == "Registry":
                return StartupManager._disable_registry_item(name)
            elif item_type == "Task Scheduler":
                return StartupManager._disable_scheduled_task(name)
            else:
                StartupManager.logger.warning(f"Unsupported startup item type for disabling: {item_type}")
                return False
        except Exception as e:
            StartupManager.logger.error(f"Error disabling startup item {name}: {e}")
            return False
    
    @staticmethod
    def delete_startup_item(name: str, path: str, item_type: str) -> bool:
        """Delete startup item
        
        Args:
            name: Startup item name
            path: Startup item path
            item_type: Startup item type ("Registry", "Startup Folder", "Task Scheduler")
            
        Returns:
            bool: Whether successful
        """
        if not sys.platform.startswith("win"):
            return False
        try:
            if item_type == "Registry":
                return StartupManager._delete_registry_item(name)
            elif item_type == "Startup Folder":
                return StartupManager._delete_folder_item(path)
            elif item_type == "Task Scheduler":
                return StartupManager._delete_scheduled_task(name)
            else:
                StartupManager.logger.warning(f"Unsupported startup item type for deletion: {item_type}")
                return False
        except Exception as e:
            StartupManager.logger.error(f"Error deleting startup item {name}: {e}")
            return False
    
    @staticmethod
    def add_startup_item(name: str, path: str, item_type: str = "Registry") -> bool:
        """Add new startup item
        
        Args:
            name: Startup item name
            path: Startup item path
            item_type: Startup item type ("Registry", "Startup Folder")
            
        Returns:
            bool: Whether successful
        """
        if not sys.platform.startswith("win"):
            return False
        try:
            if item_type == "Registry":
                return StartupManager._add_registry_item(name, path)
            elif item_type == "Startup Folder":
                return StartupManager._add_folder_item(name, path)
            else:
                StartupManager.logger.warning(f"Unsupported startup item type for adding: {item_type}")
                return False
        except Exception as e:
            StartupManager.logger.error(f"Error adding startup item {name}: {e}")
            return False
    
    @staticmethod
    def _enable_registry_item(name: str) -> bool:
        """Enable registry startup item"""
        if not sys.platform.startswith("win"):
            return False
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
                0,
                winreg.KEY_WRITE
            )
            
            # Set enabled status (all bytes set to 0)
            value = bytes([0x00] * 12)
            winreg.SetValueEx(key, name, 0, winreg.REG_BINARY, value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            StartupManager.logger.error(f"Error enabling registry startup item {name}: {e}")
            return False
    
    @staticmethod
    def _disable_registry_item(name: str) -> bool:
        """Disable registry startup item"""
        if not sys.platform.startswith("win"):
            return False
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
                0,
                winreg.KEY_WRITE
            )
            
            # Set disabled status (first byte is 0x02)
            value = bytes([0x02] + [0x00] * 11)
            winreg.SetValueEx(key, name, 0, winreg.REG_BINARY, value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            StartupManager.logger.error(f"Error disabling registry startup item {name}: {e}")
            return False
    
    @staticmethod
    def _enable_scheduled_task(name: str) -> bool:
        """Enable scheduled task"""
        if not sys.platform.startswith("win"):
            return False
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            task = scheduler.GetFolder("\\").GetTask(name)
            task.Enabled = True
            return True
        except Exception as e:
            StartupManager.logger.error(f"Error enabling scheduled task {name}: {e}")
            return False
    
    @staticmethod
    def _disable_scheduled_task(name: str) -> bool:
        """Disable scheduled task"""
        if not sys.platform.startswith("win"):
            return False
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            task = scheduler.GetFolder("\\").GetTask(name)
            task.Enabled = False
            return True
        except Exception as e:
            StartupManager.logger.error(f"Error disabling scheduled task {name}: {e}")
            return False
    
    @staticmethod
    def _delete_registry_item(name: str) -> bool:
        """Delete registry startup item"""
        if not sys.platform.startswith("win"):
            return False
        try:
            # Try to delete from HKCU
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0,
                    winreg.KEY_WRITE
                )
                winreg.DeleteValue(key, name)
                winreg.CloseKey(key)
                return True
            except OSError:
                pass
            
            # Try to delete from HKLM
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0,
                    winreg.KEY_WRITE
                )
                winreg.DeleteValue(key, name)
                winreg.CloseKey(key)
                return True
            except OSError:
                pass
            
            return False
        except Exception as e:
            StartupManager.logger.error(f"Error deleting registry startup item {name}: {e}")
            return False
    
    @staticmethod
    def _delete_folder_item(path: str) -> bool:
        """Delete startup folder item"""
        if not sys.platform.startswith("win"):
            return False
        try:
            if os.path.exists(path):
                os.remove(path)
                return True
            return False
        except Exception as e:
            StartupManager.logger.error(f"Error deleting startup folder item {path}: {e}")
            return False
    
    @staticmethod
    def _delete_scheduled_task(name: str) -> bool:
        """Delete scheduled task"""
        if not sys.platform.startswith("win"):
            return False
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            root_folder = scheduler.GetFolder("\\")
            root_folder.DeleteTask(name, 0)
            return True
        except Exception as e:
            StartupManager.logger.error(f"Error deleting scheduled task {name}: {e}")
            return False
    
    @staticmethod
    def _add_registry_item(name: str, path: str) -> bool:
        """Add registry startup item"""
        if not sys.platform.startswith("win"):
            return False
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_WRITE
            )
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, path)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            StartupManager.logger.error(f"Error adding registry startup item {name}: {e}")
            return False
    
    @staticmethod
    def _add_folder_item(name: str, path: str) -> bool:
        """Add startup folder item"""
        if not sys.platform.startswith("win"):
            return False
        try:
            startup_folder = shell.SHGetFolderPath(0, shellcon.CSIDL_STARTUP, 0, 0)
            shortcut_path = os.path.join(startup_folder, f"{name}.lnk")
            
            shell_obj = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell_obj.CreateShortCut(shortcut_path)
            shortcut.Targetpath = path
            shortcut.save()
            return True
        except Exception as e:
            StartupManager.logger.error(f"Error adding startup folder item {name}: {e}")
            return False 
        
class BootRepairThread(BaseThread):
    """Thread for running boot repair operations in the background"""
    update_progress = pyqtSignal(int)
    update_log = pyqtSignal(str)
    finished_operation = pyqtSignal(bool, str)
    
    def __init__(self, repair_type, parent=None):
        super().__init__(parent)
        self.repair_type = repair_type
        self.is_running = False
        
    def run(self):
        self.is_running = True
        
        try:
            if self.repair_type == "mbr":
                self.repair_mbr()
            elif self.repair_type == "bcd":
                self.repair_bcd()
            elif self.repair_type == "bootmgr":
                self.repair_bootmgr()
            elif self.repair_type == "winload":
                self.repair_winload()
            elif self.repair_type == "full":
                self.full_repair()
                
            self.finished_operation.emit(True, "Boot repair completed successfully!")
        except Exception as e:
            self.update_log.emit(f"Error: {str(e)}")
            self.finished_operation.emit(False, f"Boot repair failed: {str(e)}")
        
        self.is_running = False
    
    def repair_mbr(self):
        """Repair the Master Boot Record"""
        self.update_log.emit("Starting MBR repair...")
        self.update_progress.emit(10)
        
        # For safety, this is a simulation
        if self.platform_manager.is_windows():
            self.update_log.emit("Checking disk status...")
            self.update_progress.emit(30)
            
            # Simulate disk check
            for i in range(30, 60, 5):
                QThread.sleep(1)
                self.update_progress.emit(i)
                self.update_log.emit(f"Analyzing MBR structures... ({i}%)")
            
            self.update_log.emit("MBR repair would run the following command:")
            self.update_log.emit("bootrec /fixmbr")
            
            QThread.sleep(2)
            self.update_progress.emit(100)
            self.update_log.emit("MBR repair completed (simulated)")
        else:
            self.update_log.emit("MBR repair is only available on Windows.")
            self.update_progress.emit(100)
    
    def repair_bcd(self):
        """Repair the Boot Configuration Data"""
        self.update_log.emit("Starting BCD repair...")
        self.update_progress.emit(10)
        
        # For safety, this is a simulation
        if self.platform_manager.is_windows():
            self.update_log.emit("Backing up existing BCD...")
            self.update_progress.emit(20)
            
            # Simulate repair process
            for i in range(20, 70, 5):
                QThread.sleep(1)
                self.update_progress.emit(i)
                self.update_log.emit(f"Rebuilding boot configuration data... ({i}%)")
            
            self.update_log.emit("BCD repair would run the following commands:")
            self.update_log.emit("bootrec /rebuildbcd")
            
            QThread.sleep(2)
            self.update_progress.emit(100)
            self.update_log.emit("BCD repair completed (simulated)")
        else:
            self.update_log.emit("BCD repair is only available on Windows.")
            self.update_progress.emit(100)
    
    def repair_bootmgr(self):
        """Repair the Boot Manager"""
        self.update_log.emit("Starting Boot Manager repair...")
        self.update_progress.emit(10)
        
        # For safety, this is a simulation
        if self.platform_manager.is_windows():
            self.update_log.emit("Checking Boot Manager...")
            self.update_progress.emit(30)
            
            # Simulate repair process
            for i in range(30, 80, 5):
                QThread.sleep(1)
                self.update_progress.emit(i)
                self.update_log.emit(f"Repairing boot manager files... ({i}%)")
            
            self.update_log.emit("Boot Manager repair would run the following command:")
            self.update_log.emit("bootrec /fixboot")
            
            QThread.sleep(2)
            self.update_progress.emit(100)
            self.update_log.emit("Boot Manager repair completed (simulated)")
        else:
            self.update_log.emit("Boot Manager repair is only available on Windows.")
            self.update_progress.emit(100)
    
    def repair_winload(self):
        """Repair the Windows Loader"""
        self.update_log.emit("Starting Windows Loader repair...")
        self.update_progress.emit(10)
        
        # For safety, this is a simulation
        if self.platform_manager.is_windows():
            self.update_log.emit("Checking Windows boot files...")
            self.update_progress.emit(20)
            
            # Simulate repair process
            for i in range(20, 90, 7):
                QThread.sleep(1)
                self.update_progress.emit(i)
                self.update_log.emit(f"Restoring Windows Loader files... ({i}%)")
            
            self.update_log.emit("Windows Loader repair would use SFC to repair system files:")
            self.update_log.emit("sfc /scannow")
            
            QThread.sleep(2)
            self.update_progress.emit(100)
            self.update_log.emit("Windows Loader repair completed (simulated)")
        else:
            self.update_log.emit("Windows Loader repair is only available on Windows.")
            self.update_progress.emit(100)
    
    def full_repair(self):
        """Perform a full boot repair sequence"""
        self.update_log.emit("Starting full boot repair sequence...")
        self.update_progress.emit(5)
        
        # For safety, this is a simulation
        if self.platform_manager.is_windows():
            # Simulate full repair
            self.update_log.emit("Step 1: Fixing MBR...")
            self.update_progress.emit(10)
            QThread.sleep(2)
            
            self.update_log.emit("Step 2: Fixing boot sector...")
            self.update_progress.emit(25)
            QThread.sleep(2)
            
            self.update_log.emit("Step 3: Rebuilding BCD...")
            self.update_progress.emit(40)
            QThread.sleep(2)
            
            self.update_log.emit("Step 4: Repairing Windows boot files...")
            self.update_progress.emit(60)
            QThread.sleep(2)
            
            self.update_log.emit("Step 5: Scanning system files...")
            self.update_progress.emit(80)
            QThread.sleep(2)
            
            self.update_log.emit("Full boot repair would run the following commands:")
            self.update_log.emit("1. bootrec /fixmbr")
            self.update_log.emit("2. bootrec /fixboot")
            self.update_log.emit("3. bootrec /rebuildbcd")
            self.update_log.emit("4. sfc /scannow")
            
            self.update_progress.emit(100)
            self.update_log.emit("Full boot repair completed (simulated)")
        else:
            self.update_log.emit("Boot repair is only available on Windows.")
            self.update_progress.emit(100)
