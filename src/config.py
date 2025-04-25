import os
import sys
from PyQt5.QtGui import QIcon, QPixmap, QMovie
from pathlib import Path
from functools import lru_cache
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Icons")

version = "1.0.0"

# 基础资源路径
BASE_DIR = Path(__file__).parent
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
ICONS_DIR = os.path.join(RESOURCES_DIR, "icons")
THEMES_DIR = os.path.join(RESOURCES_DIR, "themes")
TRANSLATIONS_DIR = os.path.join(RESOURCES_DIR, "translations")

class ResourceManager:
    """资源管理器类，用于统一管理应用程序资源"""
    
    _initialized = False

    @classmethod
    def ensure_directory(cls, directory):
        """确保目录存在"""
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                logger.info(f"创建目录: {directory}")
            except Exception as e:
                logger.error(f"创建目录时出错 {directory}: {e}")
    
    @classmethod
    def initialize(cls):
        """初始化资源目录结构"""
        if cls._initialized:
            return True
            
        logger.info("初始化资源管理器...")
        
        # 确保所有资源目录存在
        cls.ensure_directory(RESOURCES_DIR)
        cls.ensure_directory(ICONS_DIR)
        cls.ensure_directory(THEMES_DIR)
        
        # 创建缺失的图标
        cls._create_default_icons()
        
        cls._initialized = True
        logger.info("资源管理器初始化完成")
        return True
        
    @classmethod
    def _create_default_icons(cls):
        """创建默认图标文件如果他们不存在"""
        # 确保有一个占位符图标
        placeholder_path = os.path.join(ICONS_DIR, "placeholder.svg")
        if not os.path.exists(placeholder_path):
            try:
                with open(placeholder_path, 'w', encoding='utf-8') as f:
                    f.write('''<svg width="24" height="24" xmlns="http://www.w3.org/2000/svg">
                        <rect width="24" height="24" fill="#cccccc" />
                        <text x="12" y="16" font-family="Arial" font-size="12" text-anchor="middle" fill="#666666">?</text>
                    </svg>''')
                logger.info(f"创建了占位符图标: {placeholder_path}")
            except Exception as e:
                logger.error(f"创建占位符图标时出错: {e}")

class Icon:
    """图标管理类，用于处理应用程序图标"""
    
    @staticmethod
    @lru_cache()
    def exists(path):
        """检查指定路径的图标文件是否存在"""
        try:
            # 修正文件路径检查方式
            if os.path.isabs(path):
                full_path = path
            else:
                # 获取项目根目录
                full_path = os.path.join(BASE_DIR, path)
            
            return os.path.exists(full_path) and os.path.isfile(full_path)
        except Exception as e:
            logger.error(f"检查图标是否存在时出错 {path}: {str(e)}")
            return False
    
    @staticmethod
    @lru_cache()
    def get_path(path):
        """获取图标文件的完整路径"""
        try:
            # 修正文件路径获取方式
            if os.path.isabs(path):
                full_path = path
            else:
                # 获取项目根目录
                full_path = os.path.join(BASE_DIR, path)
            
            # 检查文件是否存在
            if os.path.exists(full_path) and os.path.isfile(full_path):
                return full_path
            else:
                logger.warning(f"Icon file not found: {full_path}")
                # 返回占位符图标路径
                return os.path.join(ICONS_DIR, "placeholder.svg")
        except Exception as e:
            logger.error(f"获取图标路径时出错 {path}: {str(e)}")
            return os.path.join(ICONS_DIR, "placeholder.svg")

    @staticmethod
    def ensure_dir_exists(dir_path):
        """确保图标目录存在"""
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"创建目录时出错 {dir_path}: {str(e)}")
            return False
    
    class Icon:
        _path = os.path.join(ICONS_DIR, "icon.png")
        Path = _path
        Exist = os.path.exists(_path)
        
    class Dashboard:
        _path = os.path.join(ICONS_DIR, "dashboard.svg")
        Path = _path
        Exist = os.path.exists(_path)

    class Privacy:
        _path = os.path.join(ICONS_DIR, "privacy.svg")
        Path = _path
        Exist = os.path.exists(_path)
        
    class Driver:
        _path = os.path.join(ICONS_DIR, "driver.svg")
        Path = _path
        Exist = os.path.exists(_path)
        
    class Cleaner:
        _path = os.path.join(ICONS_DIR, "clean.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class GPU:
        _path = os.path.join(ICONS_DIR, "cpu.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class Repair:
        _path = os.path.join(ICONS_DIR, "registry.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class Dism:
        _path = os.path.join(ICONS_DIR, "dism.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class Network:
        _path = os.path.join(ICONS_DIR, "network.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class Disk:
        _path = os.path.join(ICONS_DIR, "disk.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class Boot:
        _path = os.path.join(ICONS_DIR, "startup.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class Virus:
        _path = os.path.join(ICONS_DIR, "virus.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class Settings:
        _path = os.path.join(ICONS_DIR, "settings.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class Arrow:
        _path = os.path.join(ICONS_DIR, "down-arrow.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class Optimize:
        _path = os.path.join(ICONS_DIR, "optimize.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class Clean:
        _path = os.path.join(ICONS_DIR, "clean.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class CPU:
        _path = os.path.join(ICONS_DIR, "cpu.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class Memory:
        _path = os.path.join(ICONS_DIR, "memory.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class Temperature:
        _path = os.path.join(ICONS_DIR, "temperature.svg")
        Path = _path
        Exist = os.path.exists(_path)
    
    class Info:
        _path = os.path.join(ICONS_DIR, "info.svg")
        Path = _path
        Exist = os.path.exists(_path)
        
    class SystemInfo:
        _path = os.path.join(ICONS_DIR, "info.svg")
        Path = _path
        Exist = os.path.exists(_path)
        
    class Check:
        _path = os.path.join(ICONS_DIR, "check.svg")
        Path = _path
        Exist = os.path.exists(_path)
        
    class Close:
        _path = os.path.join(ICONS_DIR, "close.svg")
        Path = _path
        Exist = os.path.exists(_path)
        
    class Undock:
        _path = os.path.join(ICONS_DIR, "undock.svg")
        Path = _path
        Exist = os.path.exists(_path)
        
    class Minimize:
        _path = os.path.join(ICONS_DIR, "minimize.svg")
        Path = _path
        Exist = os.path.exists(_path)
        
    class Maximize:
        _path = os.path.join(ICONS_DIR, "maximize.svg")
        Path = _path
        Exist = os.path.exists(_path)
        
    class Restore:
        _path = os.path.join(ICONS_DIR, "restore.svg")
        Path = _path
        Exist = os.path.exists(_path)
        
    class DownArrow:
        _path = os.path.join(ICONS_DIR, "down-arrow.svg")
        Path = _path
        Exist = os.path.exists(_path)
        
    class UpArrow:
        _path = os.path.join(ICONS_DIR, "up-arrow.svg")
        Path = _path
        Exist = os.path.exists(_path)

# 初始化资源管理器
ResourceManager.initialize()
