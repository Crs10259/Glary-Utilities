import os
from pathlib import Path
from functools import lru_cache
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Icons")

class App:
    version = "1.0.0"
    MAX_DATA_POINTS = 60

class Path:
    # Base resource paths
    BASE_DIR = Path(__file__).parent.parent.absolute()
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
    ICONS_DIR = os.path.join(RESOURCES_DIR, "icons")
    THEMES_DIR = os.path.join(RESOURCES_DIR, "themes")
    TRANSLATIONS_DIR = os.path.join(RESOURCES_DIR, "translations")

class ResourceManager:
    """Resource manager class for unified management of application resources"""
    
    _initialized = False

    @classmethod
    def ensure_directory(cls, directory):
        """Ensure directory exists"""
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
            except Exception as e:
                logger.error(f"Error creating directory {directory}: {e}")
    
    @classmethod
    def initialize(cls):
        """Initialize resource directory structure"""
        if cls._initialized:
            return True
            
        logger.info("Initializing resource manager...")
        
        # Ensure all resource directories exist
        cls.ensure_directory(Path.RESOURCES_DIR)
        cls.ensure_directory(Path.ICONS_DIR)
        cls.ensure_directory(Path.THEMES_DIR)
 
        cls._initialized = True
        logger.info("Resource manager initialization completed")
        return True

class Icon:
    """Icon management class for handling application icons"""
    
    @staticmethod
    @lru_cache()
    def exists(path):
        """Check if icon file exists at specified path"""
        try:
            # Fix file path checking method
            if os.path.isabs(path):
                full_path = path
            else:
                # Get project root directory
                full_path = os.path.normpath(os.path.join(Path.BASE_DIR, path))
            
            return os.path.exists(full_path) and os.path.isfile(full_path)
        except Exception as e:
            logger.error(f"Error checking if icon exists {path}: {str(e)}")
            return False
    
    @staticmethod
    @lru_cache()
    def get_path(path):
        """Get complete path of icon file"""
        try:
            # Fix file path getting method
            if os.path.isabs(path):
                full_path = path
            else:
                # Get project root directory
                full_path = os.path.normpath(os.path.join(Path.BASE_DIR, path))
            
            # Check if file exists
            if os.path.exists(full_path) and os.path.isfile(full_path):
                return full_path
            else:
                logger.warning(f"Icon file not found: {full_path}")
                # Return placeholder icon path
                return os.path.join(Path.ICONS_DIR, "placeholder.svg")
        except Exception as e:
            logger.error(f"Error getting icon path {path}: {str(e)}")
            return os.path.join(Path.ICONS_DIR, "placeholder.svg")

    @staticmethod
    def ensure_dir_exists(dir_path):
        """Ensure icon directory exists"""
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Error creating directory {dir_path}: {str(e)}")
            return False
    
    class Icon:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "icon.png"))
        Path = _path
        Exist = os.path.exists(_path)
        
    class Dashboard:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "dashboard.svg"))
        Path = _path
        Exist = os.path.exists(_path)

    class Privacy:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "privacy.svg"))
        Path = _path
        Exist = os.path.exists(_path)
        
    class Driver:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "driver.svg"))
        Path = _path
        Exist = os.path.exists(_path)
        
    class Cleaner:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "clean.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class GPU:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "cpu.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class Repair:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "registry.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class Dism:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "dism.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class Network:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "network.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class Disk:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "disk.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class Boot:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "startup.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class Virus:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "virus.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class Settings:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "settings.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class Arrow:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "down-arrow.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class Optimize:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "optimize.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class Clean:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "clean.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class CPU:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "cpu.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class Memory:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "memory.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class Temperature:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "temperature.svg"))
        Path = _path
        Exist = os.path.exists(_path)
    
    class Info:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "info.svg"))
        Path = _path
        Exist = os.path.exists(_path)
        
    class SystemInfo:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "info.svg"))
        Path = _path
        Exist = os.path.exists(_path)
        
    class Check:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "check.svg"))
        Path = _path
        Exist = os.path.exists(_path)
        
    class Close:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "close.svg"))
        Path = _path
        Exist = os.path.exists(_path)
        
    class Undock:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "undock.svg"))
        Path = _path
        Exist = os.path.exists(_path)
        
    class Minimize:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "minimize.svg"))
        Path = _path
        Exist = os.path.exists(_path)
        
    class Maximize:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "maximize.svg"))
        Path = _path
        Exist = os.path.exists(_path)
        
    class Restore:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "restore.svg"))
        Path = _path
        Exist = os.path.exists(_path)
        
    class DownArrow:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "down-arrow.svg"))
        Path = _path
        Exist = os.path.exists(_path)
        
    class UpArrow:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "up-arrow.svg"))
        Path = _path
        Exist = os.path.exists(_path)
        
    class Help:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "help.svg"))
        Path = _path
        Exist = os.path.exists(_path)
        
    class About:
        _path = os.path.normpath(os.path.join(Path.ICONS_DIR, "about.svg"))
        Path = _path
        Exist = os.path.exists(_path)

# Initialize resource manager
ResourceManager.initialize()
