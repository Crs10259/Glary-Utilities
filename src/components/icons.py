import os

class IconInfo:
    """存储图标信息的类"""
    def __init__(self, name, path):
        self.Name = name
        self.Path = path
        self.Exist = os.path.exists(path)

class Icons:
    """管理应用程序图标的类"""
    def __init__(self):
        # 基本路径
        self.base_path = "assets/images"
        
        # 应用程序图标
        self.Icon = IconInfo("Icon", os.path.join(self.base_path, "icon.png"))
        
        # 工具栏图标
        self.Home = IconInfo("Home", os.path.join(self.base_path, "home.png"))
        self.Cleaner = IconInfo("Cleaner", os.path.join(self.base_path, "cleaner.png"))
        self.GPU = IconInfo("GPU", os.path.join(self.base_path, "gpu.png"))
        self.Repair = IconInfo("Repair", os.path.join(self.base_path, "repair.png"))
        self.DISM = IconInfo("DISM", os.path.join(self.base_path, "dism.png"))
        self.Network = IconInfo("Network", os.path.join(self.base_path, "network.png"))
        self.Disk = IconInfo("Disk", os.path.join(self.base_path, "disk.png"))
        self.Boot = IconInfo("Boot", os.path.join(self.base_path, "boot.png"))
        self.Virus = IconInfo("Virus", os.path.join(self.base_path, "virus.png"))
        self.Settings = IconInfo("Settings", os.path.join(self.base_path, "settings.png"))
        
        # 其他图标
        self.Arrow = IconInfo("Arrow", os.path.join(self.base_path, "arrow.png"))
        self.CPU = IconInfo("CPU", os.path.join(self.base_path, "cpu.png"))
        self.Memory = IconInfo("Memory", os.path.join(self.base_path, "memory.png"))
        self.Temperature = IconInfo("Temperature", os.path.join(self.base_path, "temperature.png"))
        self.Optimize = IconInfo("Optimize", os.path.join(self.base_path, "optimize.png"))
        self.Clean = IconInfo("Clean", os.path.join(self.base_path, "clean.png"))
        self.Info = IconInfo("Info", os.path.join(self.base_path, "info.png"))

# 创建单例实例
Icon = Icons()

class Icon:
    class Home:
        Path = "assets/images/home.png"
        Exist = os.path.exists(Path)
    class Cleaner:
        Path = "assets/images/cleaner.png"
        Exist = os.path.exists(Path)
    class GPU:
        Path = "assets/images/gpu.png"
        Exist = os.path.exists(Path)
    class Repair:
        Path = "assets/images/repair.png"
        Exist = os.path.exists(Path)
    class Dism:
        Path = "assets/images/dism.png"
        Exist = os.path.exists(Path)
    class Network:
        Path = "assets/images/network.png"
        Exist = os.path.exists(Path)
    class Disk:
        Path = "assets/images/disk.png"
        Exist = os.path.exists(Path)
    class Boot:
        Path = "assets/images/boot.png"
        Exist = os.path.exists(Path)
    class Virus:
        Path = "assets/images/virus.png"
        Exist = os.path.exists(Path)
    class Settings:
        Path = "assets/images/settings.png"
        Exist = os.path.exists(Path)
    class Icon:
        Path = "assets/images/icon.png"
        Exist = os.path.exists(Path)
    class Arrow:
        Path = "assets/images/arrow.png"
        Exist = os.path.exists(Path)
    class Optimize:
        Path = "assets/images/optimize.png"
        Exist = os.path.exists(Path)
    class Clean:
        Path = "assets/images/clean.png"
        Exist = os.path.exists(Path)
    class Junk:
        Path = "assets/images/junk.png"
        Exist = os.path.exists(Path)
    class CPU:
        Path = "assets/images/cpu.png"
        Exist = os.path.exists(Path)
    class Memory:
        Path = "assets/images/memory.png"
        Exist = os.path.exists(Path)
    class Temperature:
        Path = "assets/images/temperature.png"
        Exist = os.path.exists(Path)
    class Info:
        Path = "assets/images/info.png"
        Exist = os.path.exists(Path)
        

