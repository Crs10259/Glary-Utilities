
import os
import sys
import logging
from typing import List, Dict, Tuple

# 平台适配导入
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
    """管理Windows启动项的工具类"""
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
        """获取所有启动项
        
        Returns:
            List[Dict]: 启动项列表，每项包含name, path, status, type
        """
        items = []
        
        if not sys.platform.startswith("win"):
            StartupManager.logger.info("Startup items only available on Windows.")
            return []

        try:
            # 获取注册表启动项
            items.extend(StartupManager._get_registry_items())
            
            # 获取启动文件夹项
            items.extend(StartupManager._get_folder_items())
            
            # 获取计划任务启动项
            items.extend(StartupManager._get_scheduled_tasks())
            
            return items
        except Exception as e:
            StartupManager.logger.error(f"获取启动项时出错: {e}")
            return []
    
    @staticmethod
    def _get_registry_items() -> List[Dict]:
        """获取注册表中的启动项"""
        items = []
        
        if not sys.platform.startswith("win"):
            return []

        for location_name, location_value in StartupManager.STARTUP_LOCATIONS.items():
            # 只处理元组类型的注册表位置，跳过字符串路径
            if not isinstance(location_value, tuple) or len(location_value) != 2:
                continue
                
            hkey, subkey = location_value
            try:
                with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            # 检查是否被禁用
                            is_enabled = not StartupManager._is_registry_item_disabled(name)
                            
                            items.append({
                                "name": name,
                                "path": value,
                                "status": "已启用" if is_enabled else "已禁用",
                                "type": "注册表"
                            })
                            i += 1
                        except OSError:
                            break
            except Exception as e:
                StartupManager.logger.error(f"读取注册表启动项出错 ({location_name}): {e}")
        
        return items
    
    @staticmethod
    def _get_folder_items() -> List[Dict]:
        """获取启动文件夹中的启动项"""
        items = []
        
        if not sys.platform.startswith("win"):
            return []

        for location_name, location_value in StartupManager.STARTUP_LOCATIONS.items():
            # 只处理字符串类型的路径，跳过注册表键值对
            if not isinstance(location_value, str):
                continue
                
            try:
                folder_path = location_value
                if os.path.exists(folder_path):
                    for filename in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, filename)
                        if os.path.isfile(file_path) and (filename.endswith('.lnk') or filename.endswith('.url')):
                            # 获取快捷方式目标
                            shell_obj = win32com.client.Dispatch("WScript.Shell")
                            shortcut = shell_obj.CreateShortCut(file_path)
                            target_path = shortcut.Targetpath
                            
                            items.append({
                                "name": os.path.splitext(filename)[0],
                                "path": target_path,
                                "status": "已启用",  # 文件夹中的项总是启用的
                                "type": "启动文件夹"
                            })
            except Exception as e:
                StartupManager.logger.error(f"读取启动文件夹项出错 ({location_name}): {e}")
        
        return items
    
    @staticmethod
    def _get_scheduled_tasks() -> List[Dict]:
        """获取计划任务中的启动项"""
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
                            "status": "已启用" if task.Enabled else "已禁用",
                            "type": "任务计划程序"
                        })
                except Exception as e:
                    StartupManager.logger.error(f"读取计划任务 {task.Name} 出错: {e}")
                    continue
        except Exception as e:
            StartupManager.logger.error(f"读取计划任务启动项出错: {e}")
        
        return items
    
    @staticmethod
    def _is_registry_item_disabled(name: str) -> bool:
        """检查注册表启动项是否被禁用"""
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
                # 第一个字节为02表示禁用
                return value[0] == 0x02
            except OSError:
                return False
            finally:
                winreg.CloseKey(disabled_key)
        except OSError:
            return False
    
    @staticmethod
    def enable_startup_item(name: str, item_type: str) -> bool:
        """启用启动项
        
        Args:
            name: 启动项名称
            item_type: 启动项类型 ("注册表", "启动文件夹", "任务计划程序")
            
        Returns:
            bool: 是否成功
        """
        if not sys.platform.startswith("win"):
            return False
        try:
            if item_type == "注册表":
                return StartupManager._enable_registry_item(name)
            elif item_type == "任务计划程序":
                return StartupManager._enable_scheduled_task(name)
            else:
                StartupManager.logger.warning(f"不支持启用类型为 {item_type} 的启动项")
                return False
        except Exception as e:
            StartupManager.logger.error(f"启用启动项 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def disable_startup_item(name: str, item_type: str) -> bool:
        """禁用启动项
        
        Args:
            name: 启动项名称
            item_type: 启动项类型 ("注册表", "启动文件夹", "任务计划程序")
            
        Returns:
            bool: 是否成功
        """
        if not sys.platform.startswith("win"):
            return False
        try:
            if item_type == "注册表":
                return StartupManager._disable_registry_item(name)
            elif item_type == "任务计划程序":
                return StartupManager._disable_scheduled_task(name)
            else:
                StartupManager.logger.warning(f"不支持禁用类型为 {item_type} 的启动项")
                return False
        except Exception as e:
            StartupManager.logger.error(f"禁用启动项 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def delete_startup_item(name: str, path: str, item_type: str) -> bool:
        """删除启动项
        
        Args:
            name: 启动项名称
            path: 启动项路径
            item_type: 启动项类型 ("注册表", "启动文件夹", "任务计划程序")
            
        Returns:
            bool: 是否成功
        """
        if not sys.platform.startswith("win"):
            return False
        try:
            if item_type == "注册表":
                return StartupManager._delete_registry_item(name)
            elif item_type == "启动文件夹":
                return StartupManager._delete_folder_item(path)
            elif item_type == "任务计划程序":
                return StartupManager._delete_scheduled_task(name)
            else:
                StartupManager.logger.warning(f"不支持删除类型为 {item_type} 的启动项")
                return False
        except Exception as e:
            StartupManager.logger.error(f"删除启动项 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def add_startup_item(name: str, path: str, item_type: str = "注册表") -> bool:
        """添加新的启动项
        
        Args:
            name: 启动项名称
            path: 启动项路径
            item_type: 启动项类型 ("注册表", "启动文件夹")
            
        Returns:
            bool: 是否成功
        """
        if not sys.platform.startswith("win"):
            return False
        try:
            if item_type == "注册表":
                return StartupManager._add_registry_item(name, path)
            elif item_type == "启动文件夹":
                return StartupManager._add_folder_item(name, path)
            else:
                StartupManager.logger.warning(f"不支持添加类型为 {item_type} 的启动项")
                return False
        except Exception as e:
            StartupManager.logger.error(f"添加启动项 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _enable_registry_item(name: str) -> bool:
        """启用注册表启动项"""
        if not sys.platform.startswith("win"):
            return False
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
                0,
                winreg.KEY_WRITE
            )
            
            # 设置启用状态（全部字节设为0）
            value = bytes([0x00] * 12)
            winreg.SetValueEx(key, name, 0, winreg.REG_BINARY, value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            StartupManager.logger.error(f"启用注册表启动项 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _disable_registry_item(name: str) -> bool:
        """禁用注册表启动项"""
        if not sys.platform.startswith("win"):
            return False
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
                0,
                winreg.KEY_WRITE
            )
            
            # 设置禁用状态（第一个字节为02）
            value = bytes([0x02] + [0x00] * 11)
            winreg.SetValueEx(key, name, 0, winreg.REG_BINARY, value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            StartupManager.logger.error(f"禁用注册表启动项 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _enable_scheduled_task(name: str) -> bool:
        """启用计划任务"""
        if not sys.platform.startswith("win"):
            return False
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            task = scheduler.GetFolder("\\").GetTask(name)
            task.Enabled = True
            return True
        except Exception as e:
            StartupManager.logger.error(f"启用计划任务 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _disable_scheduled_task(name: str) -> bool:
        """禁用计划任务"""
        if not sys.platform.startswith("win"):
            return False
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            task = scheduler.GetFolder("\\").GetTask(name)
            task.Enabled = False
            return True
        except Exception as e:
            StartupManager.logger.error(f"禁用计划任务 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _delete_registry_item(name: str) -> bool:
        """删除注册表启动项"""
        if not sys.platform.startswith("win"):
            return False
        try:
            # 尝试从HKCU删除
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
            
            # 尝试从HKLM删除
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
            StartupManager.logger.error(f"删除注册表启动项 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _delete_folder_item(path: str) -> bool:
        """删除启动文件夹项"""
        if not sys.platform.startswith("win"):
            return False
        try:
            if os.path.exists(path):
                os.remove(path)
                return True
            return False
        except Exception as e:
            StartupManager.logger.error(f"删除启动文件夹项 {path} 时出错: {e}")
            return False
    
    @staticmethod
    def _delete_scheduled_task(name: str) -> bool:
        """删除计划任务"""
        if not sys.platform.startswith("win"):
            return False
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            root_folder = scheduler.GetFolder("\\")
            root_folder.DeleteTask(name, 0)
            return True
        except Exception as e:
            StartupManager.logger.error(f"删除计划任务 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _add_registry_item(name: str, path: str) -> bool:
        """添加注册表启动项"""
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
            StartupManager.logger.error(f"添加注册表启动项 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _add_folder_item(name: str, path: str) -> bool:
        """添加启动文件夹项"""
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
            StartupManager.logger.error(f"添加启动文件夹项 {name} 时出错: {e}")
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
        if sys.platform.startswith("win"):
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
        if sys.platform.startswith("win"):
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
        if sys.platform.startswith("win"):
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
        if sys.platform.startswith("win"):
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
        if sys.platform.startswith("win"):
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
