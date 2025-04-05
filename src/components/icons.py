import os
import sys
import logging
from functools import lru_cache

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Icons")

# Constants
ASSETS_DIR = "assets/images"

class IconBase:
    @staticmethod
    @lru_cache()
    def exists(path):
        """Check if an icon file exists at the given path"""
        try:
            # Get the base directory (src folder)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
            # Get the base directory (src folder)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            full_path = os.path.join(base_dir, path)
            
            # Check if the file exists
            if os.path.exists(full_path) and os.path.isfile(full_path):
                return full_path
            else:
                logger.warning(f"Icon file not found: {full_path}")
                # Return a placeholder or default icon
                placeholder = os.path.join(base_dir, "assets", "images", "placeholder.png")
                if os.path.exists(placeholder):
                    return placeholder
                else:
                    return path  # Return original path if placeholder doesn't exist
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
    # Get the base directory (src folder)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, ASSETS_DIR)
    
    # Ensure the assets directory exists
    if not os.path.exists(assets_dir):
        logger.warning(f"Assets directory not found: {assets_dir}")
        IconBase.ensure_dir_exists(assets_dir)

class Icon:
    """Icon manager class that handles all application icons"""
    
    class Icon:
        _path = f"{ASSETS_DIR}/icon.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
        
    class Home:
        _path = f"{ASSETS_DIR}/home.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Cleaner:
        _path = f"{ASSETS_DIR}/cleaner.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class GPU:
        _path = f"{ASSETS_DIR}/gpu.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Repair:
        _path = f"{ASSETS_DIR}/repair.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Dism:
        _path = f"{ASSETS_DIR}/dism.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Network:
        _path = f"{ASSETS_DIR}/network.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Disk:
        _path = f"{ASSETS_DIR}/disk.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Boot:
        _path = f"{ASSETS_DIR}/boot.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Virus:
        _path = f"{ASSETS_DIR}/virus.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Settings:
        _path = f"{ASSETS_DIR}/settings.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Arrow:
        _path = f"{ASSETS_DIR}/arrow.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Optimize:
        _path = f"{ASSETS_DIR}/optimize.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Clean:
        _path = f"{ASSETS_DIR}/clean.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class CPU:
        _path = f"{ASSETS_DIR}/cpu.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Memory:
        _path = f"{ASSETS_DIR}/memory.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Temperature:
        _path = f"{ASSETS_DIR}/temperature.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
    
    class Info:
        _path = f"{ASSETS_DIR}/info.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)
        
    class SystemInfo:
        _path = f"{ASSETS_DIR}/system_info.png"
        Path = IconBase.get_path(_path)
        Exist = IconBase.exists(_path)

# Initialize icons when the module is imported
initialize_icons()
