import os
from PyQt5.QtGui import QIcon, QPixmap, QMovie

class ResourceManager:
    """资源管理器类，用于统一管理应用程序资源"""
    
    # 资源目录定义
    RESOURCES_DIR = "resources"
    IMAGES_DIR = os.path.join(RESOURCES_DIR, "images")
    ICONS_DIR = os.path.join(RESOURCES_DIR, "icons")
    THEMES_DIR = os.path.join(RESOURCES_DIR, "themes")
    
    @classmethod
    def get_image_path(cls, image_name):
        """获取图片文件路径"""
        return os.path.join(cls.IMAGES_DIR, image_name)
    
    @classmethod
    def get_icon_path(cls, icon_name):
        """获取图标文件路径"""
        return os.path.join(cls.ICONS_DIR, icon_name)
    
    @classmethod
    def get_theme_path(cls, theme_name):
        """获取主题文件路径"""
        return os.path.join(cls.THEMES_DIR, theme_name)
    
    @classmethod
    def get_pixmap(cls, image_name, directory=None):
        """获取QPixmap对象"""
        if directory is None:
            directory = cls.IMAGES_DIR
        path = os.path.join(directory, image_name)
        return QPixmap(path)
    
    @classmethod
    def get_icon(cls, icon_name):
        """获取QIcon对象"""
        path = cls.get_icon_path(icon_name)
        return QIcon(path)
    
    @classmethod
    def get_movie(cls, gif_name):
        """获取QMovie对象"""
        path = cls.get_image_path(gif_name)
        return QMovie(path)
    
    @classmethod
    def ensure_directory(cls, directory):
        """确保目录存在"""
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    @classmethod
    def initialize(cls):
        """初始化资源目录结构"""
        # 确保所有资源目录存在
        cls.ensure_directory(cls.RESOURCES_DIR)
        cls.ensure_directory(cls.IMAGES_DIR)
        cls.ensure_directory(cls.ICONS_DIR)
        cls.ensure_directory(cls.THEMES_DIR)
        
        return True 