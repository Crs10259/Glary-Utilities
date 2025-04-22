import os
import sys
import logging
from functools import lru_cache

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Icons")

# Constants - 修改为正确的资源路径
RESOURCES_DIR = "resources"
ICONS_DIR = f"{RESOURCES_DIR}/icons"

class IconBase:
    @staticmethod
    @lru_cache()
    def exists(path):
        """Check if an icon file exists at the given path"""
        try:
            # 修正文件路径检查方式
            if os.path.isabs(path):
                full_path = path
            else:
                # 获取项目根目录（不是src目录）
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                full_path = os.path.join(base_dir, path)
            
            return os.path.exists(full_path) and os.path.isfile(full_path)
        except Exception as e:
            logger.error(f"Error checking if icon exists at {path}: {str(e)}")
            return False
    
    @staticmethod
    @lru_cache()
    def get_path(path):
        """Get the full path to an icon file"""
        try:
            # 修正文件路径获取方式
            if os.path.isabs(path):
                full_path = path
            else:
                # 获取项目根目录（不是src目录）
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                full_path = os.path.join(base_dir, path)
            
            # Check if the file exists
            if os.path.exists(full_path) and os.path.isfile(full_path):
                return full_path
            else:
                logger.warning(f"Icon file not found: {full_path}")
                # 返回一个默认图标路径
                return os.path.join(base_dir, RESOURCES_DIR, "icons", "placeholder.svg")
        except Exception as e:
            logger.error(f"Error getting icon path for {path}: {str(e)}")
            return path

    @staticmethod
    def ensure_dir_exists(dir_path):
        """Ensure that the directory for icons exists"""
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Error creating directory {dir_path}: {str(e)}")
            return False

def initialize_icons():
    """Initialize all icon paths and check for existence"""
    # 获取项目根目录（不是src目录）
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    icons_dir = os.path.join(base_dir, ICONS_DIR)
    
    # 确保图标目录存在
    if not os.path.exists(icons_dir):
        logger.warning(f"Icons directory not found: {icons_dir}")
        IconBase.ensure_dir_exists(icons_dir)
    
    # 创建默认图标和占位符图标（如果不存在）
    placeholder_path = os.path.join(icons_dir, "placeholder.svg")
    if not os.path.exists(placeholder_path):
        try:
            # 创建一个简单的SVG占位符图标
            with open(placeholder_path, 'w') as f:
                f.write('''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                    <rect width="24" height="24" fill="#cccccc"/>
                    <text x="12" y="16" font-family="Arial" font-size="12" text-anchor="middle" fill="#666666">?</text>
                </svg>''')
            logger.info(f"Created placeholder icon at {placeholder_path}")
        except Exception as e:
            logger.error(f"Error creating placeholder icon: {e}")

class Icon:
    """Icon manager class that handles all application icons"""
    
    class Icon:
        _path = f"{RESOURCES_DIR}/icons/icon.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
        
    class Home:
        _path = f"{ICONS_DIR}/dashboard.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Cleaner:
        _path = f"{ICONS_DIR}/clean.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class GPU:
        _path = f"{ICONS_DIR}/cpu.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Repair:
        _path = f"{ICONS_DIR}/driver.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Dism:
        _path = f"{ICONS_DIR}/optimize.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Network:
        _path = f"{ICONS_DIR}/disk.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Disk:
        _path = f"{ICONS_DIR}/disk.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Boot:
        _path = f"{ICONS_DIR}/startup.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Virus:
        _path = f"{ICONS_DIR}/virus.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Settings:
        _path = f"{ICONS_DIR}/settings.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Arrow:
        _path = f"{ICONS_DIR}/minimize.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Optimize:
        _path = f"{ICONS_DIR}/optimize.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Clean:
        _path = f"{ICONS_DIR}/clean.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class CPU:
        _path = f"{ICONS_DIR}/cpu.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Memory:
        _path = f"{ICONS_DIR}/memory.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Temperature:
        _path = f"{ICONS_DIR}/temperature.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Info:
        _path = f"{ICONS_DIR}/info.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
        
    class SystemInfo:
        _path = f"{ICONS_DIR}/info.svg"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)

# 初始化图标
initialize_icons()
