import os
import platform
import subprocess
import psutil
import socket
import uuid
from datetime import datetime
from PyQt5.QtCore import QThread
import logging
import time

class PlatformManager:
    """平台相关的工具函数"""
    def __init__(self):
        self.current_system = platform.system().lower()
        self.logger = logging.getLogger('GlaryUtilities')

    def is_windows(self):
        """检查当前操作系统是否为Windows"""
        return self.current_system == 'windows'
    
    def is_linux(self):
        """检查当前操作系统是否为Linux"""
        return self.current_system == 'linux'
    
    def is_mac(self):
        """检查当前操作系统是否为macOS"""
        return self.current_system == 'darwin'
    
class SystemInformation(PlatformManager):
    """平台相关的工具函数"""
    
    _instance = None  # 类变量，用于存储单例实例
    _temp_failure_count = 0  # 温度数据获取失败计数
    _temp_retry_delay = 1  # 温度数据重试延迟时间（秒）
    _temp_last_attempt = 0  # 上次尝试获取温度的时间戳
    _MAX_RETRY_DELAY = 1000000  # 最大重试延迟时间（秒）

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SystemInformation, cls).__new__(cls)
            cls._instance._initialized = False  # 标记为未初始化
        return cls._instance

    def __init__(self):
        # 确保初始化只执行一次
        if not hasattr(self, '_initialized') or not self._initialized:
            super().__init__()
            self._initialized = True  # 标记为已初始化

    def get_drives_list(self):
        """获取系统所有驱动器列表，返回驱动器字典列表，包含名称、类型等信息"""
        if self.is_windows():
            return self._get_drives_list_windows()
        elif self.is_linux() or self.is_mac():
            return self._get_drives_list_unix()
        else:
            return []
        
    def _get_drives_list_windows(self):
        """获取系统所有驱动器列表，返回驱动器字典列表，包含名称、类型等信息"""
        try:
            drives = []
            if self.is_windows():
                import win32api
                import win32file
                
                drive_strings = win32api.GetLogicalDriveStrings()
                drive_letters = drive_strings.split('\000')[:-1]  # 删除最后一个空字符串
                
                for drive in drive_letters:
                    try:
                        drive_type = win32file.GetDriveType(drive)
                        drive_type_name = {
                            0: "未知",
                            1: "不存在",
                            2: "可移动磁盘",
                            3: "硬盘",
                            4: "网络硬盘",
                            5: "光盘",
                            6: "RAM磁盘"
                        }.get(drive_type, "未知")
                        
                        # 检查驱动器是否可访问
                        accessible = os.access(drive, os.R_OK)
                        
                        # 获取卷标（如果可能）
                        volume_name = ""
                        try:
                            volume_info = win32api.GetVolumeInformation(drive)
                            if volume_info and volume_info[0]:
                                volume_name = volume_info[0]
                        except:
                            pass
                        
                        # 创建显示名称（驱动器盘符 + 卷标）
                        display_name = drive
                        if volume_name:
                            display_name = f"{drive} ({volume_name})"
                        
                        # 创建驱动器信息字典
                        drive_info = {
                            "name": drive,
                            "display_name": display_name,
                            "type": drive_type_name,
                            "accessible": accessible,
                            "volume_name": volume_name
                        }
                        
                        drives.append(drive_info)
                    except Exception as e:
                        self.logger.warning(f"获取驱动器 {drive} 信息出错: {e}")
                        continue
                
            return drives  # 确保返回驱动器列表

        except Exception as e:
            self.logger.error(f"获取驱动器列表时出错: {e}")
            return []
        
    def _get_drives_list_unix(self):
        """获取Unix系统所有驱动器列表，返回驱动器字典列表，包含名称、类型等信息"""
        try:
            drives = []
            # 对于Unix系统，返回根目录
            drives.append({
                "name": "/",
                "display_name": "根目录 (/)",
                "type": "文件系统",
                "accessible": os.access("/", os.R_OK),
                "volume_name": ""
            })
                
            return drives
        except Exception as e:
            self.logger.error(f"获取Unix系统驱动器列表时出错: {e}")
            return []
    
    def get_home_dir(self):
        """获取用户主目录路径"""
        try:
            home = os.path.expanduser("~")
            return home
        except Exception as e:
            self.logger.error(f"获取用户主目录时出错: {e}")
            return os.path.dirname(os.path.abspath(__file__))
    
    def get_system_info(self):
        """获取系统基本信息"""
        try:
            info = {
                "os": platform.system() + " " + platform.release(),
                "version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
                "python_version": platform.python_version()
            }
            
            # 添加CPU信息
            cpu_info = self.get_cpu_info()
            info.update(cpu_info)
            
            # 添加内存信息
            memory = psutil.virtual_memory()
            info["memory_total"] = self.format_bytes(memory.total)
            info["memory_available"] = self.format_bytes(memory.available)
            info["memory_percent"] = f"{memory.percent}%"
            
            # 添加磁盘信息
            disk_info = {}
            for i, disk in enumerate(self.get_disk_info()):
                disk_info[f"disk_{i}_device"] = disk["device"]
                disk_info[f"disk_{i}_mountpoint"] = disk["mountpoint"]
                disk_info[f"disk_{i}_fstype"] = disk["fstype"]
                disk_info[f"disk_{i}_total"] = disk["total"]
                disk_info[f"disk_{i}_used"] = disk["used"]
            
            info.update(disk_info)
            
            return info
        except Exception as e:
            self.logger.error(f"获取系统信息时出错: {e}")
            return {"error": str(e)}
    
    def get_cpu_info(self):
        """获取CPU信息"""
        try:
            info = {}
            
            # 基本信息
            info["cpu_brand"] = platform.processor()
            info["cpu_cores_physical"] = psutil.cpu_count(logical=False)
            info["cpu_cores_logical"] = psutil.cpu_count(logical=True)
            
            # CPU频率
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                info["cpu_freq_current"] = f"{cpu_freq.current:.2f} MHz"
                if hasattr(cpu_freq, "min") and cpu_freq.min:
                    info["cpu_freq_min"] = f"{cpu_freq.min:.2f} MHz"
                if hasattr(cpu_freq, "max") and cpu_freq.max:
                    info["cpu_freq_max"] = f"{cpu_freq.max:.2f} MHz"
            
            # CPU使用率
            info["cpu_percent"] = f"{psutil.cpu_percent(interval=0.1)}%"
            
            return info
        except Exception as e:
            self.logger.error(f"获取CPU信息时出错: {e}")
            return {"cpu_error": str(e)}
    
    def get_memory_info(self):
        """获取内存信息"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            info = {
                "Total Physical Memory": self.format_bytes(memory.total),
                "Available Memory": self.format_bytes(memory.available),
                "Used Memory": self.format_bytes(memory.used),
                "Memory Usage": f"{memory.percent}%",
                "Total Swap": self.format_bytes(swap.total),
                "Used Swap": self.format_bytes(swap.used),
                "Swap Usage": f"{swap.percent}%"
            }
            
            return info
        except Exception as e:
            self.logger.error(f"获取内存信息时出错: {e}")
            return {"Memory Error": str(e)}
    
    def get_disk_info(self):
        """获取磁盘信息"""
        try:
            disks = []
            
            # 获取所有磁盘分区
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk = {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": self.format_bytes(usage.total),
                        "used": self.format_bytes(usage.used),
                        "free": self.format_bytes(usage.free),
                        "percent": f"{usage.percent}%"
                    }
                    disks.append(disk)
                except (PermissionError, OSError) as e:
                    # 某些卷可能无法访问
                    continue
            
            return disks
        except Exception as e:
            self.logger.error(f"获取磁盘信息时出错: {e}")
            return []
    
    def get_network_info(self):
        """获取网络信息"""
        try:
            info = {}
            
            # 获取主机名和IP地址
            info["hostname"] = socket.gethostname()
            try:
                info["ip_address"] = socket.gethostbyname(info["hostname"])
            except:
                info["ip_address"] = "Unknown"
            
            # 获取MAC地址
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                  for elements in range(0, 8 * 6, 8)][::-1])
            info["mac_address"] = mac_address
            
            # 获取网络接口
            interfaces = []
            for name, addrs in psutil.net_if_addrs().items():
                interface = {"name": name, "addresses": []}
                for addr in addrs:
                    address_info = {}
                    if addr.family == socket.AF_INET:
                        address_info["type"] = "IPv4"
                        address_info["address"] = addr.address
                        address_info["netmask"] = addr.netmask
                    elif addr.family == socket.AF_INET6:
                        address_info["type"] = "IPv6"
                        address_info["address"] = addr.address
                        address_info["netmask"] = addr.netmask
                    elif addr.family == psutil.AF_LINK:
                        address_info["type"] = "MAC"
                        address_info["address"] = addr.address
                    
                    if address_info:
                        interface["addresses"].append(address_info)
                
                if interface["addresses"]:
                    interfaces.append(interface)
            
            # info["interfaces"] = interfaces
            
            return info
        except Exception as e:
            self.logger.error(f"获取网络信息时出错: {e}")
            return {"error": str(e)}
    
    def format_bytes(self, bytes_value):
        """格式化字节数为可读字符串"""
        try:
            for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
                if bytes_value < 1024.0:
                    return f"{bytes_value:.2f} {unit}"
                bytes_value /= 1024.0
            return f"{bytes_value:.2f} PB"
        except:
            return "Unknown"
        
    def _format_timestamp(self, timestamp):
        """Format timestamp to a readable date/time string"""
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_gpu_info(self):
        """获取GPU信息，优先使用GPUtil库，若不可用则使用命令行工具"""
        try:
            gpu_info = None
            # 尝试使用GPUtil库获取信息
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    info = []
                    for gpu in gpus:
                        gpu_info = [
                            f"名称: {gpu.name}",
                            f"显存: {gpu.memoryTotal} MB",
                            f"驱动版本: {gpu.driver}",
                            f"显存使用率: {gpu.memoryUtil*100:.1f}%",
                            f"GPU使用率: {gpu.load*100:.1f}%",
                            f"温度: {gpu.temperature}°C" if hasattr(gpu, 'temperature') else "温度: 未知"
                        ]
                        info.append("\n".join(gpu_info))
                    return "\n\n".join(info)
                
                # GPUtil找不到GPU
                gpu_info = "使用GPUtil未检测到GPU, "
            
            except ImportError:
                self.logger.info("GPUtil库不可用，尝试使用命令行获取GPU信息")
                # 继续使用命令行获取信息
                pass
            
            # 使用系统命令获取GPU信息
            if self.is_windows():
                return self._get_gpu_info_windows()
            elif self.is_linux():
                return self._get_gpu_info_linux()
            elif self.is_mac():
                return self._get_gpu_info_mac()
            else:
                gpu_info += "使用命令行，不支持的操作系统"
            
            return gpu_info
        
        except Exception as e:
            self.logger.error(f"获取GPU信息时出错: {str(e)}")
            return f"GPU信息错误: {str(e)}"
    
    def _get_gpu_info_windows(self):
        """使用wmic命令在Windows上获取GPU信息"""
        try:
            # 尝试使用wmic获取信息
            process = subprocess.Popen(
                ["wmic", "path", "win32_VideoController", "get", "Name,AdapterRAM,DriverVersion,VideoProcessor,DriverDate"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if stderr:
                self.logger.warning(f"wmic命令执行出错: {stderr}")
            
            if not stdout or stdout.strip() == "":
                # 尝试使用PowerShell获取信息
                return self._get_gpu_info_windows_powershell()
            
            # 处理wmic输出
            lines = stdout.splitlines()
            if len(lines) <= 1:
                return self._get_gpu_info_windows_powershell()
            
            # 删除表头并过滤掉空行
            data_lines = [line for line in lines[1:] if line.strip()]
            
            if not data_lines:
                return self._get_gpu_info_windows_powershell()
            
            # 提取GPU信息
            info = []
            for i, line in enumerate(data_lines):
                parts = line.split()
                if not parts:
                    continue
                
                # 尝试解析wmic输出
                try:
                    # 解析AdapterRAM（通常是第一个数字）
                    ram = None
                    processor = None
                    driver = None
                    driver_date = None
                    name_parts = []
                    
                    for part in parts:
                        if part.isdigit() and ram is None:
                            try:
                                ram = int(part) / (1024 * 1024)  # 转换为MB
                            except:
                                pass
                        elif "." in part and driver is None and any(c.isdigit() for c in part):
                            driver = part
                        elif part.startswith(("AMD", "NVIDIA", "Intel", "GeForce", "Radeon")):
                            processor = part
                        elif "/" in part and driver_date is None and len(part) > 8:
                            driver_date = part
                        else:
                            name_parts.append(part)
                    
                    name = " ".join(name_parts) if name_parts else f"GPU {i+1}"
                    
                    gpu_info = [f"名称: {name}"]
                    if processor:
                        gpu_info.append(f"处理器: {processor}")
                    if ram:
                        gpu_info.append(f"显存: {ram:.0f} MB")
                    if driver:
                        gpu_info.append(f"驱动版本: {driver}")
                    if driver_date:
                        gpu_info.append(f"驱动日期: {driver_date}")
                    
                    # 如果信息太少，尝试使用dxdiag获取更多信息
                    if len(gpu_info) < 3:
                        dxdiag_info = self._get_gpu_info_windows_dxdiag(i)
                        if dxdiag_info and "名称:" in dxdiag_info:
                            gpu_info = dxdiag_info.split("\n")
                    
                    info.append("\n".join(gpu_info))
                except Exception as e:
                    self.logger.warning(f"解析GPU行出错: {e}")
                    info.append(f"GPU {i+1}: {line}")
            
            return "\n\n".join(info) if info else self._get_gpu_info_windows_powershell()
            
        except Exception as e:
            self.logger.error(f"Windows GPU信息获取失败: {str(e)}")
            return self._get_gpu_info_windows_powershell()
    
    def _get_gpu_info_windows_powershell(self):
        """使用PowerShell获取GPU信息"""
        try:
            process = subprocess.Popen(
                ["powershell", "-Command", "Get-WmiObject win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion, VideoProcessor, DriverDate | Format-List"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if stderr:
                self.logger.warning(f"PowerShell命令执行出错: {stderr}")
            
            if not stdout or stdout.strip() == "":
                # 尝试使用DirectX诊断工具
                return self._get_gpu_info_windows_dxdiag()
            
            # 处理PowerShell输出
            info = []
            current_gpu = []
            
            for line in stdout.splitlines():
                line = line.strip()
                if not line:
                    if current_gpu:
                        info.append("\n".join(current_gpu))
                        current_gpu = []
                    continue
                
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    if key == "Name":
                        current_gpu.append(f"名称: {value}")
                    elif key == "AdapterRAM":
                        try:
                            ram = int(value) / (1024 * 1024)
                            current_gpu.append(f"显存: {ram:.0f} MB")
                        except:
                            if value:
                                current_gpu.append(f"显存: {value}")
                    elif key == "DriverVersion":
                        current_gpu.append(f"驱动版本: {value}")
                    elif key == "VideoProcessor":
                        current_gpu.append(f"处理器: {value}")
                    elif key == "DriverDate":
                        current_gpu.append(f"驱动日期: {value}")
            
            if current_gpu:
                info.append("\n".join(current_gpu))
            
            return "\n\n".join(info) if info else self._get_gpu_info_windows_dxdiag()
            
        except Exception as e:
            self.logger.error(f"PowerShell GPU信息获取失败: {str(e)}")
            return self._get_gpu_info_windows_dxdiag()
            
    def _get_gpu_info_windows_dxdiag(self, gpu_index=None):
        """使用DirectX诊断工具获取GPU信息"""
        try:
            # 创建临时文件用于输出
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
                tmp_path = tmp.name
            
            # 运行dxdiag并输出到文件
            process = subprocess.Popen(
                ["dxdiag", "/t", tmp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            process.communicate()
            
            # 等待一会儿让dxdiag完成输出
            time.sleep(2)
            
            # 读取输出文件
            gpu_sections = []
            current_section = None
            display_section = False
            
            try:
                with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        if line.startswith("-------------"):
                            if current_section and display_section:
                                gpu_sections.append(current_section)
                            current_section = []
                            display_section = False
                        elif line.startswith("Display Devices"):
                            display_section = True
                            current_section = []
                        elif current_section is not None and display_section:
                            current_section.append(line)
                
                # 添加最后一个GPU段
                if current_section and display_section:
                    gpu_sections.append(current_section)
                
                # 清理临时文件
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                
                # 解析GPU信息
                if gpu_index is not None and 0 <= gpu_index < len(gpu_sections):
                    # 返回指定索引的GPU信息
                    return self._parse_dxdiag_display_section(gpu_sections[gpu_index])
                else:
                    # 返回所有GPU信息
                    info = []
                    for section in gpu_sections:
                        parsed = self._parse_dxdiag_display_section(section)
                        if parsed:
                            info.append(parsed)
                    
                    return "\n\n".join(info) if info else "未检测到GPU"
                
            except Exception as e:
                self.logger.error(f"读取dxdiag输出失败: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"DirectX诊断工具执行失败: {str(e)}")
            return "获取GPU信息失败"
    
    def _parse_dxdiag_display_section(self, section_lines):
        """解析DxDiag显示设备部分"""
        gpu_info = []
        
        for line in section_lines:
            if ":" not in line:
                continue
                
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            if "Card name" in key:
                gpu_info.append(f"名称: {value}")
            elif "Manufacturer" in key:
                gpu_info.append(f"制造商: {value}")
            elif "Chip type" in key:
                gpu_info.append(f"芯片类型: {value}")
            elif "Display Memory" in key:
                gpu_info.append(f"显存: {value}")
            elif "Driver Version" in key or "Driver" in key and "Version" in key:
                gpu_info.append(f"驱动版本: {value}")
            elif "Driver Date/Size" in key:
                gpu_info.append(f"驱动日期: {value.split(',')[0]}")
            elif "Current Mode" in key:
                gpu_info.append(f"当前模式: {value}")
            elif "Monitor Model" in key:
                gpu_info.append(f"显示器型号: {value}")
            elif "Monitor Name" in key:
                gpu_info.append(f"显示器: {value}")
        
        return "\n".join(gpu_info) if gpu_info else None

    def _get_gpu_info_linux(self):
        """使用lspci命令在Linux上获取GPU信息"""
        try:
            # 检查lspci命令是否可用
            try:
                subprocess.check_output(["which", "lspci"])
            except:
                return "无法获取GPU信息：lspci命令不可用"
            
            # 获取显卡信息
            process = subprocess.Popen(
                ["lspci", "-vnn", "|", "grep", "-i", "VGA", "-A", "12"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if stderr:
                self.logger.warning(f"lspci命令执行出错: {stderr}")
            
            if not stdout or stdout.strip() == "":
                # 尝试nvidia-smi命令（如果有NVIDIA显卡）
                try:
                    process = subprocess.Popen(
                        ["nvidia-smi", "--query-gpu=name,memory.total,driver_version,utilization.gpu,temperature.gpu", "--format=csv,noheader"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    stdout, stderr = process.communicate()
                    
                    if stderr and "not found" in stderr:
                        return "未检测到NVIDIA GPU"
                    
                    if not stdout or stdout.strip() == "":
                        return "未检测到GPU"
                    
                    # 处理nvidia-smi输出
                    info = []
                    for i, line in enumerate(stdout.splitlines()):
                        if not line.strip():
                            continue
                        
                        parts = line.split(",")
                        if len(parts) >= 5:
                            gpu_info = [
                                f"名称: {parts[0].strip()}",
                                f"显存: {parts[1].strip()}",
                                f"驱动版本: {parts[2].strip()}",
                                f"GPU使用率: {parts[3].strip()}",
                                f"温度: {parts[4].strip()}"
                            ]
                            info.append("\n".join(gpu_info))
                        else:
                            info.append(f"GPU {i+1}: {line.strip()}")
                    
                    return "\n\n".join(info) if info else "未检测到GPU"
                    
                except Exception as e:
                    self.logger.warning(f"nvidia-smi命令执行出错: {e}")
                    return "未检测到GPU"
            
            # 处理lspci输出
            info = []
            gpu_blocks = stdout.split("\n\n")
            
            for i, block in enumerate(gpu_blocks):
                if not block.strip():
                    continue
                
                lines = block.splitlines()
                gpu_name = "未知GPU"
                gpu_info = []
                
                for line in lines:
                    line = line.strip()
                    if "VGA compatible controller" in line or "3D controller" in line:
                        # 提取GPU名称
                        parts = line.split(":")
                        if len(parts) > 2:
                            gpu_name = parts[2].strip()
                        else:
                            gpu_name = line
                    
                    if "Memory" in line or "memory" in line:
                        gpu_info.append(f"内存: {line}")
                    if "Kernel driver in use" in line:
                        gpu_info.append(f"驱动: {line.split(':')[1].strip()}")
                    if "Kernel modules" in line:
                        gpu_info.append(f"模块: {line.split(':')[1].strip()}")
                
                block_info = [f"名称: {gpu_name}"]
                block_info.extend(gpu_info)
                info.append("\n".join(block_info))
            
            return "\n\n".join(info) if info else "未检测到GPU"
            
        except Exception as e:
            self.logger.error(f"Linux GPU信息获取失败: {str(e)}")
            return f"获取GPU信息失败: {str(e)}"
    
    def _get_gpu_info_mac(self):
        """使用system_profiler命令在macOS上获取GPU信息"""
        try:
            # 使用system_profiler获取GPU信息
            process = subprocess.Popen(
                ["system_profiler", "SPDisplaysDataType"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if stderr:
                self.logger.warning(f"system_profiler命令执行出错: {stderr}")
            
            if not stdout or stdout.strip() == "":
                return "未检测到GPU"
            
            # 处理system_profiler输出
            in_graphics_card = False
            current_gpu = []
            info = []
            
            for line in stdout.splitlines():
                line = line.strip()
                
                if not line:
                    continue
                
                if "Graphics" in line or "Chipset Model" in line:
                    if current_gpu:
                        info.append("\n".join(current_gpu))
                        current_gpu = []
                    in_graphics_card = True
                    if "Chipset Model" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            current_gpu.append(f"名称: {parts[1].strip()}")
                elif in_graphics_card:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        if "VRAM" in key:
                            current_gpu.append(f"显存: {value.strip()}")
                        elif "Vendor" in key:
                            current_gpu.append(f"厂商: {value.strip()}")
                        elif "Device" in key:
                            current_gpu.append(f"设备ID: {value.strip()}")
                        elif "Metal" in key:
                            current_gpu.append(f"Metal支持: {value.strip()}")
                    
                    if "Displays" in line:
                        in_graphics_card = False
            
            # 添加最后一个GPU
            if current_gpu:
                info.append("\n".join(current_gpu))
            
            return "\n\n".join(info) if info else "未检测到GPU"
            
        except Exception as e:
            self.logger.error(f"macOS GPU信息获取失败: {str(e)}")
            return f"获取GPU信息失败: {str(e)}" 
        
    def get_os_info(self):
        """Get operating system information"""
        os_info = {}
        
        try:
            os_info["System"] = platform.system()
            os_info["Release"] = platform.release()
            os_info["Version"] = platform.version()
            
            if platform.system() == "Windows":
                import winreg
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                        os_info["Product Name"] = winreg.QueryValueEx(key, "ProductName")[0]
                        os_info["Build Number"] = winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
                except Exception:
                    pass
            
            os_info["Platform"] = platform.platform()
            os_info["Hostname"] = platform.node()
            
            # Get boot time
            boot_time = psutil.boot_time()
            boot_time_str = self._format_timestamp(boot_time)
            os_info["Boot Time"] = boot_time_str
            
        except Exception as e:
            os_info["Error"] = str(e)
        
        return os_info
    
    def get_python_info(self):
        """Get Python information"""
        python_info = {}
        
        try:
            python_info["Version"] = platform.python_version()
            python_info["Implementation"] = platform.python_implementation()
            python_info["Compiler"] = platform.python_compiler()
            python_info["Build"] = ' '.join(platform.python_build())
            
        except Exception as e:
            python_info["Error"] = str(e)
        
        return python_info
    
    def get_disk_table_data(self):
        """获取磁盘表格数据
        
        Returns:
            list: 包含磁盘信息的列表，每个元素是一个字典，包含device、mountpoint、fstype、total、used等信息
        """
        try:
            disk_data = []
            for partition in psutil.disk_partitions():
                try:
                    disk_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype
                    }
                    
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_info['total'] = self.format_bytes(usage.total)
                        disk_info['used'] = f"{usage.percent}%"
                    except PermissionError:
                        disk_info['total'] = "N/A"
                        disk_info['used'] = "N/A"
                    except Exception as e:
                        disk_info['total'] = "Error"
                        disk_info['used'] = str(e)
                    
                    disk_data.append(disk_info)
                    
                except Exception as e:
                    disk_data.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': "Error",
                        'used': str(e)
                    })
            
            return disk_data
        
        except Exception as e:
            self.logger.error(f"获取磁盘表格数据时出错: {e}")
            return [{
                'device': "Error",
                'mountpoint': str(e),
                'fstype': "",
                'total': "",
                'used': ""
            }]

    def get_network_interfaces_data(self):
        """获取网络接口表格数据
        
        Returns:
            list: 包含网络接口信息的列表，每个元素是一个字典，包含name、address、netmask、status等信息
        """
        try:
            interface_data = []
            for name, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:  # IPv4
                        interface_info = {
                            'name': name,
                            'address': addr.address,
                            'netmask': addr.netmask,
                            'status': "Unknown"
                        }
                        
                        # 获取接口状态
                        try:
                            stats = psutil.net_if_stats()
                            if name in stats:
                                interface_info['status'] = "Up" if stats[name].isup else "Down"
                        except:
                            pass
                        
                        interface_data.append(interface_info)
            
            return interface_data
        
        except Exception as e:
            self.logger.error(f"获取网络接口表格数据时出错: {e}")
            return []

    def get_drives(self):
        """获取系统所有驱动器列表，get_drives_list 的别名"""
        return self.get_drives_list()

    def get_temperature(self):
        """获取系统温度信息，兼容不同操作系统"""
        current_time = time.time()
        
        # 检查是否需要等待更长时间再次尝试
        if self._temp_failure_count > 1:
            time_elapsed = current_time - self._temp_last_attempt
            if time_elapsed < self._temp_retry_delay:
                self.logger.info(f"等待重试周期 {self._temp_retry_delay}秒，距离下次尝试还有 {self._temp_retry_delay - time_elapsed:.1f}秒")
                # 直接返回 N/A，避免频繁报错
                return {"CPU": "N/A", "System": "N/A"}
        
        # 更新尝试时间
        self._temp_last_attempt = current_time
        
        try:
            temperature_data = {}
            
            # 尝试使用 psutil.sensors_temperatures() 获取温度
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    for chip, sensors in temps.items():
                        for sensor in sensors:
                            label = sensor.label or f"{chip}_{sensors.index(sensor)}"
                            temperature_data[label] = f"{sensor.current:.1f}°C"
                    # 成功获取温度，重置失败计数和延迟
                    self._temp_failure_count = 0
                    self._temp_retry_delay = 1
                    return temperature_data
            
            # 在 Windows 系统上，尝试使用 WMI 获取温度
            if self.is_windows():
                try:
                    import wmi
                    w = wmi.WMI(namespace="root\\wmi")
                    temperature_info = w.MSAcpi_ThermalZoneTemperature()[0]
                    # 转换为摄氏度 (原始值是 Kelvin * 10)
                    temp_celsius = (temperature_info.CurrentTemperature / 10) - 273.15
                    temperature_data["CPU"] = f"{temp_celsius:.1f}°C"
                    # 成功获取温度，重置失败计数和延迟
                    self._temp_failure_count = 0
                    self._temp_retry_delay = 1
                    return temperature_data
                except Exception as e:
                    self.logger.warning(f"获取 WMI 温度信息失败: {e}")
            
            # 在 Linux 系统上，尝试从 /sys/class/thermal 读取温度
            if self.is_linux():
                try:
                    thermal_zones = [f for f in os.listdir("/sys/class/thermal") if f.startswith("thermal_zone")]
                    for zone in thermal_zones:
                        try:
                            with open(f"/sys/class/thermal/{zone}/temp", "r") as f:
                                temp = int(f.read().strip()) / 1000  # 通常以毫摄氏度为单位
                            with open(f"/sys/class/thermal/{zone}/type", "r") as f:
                                zone_type = f.read().strip()
                            temperature_data[zone_type] = f"{temp:.1f}°C"
                        except:
                            pass
                    if temperature_data:
                        # 成功获取温度，重置失败计数和延迟
                        self._temp_failure_count = 0
                        self._temp_retry_delay = 1
                        return temperature_data
                except Exception as e:
                    self.logger.warning(f"读取 Linux 温度信息失败: {e}")
            
            # 如果上述方法都失败，增加失败计数并延长重试时间
            self._temp_failure_count += 1
            
            # 如果连续失败超过两次，指数级增加延迟时间
            if self._temp_failure_count >= 2:
                self._temp_retry_delay = min(self._temp_retry_delay * 2, self._MAX_RETRY_DELAY)
                self.logger.info(f"连续 {self._temp_failure_count} 次获取温度失败，下次重试延迟增加到 {self._temp_retry_delay} 秒")
            
            # 如果上述方法都失败，返回 N/A
            self.logger.info("无法获取真实温度数据，返回 N/A")
            temperature_data["CPU"] = "N/A"
            temperature_data["System"] = "N/A"
            return temperature_data
            
        except Exception as e:
            # 发生错误时也增加失败计数并延长重试时间
            self._temp_failure_count += 1
            if self._temp_failure_count >= 2:
                self._temp_retry_delay = min(self._temp_retry_delay * 2, self._MAX_RETRY_DELAY)
                self.logger.info(f"连续 {self._temp_failure_count} 次获取温度失败，下次重试延迟增加到 {self._temp_retry_delay} 秒")
                
            self.logger.error(f"获取温度信息时出错: {e}")
            return {"Error": f"获取温度失败: {str(e)}"}

    def get_system_temperatures(self):
        """获取系统温度的别名"""
        return self.get_temperature()

class BaseThread(QThread):
    """Base thread class for all application threads"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger('GlaryUtilities')
        self.platform_manager = PlatformManager()

