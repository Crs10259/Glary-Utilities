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
    """Platform-related utility functions"""
    def __init__(self):
        self.current_system = platform.system().lower()
        self.logger = logging.getLogger('GlaryUtilities')

    def is_windows(self):
        """Check if current operating system is Windows"""
        return self.current_system == 'windows'
    
    def is_linux(self):
        """Check if current operating system is Linux"""
        return self.current_system == 'linux'
    
    def is_mac(self):
        """Check if current operating system is macOS"""
        return self.current_system == 'darwin'
    
class SystemInformation(PlatformManager):
    """Platform-related utility functions"""
    
    _instance = None  # Class variable for storing singleton instance
    _temp_failure_count = 0  # Temperature data acquisition failure count
    _temp_retry_delay = 1  # Temperature data retry delay time (seconds)
    _temp_last_attempt = 0  # Timestamp of last temperature acquisition attempt
    _MAX_RETRY_DELAY = 1000000  # Maximum retry delay time (seconds)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SystemInformation, cls).__new__(cls)
            cls._instance._initialized = False  # Mark as uninitialized
        return cls._instance

    def __init__(self):
        # Ensure initialization only happens once
        if not hasattr(self, '_initialized') or not self._initialized:
            super().__init__()
            self._initialized = True  # Mark as initialized

    def get_drives_list(self):
        """Get list of all system drives, returns list of drive dictionaries containing name, type, etc."""
        if self.is_windows():
            return self._get_drives_list_windows()
        elif self.is_linux() or self.is_mac():
            return self._get_drives_list_unix()
        else:
            return []
        
    def _get_drives_list_windows(self):
        """Get list of all system drives, returns list of drive dictionaries containing name, type, etc."""
        try:
            drives = []
            if self.is_windows():
                import win32api
                import win32file
                
                drive_strings = win32api.GetLogicalDriveStrings()
                drive_letters = drive_strings.split('\000')[:-1]  # Remove last empty string
                
                for drive in drive_letters:
                    try:
                        drive_type = win32file.GetDriveType(drive)
                        drive_type_name = {
                            0: "Unknown",
                            1: "Not Exists",
                            2: "Removable Disk",
                            3: "Hard Disk",
                            4: "Network Disk",
                            5: "CD-ROM",
                            6: "RAM Disk"
                        }.get(drive_type, "Unknown")
                        
                        # Check if drive is accessible
                        accessible = os.access(drive, os.R_OK)
                        
                        # Get volume label (if possible)
                        volume_name = ""
                        try:
                            volume_info = win32api.GetVolumeInformation(drive)
                            if volume_info and volume_info[0]:
                                volume_name = volume_info[0]
                        except:
                            pass
                        
                        # Create display name (drive letter + volume label)
                        display_name = drive
                        if volume_name:
                            display_name = f"{drive} ({volume_name})"
                        
                        # Create drive information dictionary
                        drive_info = {
                            "name": drive,
                            "display_name": display_name,
                            "type": drive_type_name,
                            "accessible": accessible,
                            "volume_name": volume_name
                        }
                        
                        drives.append(drive_info)
                    except Exception as e:
                        self.logger.warning(f"Error getting drive {drive} information: {e}")
                        continue
                
            return drives  # Ensure drive list is returned

        except Exception as e:
            self.logger.error(f"Error getting drive list: {e}")
            return []
        
    def _get_drives_list_unix(self):
        """Get list of all Unix system drives, returns list of drive dictionaries containing name, type, etc."""
        try:
            drives = []
            # For Unix systems, return root directory
            drives.append({
                "name": "/",
                "display_name": "Root Directory (/)",
                "type": "File System",
                "accessible": os.access("/", os.R_OK),
                "volume_name": ""
            })
                
            return drives
        except Exception as e:
            self.logger.error(f"Error getting Unix system drive list: {e}")
            return []
    
    def get_home_dir(self):
        """Get user home directory path"""
        try:
            home = os.path.expanduser("~")
            return home
        except Exception as e:
            self.logger.error(f"Error getting user home directory: {e}")
            return os.path.dirname(os.path.abspath(__file__))
    
    def get_system_info(self):
        """Get basic system information"""
        try:
            info = {
                "os": platform.system() + " " + platform.release(),
                "version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
                "python_version": platform.python_version()
            }
            
            # Add CPU information
            cpu_info = self.get_cpu_info()
            info.update(cpu_info)
            
            # Add memory information
            memory = psutil.virtual_memory()
            info["memory_total"] = self.format_bytes(memory.total)
            info["memory_available"] = self.format_bytes(memory.available)
            info["memory_percent"] = f"{memory.percent}%"
            
            # Add disk information
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
            self.logger.error(f"Error getting system information: {e}")
            return {"error": str(e)}
    
    def get_cpu_info(self):
        """Get CPU information"""
        try:
            info = {}
            
            # Basic information
            info["cpu_brand"] = platform.processor()
            info["cpu_cores_physical"] = psutil.cpu_count(logical=False)
            info["cpu_cores_logical"] = psutil.cpu_count(logical=True)
            
            # CPU frequency
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                info["cpu_freq_current"] = f"{cpu_freq.current:.2f} MHz"
                if hasattr(cpu_freq, "min") and cpu_freq.min:
                    info["cpu_freq_min"] = f"{cpu_freq.min:.2f} MHz"
                if hasattr(cpu_freq, "max") and cpu_freq.max:
                    info["cpu_freq_max"] = f"{cpu_freq.max:.2f} MHz"
            
            # CPU usage
            info["cpu_percent"] = f"{psutil.cpu_percent(interval=0.1)}%"
            
            return info
        except Exception as e:
            self.logger.error(f"Error getting CPU information: {e}")
            return {"cpu_error": str(e)}
    
    def get_memory_info(self):
        """Get memory information"""
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
            self.logger.error(f"Error getting memory information: {e}")
            return {"Memory Error": str(e)}
    
    def get_disk_info(self):
        """Get disk information"""
        try:
            disks = []
            
            # Get all disk partitions
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
                    # Some volumes may not be accessible
                    continue
            
            return disks
        except Exception as e:
            self.logger.error(f"Error getting disk information: {e}")
            return []
    
    def get_network_info(self):
        """Get network information"""
        try:
            info = {}
            
            # Get hostname and IP address
            info["hostname"] = socket.gethostname()
            try:
                info["ip_address"] = socket.gethostbyname(info["hostname"])
            except:
                info["ip_address"] = "Unknown"
            
            # Get MAC address
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                  for elements in range(0, 8 * 6, 8)][::-1])
            info["mac_address"] = mac_address
            
            # Get network interfaces
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
            self.logger.error(f"Error getting network information: {e}")
            return {"error": str(e)}
    
    def format_bytes(self, bytes_value):
        """Format bytes to readable string"""
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
        """Get GPU information, prioritize GPUtil library, fallback to command line tools"""
        try:
            gpu_info = None
            # Try to use GPUtil library to get information
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    info = []
                    for gpu in gpus:
                        gpu_info = [
                            f"Name: {gpu.name}",
                            f"Memory: {gpu.memoryTotal} MB",
                            f"Driver Version: {gpu.driver}",
                            f"Memory Usage: {gpu.memoryUtil*100:.1f}%",
                            f"GPU Usage: {gpu.load*100:.1f}%",
                            f"Temperature: {gpu.temperature}°C" if hasattr(gpu, 'temperature') else "Temperature: Unknown"
                        ]
                        info.append("\n".join(gpu_info))
                    return "\n\n".join(info)
                
                # GPUtil couldn't find GPU
                gpu_info = "GPUtil didn't detect GPU, "
            
            except ImportError:
                self.logger.info("GPUtil library not available, trying command line to get GPU information")
                # Continue using command line to get information
                pass
            
            # Use system commands to get GPU information
            if self.is_windows():
                return self._get_gpu_info_windows()
            elif self.is_linux():
                return self._get_gpu_info_linux()
            elif self.is_mac():
                return self._get_gpu_info_mac()
            else:
                gpu_info += "using command line, unsupported operating system"
            
            return gpu_info
        
        except Exception as e:
            self.logger.error(f"Error getting GPU information: {str(e)}")
            return f"GPU information error: {str(e)}"
    
    def _get_gpu_info_windows(self):
        """Use wmic command to get GPU information on Windows"""
        try:
            # Try to use wmic to get information
            process = subprocess.Popen(
                ["wmic", "path", "win32_VideoController", "get", "Name,AdapterRAM,DriverVersion,VideoProcessor,DriverDate"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if stderr:
                self.logger.warning(f"wmic command execution error: {stderr}")
            
            if not stdout or stdout.strip() == "":
                # Try to use PowerShell to get information
                return self._get_gpu_info_windows_powershell()
            
            # Process wmic output
            lines = stdout.splitlines()
            if len(lines) <= 1:
                return self._get_gpu_info_windows_powershell()
            
            # Remove header and filter out empty lines
            data_lines = [line for line in lines[1:] if line.strip()]
            
            if not data_lines:
                return self._get_gpu_info_windows_powershell()
            
            # Extract GPU information
            info = []
            for i, line in enumerate(data_lines):
                parts = line.split()
                if not parts:
                    continue
                
                # Try to parse wmic output
                try:
                    # Parse AdapterRAM (usually the first number)
                    ram = None
                    processor = None
                    driver = None
                    driver_date = None
                    name_parts = []
                    
                    for part in parts:
                        if part.isdigit() and ram is None:
                            try:
                                ram = int(part) / (1024 * 1024)  # Convert to MB
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
                    
                    gpu_info = [f"Name: {name}"]
                    if processor:
                        gpu_info.append(f"Processor: {processor}")
                    if ram:
                        gpu_info.append(f"Memory: {ram:.0f} MB")
                    if driver:
                        gpu_info.append(f"Driver Version: {driver}")
                    if driver_date:
                        gpu_info.append(f"Driver Date: {driver_date}")
                    
                    # If too little information, try to use dxdiag to get more information
                    if len(gpu_info) < 3:
                        dxdiag_info = self._get_gpu_info_windows_dxdiag(i)
                        if dxdiag_info and "Name:" in dxdiag_info:
                            gpu_info = dxdiag_info.split("\n")
                    
                    info.append("\n".join(gpu_info))
                except Exception as e:
                    self.logger.warning(f"Error parsing GPU line: {e}")
                    info.append(f"GPU {i+1}: {line}")
            
            return "\n\n".join(info) if info else self._get_gpu_info_windows_powershell()
            
        except Exception as e:
            self.logger.error(f"Windows GPU information acquisition failed: {str(e)}")
            return self._get_gpu_info_windows_powershell()
    
    def _get_gpu_info_windows_powershell(self):
        """Use PowerShell to get GPU information"""
        try:
            process = subprocess.Popen(
                ["powershell", "-Command", "Get-WmiObject win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion, VideoProcessor, DriverDate | Format-List"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if stderr:
                self.logger.warning(f"PowerShell command execution error: {stderr}")
            
            if not stdout or stdout.strip() == "":
                # Try to use DirectX diagnostic tool
                return self._get_gpu_info_windows_dxdiag()
            
            # Process PowerShell output
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
                        current_gpu.append(f"Name: {value}")
                    elif key == "AdapterRAM":
                        try:
                            ram = int(value) / (1024 * 1024)
                            current_gpu.append(f"Memory: {ram:.0f} MB")
                        except:
                            if value:
                                current_gpu.append(f"Memory: {value}")
                    elif key == "DriverVersion":
                        current_gpu.append(f"Driver Version: {value}")
                    elif key == "VideoProcessor":
                        current_gpu.append(f"Processor: {value}")
                    elif key == "DriverDate":
                        current_gpu.append(f"Driver Date: {value}")
            
            if current_gpu:
                info.append("\n".join(current_gpu))
            
            return "\n\n".join(info) if info else self._get_gpu_info_windows_dxdiag()
            
        except Exception as e:
            self.logger.error(f"PowerShell GPU information acquisition failed: {str(e)}")
            return self._get_gpu_info_windows_dxdiag()
            
    def _get_gpu_info_windows_dxdiag(self, gpu_index=None):
        """Use DirectX diagnostic tool to get GPU information"""
        try:
            # Create temporary file for output
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
                tmp_path = tmp.name
            
            # Run dxdiag and output to file
            process = subprocess.Popen(
                ["dxdiag", "/t", tmp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            process.communicate()
            
            # Wait a moment for dxdiag to complete output
            time.sleep(2)
            
            # Read output file
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
                
                # Add the last GPU section
                if current_section and display_section:
                    gpu_sections.append(current_section)
                
                # Clean up temporary file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                
                # Parse GPU information
                if gpu_index is not None and 0 <= gpu_index < len(gpu_sections):
                    # Return GPU information for specified index
                    return self._parse_dxdiag_display_section(gpu_sections[gpu_index])
                else:
                    # Return all GPU information
                    info = []
                    for section in gpu_sections:
                        parsed = self._parse_dxdiag_display_section(section)
                        if parsed:
                            info.append(parsed)
                    
                    return "\n\n".join(info) if info else "No GPU detected"
                
            except Exception as e:
                self.logger.error(f"Failed to read dxdiag output: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"DirectX diagnostic tool execution failed: {str(e)}")
            return "Failed to get GPU information"
    
    def _parse_dxdiag_display_section(self, section_lines):
        """Parse DxDiag display device section"""
        gpu_info = []
        
        for line in section_lines:
            if ":" not in line:
                continue
                
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            if "Card name" in key:
                gpu_info.append(f"Name: {value}")
            elif "Manufacturer" in key:
                gpu_info.append(f"Manufacturer: {value}")
            elif "Chip type" in key:
                gpu_info.append(f"Chip Type: {value}")
            elif "Display Memory" in key:
                gpu_info.append(f"Memory: {value}")
            elif "Driver Version" in key or "Driver" in key and "Version" in key:
                gpu_info.append(f"Driver Version: {value}")
            elif "Driver Date/Size" in key:
                gpu_info.append(f"Driver Date: {value.split(',')[0]}")
            elif "Current Mode" in key:
                gpu_info.append(f"Current Mode: {value}")
            elif "Monitor Model" in key:
                gpu_info.append(f"Monitor Model: {value}")
            elif "Monitor Name" in key:
                gpu_info.append(f"Monitor: {value}")
        
        return "\n".join(gpu_info) if gpu_info else None

    def _get_gpu_info_linux(self):
        """Use lspci command to get GPU information on Linux"""
        try:
            # Check if lspci command is available
            try:
                subprocess.check_output(["which", "lspci"])
            except:
                return "Cannot get GPU information: lspci command not available"
            
            # Get graphics card information
            process = subprocess.Popen(
                ["lspci", "-vnn", "|", "grep", "-i", "VGA", "-A", "12"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if stderr:
                self.logger.warning(f"lspci command execution error: {stderr}")
            
            if not stdout or stdout.strip() == "":
                # Try nvidia-smi command (if NVIDIA graphics card is available)
                try:
                    process = subprocess.Popen(
                        ["nvidia-smi", "--query-gpu=name,memory.total,driver_version,utilization.gpu,temperature.gpu", "--format=csv,noheader"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    stdout, stderr = process.communicate()
                    
                    if stderr and "not found" in stderr:
                        return "No NVIDIA GPU detected"
                    
                    if not stdout or stdout.strip() == "":
                        return "No GPU detected"
                    
                    # Process nvidia-smi output
                    info = []
                    for i, line in enumerate(stdout.splitlines()):
                        if not line.strip():
                            continue
                        
                        parts = line.split(",")
                        if len(parts) >= 5:
                            gpu_info = [
                                f"Name: {parts[0].strip()}",
                                f"Memory: {parts[1].strip()}",
                                f"Driver Version: {parts[2].strip()}",
                                f"GPU Usage: {parts[3].strip()}",
                                f"Temperature: {parts[4].strip()}"
                            ]
                            info.append("\n".join(gpu_info))
                        else:
                            info.append(f"GPU {i+1}: {line.strip()}")
                    
                    return "\n\n".join(info) if info else "No GPU detected"
                    
                except Exception as e:
                    self.logger.warning(f"nvidia-smi command execution error: {e}")
                    return "No GPU detected"
            
            # Process lspci output
            info = []
            gpu_blocks = stdout.split("\n\n")
            
            for i, block in enumerate(gpu_blocks):
                if not block.strip():
                    continue
                
                lines = block.splitlines()
                gpu_name = "Unknown GPU"
                gpu_info = []
                
                for line in lines:
                    line = line.strip()
                    if "VGA compatible controller" in line or "3D controller" in line:
                        # Extract GPU name
                        parts = line.split(":")
                        if len(parts) > 2:
                            gpu_name = parts[2].strip()
                        else:
                            gpu_name = line
                    
                    if "Memory" in line or "memory" in line:
                        gpu_info.append(f"Memory: {line}")
                    if "Kernel driver in use" in line:
                        gpu_info.append(f"Driver: {line.split(':')[1].strip()}")
                    if "Kernel modules" in line:
                        gpu_info.append(f"Module: {line.split(':')[1].strip()}")
                
                block_info = [f"Name: {gpu_name}"]
                block_info.extend(gpu_info)
                info.append("\n".join(block_info))
            
            return "\n\n".join(info) if info else "No GPU detected"
            
        except Exception as e:
            self.logger.error(f"Linux GPU information acquisition failed: {str(e)}")
            return f"Failed to get GPU information: {str(e)}"
    
    def _get_gpu_info_mac(self):
        """Use system_profiler command to get GPU information on macOS"""
        try:
            # Use system_profiler to get GPU information
            process = subprocess.Popen(
                ["system_profiler", "SPDisplaysDataType"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if stderr:
                self.logger.warning(f"system_profiler command execution error: {stderr}")
            
            if not stdout or stdout.strip() == "":
                return "No GPU detected"
            
            # Process system_profiler output
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
                            current_gpu.append(f"Name: {parts[1].strip()}")
                elif in_graphics_card:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        if "VRAM" in key:
                            current_gpu.append(f"Memory: {value.strip()}")
                        elif "Vendor" in key:
                            current_gpu.append(f"Vendor: {value.strip()}")
                        elif "Device" in key:
                            current_gpu.append(f"Device ID: {value.strip()}")
                        elif "Metal" in key:
                            current_gpu.append(f"Metal Support: {value.strip()}")
                    
                    if "Displays" in line:
                        in_graphics_card = False
            
            # Add the last GPU
            if current_gpu:
                info.append("\n".join(current_gpu))
            
            return "\n\n".join(info) if info else "No GPU detected"
            
        except Exception as e:
            self.logger.error(f"macOS GPU information acquisition failed: {str(e)}")
            return f"Failed to get GPU information: {str(e)}" 
        
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
        """Get disk table data
        
        Returns:
            list: List containing disk information, each element is a dictionary containing device, mountpoint, fstype, total, used, etc.
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
            self.logger.error(f"Error getting disk table data: {e}")
            return [{
                'device': "Error",
                'mountpoint': str(e),
                'fstype': "",
                'total': "",
                'used': ""
            }]

    def get_network_interfaces_data(self):
        """Get network interface table data
        
        Returns:
            list: List containing network interface information, each element is a dictionary containing name, address, netmask, status, etc.
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
                        
                        # Get interface status
                        try:
                            stats = psutil.net_if_stats()
                            if name in stats:
                                interface_info['status'] = "Up" if stats[name].isup else "Down"
                        except:
                            pass
                        
                        interface_data.append(interface_info)
            
            return interface_data
        
        except Exception as e:
            self.logger.error(f"Error getting network interface table data: {e}")
            return []

    def get_drives(self):
        """Get list of all system drives, alias for get_drives_list"""
        return self.get_drives_list()

    def get_temperature(self):
        """Get system temperature information, compatible with different operating systems"""
        current_time = time.time()
        
        # Check if need to wait longer before retrying
        if self._temp_failure_count > 1:
            time_elapsed = current_time - self._temp_last_attempt
            if time_elapsed < self._temp_retry_delay:
                self.logger.info(f"Waiting for retry cycle {self._temp_retry_delay} seconds, {self._temp_retry_delay - time_elapsed:.1f} seconds until next attempt")
                # Return N/A directly to avoid frequent errors
                return {"CPU": "N/A", "System": "N/A"}
        
        # Update attempt time
        self._temp_last_attempt = current_time
        
        try:
            temperature_data = {}
            
            # Try to use psutil.sensors_temperatures() to get temperature
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    for chip, sensors in temps.items():
                        for sensor in sensors:
                            label = sensor.label or f"{chip}_{sensors.index(sensor)}"
                            temperature_data[label] = f"{sensor.current:.1f}°C"
                    # Successfully got temperature, reset failure count and delay
                    self._temp_failure_count = 0
                    self._temp_retry_delay = 1
                    return temperature_data
            
            # On Windows system, try to use WMI to get temperature
            if self.is_windows():
                try:
                    import wmi
                    w = wmi.WMI(namespace="root\\wmi")
                    temperature_info = w.MSAcpi_ThermalZoneTemperature()[0]
                    # Convert to Celsius (original value is Kelvin * 10)
                    temp_celsius = (temperature_info.CurrentTemperature / 10) - 273.15
                    temperature_data["CPU"] = f"{temp_celsius:.1f}°C"
                    # Successfully got temperature, reset failure count and delay
                    self._temp_failure_count = 0
                    self._temp_retry_delay = 1
                    return temperature_data
                except Exception as e:
                    self.logger.warning(f"Failed to get WMI temperature information: {e}")
            
            # On Linux system, try to read temperature from /sys/class/thermal
            if self.is_linux():
                try:
                    thermal_zones = [f for f in os.listdir("/sys/class/thermal") if f.startswith("thermal_zone")]
                    for zone in thermal_zones:
                        try:
                            with open(f"/sys/class/thermal/{zone}/temp", "r") as f:
                                temp = int(f.read().strip()) / 1000  # Usually in millidegrees Celsius
                            with open(f"/sys/class/thermal/{zone}/type", "r") as f:
                                zone_type = f.read().strip()
                            temperature_data[zone_type] = f"{temp:.1f}°C"
                        except:
                            pass
                    if temperature_data:
                        # Successfully got temperature, reset failure count and delay
                        self._temp_failure_count = 0
                        self._temp_retry_delay = 1
                        return temperature_data
                except Exception as e:
                    self.logger.warning(f"Failed to read Linux temperature information: {e}")
            
            # If all above methods fail, increase failure count and extend retry time
            self._temp_failure_count += 1
            
            # If consecutive failures exceed twice, exponentially increase delay time
            if self._temp_failure_count >= 2:
                self._temp_retry_delay = min(self._temp_retry_delay * 2, self._MAX_RETRY_DELAY)
                self.logger.info(f"Consecutive {self._temp_failure_count} temperature acquisition failures, next retry delay increased to {self._temp_retry_delay} seconds")
            
            # If all above methods fail, return N/A
            self.logger.info("Cannot get real temperature data, returning N/A")
            temperature_data["CPU"] = "N/A"
            temperature_data["System"] = "N/A"
            return temperature_data
            
        except Exception as e:
            # Also increase failure count and extend retry time when error occurs
            self._temp_failure_count += 1
            if self._temp_failure_count >= 2:
                self._temp_retry_delay = min(self._temp_retry_delay * 2, self._MAX_RETRY_DELAY)
                self.logger.info(f"Consecutive {self._temp_failure_count} temperature acquisition failures, next retry delay increased to {self._temp_retry_delay} seconds")
                
            self.logger.error(f"Error getting temperature information: {e}")
            return {"Error": f"Failed to get temperature: {str(e)}"}

    def get_system_temperatures(self):
        """Alias for getting system temperatures"""
        return self.get_temperature()

class BaseThread(QThread):
    """Base thread class for all application threads"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger('GlaryUtilities')
        self.platform_manager = PlatformManager()

