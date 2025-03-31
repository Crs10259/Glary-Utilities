import os
import sys
import platform
import subprocess
import shutil
import tempfile

class PlatformUtils:
    """提供多平台兼容的工具函数的工具类"""
    
    @staticmethod
    def get_system():
        """获取当前操作系统类型
        
        Returns:
            str: 'Windows', 'Linux', 'Darwin' (macOS), 或 'Unknown'
        """
        system = platform.system()
        if system in ['Windows', 'Linux', 'Darwin']:
            return system
        return 'Unknown'
    
    @staticmethod
    def is_windows():
        """检查当前操作系统是否为Windows
        
        Returns:
            bool: 如果是Windows则返回True
        """
        return platform.system() == 'Windows'
    
    @staticmethod
    def is_linux():
        """检查当前操作系统是否为Linux
        
        Returns:
            bool: 如果是Linux则返回True
        """
        return platform.system() == 'Linux'
    
    @staticmethod
    def is_macos():
        """检查当前操作系统是否为macOS
        
        Returns:
            bool: 如果是macOS则返回True
        """
        return platform.system() == 'Darwin'
    
    @staticmethod
    def get_home_dir():
        """获取用户主目录
        
        Returns:
            str: 用户主目录的绝对路径
        """
        return os.path.expanduser('~')
    
    @staticmethod
    def get_temp_dir():
        """获取临时目录
        
        Returns:
            str: 临时目录的绝对路径
        """
        return tempfile.gettempdir()
    
    @staticmethod
    def get_drives():
        """获取可用驱动器列表
        
        Returns:
            list: 可用驱动器列表，每个元素是一个字典，包含驱动器信息
        """
        drives = []
        
        if PlatformUtils.is_windows():
            # Windows，使用Windows API获取驱动器
            try:
                from ctypes import windll
                import string
                
                # 获取驱动器位掩码
                bitmask = windll.kernel32.GetLogicalDrives()
                
                # 将位掩码转换为驱动器字母
                for letter in string.ascii_uppercase:  # A到Z
                    if bitmask & (1 << (ord(letter) - ord('A'))):
                        drive = f"{letter}:"
                        try:
                            # 检查驱动器类型
                            drive_path = f"{drive}\\"
                            drive_type = windll.kernel32.GetDriveTypeW(drive_path)
                            
                            # 确定驱动器类型
                            if drive_type == 2:
                                type_name = "可移动"
                            elif drive_type == 3:
                                type_name = "固定"
                            elif drive_type == 4:
                                type_name = "网络"
                            elif drive_type == 5:
                                type_name = "光盘"
                            else:
                                type_name = "未知"
                            
                            # 检查驱动器是否可访问
                            if os.path.exists(drive):
                                try:
                                    # 获取可用空间
                                    total, used, free = shutil.disk_usage(drive)
                                    drives.append({
                                        "name": drive,
                                        "display_name": f"{drive} ({type_name})",
                                        "type": type_name,
                                        "total": total,
                                        "free": free,
                                        "accessible": True
                                    })
                                except:
                                    drives.append({
                                        "name": drive,
                                        "display_name": f"{drive} ({type_name})",
                                        "type": type_name,
                                        "accessible": False
                                    })
                        except:
                            # 驱动器不可访问
                            pass
            except Exception as e:
                print(f"获取驱动器列表时出错: {e}")
        
        elif PlatformUtils.is_linux():
            # Linux，获取挂载点
            try:
                # 使用df命令获取挂载信息
                result = subprocess.run(['df', '-h'], stdout=subprocess.PIPE, text=True)
                
                # 解析输出
                lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 6:
                        device = parts[0]
                        mount_point = parts[5]
                        
                        # 跳过特殊文件系统
                        if device.startswith('/dev/'):
                            try:
                                total, used, free = shutil.disk_usage(mount_point)
                                drives.append({
                                    "name": mount_point,
                                    "display_name": f"{mount_point} ({device})",
                                    "device": device,
                                    "total": total,
                                    "free": free,
                                    "accessible": True
                                })
                            except:
                                # 无法访问的挂载点
                                pass
            except Exception as e:
                print(f"获取挂载点列表时出错: {e}")
        
        elif PlatformUtils.is_macos():
            # macOS，获取卷
            try:
                # 使用df命令获取挂载信息
                result = subprocess.run(['df', '-h'], stdout=subprocess.PIPE, text=True)
                
                # 解析输出
                lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 9:
                        device = parts[0]
                        mount_point = parts[8]
                        
                        # 跳过特殊文件系统
                        if device.startswith('/dev/'):
                            try:
                                total, used, free = shutil.disk_usage(mount_point)
                                drives.append({
                                    "name": mount_point,
                                    "display_name": mount_point,
                                    "device": device,
                                    "total": total,
                                    "free": free,
                                    "accessible": True
                                })
                            except:
                                # 无法访问的挂载点
                                pass
            except Exception as e:
                print(f"获取卷列表时出错: {e}")
        
        return drives
    
    @staticmethod
    def run_command(cmd, shell=False, check=False, capture_output=True, text=True, timeout=None):
        """运行命令并返回结果
        
        Args:
            cmd (list or str): 要运行的命令
            shell (bool): 是否在shell中运行命令
            check (bool): 如果命令返回非零退出状态，是否引发异常
            capture_output (bool): 是否捕获输出
            text (bool): 是否以文本模式捕获输出
            timeout (int): 命令超时秒数
            
        Returns:
            subprocess.CompletedProcess: 命令执行结果
        """
        try:
            # 在Windows上，使用CREATE_NO_WINDOW标志
            creation_flags = 0
            if PlatformUtils.is_windows() and hasattr(subprocess, 'CREATE_NO_WINDOW'):
                creation_flags = subprocess.CREATE_NO_WINDOW
            
            return subprocess.run(
                cmd,
                shell=shell,
                check=check,
                capture_output=capture_output,
                text=text,
                timeout=timeout,
                creationflags=creation_flags if PlatformUtils.is_windows() else 0
            )
        except Exception as e:
            # 处理错误
            if isinstance(e, subprocess.TimeoutExpired):
                print(f"命令执行超时: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
            else:
                print(f"命令执行错误: {e}")
            
            # 创建模拟的结果对象
            class MockResult:
                def __init__(self):
                    self.returncode = -1
                    self.stdout = ""
                    self.stderr = str(e)
            
            return MockResult()
    
    @staticmethod
    def get_executable_path(executable):
        """获取可执行文件的完整路径
        
        Args:
            executable (str): 可执行文件名
            
        Returns:
            str: 可执行文件的完整路径，如果找不到则返回None
        """
        try:
            # 在Windows上，.exe可能是隐含的
            if PlatformUtils.is_windows() and not executable.lower().endswith('.exe'):
                executable_with_ext = executable + '.exe'
            else:
                executable_with_ext = executable
            
            # 使用which或where命令查找可执行文件
            if PlatformUtils.is_windows():
                result = PlatformUtils.run_command(['where', executable_with_ext])
            else:
                result = PlatformUtils.run_command(['which', executable])
            
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip().split('\n')[0]  # 返回第一个匹配项
            
            return None
        except Exception as e:
            print(f"查找可执行文件时出错: {e}")
            return None 