import os
import sys
import winreg
import logging
from typing import List, Dict, Tuple
import win32api
import win32con
import win32gui
import win32process
import win32security
import win32com.client
from win32com.shell import shell, shellcon

logger = logging.getLogger(__name__)

class StartupManager:
    """管理Windows启动项的工具类"""
    
    STARTUP_LOCATIONS = {
        "HKCU_RUN": (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        "HKLM_RUN": (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        "STARTUP_FOLDER": shell.SHGetFolderPath(0, shellcon.CSIDL_STARTUP, 0, 0),
        "COMMON_STARTUP": shell.SHGetFolderPath(0, shellcon.CSIDL_COMMON_STARTUP, 0, 0)
    }
    
    @staticmethod
    def get_startup_items() -> List[Dict]:
        """获取所有启动项
        
        Returns:
            List[Dict]: 启动项列表，每项包含name, path, status, type
        """
        items = []
        
        try:
            # 获取注册表启动项
            items.extend(StartupManager._get_registry_items())
            
            # 获取启动文件夹项
            items.extend(StartupManager._get_folder_items())
            
            # 获取计划任务启动项
            items.extend(StartupManager._get_scheduled_tasks())
            
            return items
        except Exception as e:
            logger.error(f"获取启动项时出错: {e}")
            return []
    
    @staticmethod
    def _get_registry_items() -> List[Dict]:
        """获取注册表中的启动项"""
        items = []
        
        for location_name, (hkey, subkey) in StartupManager.STARTUP_LOCATIONS.items():
            if not isinstance(hkey, int):  # 跳过非注册表位置
                continue
                
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
                        except WindowsError:
                            break
            except Exception as e:
                logger.error(f"读取注册表启动项出错 ({location_name}): {e}")
        
        return items
    
    @staticmethod
    def _get_folder_items() -> List[Dict]:
        """获取启动文件夹中的启动项"""
        items = []
        
        for location_name, folder_path in StartupManager.STARTUP_LOCATIONS.items():
            if not isinstance(folder_path, str):  # 跳过非文件夹位置
                continue
                
            try:
                if os.path.exists(folder_path):
                    for filename in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, filename)
                        if os.path.isfile(file_path) and (filename.endswith('.lnk') or filename.endswith('.url')):
                            # 获取快捷方式目标
                            shell = win32com.client.Dispatch("WScript.Shell")
                            shortcut = shell.CreateShortCut(file_path)
                            target_path = shortcut.Targetpath
                            
                            items.append({
                                "name": os.path.splitext(filename)[0],
                                "path": target_path,
                                "status": "已启用",  # 文件夹中的项总是启用的
                                "type": "启动文件夹"
                            })
            except Exception as e:
                logger.error(f"读取启动文件夹项出错 ({location_name}): {e}")
        
        return items
    
    @staticmethod
    def _get_scheduled_tasks() -> List[Dict]:
        """获取计划任务中的启动项"""
        items = []
        
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
                    logger.error(f"读取计划任务 {task.Name} 出错: {e}")
                    continue
        except Exception as e:
            logger.error(f"读取计划任务启动项出错: {e}")
        
        return items
    
    @staticmethod
    def _is_registry_item_disabled(name: str) -> bool:
        """检查注册表启动项是否被禁用"""
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
            except WindowsError:
                return False
            finally:
                winreg.CloseKey(disabled_key)
        except WindowsError:
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
        try:
            if item_type == "注册表":
                return StartupManager._enable_registry_item(name)
            elif item_type == "任务计划程序":
                return StartupManager._enable_scheduled_task(name)
            else:
                logger.warning(f"不支持启用类型为 {item_type} 的启动项")
                return False
        except Exception as e:
            logger.error(f"启用启动项 {name} 时出错: {e}")
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
        try:
            if item_type == "注册表":
                return StartupManager._disable_registry_item(name)
            elif item_type == "任务计划程序":
                return StartupManager._disable_scheduled_task(name)
            else:
                logger.warning(f"不支持禁用类型为 {item_type} 的启动项")
                return False
        except Exception as e:
            logger.error(f"禁用启动项 {name} 时出错: {e}")
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
        try:
            if item_type == "注册表":
                return StartupManager._delete_registry_item(name)
            elif item_type == "启动文件夹":
                return StartupManager._delete_folder_item(path)
            elif item_type == "任务计划程序":
                return StartupManager._delete_scheduled_task(name)
            else:
                logger.warning(f"不支持删除类型为 {item_type} 的启动项")
                return False
        except Exception as e:
            logger.error(f"删除启动项 {name} 时出错: {e}")
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
        try:
            if item_type == "注册表":
                return StartupManager._add_registry_item(name, path)
            elif item_type == "启动文件夹":
                return StartupManager._add_folder_item(name, path)
            else:
                logger.warning(f"不支持添加类型为 {item_type} 的启动项")
                return False
        except Exception as e:
            logger.error(f"添加启动项 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _enable_registry_item(name: str) -> bool:
        """启用注册表启动项"""
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
            logger.error(f"启用注册表启动项 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _disable_registry_item(name: str) -> bool:
        """禁用注册表启动项"""
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
            logger.error(f"禁用注册表启动项 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _enable_scheduled_task(name: str) -> bool:
        """启用计划任务"""
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            task = scheduler.GetFolder("\\").GetTask(name)
            task.Enabled = True
            return True
        except Exception as e:
            logger.error(f"启用计划任务 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _disable_scheduled_task(name: str) -> bool:
        """禁用计划任务"""
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            task = scheduler.GetFolder("\\").GetTask(name)
            task.Enabled = False
            return True
        except Exception as e:
            logger.error(f"禁用计划任务 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _delete_registry_item(name: str) -> bool:
        """删除注册表启动项"""
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
            except WindowsError:
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
            except WindowsError:
                pass
            
            return False
        except Exception as e:
            logger.error(f"删除注册表启动项 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _delete_folder_item(path: str) -> bool:
        """删除启动文件夹项"""
        try:
            if os.path.exists(path):
                os.remove(path)
                return True
            return False
        except Exception as e:
            logger.error(f"删除启动文件夹项 {path} 时出错: {e}")
            return False
    
    @staticmethod
    def _delete_scheduled_task(name: str) -> bool:
        """删除计划任务"""
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            root_folder = scheduler.GetFolder("\\")
            root_folder.DeleteTask(name, 0)
            return True
        except Exception as e:
            logger.error(f"删除计划任务 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _add_registry_item(name: str, path: str) -> bool:
        """添加注册表启动项"""
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
            logger.error(f"添加注册表启动项 {name} 时出错: {e}")
            return False
    
    @staticmethod
    def _add_folder_item(name: str, path: str) -> bool:
        """添加启动文件夹项"""
        try:
            startup_folder = shell.SHGetFolderPath(0, shellcon.CSIDL_STARTUP, 0, 0)
            shortcut_path = os.path.join(startup_folder, f"{name}.lnk")
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = path
            shortcut.save()
            return True
        except Exception as e:
            logger.error(f"添加启动文件夹项 {name} 时出错: {e}")
            return False 