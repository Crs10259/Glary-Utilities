import os
import sys
import platform
import subprocess
import psutil
import shutil
import socket
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PlatformUtils:
    """平台相关的工具函数"""
    
    @staticmethod
    def is_windows():
        """检查当前操作系统是否为Windows"""
        return platform.system().lower() == 'windows'
    
    @staticmethod
    def is_linux():
        """检查当前操作系统是否为Linux"""
        return platform.system().lower() == 'linux'
    
    @staticmethod
    def is_mac():
        """检查当前操作系统是否为macOS"""
        return platform.system().lower() == 'darwin'
    
    @staticmethod
    def get_drives():
        """获取系统所有驱动器列表，返回驱动器字典列表，包含名称、类型等信息"""
        try:
            drives = []
            if PlatformUtils.is_windows():
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
                        logger.warning(f"获取驱动器 {drive} 信息出错: {e}")
                        continue
                        
            elif PlatformUtils.is_linux() or PlatformUtils.is_mac():
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
            logger.error(f"获取驱动器列表时出错: {e}")
            return []
    
    @staticmethod
    def get_home_dir():
        """获取用户主目录路径"""
        try:
            home = os.path.expanduser("~")
            return home
        except Exception as e:
            logger.error(f"获取用户主目录时出错: {e}")
            return os.path.dirname(os.path.abspath(__file__))
    
    @staticmethod
    def get_system_info():
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
            cpu_info = PlatformUtils.get_cpu_info()
            info.update(cpu_info)
            
            # 添加内存信息
            memory = psutil.virtual_memory()
            info["memory_total"] = PlatformUtils.format_bytes(memory.total)
            info["memory_available"] = PlatformUtils.format_bytes(memory.available)
            info["memory_percent"] = f"{memory.percent}%"
            
            # 添加磁盘信息
            disk_info = {}
            for i, disk in enumerate(PlatformUtils.get_disk_info()):
                disk_info[f"disk_{i}_device"] = disk["device"]
                disk_info[f"disk_{i}_mountpoint"] = disk["mountpoint"]
                disk_info[f"disk_{i}_fstype"] = disk["fstype"]
                disk_info[f"disk_{i}_total"] = disk["total"]
                disk_info[f"disk_{i}_used"] = disk["used"]
            
            info.update(disk_info)
            
            return info
        except Exception as e:
            logger.error(f"获取系统信息时出错: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_cpu_info():
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
            logger.error(f"获取CPU信息时出错: {e}")
            return {"cpu_error": str(e)}
    
    @staticmethod
    def get_memory_info():
        """获取内存信息"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            info = {
                "Total Physical Memory": PlatformUtils.format_bytes(memory.total),
                "Available Memory": PlatformUtils.format_bytes(memory.available),
                "Used Memory": PlatformUtils.format_bytes(memory.used),
                "Memory Usage": f"{memory.percent}%",
                "Total Swap": PlatformUtils.format_bytes(swap.total),
                "Used Swap": PlatformUtils.format_bytes(swap.used),
                "Swap Usage": f"{swap.percent}%"
            }
            
            return info
        except Exception as e:
            logger.error(f"获取内存信息时出错: {e}")
            return {"Memory Error": str(e)}
    
    @staticmethod
    def get_disk_info():
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
                        "total": PlatformUtils.format_bytes(usage.total),
                        "used": PlatformUtils.format_bytes(usage.used),
                        "free": PlatformUtils.format_bytes(usage.free),
                        "percent": f"{usage.percent}%"
                    }
                    disks.append(disk)
                except (PermissionError, OSError) as e:
                    # 某些卷可能无法访问
                    continue
            
            return disks
        except Exception as e:
            logger.error(f"获取磁盘信息时出错: {e}")
            return []
    
    @staticmethod
    def get_network_info():
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
            
            info["interfaces"] = interfaces
            
            return info
        except Exception as e:
            logger.error(f"获取网络信息时出错: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def format_bytes(bytes_value):
        """格式化字节数为可读字符串"""
        try:
            for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
                if bytes_value < 1024.0:
                    return f"{bytes_value:.2f} {unit}"
                bytes_value /= 1024.0
            return f"{bytes_value:.2f} PB"
        except:
            return "Unknown"
    
    @staticmethod
    def get_gpu_info():
        """获取GPU信息，优先使用GPUtil库，若不可用则使用命令行工具"""
        try:
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
                return "使用GPUtil未检测到GPU"
            
            except ImportError:
                logger.info("GPUtil库不可用，尝试使用命令行获取GPU信息")
                # 继续使用命令行获取信息
                pass
            
            # 使用系统命令获取GPU信息
            if PlatformUtils.is_windows():
                return PlatformUtils._get_gpu_info_windows()
            elif PlatformUtils.is_linux():
                return PlatformUtils._get_gpu_info_linux()
            elif PlatformUtils.is_mac():
                return PlatformUtils._get_gpu_info_mac()
            else:
                return "不支持的操作系统"
                
        except Exception as e:
            logger.error(f"获取GPU信息时出错: {str(e)}")
            return f"GPU信息错误: {str(e)}"
    
    @staticmethod
    def _get_gpu_info_windows():
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
                logger.warning(f"wmic命令执行出错: {stderr}")
            
            if not stdout or stdout.strip() == "":
                # 尝试使用PowerShell获取信息
                return PlatformUtils._get_gpu_info_windows_powershell()
            
            # 处理wmic输出
            lines = stdout.splitlines()
            if len(lines) <= 1:
                return PlatformUtils._get_gpu_info_windows_powershell()
            
            # 删除表头并过滤掉空行
            data_lines = [line for line in lines[1:] if line.strip()]
            
            if not data_lines:
                return PlatformUtils._get_gpu_info_windows_powershell()
            
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
                        dxdiag_info = PlatformUtils._get_gpu_info_windows_dxdiag(i)
                        if dxdiag_info and "名称:" in dxdiag_info:
                            gpu_info = dxdiag_info.split("\n")
                    
                    info.append("\n".join(gpu_info))
                except Exception as e:
                    logger.warning(f"解析GPU行出错: {e}")
                    info.append(f"GPU {i+1}: {line}")
            
            return "\n\n".join(info) if info else PlatformUtils._get_gpu_info_windows_powershell()
            
        except Exception as e:
            logger.error(f"Windows GPU信息获取失败: {str(e)}")
            return PlatformUtils._get_gpu_info_windows_powershell()
    
    @staticmethod
    def _get_gpu_info_windows_powershell():
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
                logger.warning(f"PowerShell命令执行出错: {stderr}")
            
            if not stdout or stdout.strip() == "":
                # 尝试使用DirectX诊断工具
                return PlatformUtils._get_gpu_info_windows_dxdiag()
            
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
            
            return "\n\n".join(info) if info else PlatformUtils._get_gpu_info_windows_dxdiag()
            
        except Exception as e:
            logger.error(f"PowerShell GPU信息获取失败: {str(e)}")
            return PlatformUtils._get_gpu_info_windows_dxdiag()
            
    @staticmethod
    def _get_gpu_info_windows_dxdiag(gpu_index=None):
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
            import time
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
                    return PlatformUtils._parse_dxdiag_display_section(gpu_sections[gpu_index])
                else:
                    # 返回所有GPU信息
                    info = []
                    for section in gpu_sections:
                        parsed = PlatformUtils._parse_dxdiag_display_section(section)
                        if parsed:
                            info.append(parsed)
                    
                    return "\n\n".join(info) if info else "未检测到GPU"
                
            except Exception as e:
                logger.error(f"读取dxdiag输出失败: {e}")
                return None
                
        except Exception as e:
            logger.error(f"DirectX诊断工具执行失败: {str(e)}")
            return "获取GPU信息失败"
    
    @staticmethod
    def _parse_dxdiag_display_section(section_lines):
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
    
    @staticmethod
    def _get_gpu_info_linux():
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
                logger.warning(f"lspci命令执行出错: {stderr}")
            
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
                    logger.warning(f"nvidia-smi命令执行出错: {e}")
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
            logger.error(f"Linux GPU信息获取失败: {str(e)}")
            return f"获取GPU信息失败: {str(e)}"
    
    @staticmethod
    def _get_gpu_info_mac():
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
                logger.warning(f"system_profiler命令执行出错: {stderr}")
            
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
            logger.error(f"macOS GPU信息获取失败: {str(e)}")
            return f"获取GPU信息失败: {str(e)}" 